# Guide Linear — anomalies & évolutions via le MCP linear-prism (recette)

Référence d'usage pour les 4 skills de recette. Le dialogue passe par le **MCP du plugin
`linear-prism`** (serveur hébergé `https://mcp.linear.app/mcp`, authentifié en OAuth via `/mcp` —
**aucune clé API**). Ce plugin est **externe à la Factory** ; les skills le détectent et, s'il est
absent, la **création** bascule en **mode brouillon** (la **mise à jour** et la **requalification**,
elles, ont besoin du MCP).

Une **anomalie** et une **évolution** sont chacune un **ticket Linear ordinaire** — distingué par un
**label** (`anomaly` / `evolution`) et **rattaché à sa feature** par le label `feature:<id>`. Il n'y
a **aucun identifiant maison** (pas de « A01-F02 ») : l'objet est identifié par la **clé Linear
native** (ex. `ENG-321`), et son lien à la feature vit dans le **label** + le **champ `feature`** du
manifeste. C'est ce lien qui porte l'**analyse d'impact**.

## Détection (avant tout)
Sonder `mcp__plugin_linear-prism_linear__list_teams`.
- **Répond** (liste d'équipes) → le MCP est prêt, continuer.
- **Échoue / indisponible** → dire en clair que la recette Linear a besoin du plugin `linear-prism` et
  d'une authentification (`/mcp`). Pour une **création**, proposer le **mode brouillon** ; pour une
  **mise à jour / requalification**, expliquer qu'il faut installer puis **relancer**.

## Installation du plugin linear-prism (si le MCP est absent)
1. **Ajouter la marketplace** : `/plugin marketplace add shinpr/linear-prism`
   (variante bundle : `/plugin marketplace add shinpr/claude-code-workflows`).
2. **Installer** : `/plugin install linear-prism@linear-prism`
   (ou `/plugin install linear-prism@claude-code-workflows` pour la variante bundle).
3. **Redémarrer Claude Code** (pour charger le serveur MCP du plugin).
4. **S'authentifier** : `/mcp`, choisir le serveur `linear`, terminer le login OAuth dans le navigateur.

Revalider avec `list_teams`.

## Pré-requis d'équipe : le statut « Requalifiée en évolution »
Pour que `anomalie-corriger` puisse fermer une anomalie **requalifiée**, ce statut doit **exister**
dans le flux de l'équipe Linear, rangé dans la **famille des statuts d'annulation (type `canceled`)** :
une anomalie requalifiée est une anomalie **fermée sans correction** (ce n'était pas un défaut).
- **Sonder** : `list_issue_statuses({team})` → chercher un état de **type `canceled`** dont le nom
  évoque la requalification (ex. « Requalifiée en évolution »).
- **Absent** → **le MCP ne crée pas les états de workflow** (réglage d'équipe). Dire en clair au PO /
  à l'admin Linear de **le créer une fois** dans les réglages de l'équipe (catégorie « Annulé »,
  libellé « Requalifiée en évolution »), puis relancer. **Ne pas inventer** un autre état de fermeture.

## Labels
- `feature:<id>` (**toujours**) — rattache l'objet à la feature (`id` de `architecture.feature_sequence`).
- `anomaly` **ou** `evolution` — la nature. **Jamais `MVP`** (l'architecture n'a aucune notion de MVP).
- Si un label n'existe pas, le créer via `create_issue_label` ou l'omettre (best-effort, ne pas bloquer).

## Créer une anomalie (`anomalie-creer`)
`mcp__plugin_linear-prism_linear__save_issue` — création quand on ne passe **pas** d'`id` :
- **`team`** (obligatoire).
- **`title`** — intitulé métier court et parlant (ex. `Le total du panier ignore la remise`).
- **`description`** — **Markdown** (newlines littéraux) portant **au minimum** :
  ```markdown
  **Feature concernée :** 002 — Panier

  **Comportement attendu :** …
  **Comportement constaté :** …
  **Cas d'usage / critère de recette qui échoue :** …
  **Étapes pour reproduire :**
  1. …
  2. …
  ```
- **`labels`** — `feature:<id>` + `anomaly`. **`state`** — Todo/unstarted si résolu (`list_issue_statuses`).
- Récupérer dans la réponse : l'**id interne**, l'**identifier** (ex. `ENG-321`) et l'**url**.
- **Tant qu'un de ces champs manque**, l'anomalie n'est **pas prête** : poser la question manquante
  (un point à la fois) avant de créer.

## Créer une évolution (`evolution-creer`)
Même `save_issue`, labels `feature:<id>` + `evolution`. La `description` porte **au minimum** :
```markdown
**Feature concernée :** 002 — Panier

**Comportement actuel :** …
**Comportement souhaité :** …
**Cas d'usage qui motive le changement :** …
**Écart de spécification proposé :** on change l'exigence « … » en « … ».
```
L'**écart de spécification** doit être **précis et circonscrit** (« on change telle exigence »), **pas**
une réécriture de toute la spec. Tant qu'il n'est pas clair et borné, l'évolution n'est **pas prête**.

## Trouver un objet existant (les skills développeur)
- D'abord le manifeste `recette.anomalies[]` / `recette.evolutions[]` (par `identifier`, `feature`,
  mot-clé du `title`).
- Sinon interroger Linear : `list_issues({query: "<mots-clés>", team})` (titre + description) ; filtrer
  par label `anomaly` / `evolution` et `feature:<id>` au besoin.
- `get_issue({id})` pour lire l'**état courant**, la **description**, le `branchName` git.
- **Confirmer l'objet** avant toute écriture.

## Mettre à jour l'état (prise en charge, clôture)
Un seul outil `save_issue` **crée ou met à jour** : passer un **`id`** (l'`identifier`) déclenche la mise à jour.
- **Résoudre l'état** : `list_issue_statuses({team})` → types `backlog / unstarted / started /
  completed / canceled / triage`. Prise en charge → `started` ; terminé → **`completed`**.
- **Changer l'état** : `save_issue({id, state})` — `state` accepte le **nom** (`"Done"`), le **type**
  (`completed`) ou l'**UUID**.
- **Idempotence** : lire l'état courant (`get_issue`) **avant** d'écrire ; s'il est déjà le bon, ne rien faire.

## Requalifier une anomalie en évolution (`anomalie-corriger`, cas particulier)
Quand le développeur constate que **le code est conforme à la spec** (ce n'était pas un défaut) :
1. **État** : `save_issue({id, state: "Requalifiée en évolution"})` (type `canceled` — voir pré-requis d'équipe).
2. **Commentaire** (ici **on utilise** `save_comment`, contrairement à une simple MAJ d'état) :
   `save_comment({issueId, body})` — expliquer en clair **pourquoi ce n'est pas un défaut**
   (« le code est conforme à la spécification ; voici le cas d'usage que la spécification ne
   couvrait pas : … »).
3. **Ne pas créer l'évolution** : c'est au **PO** d'ouvrir l'évolution (il porte le périmètre). Le lien
   entre l'anomalie requalifiée et la future évolution (relation d'issues Linear) sera posé **plus
   tard**, quand le PO lancera `evolution-creer`. Consigner `state: "requalified"` (et `requalified_to`
   quand l'évolution existera) dans le manifeste.

## Relations entre objets (dépendances, filiation)
`save_issue({id, blockedBy: ["<identifier>"]})` pour une dépendance ; les relations `blocks`/`blockedBy`
sont **append-only**. La filiation anomalie→évolution se pose côté PO à la création de l'évolution.

## Le bloc manifeste `recette`
Écriture **silencieuse** (read-modify-write + revalidation JSON), jamais narrée. Séparé de
`linear.issues[]` (features) pour ne pas casser `check_linear.py`.
```json
"recette": {
  "phase": "active", "team": null, "project": null,
  "anomalies": [
    { "feature": "002", "title": "…", "identifier": "ENG-321", "issue_id": "…",
      "url": "https://linear.app/…", "state": "in_progress",
      "requalified_to": null,
      "trace": { "spec_verified": false, "tasks_updated": false, "linear_synced": false } }
  ],
  "evolutions": [
    { "feature": "002", "title": "…", "identifier": "ENG-322", "issue_id": "…",
      "url": "https://linear.app/…", "state": "in_progress", "reopened": true,
      "perimeter": { "requirements": ["FR-004"], "files": ["specs/002-*/spec.md"] },
      "trace": { "spec_updated": false, "plan_regenerated": false, "tasks_regenerated": false,
                 "linear_synced": false, "non_regression_passed": false } }
  ]
}
```
- `state` anomalie : `draft` (MCP absent), `in_progress`, `requalified`, `done`.
- `state` évolution : `draft`, `in_progress`, `done`.
- `trace` : ce que `scripts/check_recette.py` exige **à la fermeture** (règle d'or « pas de clôture sans trace »).

## Mode brouillon (repli, MCP absent — création seulement)
Écrire `recette-drafts.md` (à la racine du projet) : une section par objet avec **titre**, **nature**
(anomalie/évolution), **feature**, et la **description** au format ci-dessus. Consigner l'objet avec
`state: "draft"`. L'équipe le crée dans Linear quand `linear-prism` est prêt (relancer le skill).
