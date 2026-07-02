#!/usr/bin/env python
"""Installe (par FUSION) les hooks de test (Stop + PostToolUse) dans .claude/settings.json.

Ne JAMAIS ecraser un evenement existant (ex. le hook `SessionEnd` du compteur de couts) : on lit
le fichier, on ajoute Stop/PostToolUse s'ils manquent, on reecrit. Idempotent, ordre-independant.

Usage : python install_test_hooks.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import sys

MARKER = "tests_guard.py"
ENTRIES = {
    "PostToolUse": {"matcher": "Write|Edit",
                    "hooks": [{"type": "command",
                               "command": "python .claude/hooks/tests_guard.py posttooluse",
                               "timeout": 30}]},
    "Stop": {"matcher": "*",
             "hooks": [{"type": "command",
                        "command": "python .claude/hooks/tests_guard.py stop",
                        "timeout": 60}]},
}


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
            print(f"ERREUR: {settings} JSON invalide — abandon (pas d'ecrasement).", file=sys.stderr)
            return 1

    hooks = data.setdefault("hooks", {})
    added = []
    for event, entry in ENTRIES.items():
        arr = hooks.setdefault(event, [])
        if any(MARKER in (h.get("command") or "") for g in arr for h in g.get("hooks", [])):
            continue
        arr.append(entry)
        added.append(event)
    with open(settings, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"hooks de test : {('ajoutes ' + ', '.join(added)) if added else 'deja presents'}"
          f" ; evenements presents : {', '.join(sorted(hooks))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
