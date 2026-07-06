#!/usr/bin/env python
"""Installe la protection de branche LOCALE (garde-fous git) dans le repo cible.

Idempotent. Modele : `install_test_hooks.py`. Etapes :
  1. copie `.githooks/{branch_guard.py, pre-push, pre-commit, protected-branches?}` a la racine du
     depot git (dossier `.githooks/`, commite -> partage par l'equipe) ;
  2. rend `pre-push`/`pre-commit` executables (best-effort ; no-op sous Windows) ;
  3. active les hooks pour CE clone : `git -C <racine> config core.hooksPath .githooks` ;
  4. pose (par FUSION) un hook `SessionStart` dans `.claude/settings.json` qui relance
     `git config core.hooksPath .githooks` a chaque ouverture de session -> reactivation AUTOMATIQUE
     pour quiconque ouvre le repo dans Claude Code (plus besoin de le lancer a la main) ;
  5. consigne dans le manifeste : `architecture.branch_protection` (read-modify-write).

Usage : python install_branch_protection.py <racine-du-repo-cible>
"""
import json
import os
import stat
import subprocess
import sys

HOOK_FILES = ("branch_guard.py", "pre-push", "pre-commit")
EXEC_FILES = ("pre-push", "pre-commit")
PROTECTED_DEFAULT = ["main", "master"]
HOOKS_PATH_CMD = "git config core.hooksPath .githooks"
SESSIONSTART = {"hooks": [{"type": "command", "command": HOOKS_PATH_CMD, "timeout": 5}]}


def _load_manifest(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _install_session_hook(root, notes):
    """Fusionne un hook SessionStart qui reactive core.hooksPath a chaque session (pattern couts).

    Ne JAMAIS ecraser un evenement existant (ex. SessionEnd du compteur de couts). Idempotent.
    """
    settings = os.path.join(root, ".claude", "settings.json")
    os.makedirs(os.path.dirname(settings), exist_ok=True)
    data = {}
    if os.path.isfile(settings):
        try:
            data = json.load(open(settings, encoding="utf-8")) or {}
        except ValueError:
            print(f"ATTENTION: {settings} JSON invalide — hook SessionStart non pose (pas d'ecrasement).",
                  file=sys.stderr)
            return
    hooks = data.setdefault("hooks", {})
    ss = hooks.setdefault("SessionStart", [])
    if any("core.hooksPath" in (h.get("command") or "") for g in ss for h in g.get("hooks", [])):
        notes.append("SessionStart deja present")
    else:
        ss.append(SESSIONSTART)
        notes.append("SessionStart ajoute (reactive core.hooksPath a chaque session)")
    try:
        with open(settings, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    except OSError as exc:
        print(f"ATTENTION: settings.json non ecrit ({exc}).", file=sys.stderr)


def main(argv):
    if len(argv) < 2:
        print("ERREUR: usage: install_branch_protection.py <racine-du-repo-cible>", file=sys.stderr)
        return 1
    root = os.path.abspath(argv[1])
    if not os.path.isdir(root):
        print(f"ERREUR: racine introuvable: {root}", file=sys.stderr)
        return 1

    # Les hooks git ne fonctionnent qu'a la RACINE DU DEPOT git : `core.hooksPath` (meme relatif)
    # est resolu par git relativement au toplevel, pas au sous-dossier courant. Si le cwd est un
    # sous-dossier du depot, poser `.githooks/` dans le cwd serait IGNORE par git. On installe donc
    # toujours a la racine du depot.
    try:
        top = subprocess.run(
            ["git", "-C", root, "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        git_root = os.path.abspath(top) if top else root
    except (OSError, subprocess.CalledProcessError):
        print("ATTENTION: pas un depot git — protection de branche non posee. "
              "Initialise un depot (git init) puis relance.", file=sys.stderr)
        return 0  # non bloquant : sans git, pas de protection possible

    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".githooks")
    dst_dir = os.path.join(git_root, ".githooks")
    os.makedirs(dst_dir, exist_ok=True)
    notes = []
    if os.path.normcase(git_root) != os.path.normcase(root):
        notes.append(f"hooks poses a la racine du depot ({git_root}), pas dans le sous-dossier courant")

    # 1-2. Copier les hooks + rendre executables.
    # Normaliser en fins de ligne LF : `pre-push`/`pre-commit` sont execute's via leur shebang par
    # git (y compris sous Windows, via le sh embarque) — un CRLF dans le shebang casse l'interpreteur.
    for name in HOOK_FILES:
        src = os.path.join(src_dir, name)
        if not os.path.isfile(src):
            print(f"ERREUR: fichier source manquant: {src}", file=sys.stderr)
            return 1
        dst = os.path.join(dst_dir, name)
        with open(src, encoding="utf-8") as fsrc:
            content = fsrc.read()
        with open(dst, "w", encoding="utf-8", newline="\n") as fdst:
            fdst.write(content)
        if name in EXEC_FILES:
            try:
                st = os.stat(dst)
                os.chmod(dst, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            except OSError:
                pass
    notes.append(f"hooks copies: {', '.join(HOOK_FILES)}")

    # 3. Activer pour ce clone (config posee sur le depot, hooksPath relatif a sa racine).
    try:
        subprocess.run(
            ["git", "-C", git_root, "config", "core.hooksPath", ".githooks"],
            check=True, capture_output=True, text=True,
        )
        notes.append("core.hooksPath = .githooks (ce clone)")
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ATTENTION: impossible de poser core.hooksPath ({exc}). "
              f"Lance manuellement: git config core.hooksPath .githooks", file=sys.stderr)

    # 4. Hook SessionStart : reactive core.hooksPath a chaque session (auto pour toute l'equipe).
    _install_session_hook(root, notes)

    # 5. Manifeste (best-effort, silencieux si absent).
    manifest_path = os.path.join(root, ".factory", "manifest.json")
    manifest = _load_manifest(manifest_path)
    if manifest is not None:
        arch = manifest.setdefault("architecture", {})
        arch["branch_protection"] = {
            "installed": True,
            "hooks_path": ".githooks",
            "protected": PROTECTED_DEFAULT,
        }
        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
                f.write("\n")
            notes.append("manifeste: architecture.branch_protection")
        except OSError as exc:
            print(f"ATTENTION: manifeste non mis a jour ({exc}).", file=sys.stderr)

    print("PROTECTION DE BRANCHE OK - " + " ; ".join(notes))
    print("Reactivation AUTOMATIQUE a chaque session (hook SessionStart). Limites : la 1re session "
          "Claude Code demande la confiance des hooks (un 'oui' par personne) ; un dev hors Claude "
          "Code ou un '--no-verify' contourne — seule barriere non contournable : ruleset serveur GitHub + CI.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
