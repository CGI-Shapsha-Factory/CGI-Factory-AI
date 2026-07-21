#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase maintenance (anomalies et evolutions).

La maintenance ne produit pas d'artefacts commites : les objets (anomalies, evolutions, statuts,
commentaires) vivent dans Linear, et les mises a jour de specification vivent dans specs/
(SpecKit). Ce garde-fou valide donc le RACCORDEMENT de la maintenance, pas un dossier de sortie.

Lit le manifeste partage d'un projet (`manifest.json` a la racine par defaut ; repli
`cadrage-out/manifest.json` legacy) et echoue si :
  - bloc `maintenance` absent ;
  - equipe Linear non retenue (team) ;
  - labels `Anomalie` / `Evolution` non resolus (UUID null) ;
  - statut de requalification mal declare (nom vide ou drapeau de presence non booleen) ;
  - gabarits absents de `.factory/maintenance/` (relancer maintenance-init).

Le drapeau `present` du statut de requalification reflete un constat (le statut existe dans
l'equipe Linear) : ce script ne le force jamais, et `present: false` n'est pas bloquant en soi
(la marche a suivre manuelle est affichee par maintenance-init). Exit 0 si tout est present, sinon 1.

Usage:
    python check_maintenance.py [chemin/vers/manifest.json]
"""
import json
import os
import sys

GABARITS = ("gabarit-anomalie.md", "gabarit-evolution.md")


def _manifest_path(argv):
    """Manifeste a la racine (`manifest.json`) par defaut ; repli `cadrage-out/manifest.json` (legacy)."""
    if len(argv) > 1:
        return argv[1]
    return "manifest.json" if os.path.isfile("manifest.json") else "cadrage-out/manifest.json"


def _project_root(manifest_path):
    """Racine du projet : le dossier du manifeste (remonte d'un cran si manifeste legacy dans cadrage-out/)."""
    root = os.path.dirname(os.path.abspath(manifest_path))
    if os.path.basename(root) == "cadrage-out":
        root = os.path.dirname(root)
    return root


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

    maintenance = manifest.get("maintenance")
    if not isinstance(maintenance, dict):
        print("ERREUR: bloc `maintenance` absent (lancer maintenance-init).", file=sys.stderr)
        return 1

    problems = []

    if not maintenance.get("team"):
        problems.append("equipe Linear non retenue (relancer maintenance-init avec le MCP linear-prism disponible)")

    labels = maintenance.get("labels")
    if not isinstance(labels, dict):
        problems.append("labels de maintenance absents du manifeste (relancer maintenance-init)")
    else:
        for key in ("anomalie", "evolution"):
            if not labels.get(key):
                problems.append(f"label `{key.capitalize()}` non resolu dans Linear (relancer maintenance-init)")

    statut = maintenance.get("statut_requalification")
    if not isinstance(statut, dict):
        problems.append("statut de requalification non declare (relancer maintenance-init)")
    else:
        if not statut.get("name"):
            problems.append("statut de requalification sans nom")
        if not isinstance(statut.get("present"), bool):
            problems.append("presence du statut de requalification non verifiee (relancer maintenance-init)")

    root = _project_root(path)
    for gabarit in GABARITS:
        gpath = os.path.join(root, ".factory", "maintenance", gabarit)
        if not os.path.isfile(gpath):
            problems.append(f"gabarit manquant: .factory/maintenance/{gabarit} (relancer maintenance-init)")

    if problems:
        print("MAINTENANCE INCOMPLETE - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    statut_msg = "statut de requalification present" if statut.get("present") else \
        "statut de requalification a creer a la main (marche a suivre affichee par maintenance-init)"
    print(f"MAINTENANCE OK - equipe et labels resolus, gabarits en place, {statut_msg}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
