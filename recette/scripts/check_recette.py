#!/usr/bin/env python
"""Garde-fou deterministe (sans IA) de la recette : anomalies et evolutions (plugin recette).

Les skills de recette consignent chaque anomalie/evolution dans le bloc `recette` du manifeste
(.factory/manifest.json par defaut). Ce garde-fou lit le manifeste et echoue si :
  - le bloc `recette` est absent (aucun skill de recette n'a tourne) ;
  - un objet (anomalie/evolution) est rattache a une feature INCONNUE de
    `architecture.feature_sequence` (le lien feature qui porte l'analyse d'impact est casse) ;
  - un objet non-brouillon n'a pas d'identifiant Linear (`identifier`/`issue_id`) ;
  - un objet FERME (anomalie `done`/`requalified`, evolution `done`) n'a pas sa trace de cloture
    COMPLETE (la regle d'or : on ne referme jamais sans avoir mis la trace a jour).

C'est la traduction deterministe de la discipline de cloture : une anomalie/evolution n'est
"terminee" que lorsque la specification, les taches et Linear refletent le nouvel etat (et, pour
une evolution, la non-regression est prouvee). Exit 0 si tout est coherent, sinon 1.

Le lien feature passe par le champ `feature` (= un id de architecture.feature_sequence), jamais
par un identifiant maison : c'est ce lien qui permet l'analyse d'impact inter-features.

Usage:
    python check_recette.py [chemin/vers/manifest.json]
"""
import json
import sys

# etats qui ne sont pas encore dans Linear : pas d'identifiant exige, pas de cloture possible.
DRAFT_STATES = {"draft"}

# etats de cloture par nature -> les cles de trace exigees (toutes doivent etre vraies).
ANOMALY_CLOSED = {
    "done": ("spec_verified", "tasks_updated", "linear_synced"),
    "requalified": ("linear_synced",),
}
EVOLUTION_CLOSED = {
    "done": ("spec_updated", "plan_regenerated", "tasks_regenerated",
             "linear_synced", "non_regression_passed"),
}


def _feature_ids(manifest):
    """Ensemble des ids de features connus (architecture.feature_sequence)."""
    seq = (manifest.get("architecture") or {}).get("feature_sequence") or []
    ids = set()
    for it in seq:
        fid = it.get("id") if isinstance(it, dict) else it
        if fid is not None:
            ids.add(str(fid))
    return ids


def _check_object(obj, kind, closed_map, feature_ids, problems):
    if not isinstance(obj, dict):
        problems.append(f"{kind}: entree non conforme (objet attendu)")
        return
    label = obj.get("title") or obj.get("identifier") or obj.get("feature") or "?"

    # 1. Lien feature (porte l'analyse d'impact).
    feature = obj.get("feature")
    if not feature:
        problems.append(f"{kind} '{label}': aucune feature rattachee")
    elif feature_ids and str(feature) not in feature_ids:
        problems.append(f"{kind} '{label}': feature '{feature}' inconnue de la sequence")

    state = (obj.get("state") or "in_progress").lower()

    # 2. Identifiant Linear obligatoire des que l'objet existe (sauf brouillon).
    if state not in DRAFT_STATES and not (obj.get("identifier") or obj.get("issue_id")):
        problems.append(f"{kind} '{label}': etat '{state}' sans identifiant Linear")

    # 3. Trace de cloture complete pour un objet ferme.
    if state in closed_map:
        required = closed_map[state]
        trace = obj.get("trace")
        if not isinstance(trace, dict):
            problems.append(f"{kind} '{label}': ferme ('{state}') sans trace de cloture")
        else:
            missing = [k for k in required if not trace.get(k)]
            if missing:
                problems.append(
                    f"{kind} '{label}': cloture incomplete, manque {', '.join(missing)}")


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

    recette = manifest.get("recette")
    if not isinstance(recette, dict):
        print("ERREUR: bloc `recette` absent (aucun skill de recette n'a tourne).", file=sys.stderr)
        return 1

    feature_ids = _feature_ids(manifest)
    problems = []

    anomalies = recette.get("anomalies") or []
    evolutions = recette.get("evolutions") or []
    for obj in anomalies:
        _check_object(obj, "anomalie", ANOMALY_CLOSED, feature_ids, problems)
    for obj in evolutions:
        _check_object(obj, "evolution", EVOLUTION_CLOSED, feature_ids, problems)

    if problems:
        print("RECETTE INCOMPLETE - points bloquants :", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1

    print(f"RECETTE OK - {len(anomalies)} anomalie(s), {len(evolutions)} evolution(s), "
          "traces de cloture completes.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
