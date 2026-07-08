#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la porte des briefs (cadrage).

Lit le manifeste d'un projet (cadrage-out/manifest.json par defaut) et echoue si la
porte DURE de `cadrage-briefs` n'est pas franchie :
  - `definition_of_ready.decoupage_arbitrated` != true (revue de couplage non faite) ;
  - `definition_of_ready.demonstrateur_converged` != true (maquette non validee client).

Empeche de finaliser des briefs sans la revue de couplage humaine ET la convergence du
demonstrateur. Exit 0 si les deux portes humaines sont franchies, sinon 1. Reutilisable a
la main, en hook git, ou en CI (socle deterministe de la factory).

Usage:
    python check_ready.py [chemin/vers/manifest.json]
"""
import json
import sys


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

    dor = manifest.get("definition_of_ready") or {}
    demo = manifest.get("demonstrateur") or {}
    problems = []
    if not dor.get("decoupage_arbitrated"):
        problems.append("revue de couplage non faite (decoupage non arbitre)")
    if not dor.get("demonstrateur_converged"):
        problems.append("maquette non validee par le client (demonstrateur non converge)")
    elif not demo.get("external_ref"):
        problems.append("demonstrateur marque converge SANS maquette referencee (external_ref nul) - validation fantome")

    if problems:
        print("BRIEFS BLOQUES - la porte n'est pas franchie :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("PORTE BRIEFS OK - revue de couplage faite et maquette validee.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
