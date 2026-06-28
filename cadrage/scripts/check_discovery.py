#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la passe decouverte.

Lit le manifeste d'un projet (factory-docs/manifest.json par defaut) et echoue
si la couverture des 13 questions de cadrage est incomplete :
  - une question au statut `pending` -> non posee, trou bloquant.

Aucune provenance n'est exigee (on n'ecrit pas de `source`). Une question
`deferred` (laissee de cote par l'utilisateur) ou `na` est toleree.

Exit 0 si tout est couvert (answered, na, ou deferred), sinon 1.
Reutilisable a la main, en hook git, ou en CI (socle deterministe de la factory).

Usage:
    python check_discovery.py [chemin/vers/manifest.json]
"""
import json
import sys

REQUIRED_IDS = [f"Q{i}" for i in range(1, 14)]
OK_STATUSES = {"answered", "na", "deferred"}


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
        if status not in OK_STATUSES:
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
