#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase design.

Lit le manifeste partage d'un projet (factory-docs/manifest.json par defaut) et echoue si
le contrat de design est incomplet :
  - bloc `design` absent ;
  - maquette validee non referencee ;
  - tokens DTCG non ecrits (fichier absent) ;
  - aucun composant ;
  - un composant sans etats definis ;
  - aucun parcours (couverture des use cases non figee) ;
  - front-end non aligne / format de livraison des tokens absent ;
  - cible d'accessibilite absente.

La validation de couverture (`coverage_validated`) reste une porte HUMAINE : ce script ne
la verifie pas, comme la coherence de l'architecte. Exit 0 si tout est present, sinon 1.

Usage:
    python check_design.py [chemin/vers/manifest.json]
"""
import json
import sys


def main(argv):
    path = argv[1] if len(argv) > 1 else "factory-docs/manifest.json"
    try:
        with open(path, encoding="utf-8") as f:
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

    if not design.get("source_maquette"):
        problems.append("maquette validee non referencee (source_maquette)")

    tokens = design.get("tokens") or {}
    if not tokens.get("file"):
        problems.append("tokens DTCG non ecrits (aucun fichier de tokens)")

    components = design.get("components") or []
    if not components:
        problems.append("aucun composant defini")

    states = design.get("component_states") or {}
    for comp in components:
        comp_states = states.get(comp) if isinstance(states, dict) else None
        if not comp_states:
            problems.append(f"composant '{comp}' sans etats definis")

    if not design.get("journeys"):
        problems.append("aucun parcours (couverture des use cases non figee)")

    align = design.get("stack_alignment") or {}
    if not align.get("frontend"):
        problems.append("front-end non aligne sur la stack de l'architecte")
    if not align.get("token_delivery"):
        problems.append("format de livraison des tokens absent")

    access = design.get("accessibility") or {}
    if not access.get("standard") or not access.get("target"):
        problems.append("cible d'accessibilite (standard/niveau) absente")

    if problems:
        print("DESIGN INCOMPLET - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("DESIGN OK - contrat de design present et coherent.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
