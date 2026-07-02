#!/usr/bin/env python
"""Installe (par FUSION) les hooks du compteur de cout dans .claude/settings.json.

- `Stop`       -> `turn_cost.py turn`      : mesure EN TEMPS REEL, une ligne par tour.
- `SessionEnd` -> `turn_cost.py reconcile` : backstop (rattrape un tour rate).

Ne JAMAIS ecraser les hooks existants (ex. `Stop`/`PostToolUse` de test poses par l'architecte) :
on lit le fichier, on ajoute les evenements manquants, on reecrit. Idempotent, ordre-independant.
Notre hook `Stop` NE BLOQUE JAMAIS (exit 0) : il coexiste avec le `Stop` de test qui, lui, peut bloquer.

Usage : python install_cost_hook.py [racine_projet]   (defaut : cwd)
"""
import json
import os
import sys

MARKER = "turn_cost.py"
ENTRIES = {
    "Stop": {"hooks": [{"type": "command",
                        "command": "python .claude/hooks/turn_cost.py turn", "timeout": 30}]},
    "SessionEnd": {"hooks": [{"type": "command",
                              "command": "python .claude/hooks/turn_cost.py reconcile", "timeout": 30}]},
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
    print(f"compteur de cout : {('ajoute ' + ', '.join(added)) if added else 'deja present'}"
          f" ; evenements presents : {', '.join(sorted(hooks))}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
