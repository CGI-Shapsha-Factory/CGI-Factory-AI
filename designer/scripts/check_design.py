#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase design (atelier de couverture).

Le plugin ne genere PAS le design system (il nait dans Claude Design, son export est committe dans
designer-out/maquette-de-claude-design/). Ce garde-fou valide la COUVERTURE de l'atelier, pas des tokens.

Lit le manifeste partage d'un projet (`manifest.json` a la racine par defaut ; repli
`cadrage-out/manifest.json` legacy) et echoue si :
  - bloc `design` absent ;
  - checklist absente ou un bloc vide (foundation / experience / technical) ;
  - un item de checklist au statut `open` (couverture incomplete) ;
  - un item avec un statut invalide (hors open/deduced/decided/sans_objet) ;
  - prompt Claude Design non genere (prompt_path) ou fichier absent du disque ;
  - rapport de couverture absent (coverage_report_path) ou fichier absent du disque ;
  - handoff design (guidelines) absent (guidelines_path) ou fichier absent du disque ;
  - export du design system absent ou vide (designer-out/maquette-de-claude-design/ :
    au moins un fichier, dossier d'export ou ZIP committe).

Les chemins du manifeste sont resolus depuis la racine du projet (le dossier du manifeste ;
pour le repli legacy cadrage-out/manifest.json, son dossier parent).

Les portes `coverage_sufficient` et `design_validated` restent des gestes HUMAINS : ce script
ne les force jamais. Exit 0 si tout est present, sinon 1.

Usage:
    python check_design.py [chemin/vers/manifest.json]
"""
import json
import os
import sys

VALID_STATUS = {"open", "deduced", "decided", "sans_objet"}


def _manifest_path(argv):
    """Manifeste a la racine (`manifest.json`) par defaut ; repli `cadrage-out/manifest.json` (legacy)."""
    if len(argv) > 1:
        return argv[1]
    return "manifest.json" if os.path.isfile("manifest.json") else "cadrage-out/manifest.json"


def main(argv):
    path = _manifest_path(argv)
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

    # Racine du projet : dossier du manifeste (repli legacy : parent de cadrage-out/).
    root = os.path.dirname(os.path.abspath(path))
    if os.path.basename(root) == "cadrage-out":
        root = os.path.dirname(root)

    def _resolve(p):
        return p if os.path.isabs(p) else os.path.join(root, p)

    for field, label in (("prompt_path", "prompt Claude Design non genere"),
                         ("coverage_report_path", "rapport de couverture absent"),
                         ("guidelines_path", "handoff design (guidelines) absent")):
        val = design.get(field)
        if not val:
            problems.append(f"{label} ({field})")
        elif not os.path.isfile(_resolve(val)):
            problems.append(f"{label} : fichier introuvable sur le disque ({field} = {val})")

    maquette = os.path.join(root, "designer-out", "maquette-de-claude-design")
    has_export = False
    if os.path.isdir(maquette):
        for _dirpath, _dirnames, filenames in os.walk(maquette):
            if filenames:
                has_export = True
                break
    if not has_export:
        problems.append("export du design system absent ou vide "
                        "(designer-out/maquette-de-claude-design/ : deposer l'export ou le ZIP committe)")

    if problems:
        print("DESIGN INCOMPLET - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"DESIGN OK - couverture complete ({total} items statues), "
          "prompt + rapport + handoff + export presents sur le disque.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
