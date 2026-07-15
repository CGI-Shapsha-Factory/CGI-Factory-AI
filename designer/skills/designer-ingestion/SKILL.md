---
name: designer-ingestion
description: Ingère en parallèle les handoffs cadrage et architecte et pré-remplit la checklist de couverture (mécanique, sans décision humaine).
---

# designer-ingestion

Première étape — **mécanique** — de l'atelier design : (re)lit **tous les handoffs committés** en parallèle
et **pré-remplit** la checklist de couverture. **Aucune décision humaine, aucun item n'est montré** : le
skill prépare la matière que `designer-atelier` déroulera ensuite avec l'humain. **Le design system naît
dans Claude Design** (pas ici).

## Objectif
Rendre la checklist `design.checklist` **pré-remplie** depuis les handoffs Cadrage (C) et Architecte (A), et
poser `design.inputs.cadrage_ok` / `design.inputs.design_impact_ok`, **avant** tout travail humain.

## Entrées (matière de la checklist)
- **Cadrage (C)** : `product-brief.md` (vision, ton), `glossaire.md` (entités/données affichées),
  `spec-index.md` (**parcours / use cases**), **maquette validée** (`demonstrateur`, `client_validated`)
  comme **direction, pas cible** — le designer a autorité pour la faire évoluer.
  > **Lecture seule.** `cadrage-out/spec-index.md` est un **artefact du cadrage** : l'ingestion le **lit**
  > (parcours, use cases) pour nourrir le versant expérience, mais ne le **crée ni ne le modifie jamais**.
- **Architecte (A)** : **`impact-design.md`** (section *Décisions à impact design* : stack front + style,
  contrats transverses visibles, conventions d'API qui décident les états d'UI, NFR qui se voient).
- Conventions : `references/question-map.md` (pilote le pré-remplissage),
  `references/coverage-checklist-guide.md`, `references/states-catalog.md`.

## Pré-requis (vérification silencieuse)
`designer-init` a tourné : le manifeste contient le bloc `design` avec la checklist semée. Sinon, orienter
en clair (sans nom de champ) : « l'atelier design n'est pas encore amorcé — lance d'abord
`/designer:designer-init` ».

## Procédure
**Toujours (re)lire les handoffs depuis les fichiers committés**, même si tu crois les avoir déjà lus plus
tôt dans cette session — **ne jamais** t'appuyer sur la mémoire du chat (exécution reproductible par
n'importe qui). **Lire tous les handoffs pertinents, en parallèle, pour ne rien manquer.** Dispatcher des sous-agents
lecteurs (`agentType: "designer-reader"`), **un par lot**, chacun avec un **schéma de sortie structuré**,
en **un seul message** (appels parallèles), puis synthétiser. Lots :
1. **Cadrage** — `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`.
   Extraire : ton/vision, entités/données affichées, parcours / use cases, états d'écran impliqués.
2. **Architecte** — `architecte-out/impact-design.md`. Extraire : stack front + style, contrats
   transverses visibles, conventions d'API → états d'UI, NFR qui se voient (a11y, responsive, i18n, perf).

*(Garde simple : entrée minuscule → un seul lecteur ; sinon fan-out.)* **Passe de complétude** : vérifier
qu'aucun élément des handoffs n'a été manqué avant de pré-remplir.

**Pré-remplir la checklist** (`design.checklist`) depuis les retours structurés : items d'origine **C**
(parcours, états d'écran, hiérarchie…), items d'origine **A** depuis `impact-design.md` (erreurs, async,
listes, identité/rôles, navigation, accessibilité visée, responsive, i18n, perf ; thématisation). Chaque
item ainsi rempli passe en interne à `status: deduced` (montré **validé**) avec sa `note`. Marquer
`design.inputs.cadrage_ok` / `design.inputs.design_impact_ok`. Le pré-remplissage suit
`references/question-map.md`.

## Sortie
- Checklist pré-remplie : les items déductibles des handoffs sont en `deduced` (montrés **validé**), les
  autres restent **à traiter** pour l'atelier. **Rien d'inventé**, rien n'est **comblé** de force.
- En chat : **aucun item montré, aucun code, aucun nom de champ** — juste un **bilan en prose** de ce que
  les handoffs couvrent déjà + la suite.

## Mise à jour du manifeste
Read-modify-write + revalidation JSON, **en silence** :
- `design.checklist.*[].status` : `open` → `deduced` (+ `note`, `origin`) pour chaque item déduit d'un handoff.
- `design.inputs.cadrage_ok`, `design.inputs.design_impact_ok`.
- **`design.phase` reste `"init"`** (l'ingestion n'introduit pas de nouvel état de phase).

## Règles invariantes appliquées ici
- **Relire depuis les fichiers committés**, jamais la mémoire du chat (reproductible par n'importe qui).
- **Marquer, ne pas inventer** ; ne rien combler de force (un item non déductible reste **à traiter**).
- **Lecture seule du cadrage** : `spec-index.md` est lu, jamais créé ni écrit (artefact du cadrage).
- **Aucune décision de design** : l'ingestion pré-remplit, elle ne tranche pas.
- **Pas de fuite de champ** en sortie utilisateur ; **manifeste mis à jour en silence** (voir
  `references/ux-conventions.md`).

Étape suivante : `/designer:designer-atelier` — dérouler la checklist de couverture (fondation, expérience, technique) et arbitrer les choix d'expérience.
