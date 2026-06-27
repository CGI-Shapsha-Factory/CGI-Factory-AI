#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la phase convergence (assembleur).

Lit le manifeste partage d'un projet (factory-docs/manifest.json par defaut) et echoue si la
convergence est incomplete :
  - bloc `assembly` absent ;
  - repo SpecKit cible non renseigne ;
  - constitution / CLAUDE.md / glossaire / MEMORY.md non generes ;
  - plan d'attaque absent ;
  - une feature de `architecture.feature_sequence` sans ses 3 faces (functional, technical,
    design) ou marquee non coherente.

Les portes HUMAINES (`coherence_validated`, `team_validated`, `linear_initialized`) ne sont
PAS verifiees ici - comme la coherence de l'architecte / la couverture du designer. Exit 0 si
tout est present, sinon 1.

Usage:
    python check_assembly.py [chemin/vers/manifest.json]
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

    asm = manifest.get("assembly")
    if not isinstance(asm, dict):
        print("ERREUR: bloc `assembly` absent (lancer assembleur-init).", file=sys.stderr)
        return 1

    problems = []

    if not asm.get("target_repo"):
        problems.append("repo SpecKit cible non renseigne (target_repo)")
    if not asm.get("constitution_generated"):
        problems.append("constitution non generee")
    if not asm.get("claude_md_generated"):
        problems.append("CLAUDE.md projet non genere")
    if not asm.get("glossary_consolidated"):
        problems.append("glossaire non consolide")
    if not asm.get("memory_index_generated"):
        problems.append("MEMORY.md (index) non genere")
    if not asm.get("attack_plan"):
        problems.append("plan d'attaque absent")

    # Couverture des 3 faces par feature, sur la sequence figee par l'architecte.
    seq = (manifest.get("architecture") or {}).get("feature_sequence") or []
    # Registre canonique : entrees = objets {id, uc, name, mvp}. Tolere les bare strings (legacy).
    seq_ids = [it.get("id") if isinstance(it, dict) else it for it in seq]
    faces = asm.get("feature_faces") or []
    by_feat = {f.get("feature"): f for f in faces if isinstance(f, dict)}
    if not seq_ids:
        problems.append("aucune feature_sequence (architecture) a converger")
    for feat in seq_ids:
        f = by_feat.get(feat)
        if not f:
            problems.append(f"feature '{feat}' sans ses 3 faces (absente de feature_faces)")
            continue
        missing = [k for k in ("functional", "technical", "design") if not f.get(k)]
        if missing:
            problems.append(f"feature '{feat}' faces manquantes: {missing}")
        if f.get("coherent") is False:
            problems.append(f"feature '{feat}' faces contradictoires (non coherente)")

    # Couverture INVERSE : aucun brief (cadrage) ni parcours (designer) orphelin.
    # Une feature peut bundler plusieurs use cases (`ucs`) ; `uc` (singulier) est tolere.
    def _feat_ucs(it):
        if not isinstance(it, dict):
            return []
        return it.get("ucs") or ([it["uc"]] if it.get("uc") else [])
    seq_ucs = {u for it in seq for u in _feat_ucs(it)}
    if seq_ucs:
        brief_ucs = {b.get("id") for b in (manifest.get("artifacts") or {}).get("briefs") or [] if isinstance(b, dict)}
        journey_ucs = {j.get("uc") for j in (manifest.get("design") or {}).get("journeys_coverage") or [] if isinstance(j, dict)}
        for uc in sorted(u for u in brief_ucs - seq_ucs if u):
            problems.append(f"brief cadrage '{uc}' orphelin (aucune feature dans feature_sequence)")
        for uc in sorted(u for u in journey_ucs - seq_ucs if u):
            problems.append(f"parcours designer '{uc}' orphelin (aucune feature dans feature_sequence)")

    if problems:
        print("CONVERGENCE INCOMPLETE - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print("ASSEMBLAGE OK - les 3 contrats convergent, pack SpecKit present.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
