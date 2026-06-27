---
name: cadrage-clarification
description: Agrège tous les points ouverts en une liste de balayage client priorisée.
---

# cadrage-clarification

Boucle de feedback. Consolide **tous les points à valider** du projet en un
registre unique et en tire une **liste de balayage** que tu déroules avec le
client en atelier — notamment l'atelier de validation du démonstrateur.

## Objectif

Maintenir le registre `validation_points` et produire une checklist client
actionnable, priorisée, qui lève les points bloquants d'abord, sans noyer le
client.

## Entrée

- Tous les marqueurs des artefacts : `[À VALIDER]`, `[NON COUVERT EN ATELIER]`,
  `[À CHIFFRER]`, `[REMIS EN CAUSE]` (capture, vision, glossaire, spec index,
  coupling map, briefs).
- Les conflits signalés du glossaire et les souhaits hors périmètre repérés.
- Le registre `validation_points` existant (alimenté par les autres skills).

## Porte d'entrée

**Au moins un point ouvert** (un marqueur d'artefact ou un `validation_point`
`open`). Sinon, **ne génère rien** et signale qu'il n'y a rien à clarifier.

## Les cinq types de points

Le registre agrège **tous les types**, pas seulement les trous :

| type | origine typique |
|------|-----------------|
| `gap` | trou `[À VALIDER]` / `[NON COUVERT EN ATELIER]` |
| `glossary-conflict` | définition divergente / ambiguïté du glossaire |
| `contradiction` | acquis `[REMIS EN CAUSE]` (retour de démonstrateur) |
| `unmeasured` | critère de succès `[À CHIFFRER]` |
| `out-scope` | souhait hors périmètre à confirmer |

## Procédure

1. **Collecter** tous les points (marqueurs des artefacts + `validation_points`
   existants + conflits + souhaits hors périmètre).
2. **Réconcilier le registre `validation_points` (idempotence).** Rapprocher par
   identité (ref + énoncé) des entrées existantes : **ne pas dupliquer**, préserver
   les `answered` / `invalidated`, ajouter les nouveaux `open`, retirer du
   balayage ce qui est résolu. Aucun point déjà tranché n'est reposé.
3. **Typer** chaque point parmi les cinq types.
4. **Grouper par thème** (parties prenantes, périmètre, objectifs/métriques,
   intégration, sémantique/glossaire, couplage, retour démonstrateur…).
5. **Formuler des énoncés spécifiques et répondables** — pas « préciser le
   besoin » mais « quelle est la cible chiffrée de réduction du temps d'appel ? ».
6. **Prioriser** : d'abord ce qui bloque un artefact ou une porte (point
   bloquant), ensuite le raffinement.
7. **Relier chaque point à l'artefact qu'il débloque** (et au skill qui le
   reprendra).
8. **Plafonner par session** (~8–10 points), surplus reporté en « lot suivant ».

## Sortie — `clarifications.md` (liste de balayage client)

Checklist destinée au client, groupée par thème. Chaque point : énoncé répondable,
type, priorité, artefact débloqué, origine. Plafond par session, report explicite
du surplus. C'est l'ordre du jour que tu déroules en atelier de validation.

## Porte de sortie

- Le registre agrège bien les **cinq types** de points.
- La liste de balayage est **exploitable en atelier** : énoncés spécifiques,
  groupés, priorisés, plafonnés, chacun relié à son artefact.
- **Idempotence** : aucun doublon, aucun point déjà résolu reposé.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `validation_points[]` : registre réconcilié (ajouts `open`, statuts préservés).
- `updated_at`.
- Ne modifie aucune porte (ni `decoupage_arbitrated`, ni
  `demonstrateur_converged` — calculés ailleurs).

## Règles invariantes appliquées ici

- **Marquer, ne pas inventer.** Le skill exploite les points marqués ; il ne
  comble rien, il aide l'humain à les lever.
- **Idempotence.** Réconcilie le registre, ne le régénère pas à l'aveugle.
- **Skill indépendant.** Lit les artefacts et le manifeste, sans orchestrateur.

Étape suivante : `/cadrage:cadrage-retour-demonstrateur` — dérouler la liste en atelier puis ingérer le retour client.
