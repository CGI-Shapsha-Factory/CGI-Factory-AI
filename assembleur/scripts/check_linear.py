#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la creation des tickets Linear (init-issues-linear).

Le skill `init-issues-linear` cree UN ticket Linear par feature approuvee (via le MCP linear-prism)
et consigne le resultat dans le bloc `linear` du manifeste. Ce garde-fou lit le manifeste
(.factory/manifest.json par defaut) et echoue si :
  - le bloc `linear` est absent (le skill n'a pas tourne) ;
  - une feature de `architecture.feature_sequence` n'est PAS traitee (ni ticket, ni decision
    explicite skipped/merged dans `linear.issues`) ;
  - un ticket marque `status: "created"` n'a pas d'identifiant Linear (`issue_id`/`identifier`).

Un ticket `skipped` / `merged` compte comme "traite" (le user a pu fusionner/ecarter des features
dans la boucle interactive). Exit 0 si tout est coherent, sinon 1.

Usage:
    python check_linear.py [chemin/vers/manifest.json]
"""
import json
import sys

# statuts consideres comme "traites" sans exiger d'identifiant Linear.
NON_CREATED_STATUSES = {"skipped", "merged", "draft"}


def main(argv):
    path = argv[1] if len(argv) > 1 else ".factory/manifest.json"
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
        print("ERREUR: bloc `linear` absent (lancer init-issues-linear).", file=sys.stderr)
        return 1

    issues = linear.get("issues") or []
    by_id = {it.get("id"): it for it in issues if isinstance(it, dict) and it.get("id")}
    problems = []

    # 1. Couverture : chaque feature de la sequence est traitee (ticket OU decision explicite).
    seq = (manifest.get("architecture") or {}).get("feature_sequence") or []
    for it in seq:
        fid = it.get("id") if isinstance(it, dict) else it
        if fid and fid not in by_id:
            problems.append(f"feature '{fid}' non traitee par init-issues-linear (ni ticket, ni skip/merge)")

    # 2. Coherence : un ticket "created" doit porter un identifiant Linear.
    for it in issues:
        if not isinstance(it, dict):
            continue
        status = (it.get("status") or "created").lower()
        if status in NON_CREATED_STATUSES:
            continue
        if not (it.get("issue_id") or it.get("identifier")):
            fid = it.get("id") or it.get("name") or "?"
            problems.append(f"ticket feature '{fid}' marque cree sans identifiant Linear")

    if problems:
        print("TICKETS LINEAR INCOMPLETS - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    n = sum(1 for it in issues if (it.get("status") or "created").lower() not in NON_CREATED_STATUSES)
    print(f"TICKETS LINEAR OK - {n} ticket(s) cree(s), une feature = une decision.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
