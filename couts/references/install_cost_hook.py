#!/usr/bin/env python
"""Installe (par FUSION) le hook SessionEnd du compteur de cout dans .claude/settings.json.

Ne JAMAIS ecraser les hooks existants (ex. Stop/PostToolUse poses par l'architecte) : on lit le
fichier, on ajoute l'evenement SessionEnd s'il manque, on reecrit. Idempotent.

Usage : python install_cost_hook.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import sys

COMMAND = "python .claude/hooks/session_cost.py"
MARKER = "session_cost.py"


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
            print(f"ERREUR: {settings} n'est pas un JSON valide — abandon (pas d'ecrasement).",
                  file=sys.stderr)
            return 1

    hooks = data.setdefault("hooks", {})
    session_end = hooks.setdefault("SessionEnd", [])

    # deja installe ?
    for group in session_end:
        for h in group.get("hooks", []):
            if MARKER in (h.get("command") or ""):
                print("SessionEnd (cout) deja present — rien a faire.")
                return 0

    session_end.append({"hooks": [{"type": "command", "command": COMMAND, "timeout": 30}]})
    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    others = [e for e in hooks if e != "SessionEnd"]
    print(f"SessionEnd (cout) ajoute a {settings}"
          + (f" ; evenements preserves : {', '.join(others)}" if others else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
