---
name: evolution-creer
description: Le PO crée une évolution complète et bien rattachée à sa feature dans Linear, portant un écart de spécification précis et circonscrit (pas une réécriture) — via le MCP linear-prism.
---

# evolution-creer

**Le PO crée une évolution.** À lancer **en recette**, quand le PO constate que **la feature respecte
sa spécification mais que cette spécification doit changer** pour répondre au vrai besoin. Le skill
garantit qu'une évolution **naît complète, bien rattachée, et surtout porteuse de la modification de
spécification souhaitée** — car c'est la spec mise à jour qui guidera le code.

## Objectif
Produire **une évolution dans Linear**, complète et au bon format, **portant la proposition de
changement de spécification**, prête à être prise par un développeur (`/recette:evolution-realiser`).
Rattachée à sa feature par le label `feature:<id>` + le label `evolution`.

## Frontière (exception assumée)
Créer un ticket est une écriture vers un **système externe** (Linear) ; la seule écriture propre à la
Factory est le bloc `recette` du manifeste. Dialogue via le **MCP `linear-prism`** — voir
`references/recette-linear-guide.md`.

## Pré-requis (vérification silencieuse)
Lire `.factory/manifest.json` : la feature visée est **connue** (`architecture.feature_sequence`) et
**livrée** (si un marqueur de cycle de vie existe et dit « en fabrication », refuser en clair). Le
bloc `recette` peut ne pas exister → le créer (silencieux). MCP : `list_teams` ; si absent, mode
brouillon possible (comme pour l'anomalie).

## Étape 1 — Détecter Linear (MCP linear-prism)
Sonder `list_teams`. Disponible → continuer. Indisponible → instructions d'installation + **mode
brouillon** (`recette-drafts.md`, `state: "draft"`).

## Étape 2 — Recueillir l'évolution (un point à la fois)
Recueillir, en commençant par **la feature concernée** (un `id` de `architecture.feature_sequence`),
puis les champs ci-dessous. Cf. `references/interactive-loop.md`.

## Étape 3 — Compléter jusqu'à ce qu'elle soit prête
Une évolution est **prête** quand elle porte **au minimum** :
1. la **feature concernée** (rattachement) ;
2. le **comportement actuel** ;
3. le **comportement souhaité** ;
4. le **cas d'usage qui motive** le changement ;
5. une **proposition de mise à jour de la spécification** — et c'est le point clé.

**La proposition de changement doit être un écart PRÉCIS** par rapport à la spécification existante
(« on change telle exigence en telle exigence »), **pas** une réécriture de toute la spécification.
**Plus le changement décrit est étroit, plus l'implémentation qui en découlera sera étroite** — c'est
le premier des garde-fous chirurgicaux. **Tant que la proposition n'est pas claire et circonscrite**,
l'évolution n'est **pas prête** : poser la question (un point à la fois).

## Étape 4 — Cible Linear puis créer (après confirmation)
1. **Cible** (une fois) : équipe, projet optionnel, état initial Todo/unstarted (silencieux).
2. **Confirmer** l'évolution au PO (recommandé + ajuster + saisir), en insistant sur **l'écart de
   spécification**. **Ne rien créer** tant que ce n'est pas approuvé.
3. **Créer** : `save_issue({team, title, description, labels: ["feature:<id>", "evolution"], state})`
   → `identifier`/`url`. La `description` porte les 5 champs de l'Étape 3 (dont l'écart de spec).
4. **Consigner** dans `recette.evolutions[]` (silencieux) : `feature`, `title`, `identifier`,
   `issue_id`, `url`, `state: "in_progress"` (ou `"draft"`), `perimeter` (les exigences visées si
   connues), `trace` à faux.

## Vérification avant de conclure
- L'évolution **existe** (ou est en brouillon) avec ses 5 champs (dont l'écart de spec **circonscrit**),
  le label `feature:<id>` et le label `evolution`.
- Le bloc `recette` **reparse sans erreur** ; mise à jour **en silence**.
- Restitution **en prose**, **une** phrase de suite.

## Règles invariantes
- **L'écart de spec commande.** Une évolution porte un changement de spécification **précis et borné**.
- **Pas de réécriture.** On décrit l'exigence qui change, pas toute la spec.
- **Confirmer avant de créer.** Action externe, difficile à défaire.
- **Un point à la fois.** Questions en prose, une par une ; pas de tableau.
- **Rien d'inventé.** Seulement ce que le PO a validé.
- **Manifeste en silence.** Restitution en prose.

Étape suivante : un développeur réalise l'évolution avec `/recette:evolution-realiser`.
