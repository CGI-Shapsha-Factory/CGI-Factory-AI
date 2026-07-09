#!/usr/bin/env python
"""Garde-fou deterministe du dispositif de couts.

Verifie que le compteur est correctement pose et que le journal est exploitable :
  - `.factory/couts/price-table.json` present, valide, date + tiers ;
  - `.claude/hooks/turn_cost.py` present et hook SessionEnd (compteur) enregistre ;
  - chaque enregistrement du journal `.factory/couts/**/*.jsonl` parse et porte les champs attendus.

Usage : python check_costs.py [chemin/vers/manifest.json]   (defaut : manifest.json a la racine, repli cadrage-out/)
Exit 0 si OK, 1 sinon.
"""
import glob
import json
import os
import sys


def _manifest_path(argv):
    """Manifeste a la racine (`manifest.json`) par defaut ; repli `cadrage-out/manifest.json` (legacy)."""
    if len(argv) > 1:
        return argv[1]
    return "manifest.json" if os.path.isfile("manifest.json") else "cadrage-out/manifest.json"


def _project_root(manifest_path):
    """Racine = dossier du manifeste ; si le manifeste est dans `cadrage-out/` (legacy), on remonte."""
    d = os.path.dirname(os.path.abspath(manifest_path))
    return os.path.dirname(d) if os.path.basename(d) == "cadrage-out" else d


def main(argv):
    manifest = _manifest_path(argv)
    root = _project_root(manifest)
    problems = []

    cost_dir = os.path.join(root, ".factory", "couts")
    pt = os.path.join(cost_dir, "price-table.json")
    if not os.path.isfile(pt):
        problems.append("price-table.json absent (lancer couts-init)")
    else:
        try:
            d = json.load(open(pt, encoding="utf-8"))
            if not d.get("date"):
                problems.append("price-table.json sans 'date' (piege #2 : table datee)")
            if not d.get("tiers"):
                problems.append("price-table.json sans 'tiers' (haiku/sonnet/opus/fable)")
        except ValueError:
            problems.append("price-table.json JSON invalide")

    if not os.path.isfile(os.path.join(root, ".claude", "hooks", "turn_cost.py")):
        problems.append(".claude/hooks/turn_cost.py absent (hook non pose)")
    se = os.path.join(root, ".claude", "settings.json")
    if os.path.isfile(se):
        try:
            hooks = (json.load(open(se, encoding="utf-8")) or {}).get("hooks", {})
            found = any("turn_cost.py" in (h.get("command") or "")
                        for g in hooks.get("SessionEnd", []) for h in g.get("hooks", []))
            if not found:
                problems.append("hook SessionEnd du compteur (turn_cost.py) non enregistre dans .claude/settings.json")
        except ValueError:
            problems.append(".claude/settings.json JSON invalide")
    else:
        problems.append(".claude/settings.json absent (hook non pose)")

    # .gitignore doit couvrir .factory/couts/ (donnees individuelles, jamais poussees)
    gitignore = os.path.join(root, ".gitignore")
    if not os.path.isfile(gitignore):
        problems.append(".gitignore absent — .factory/couts/ non git-ignore (lancer couts-init)")
    else:
        try:
            lines_gi = open(gitignore, encoding="utf-8").read().splitlines()
            covered = any(
                line.strip() in (".factory/couts/", ".factory/couts", ".factory/")
                for line in lines_gi
            )
            if not covered:
                problems.append(
                    ".factory/couts/ non git-ignore — ajouter la ligne dans .gitignore (lancer couts-init)"
                )
        except OSError:
            problems.append(".gitignore illisible")

    required = {"session_id", "key", "tokens", "attribution"}
    for jf in glob.glob(os.path.join(root, ".factory", "couts", "**", "*.jsonl"), recursive=True):
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
