#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase architecture.

Lit le manifeste partage d'un projet (.factory/manifest.json par defaut) et
echoue si le contrat technique est incomplet :
  - bloc `architecture` absent ;
  - profil d'equipe non renseigne (seule reponse demandee a l'utilisateur) ;
  - aucun composant ;
  - stack sans langage ;
  - un langage de la stack sans fichier de conventions installe ;
  - aucune feature sequencee (numerotation non figee) ;
  - walking skeleton non designe ;
  - section `Decisions a impact design` non produite (handoff designer) ;
  - un marqueur residuel ([A VALIDER]/[A CHIFFRER]/[A DEFINIR]) subsiste dans un
    fichier de `architecte-out/` (tout point doit etre tranche en session).

Exit 0 si tout est present et coherent, sinon 1. Reutilisable a la main, en hook
git, ou en CI (socle deterministe de la factory).

Usage:
    python check_architecture.py [chemin/vers/manifest.json]
"""
import glob
import json
import os
import re
import sys

MARKER_RE = re.compile(r"\[\s*(?:À|A)\s+(?:VALIDER|CHIFFRER|D[ÉE]FINIR)\s*\]", re.IGNORECASE)


def residual_markers(manifest_path):
    """Renvoie la liste (fichier, marqueur) des marqueurs residuels dans architecte-out/."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(manifest_path)))
    out_dir = os.path.join(root, "architecte-out")
    hits = []
    for md in glob.glob(os.path.join(out_dir, "**", "*.md"), recursive=True):
        try:
            text = open(md, encoding="utf-8").read()
        except OSError:
            continue
        for m in set(MARKER_RE.findall(text)):
            hits.append((os.path.relpath(md, root), m))
    return hits


def main(argv):
    path = argv[1] if len(argv) > 1 else ".factory/manifest.json"
    try:
        with open(path, encoding="utf-8") as f:
            manifest = json.load(f)
    except FileNotFoundError:
        print(f"ERREUR: manifeste introuvable: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERREUR: manifeste JSON invalide: {exc}", file=sys.stderr)
        return 1

    arch = manifest.get("architecture")
    if not isinstance(arch, dict):
        print("ERREUR: bloc `architecture` absent (lancer architecte-init).", file=sys.stderr)
        return 1

    problems = []

    if not arch.get("team_profile"):
        problems.append("profil d'equipe non renseigne (question #13 a poser)")

    if not arch.get("components"):
        problems.append("aucun composant defini")

    stack = arch.get("stack") or {}
    languages = stack.get("languages") or []
    if not languages:
        problems.append("stack sans langage")

    installed = arch.get("conventions_installed") or []
    installed_norm = {str(x).lower() for x in installed}
    for lang in languages:
        if str(lang).lower() not in installed_norm:
            problems.append(f"langage '{lang}' sans fichier de conventions installe")

    seq = arch.get("feature_sequence") or []
    if not seq:
        problems.append("liste de features numerotee/sequencee non figee")
    else:
        for it in seq:
            ucs = it.get("ucs") if isinstance(it, dict) else None
            ok = isinstance(it, dict) and it.get("id") and ((isinstance(ucs, list) and ucs) or it.get("uc"))
            if not ok:
                problems.append("feature_sequence : entree sans {id, ucs} (registre canonique incomplet)")
                break

    if not arch.get("walking_skeleton"):
        problems.append("walking skeleton non designe")

    if not arch.get("design_impact"):
        problems.append("section `Decisions a impact design` non produite (handoff designer)")

    for rel, marker in residual_markers(path):
        problems.append(f"marqueur residuel {marker} dans {rel} (a trancher en session)")

    if problems:
        print("ARCHITECTURE INCOMPLETE - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("ARCHITECTURE OK - contrat technique present et coherent.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
