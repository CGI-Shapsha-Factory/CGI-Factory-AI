#!/usr/bin/env python
"""Installe le hook d'alignement SpecKit : copie le garde-fou PUIS fusionne le hook PostToolUse.

Deux gestes deterministes (jamais laisses au modele), miroir de l'enforcement architecte et du hook
sync tasks->Linear :
  1. COPIE `check_speckit_alignment.py` (depuis `assembleur/scripts/`) -> `<racine>/.claude/hooks/`
     (jamais d'ecrasement — idempotent).
  2. FUSIONNE le hook `PostToolUse` (matcher Write|Edit) dans `.claude/settings.json` SANS ecraser un
     hook existant (tests_guard/format_guard de l'architecte, tasks_linear_hook, SessionEnd des couts).

Le garde-fou detecte, a chaque edition d'un fichier sous `specs/<dir>/`, un numero de feature en
collision / timestamp / hors registre canonique, et pousse l'agent a recreer le dossier avec
`SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug`. Il ne parle a aucun systeme externe.

Usage : python install_align_hook.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import shutil
import sys

MARKER = "check_speckit_alignment.py"
CMD = 'python "${CLAUDE_PROJECT_DIR}/.claude/hooks/check_speckit_alignment.py" posttooluse'
ENTRY = {"matcher": "Write|Edit",
         "hooks": [{"type": "command", "command": CMD, "timeout": 30}]}

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "scripts", "check_speckit_alignment.py")


def _copy_asset(root):
    dst = os.path.join(root, ".claude", "hooks", "check_speckit_alignment.py")
    if os.path.isfile(dst):
        print("garde-fou alignement SpecKit : deja present (.claude/hooks/check_speckit_alignment.py)")
        return
    if not os.path.isfile(SRC):
        print(f"ATTENTION: source introuvable, non copiee : {SRC}", file=sys.stderr)
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(SRC, dst)
    print("garde-fou alignement SpecKit : copie -> .claude/hooks/check_speckit_alignment.py")


def main(argv):
    root = os.path.abspath(argv[1] if len(argv) > 1 else os.getcwd())
    claude_dir = os.path.join(root, ".claude")
    settings = os.path.join(claude_dir, "settings.json")
    os.makedirs(claude_dir, exist_ok=True)

    _copy_asset(root)

    data = {}
    if os.path.isfile(settings):
        try:
            data = json.load(open(settings, encoding="utf-8")) or {}
        except ValueError:
            print(f"ERREUR: {settings} JSON invalide — abandon (pas d'ecrasement).", file=sys.stderr)
            return 1

    arr = data.setdefault("hooks", {}).setdefault("PostToolUse", [])
    found = any(MARKER in (h.get("command") or "")
                for g in arr for h in g.get("hooks", []))
    if found:
        print("hook PostToolUse alignement SpecKit : deja enregistre dans .claude/settings.json")
        return 0
    arr.append(ENTRY)
    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"hook PostToolUse alignement SpecKit : ajoute ; evenements presents : {', '.join(sorted(data['hooks']))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
