#!/usr/bin/env python
"""Installe le hook de FORMATAGE PostToolUse (format_guard.py) dans un projet.

Deux gestes atomiques (jamais laisses au modele — lecon du hook de test) :
  1. COPIE `format_guard.py` -> `<racine>/.claude/hooks/` (sans ecraser un fichier existant).
  2. FUSIONNE un hook `PostToolUse` (matcher Write|Edit) dans `.claude/settings.json`, SANS ecraser
     un evenement/hook existant (ex. le PostToolUse de tests_guard, le SessionEnd du compteur de couts).
Sans l'etape 1, le hook enregistre pointerait vers un script absent (hook mort).

Usage : python install_format_hook.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import shutil
import sys

MARKER = "format_guard.py"
ENTRY = {
    "matcher": "Write|Edit",
    "hooks": [{"type": "command", "command": "python .claude/hooks/format_guard.py", "timeout": 30}],
}
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, ".claude", "hooks", "format_guard.py")


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

    settings = os.path.join(root, ".claude", "settings.json")
    data = {}
    if os.path.isfile(settings):
        try:
            data = json.load(open(settings, encoding="utf-8")) or {}
        except ValueError:
            print(f"ERREUR: {settings} JSON invalide — abandon (pas d'ecrasement).", file=sys.stderr)
            return 1

    arr = data.setdefault("hooks", {}).setdefault("PostToolUse", [])
    present = any(MARKER in (h.get("command") or "") for g in arr for h in g.get("hooks", []))
    if not present:
        arr.append(ENTRY)
    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"hook de formatage : script {copied} ; "
          f"PostToolUse {'deja present' if present else 'ajoute'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
