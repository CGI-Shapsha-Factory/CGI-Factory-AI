#!/usr/bin/env python
"""Installe le hook de FORMATAGE PostToolUse (format_guard.py) dans un projet.

Trois gestes atomiques (jamais laisses au modele - lecon du hook de test) :
  1. COPIE `format_guard.py` -> `<racine>/.claude/hooks/` (sans ecraser un fichier existant).
  2. COPIE la config du formateur `ruff.toml` -> `<racine>/conventions/python/ruff.toml` (sans
     ecraser) - c'est le fichier que le hook passe a `ruff format --config` (preferences completes).
  3. FUSIONNE un hook `PostToolUse` (matcher Write|Edit) dans `.claude/settings.json`, SANS ecraser
     un evenement/hook existant (ex. le PostToolUse de tests_guard, le SessionEnd du compteur de couts).
Sans l'etape 1, le hook enregistre pointerait vers un script absent (hook mort). Sans l'etape 2, le
hook retomberait sur les seuls reglages de `.editorconfig`.

Usage : python install_format_hook.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import shutil
import sys

MARKER = "format_guard.py"
# Chemin ANCRE sur la racine via ${CLAUDE_PROJECT_DIR} (un chemin relatif nu casse quand le
# hook tourne depuis un sous-dossier). Cf. install_test_hooks.py.
CMD = 'python "${CLAUDE_PROJECT_DIR}/.claude/hooks/format_guard.py"'
ENTRY = {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": CMD, "timeout": 30}],
}
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, ".claude", "hooks", "format_guard.py")
RUFF_SRC = os.path.join(HERE, "..", "conventions", "python", "ruff.toml")
RUFF_REL = os.path.join("conventions", "python", "ruff.toml")


def _copy_no_overwrite(src, dst):
    """Copie src->dst sans ecraser ; renvoie 'copie' | 'deja present' | 'source manquante'."""
    if os.path.isfile(dst):
        return "deja present"
    if not os.path.isfile(src):
        return "source manquante"
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    shutil.copyfile(src, dst)
    return "copie"


def main(argv):
    root = os.path.abspath(argv[1] if len(argv) > 1 else os.getcwd())
    hooks_dir = os.path.join(root, ".claude", "hooks")
    os.makedirs(hooks_dir, exist_ok=True)

    dst = os.path.join(hooks_dir, "format_guard.py")
    if os.path.isfile(dst):
        copied = "deja present"
    elif os.path.isfile(SRC):
        shutil.copyfile(SRC, dst)
        copied = "copie"
    else:
        print(f"ATTENTION: source introuvable, hook de formatage non pose: {SRC}", file=sys.stderr)
        return 1

    ruff_state = _copy_no_overwrite(RUFF_SRC, os.path.join(root, RUFF_REL))

    settings = os.path.join(root, ".claude", "settings.json")
    data = {}
    if os.path.isfile(settings):
        try:
            data = json.load(open(settings, encoding="utf-8")) or {}
        except ValueError:
            print(f"ERREUR: {settings} JSON invalide - abandon (pas d'ecrasement).", file=sys.stderr)
            return 1

    arr = data.setdefault("hooks", {}).setdefault("PostToolUse", [])
    present, upgraded = False, False
    for g in arr:
        for h in g.get("hooks", []):
            if MARKER in (h.get("command") or ""):
                present = True
                if h.get("command") != CMD:  # migre un ancien chemin relatif nu
                    h["command"] = CMD
                    upgraded = True
    if not present:
        arr.append(ENTRY)
    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    posttooluse = "migre -> CLAUDE_PROJECT_DIR" if upgraded else ("deja present" if present else "ajoute")
    print(f"hook de formatage : script {copied} ; ruff.toml {ruff_state} ; PostToolUse {posttooluse}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
