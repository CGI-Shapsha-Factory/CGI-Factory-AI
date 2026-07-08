#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase design (atelier de couverture).

Le plugin ne genere PAS le design system (il nait dans Claude Design, son export est committe dans
designer-out/maquette-de-claude-design/). Ce garde-fou valide la COUVERTURE de l'atelier, pas des tokens.

Lit le manifeste partage d'un projet (cadrage-out/manifest.json par defaut) et echoue si :
  - bloc `design` absent ;
  - checklist absente ou un bloc vide (foundation / experience / technical) ;
  - un item de checklist au statut `open` (couverture incomplete) ;
  - un item avec un statut invalide (hors open/deduced/decided/sans_objet) ;
  - prompt Claude Design non genere (prompt_path) ;
  - rapport de couverture absent (coverage_report_path) ;
  - handoff design (guidelines) absent (guidelines_path).

Les portes `coverage_sufficient` et `design_validated` restent des gestes HUMAINS : ce script
ne les force jamais. Exit 0 si tout est present, sinon 1.

Usage:
    python check_design.py [chemin/vers/manifest.json]
"""
import json
import sys

VALID_STATUS = {"open", "deduced", "decided", "sans_objet"}


def main(argv):
    path = argv[1] if len(argv) > 1 else "cadrage-out/manifest.json"
    try:
        with open(path, encoding="utf-8-sig") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"ERREUR: manifeste introuvable: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERREUR: manifeste JSON invalide: {exc}", file=sys.stderr)
        return 1

    design = manifest.get("design")
    if not isinstance(design, dict):
        print("ERREUR: bloc `design` absent (lancer designer-init).", file=sys.stderr)
        return 1

    problems = []

    checklist = design.get("checklist")
    if not isinstance(checklist, dict):
        problems.append("checklist de couverture absente (lancer designer-init)")
        checklist = {}

    open_ids, bad_status = [], []
    total = 0
    for bloc in ("foundation", "experience", "technical"):
        items = checklist.get(bloc)
        if not items:
            problems.append(f"bloc de checklist `{bloc}` vide")
            continue
        for it in items:
            total += 1
            st = it.get("status") if isinstance(it, dict) else None
            iid = (it.get("id") if isinstance(it, dict) else None) or "?"
            if st not in VALID_STATUS:
                bad_status.append(iid)
            elif st == "open":
                open_ids.append(iid)

    if bad_status:
        problems.append("items au statut invalide : " + ", ".join(bad_status))
    if open_ids:
        problems.append("items de checklist non couverts (statut `open`) : " + ", ".join(open_ids))

    if not design.get("prompt_path"):
        problems.append("prompt Claude Design non genere (prompt_path)")
    if not design.get("coverage_report_path"):
        problems.append("rapport de couverture absent (coverage_report_path)")
    if not design.get("guidelines_path"):
        problems.append("handoff design (guidelines) absent (guidelines_path)")

    if problems:
        print("DESIGN INCOMPLET - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"DESIGN OK - couverture complete ({total} items statues), prompt + rapport + handoff presents.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
