#!/usr/bin/env python
"""Installe (par FUSION) le compteur de cout dans .claude/settings.json :

- hook **`SessionEnd`** -> `turn_cost.py` (ecrit le journal a la fin de session ; PAS de hook par tour
  -> zero latence pendant le dev).

Ne JAMAIS ecraser un hook existant (ex. `Stop`/`PostToolUse` de test de l'architecte). Idempotent.
Usage : python install_cost_hook.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import sys

MARKER = "turn_cost.py"
SESSIONEND = {"hooks": [{"type": "command", "command": "python .claude/hooks/turn_cost.py", "timeout": 30}]}


def main(argv):
    root = os.path.abspath(argv[1] if len(argv) > 1 else os.getcwd())
    claude_dir = os.path.join(root, ".claude")
    settings = os.path.join(claude_dir, "settings.json")
    os.makedirs(claude_dir, exist_ok=True)

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
        se.append(SESSIONEND)
        notes.append("SessionEnd ajoute")

    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("compteur de cout : " + " ; ".join(notes)
          + f" ; evenements hooks : {', '.join(sorted(hooks))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
