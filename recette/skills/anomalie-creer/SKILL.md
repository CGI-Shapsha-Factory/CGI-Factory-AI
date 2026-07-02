---
name: anomalie-creer
description: Le PO crée une anomalie complète et bien rattachée à sa feature dans Linear (comportement attendu vs constaté, cas/critère qui échoue, étapes de repro) — à la main ou depuis l'outil de recette — via le MCP linear-prism.
---

# anomalie-creer

**Le PO crée une anomalie.** À lancer **en recette**, quand le PO constate que **le logiciel ne
respecte pas sa spécification**. Ce skill garantit qu'une anomalie **naît complète et bien
rattachée** à sa feature : le vrai risque, ce sont les anomalies trouées où il manque l'information
qui permettrait au développeur de travailler.

## Objectif
Produire **une anomalie dans Linear**, complète et au bon format, prête à être prise par un
développeur (`/recette:anomalie-corriger`). Rattachée à sa feature par le label `feature:<id>` + le
label `anomaly`. Chaque anomalie est **confirmée avant création**.

## Frontière (exception assumée)
La recette **travaille dans le repo cible**, mais **créer un ticket** est une écriture vers un
**système externe** (Linear). La seule écriture propre à la Factory est le bloc `recette` du
manifeste. Le dialogue passe par le **MCP du plugin `linear-prism`** — voir
`references/recette-linear-guide.md`.

**Double déclencheur (une seule porte de création).** Ce skill s'invoque de deux façons, qui
**convergent** vers la même validation + création :
- **à la main** par le PO (dialogue interactif) ;
- par l'**outil de recette** (extension navigateur / analyse assistée) qui a détecté un écart et
  passe une **anomalie candidate** (titre + champs pré-remplis). Dans ce cas, le skill **valide la
  complétude**, demande **la confirmation du PO**, puis crée. Un outil externe ne crée **jamais**
  l'anomalie dans son coin : il passe **toujours** par ce skill.

## Pré-requis (vérification silencieuse)
Lire `.factory/manifest.json` **sans l'annoncer** :
- La feature visée est **connue** (`architecture.feature_sequence`). Si un **marqueur de cycle de
  vie** existe et indique que la feature est **encore en fabrication** (pas livrée), **refuser en
  clair** : « Cette feature n'est pas encore livrée : avant la livraison, on est en fabrication, il
  n'y a pas d'anomalie à tracer. » (Tant que le plugin compagnon anti-écrasement n'existe pas, ce
  marqueur peut être absent → procéder.)
- Le bloc `recette` peut ne pas encore exister → le **créer** (silencieux) à la première anomalie.

## Étape 1 — Détecter Linear (MCP linear-prism)
Sonder `mcp__plugin_linear-prism_linear__list_teams` (cf. `references/recette-linear-guide.md`).
- **Disponible** → continuer.
- **Indisponible** → **ne pas bloquer** : afficher les **instructions d'installation** (section
  « Installation » du guide) et **proposer le mode brouillon** — préparer l'anomalie dans
  `recette-drafts.md` (à créer dans Linear plus tard), la consigner `state: "draft"`.

## Étape 2 — Recueillir l'anomalie
Deux entrées possibles :
- **Candidate de l'outil** → charger les champs pré-remplis, puis passer à l'Étape 3 (compléter/valider).
- **À la main** → recueillir **un point à la fois** (cf. `references/interactive-loop.md`), en
  commençant par **la feature concernée** (un `id` de `architecture.feature_sequence`).

## Étape 3 — Compléter jusqu'à ce qu'elle soit prête
Une anomalie est **prête** quand elle porte **au minimum** :
1. la **feature concernée** (rattachement) ;
2. le **comportement attendu** (ce que la spec promet) ;
3. le **comportement constaté** (ce que fait le logiciel) ;
4. le **cas d'usage / critère de recette qui échoue** ;
5. les **étapes pour reproduire**.

**Tant qu'un de ces éléments manque**, le signaler en clair et **poser la question** (un point à la
fois) ; ne **pas** considérer l'anomalie comme prête. Ne rien inventer.

## Étape 4 — Cible Linear puis créer (après confirmation)
1. **Cible** (une fois) : équipe (`list_teams`), projet optionnel (`list_projects`), état initial
   Todo/unstarted. Consigner `team`/`project` **en silence**.
2. **Confirmer** l'anomalie au PO (recommandé + ajuster + saisir) : titre + description. **Ne rien
   créer** tant que ce n'est pas approuvé.
3. **Créer** (cf. guide) : `save_issue({team, title, description, labels: ["feature:<id>", "anomaly"], state})`
   → récupérer `identifier`/`url`. La `description` porte les 5 champs de l'Étape 3.
4. **Consigner** dans `recette.anomalies[]` (en silence) : `feature`, `title`, `identifier`,
   `issue_id`, `url`, `state: "in_progress"` (ou `"draft"` si MCP absent), `trace` initialisée à faux.

## Vérification avant de conclure
- L'anomalie **existe** dans Linear (ou est en brouillon) avec ses 5 champs, le label `feature:<id>`
  et le label `anomaly`.
- Le bloc `recette` du manifeste **reparse sans erreur** ; mise à jour **en silence**.
- Restitution **en prose** (« j'ai créé l'anomalie *Le total du panier ignore la remise* sur la
  feature Panier »), **une** phrase de suite.

## Règles invariantes
- **Une seule porte, deux déclencheurs.** Humain ou outil de recette : même validation, même format.
- **Anomalie complète ou rien.** Pas de création tant qu'un des 5 champs manque.
- **Confirmer avant de créer.** Action externe, difficile à défaire.
- **Un point à la fois.** Questions en prose, une par une (cf. `interactive-loop.md`) ; pas de tableau.
- **Rien d'inventé.** On ne crée que ce que le PO a validé.
- **Manifeste en silence.** Aucun nom de clé à l'écran ; restitution en prose.

Étape suivante : un développeur prend l'anomalie avec `/recette:anomalie-corriger`.
