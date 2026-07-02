#!/usr/bin/env python
"""Garde-fou deterministe du dispositif de couts.

Verifie que le compteur est correctement pose et que le journal est exploitable :
  - `.factory/cost/price-table.json` present, valide, date + modeles ;
  - `.factory/cost/cost-config.json` present et valide ;
  - `.claude/hooks/session_cost.py` present et hook SessionEnd enregistre ;
  - chaque ligne du journal `.factory/costs/**/*.jsonl` parse et porte les champs attendus.

Usage : python check_costs.py [chemin/vers/.factory/manifest.json]   (defaut : .factory/manifest.json)
Exit 0 si OK, 1 sinon.
"""
import glob
import json
import os
import sys


def main(argv):
    manifest = argv[1] if len(argv) > 1 else ".factory/manifest.json"
    root = os.path.dirname(os.path.dirname(os.path.abspath(manifest)))
    problems = []

    cost_dir = os.path.join(root, ".factory", "cost")
    pt = os.path.join(cost_dir, "price-table.json")
    if not os.path.isfile(pt):
        problems.append("price-table.json absent (lancer couts-init)")
    else:
        try:
            d = json.load(open(pt, encoding="utf-8"))
            if not d.get("date"):
                problems.append("price-table.json sans 'date' (piege #2 : table datee)")
            if not d.get("models"):
                problems.append("price-table.json sans 'models'")
        except ValueError:
            problems.append("price-table.json JSON invalide")

    cfg = os.path.join(cost_dir, "cost-config.json")
    if not os.path.isfile(cfg):
        problems.append("cost-config.json absent (lancer couts-init)")
    else:
        try:
            json.load(open(cfg, encoding="utf-8"))
        except ValueError:
            problems.append("cost-config.json JSON invalide")

    if not os.path.isfile(os.path.join(root, ".claude", "hooks", "session_cost.py")):
        problems.append(".claude/hooks/session_cost.py absent (hook non pose)")
    se = os.path.join(root, ".claude", "settings.json")
    if os.path.isfile(se):
        try:
            hooks = (json.load(open(se, encoding="utf-8")) or {}).get("hooks", {})
            found = any("session_cost.py" in (h.get("command") or "")
                        for g in hooks.get("SessionEnd", []) for h in g.get("hooks", []))
            if not found:
                problems.append("hook SessionEnd du compteur non enregistre dans .claude/settings.json")
        except ValueError:
            problems.append(".claude/settings.json JSON invalide")
    else:
        problems.append(".claude/settings.json absent (hook non pose)")

    required = {"session_id", "tokens", "attribution"}
    for jf in glob.glob(os.path.join(root, ".factory", "costs", "**", "*.jsonl"), recursive=True):
        try:
            for i, line in enumerate(open(jf, encoding="utf-8"), 1):
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                miss = required - set(rec)
                if miss:
                    problems.append(f"{os.path.relpath(jf, root)}:{i} champs manquants {sorted(miss)}")
        except ValueError:
            problems.append(f"{os.path.relpath(jf, root)} : JSONL invalide")

    if problems:
        print("DISPOSITIF DE COUTS INCOMPLET :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("COUTS OK — compteur pose, table datee, journal exploitable.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
