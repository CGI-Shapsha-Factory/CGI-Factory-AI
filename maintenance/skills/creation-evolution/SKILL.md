---
name: creation-evolution
description: Accompagne le PO pour créer dans Linear une évolution de maintenance complète, portant une proposition de mise à jour de la spécification précise et circonscrite, rattachée au ticket Feature.
---

# creation-evolution

Skill du **PO en recette**, quand il constate que la feature **respecte sa spécification**
mais que cette spécification doit changer pour répondre au vrai besoin (cf.
`references/regles-maintenance.md`). Son rôle : garantir qu'une évolution naît complète, bien
rattachée, et surtout qu'elle porte clairement **la modification de spécification souhaitée** -
car c'est la spécification mise à jour qui guidera le code.

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** (le cwd) - **jamais** un dossier parent. Tous
les chemins (`manifest.json`, `.factory/maintenance/`, `specs/`) se résolvent **sous ce dossier**.
**Ne jamais remonter l'arborescence.**

## Pré-requis (vérification silencieuse)
- **MCP Linear disponible** (`list_teams` répond - cf. `references/linear-maintenance.md`). Sinon,
  **ne rien créer** : refuser en clair et afficher les instructions d'installation.
- **Terrain de maintenance posé** : le bloc `maintenance` du manifeste et le gabarit
  `.factory/maintenance/gabarit-evolution.md` existent. Sinon, proposer en clair de lancer d'abord
  `/maintenance:maintenance-init`.
- **Frontière de la livraison franchie** : la feature visée est livrée (ticket Feature dans
  Linear + `specs/<feature>/`). Sinon, le dire en clair et ne rien créer (un besoin sur une
  feature en fabrication se traite dans la fabrication, pas en recette).

## Procédure
1. **Identifier la feature concernée** et résoudre son **ticket Feature parent** (mêmes règles
   que `creation-anomalie` : registre du manifeste, anti-orphelin, identifiant Linear du
   ticket Feature en parent).
2. **Compléter le gabarit, section par section** (`.factory/maintenance/gabarit-evolution.md`),
   en boucle interactive (`references/interactive-loop.md`) :
   - le **comportement actuel** (conforme à la spécification - c'est le principe d'une
     évolution) ;
   - le **comportement souhaité** ;
   - le **cas d'usage** qui motive le changement ;
   - la **proposition de mise à jour de la spécification**. C'est la section clé : **lire
     `specs/<feature>/spec.md`** et aider le PO à formuler un **écart précis** par rapport à
     la spécification existante ("l'exigence FR-00x devient ..."), en nommant la ou les
     exigences qui changent - **jamais une réécriture** de toute la spécification. Plus le
     changement décrit est étroit, plus l'implémentation qui en découle sera étroite (première
     discipline chirurgicale, cf. `references/regles-maintenance.md`).
3. **Porte de complétude renforcée.** Tant qu'une section est vide **ou que la proposition de
   changement n'est pas claire et circonscrite** (elle ne nomme pas les exigences touchées, ou
   elle réécrit plus que l'écart), le skill le signale en clair et ne crée rien.
4. **Lien avec une anomalie requalifiée** (le cas échéant) : si cette évolution fait suite à
   une anomalie refermée en "Requalifiée en évolution", citer son identifiant Linear dans la
   proposition (et poser la relation entre les deux tickets si l'outil le permet,
   best-effort) - le fil reste visible des deux côtés.
5. **Relecture et validation humaine**, puis **création** : `save_issue` avec l'équipe, un
   titre métier court, le ticket Feature en parent, le **label `Evolution`**, l'état
   **Backlog**, et le gabarit rempli en description. Restituer l'identifiant Linear et l'url.

## Résultat attendu
Une évolution créée dans Linear, complète, rattachée à sa feature, portant la proposition de
changement de spécification, prête à être prise par un développeur. Aucune écriture dans le
repo ni dans le manifeste.

## Règles invariantes
- **La création d'une évolution est un geste du PO** : ce skill ne s'auto-déclenche jamais
  après une requalification.
- **Écart circonscrit ou rien** : une proposition floue ou trop large ne part pas dans Linear.
- **Ne rien inventer** ; **typographie humaine** (cf. `references/ux-conventions.md`).

Étape suivante : `/maintenance:realisation-evolution` - quand un développeur prend l'évolution en charge.
