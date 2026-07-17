#!/usr/bin/env python
"""Installe le compteur de cout : copie le script PUIS fusionne le hook dans .claude/settings.json.

Deux gestes deterministes (jamais laisses au modele), miroir des installeurs assembleur :
  1. COPIE `turn_cost.py` -> `<racine>/.claude/hooks/` (jamais d'ecrasement - idempotent).
  2. FUSIONNE le hook **`SessionEnd`** -> `turn_cost.py` (ecrit le journal a la fin de session ;
     PAS de hook par tour -> zero latence pendant le dev).

Le lanceur Python est detecte a l'installation (`python` / `py -3` / `python3`) et le chemin est
ancre sur `${CLAUDE_PROJECT_DIR}` (jamais un chemin relatif dependant du cwd du hook).

Ne JAMAIS ecraser un hook existant (ex. `Stop`/`PostToolUse` de test de l'architecte). Idempotent.
Usage : python install_cost_hook.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import shutil
import sys

MARKER = "turn_cost.py"

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "turn_cost.py")


def _launcher():
    """Detecte le lanceur Python disponible sur la machine (baked dans la commande du hook)."""
    if shutil.which("python"):
        return "python"
    if shutil.which("py"):
        return "py -3"
    if shutil.which("python3"):
        return "python3"
    return "python"


def _copy_asset(root):
    dst = os.path.join(root, ".claude", "hooks", "turn_cost.py")
    if os.path.isfile(dst):
        print("compteur de cout : script deja present (.claude/hooks/turn_cost.py)")
        return
    if not os.path.isfile(SRC):
        print(f"ATTENTION: source introuvable, non copiee : {SRC}", file=sys.stderr)
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(SRC, dst)
    print("compteur de cout : copie -> .claude/hooks/turn_cost.py")


def main(argv):
    root = os.path.abspath(argv[1] if len(argv) > 1 else os.getcwd())
    claude_dir = os.path.join(root, ".claude")
    settings = os.path.join(claude_dir, "settings.json")
    os.makedirs(claude_dir, exist_ok=True)

    _copy_asset(root)

    cmd = _launcher() + ' "${CLAUDE_PROJECT_DIR}/.claude/hooks/turn_cost.py"'
    sessionend = {"hooks": [{"type": "command", "command": cmd, "timeout": 30}]}

    data = {}
    if os.path.isfile(settings):
        try:
            data = json.load(open(settings, encoding="utf-8")) or {}
        except ValueError:
            print(f"ERREUR: {settings} JSON invalide - abandon (pas d'ecrasement).", file=sys.stderr)
            return 1

    notes = []
    hooks = data.setdefault("hooks", {})
    se = hooks.setdefault("SessionEnd", [])
    if any(MARKER in (h.get("command") or "") for g in se for h in g.get("hooks", [])):
        notes.append("SessionEnd deja present")
    else:
        se.append(sessionend)
        notes.append("SessionEnd ajoute")

    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("compteur de cout : " + " ; ".join(notes)
          + f" ; evenements hooks : {', '.join(sorted(hooks))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
