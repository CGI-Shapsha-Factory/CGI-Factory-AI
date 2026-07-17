#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) du pont Linear (premier-alimente-linear).

**Les tickets vivent dans Linear, jamais dans le manifeste.** La carte des tickets (Feature, Task
par FR, Task par phase) et l'etat d'avancement ont Linear pour SEULE source de verite : idempotence
via `list_issues` (titre exact pour une Feature, jetons `FR-00x -` / `Phase N -` pour les Task).
Un script local ne peut pas interroger le MCP : ce garde-fou ne valide donc QUE ce qui est
verifiable hors-ligne, honnetement :
  - le bloc `linear` est absent -> le skill n'a pas tourne (exit 1) ;
  - le bloc `linear` est present mais sans equipe (`team`) -> configuration incomplete (exit 1).

La verification des tickets eux-memes est le travail du skill (relire `list_issues` avant de
conclure) - jamais celui d'un script hors-ligne. Exit 0 si la configuration est posee, sinon 1.

Compatibilite : un manifeste historique portant encore `linear.issues[]` reste valide (le champ est
ignore - Linear fait foi).

Usage:
    python check_linear.py [chemin/vers/manifest.json]
"""
import json
import os
import sys


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

    linear = manifest.get("linear")
    if not isinstance(linear, dict):
        print("ERREUR: bloc `linear` absent (lancer premier-alimente-linear).", file=sys.stderr)
        return 1

    if not linear.get("team"):
        print("PONT LINEAR INCOMPLET - points bloquants :", file=sys.stderr)
        print("  - aucune equipe Linear configuree (relancer premier-alimente-linear)", file=sys.stderr)
        return 1

    print("PONT LINEAR OK - configuration posee (equipe definie) ; "
          "les tickets et leur etat se verifient dans Linear, pas ici.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
