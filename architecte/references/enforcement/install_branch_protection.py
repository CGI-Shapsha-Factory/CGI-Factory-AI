#!/usr/bin/env python
"""Installe la protection de branche LOCALE (garde-fous git) dans le repo cible.

Idempotent. Modele : `install_test_hooks.py`. Etapes :
  1. copie `.githooks/{branch_guard.py, pre-push, pre-commit, protected-branches?}` a la racine
     du repo cible (dossier `.githooks/`, commite -> partage par l'equipe) ;
  2. rend `pre-push`/`pre-commit` executables (best-effort ; no-op sous Windows) ;
  3. active les hooks pour CE clone : `git -C <racine> config core.hooksPath .githooks` ;
  4. consigne dans le manifeste : `architecture.branch_protection` (read-modify-write) ;
  5. rappelle que chaque collaborateur doit lancer une fois `git config core.hooksPath .githooks`
     (git n'active pas core.hooksPath depuis une config commitee -> limite de l'approche locale).

Usage : python install_branch_protection.py <racine-du-repo-cible>
"""
import json
import os
import stat
import subprocess
import sys

HOOK_FILES = ("branch_guard.py", "pre-push", "pre-commit")
EXEC_FILES = ("pre-push", "pre-commit")
PROTECTED_DEFAULT = ["main", "master", "develop"]


def _load_manifest(path):
    if not os.path.isfile(path):
        return None
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def main(argv):
    if len(argv) < 2:
        print("ERREUR: usage: install_branch_protection.py <racine-du-repo-cible>", file=sys.stderr)
        return 1
    root = os.path.abspath(argv[1])
    if not os.path.isdir(root):
        print(f"ERREUR: racine introuvable: {root}", file=sys.stderr)
        return 1

    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".githooks")
    dst_dir = os.path.join(root, ".githooks")
    os.makedirs(dst_dir, exist_ok=True)
    notes = []

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

    # 3. Activer pour ce clone.
    try:
        subprocess.run(
            ["git", "-C", root, "config", "core.hooksPath", ".githooks"],
            check=True, capture_output=True, text=True,
        )
        notes.append("core.hooksPath = .githooks (ce clone)")
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"ATTENTION: impossible de poser core.hooksPath ({exc}). "
              f"Lance manuellement: git config core.hooksPath .githooks", file=sys.stderr)

    # 4. Manifeste (best-effort, silencieux si absent).
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
    print("Rappel (par-clone) : chaque collaborateur lance une fois, a la racine du repo :")
    print("    git config core.hooksPath .githooks")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
