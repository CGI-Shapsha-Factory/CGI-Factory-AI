#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la passe decouverte.

Lit le manifeste d'un projet (`manifest.json` a la racine par defaut ; repli
`cadrage-out/manifest.json` legacy) et echoue si la couverture des 19 questions de cadrage est incomplete :
  - une question au statut `pending` -> non posee, trou bloquant.

Aucune provenance n'est exigee (on n'ecrit pas de `source`). Une question
`deferred` (laissee de cote par l'utilisateur) ou `na` est toleree en mode par defaut.

Deux modes :
  - defaut (mi-parcours, cadrage-extraction) : exit 0 si tout est couvert (answered, na, deferred) ;
  - `--strict` (porte Definition of Ready, cadrage-completude) : une question `deferred` est AUSSI
    bloquante (le verdict DoR reste rouge tant qu'une question est laissee de cote) ; seuls
    `answered` et `na` passent.

Reutilisable a la main, en hook git, ou en CI (socle deterministe de la factory).

Usage:
    python check_discovery.py [--strict] [chemin/vers/manifest.json]
"""
import json
import os
import sys

REQUIRED_IDS = [f"Q{i}" for i in range(1, 20)]
OK_STATUSES = {"answered", "na", "deferred"}
STRICT_OK_STATUSES = {"answered", "na"}


def _manifest_path(args):
    """Manifeste a la racine (`manifest.json`) par defaut ; repli `cadrage-out/manifest.json` (legacy)."""
    if args:
        return args[0]
    return "manifest.json" if os.path.isfile("manifest.json") else "cadrage-out/manifest.json"


def main(argv):
    strict = "--strict" in argv[1:]
    args = [a for a in argv[1:] if a != "--strict"]
    ok_statuses = STRICT_OK_STATUSES if strict else OK_STATUSES
    path = _manifest_path(args)
    try:
        with open(path, encoding="utf-8-sig") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"ERREUR: manifeste introuvable: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERREUR: manifeste JSON invalide: {exc}", file=sys.stderr)
        return 1

    discovery = manifest.get("discovery")
    if not isinstance(discovery, list):
        print("ERREUR: bloc `discovery` absent ou invalide dans le manifeste.", file=sys.stderr)
        return 1

    by_id = {entry.get("id"): entry for entry in discovery if isinstance(entry, dict)}
    problems = []

    for qid in REQUIRED_IDS:
        entry = by_id.get(qid)
        if entry is None:
            problems.append(f"{qid}: question absente du bloc discovery")
            continue
        status = entry.get("status")
        if status not in ok_statuses:
            if strict and status == "deferred":
                problems.append(f"{qid}: statut `deferred` (laissee de cote - bloquant pour la DoR)")
            else:
                problems.append(f"{qid}: statut `{status}` (question non posee)")
            continue

    if problems:
        print("DISCOVERY INCOMPLETE - trous bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"DISCOVERY OK - les {len(REQUIRED_IDS)} questions sont couvertes.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
