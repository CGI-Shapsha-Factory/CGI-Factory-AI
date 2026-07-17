# Guide Linear : création et mise à jour des tickets via le MCP linear-prism (assembleur)

Référence d'usage pour `premier-alimente-linear` (création) et `update-issue-linear` (mise à jour). Le
dialogue passe par le **MCP du plugin `linear-prism`** (serveur hébergé `https://mcp.linear.app/mcp`,
authentifié en OAuth via `/mcp` - **aucune clé API** à gérer). Ce plugin est **externe à la Factory**
(voir "Installation" ci-dessous) : les skills le détectent et, s'il est absent, **ne créent ni ne
mettent à jour rien** - ils refusent et renvoient aux instructions d'installation.

## Détection (avant tout)
Sonder `mcp__plugin_linear-prism_linear__list_teams`.
- **Répond** (liste d'équipes) -> le MCP est prêt, continuer.
- **Échoue / indisponible** -> **ne rien créer ni mettre à jour**. Refuser en clair : "Je ne peux
  pas créer/mettre à jour de tickets Linear : le MCP `linear-prism` n'est pas disponible." Puis
  renvoyer à la section "Installation du plugin linear-prism" ci-dessous (ajouter la marketplace,
  installer, redémarrer, s'authentifier via `/mcp`), et relancer une fois prêt.

## Installation du plugin linear-prism (si le MCP est absent)
`linear-prism` est un **plugin tiers** (externe à la Factory) qui **empaquette la configuration du
serveur MCP Linear hébergé** (`https://mcp.linear.app/mcp`, **OAuth - aucune clé API**). S'il n'est
pas détecté, guider l'utilisateur pas-à-pas :

1. **Ajouter la marketplace** : `/plugin marketplace add shinpr/linear-prism`
   (variante "bundle" si l'équipe le distribue ainsi : `/plugin marketplace add shinpr/claude-code-workflows`).
2. **Installer le plugin** : `/plugin install linear-prism@linear-prism`
   (ou `/plugin install linear-prism@claude-code-workflows` pour la variante bundle - le suffixe
   `@<marketplace>` doit correspondre à la marketplace ajoutée).
3. **Redémarrer Claude Code** (pour charger le serveur MCP du plugin).
4. **S'authentifier** : lancer **`/mcp`**, choisir le serveur `linear`, terminer le login OAuth dans
   le navigateur.

Revalider ensuite avec la **détection** ci-dessus (`list_teams` répond). Tant que ce n'est pas fait,
**ni la création ni la mise à jour** ne sont possibles : refuser et attendre l'installation
(relancer une fois installé).

## Accès par clé API (Quark / environnement sans OAuth)
Le serveur MCP Linear s'authentifie en **OAuth** (défaut, ci-dessus) **ou** par **clé API**. Dans un
environnement où le flux OAuth `/mcp` n'est pas disponible (ex. le PO qui pilote depuis **Quark** et
demande une action en **écriture**), utiliser une **clé API personnelle** :
1. Linear -> **Settings -> Security & access -> Personal API keys -> New API key**.
2. Nommer la clé, lui donner un **accès en écriture** (*Write* / *Create issues* selon le besoin), la
   **restreindre à l'équipe** du projet, puis **Create**. La clé n'est **affichée qu'une fois** - la
   copier immédiatement (format `lin_api_...`).
3. La stocker dans un fichier **`.env`** (jamais commité, ajouté au `.gitignore`) : `LINEAR_API_KEY=lin_api_...`.
4. Le MCP `linear-prism` lit alors `LINEAR_API_KEY` pour s'authentifier (pas de login OAuth).

**Ne jamais** afficher, loguer ni committer la clé. C'est cette section que `create-cowork-md`
reprend dans `init-cowork.md` ("Accès Linear pour Quark").

## Cible (une seule fois, avant la boucle)
- **Équipe** (obligatoire pour créer) : `list_teams` -> présenter en 3 options (recommandée =
  celle qui correspond au projet / à l'organisation, alternative(s), "saisir"). Retenir le
  `team` (nom ou id).
- **Projet** (optionnel) : `list_projects({team})` -> proposer un projet existant ou en créer un au
  nom du produit. Retenir le `project`.
- **État initial = Backlog** : `list_issue_statuses({team})` -> viser le type **`backlog`**, tickets
  **non assignés**. **Toute nouvelle issue** (Feature comme Task) est créée en **Backlog**, jamais en
  Todo. Si l'état n'est pas résolvable proprement, laisser l'état par défaut de l'équipe.

## Créer un ticket (par feature)
`mcp__plugin_linear-prism_linear__save_issue` - création quand on ne passe **pas** d'`id` :
- **`team`** (obligatoire) - l'équipe retenue.
- **`title`** (obligatoire) - l'intitulé métier en clair (ex. `001 - Recherche Q&A sourcée`).
- **`description`** - **Markdown** (newlines littéraux, pas d'échappement) : la description d'une
  ligne + un court contexte (parcours principal, critère de succès clé). Voir la face fonctionnelle
  de la graine `assembleur-out/features/<id>-*.md`.
- **`project`** - si retenu. **`state`** - **Backlog** (type `backlog`).
- **`labels`** - le label plat **`Feature`** (taxonomie) **seul** (+ `walking-skeleton` si la feature
  001 / le walking skeleton). **Jamais** de label de numérotation **`feature:<id>`** / `Issue:<id>`
  (l'`identifier` Linear `<TEAM>-<n>` porte déjà le numéro), **jamais** `MVP`. Les labels plats
  **`Feature`** / **`Task`** **préexistent** dans l'espace de travail : les **résoudre par nom** via
  `list_issue_labels` (comparaison **insensible à la casse**) et passer leurs **UUID** dans `labelIds`
  - **ne pas les créer**. Un label absent : le créer via `create_issue_label` ou l'omettre (best-effort,
  ne pas bloquer). Note : `save_issue` prend `labelIds` (UUID), pas des noms - d'où la résolution préalable.
- Récupérer dans la réponse : l'**id interne**, l'**identifier** (ex. `ENG-123`) et l'**url**.

## Sous-tickets Task par Functional Requirement (`premier-alimente-linear`)
Chaque "chose à faire" d'une feature est un **vrai sous-ticket `Task`** (pas une checkbox dans la
description). `premier-alimente-linear` crée **un `Task` par Functional Requirement** (`FR-xxx`) de la
graine `assembleur-out/features/<id>-*.md`, **rattaché** à la Feature :

`save_issue({team, title: "FR-00x - <intitulé fonctionnel court>", parentId: "<issue_id UUID de la
Feature>", labelIds: ["<UUID Task>"], description: "<énoncé du FR, 1 ligne>", state: <Backlog>})`

- **`parentId` = l'UUID interne** (`issue_id`) de la Feature, **pas** l'`identifier` (`ENG-123`).
- **State = Backlog** (comme la Feature). Label **`Task`** seul.
- Récupérer `issue_id` / `identifier` / `url` et consigner dans `linear.issues[].sub_issues[]` avec le
  champ **`fr`** (clé stable = `id` de feature + `fr`).

*(Niveau distinct, plus tard : `creation-task-linear` crée en plus un `Task` par **phase** de
`tasks.md` après SpecKit - voir ci-dessous. Les deux niveaux coexistent sous la même Feature,
distingués dans le manifeste par `fr` vs `phase`.)*

## Dépendances entre features -> relations bloquantes
La carte `assembleur-out/feature-map.md` porte la colonne **"Dépend de"**. Les features sont
traitées **dans l'ordre** (001, 002, ...) ; une dépendance pointe vers une feature **antérieure**,
donc **déjà créée**. Sur le ticket parent de la feature dépendante, poser :
`save_issue({id: "<identifier de la feature>", blockedBy: ["<identifier de la dépendance>"]})`
(ou passer `blockedBy` dès la création). `blocks`/`blockedBy` sont **append-only**.

## Sous-tickets par phase (`tasks.md`) -> pour `creation-task-linear`
Après `/speckit.tasks`, chaque feature a un `specs/<feature>/tasks.md`. On crée **un vrai sous-ticket
par phase** (contrairement à la checklist-dans-la-description du ticket de feature).

- **Parser `tasks.md`** (lecture seule) : phases = lignes `^## Phase (\d+): (.+)$` ; tâches d'une
  phase = lignes `^- \[[ xX]\] (T\d{3})(?: \[P\])?(?: \[US\d+\])? (.+)$`. Les phases sont
  **séquentielles** (Setup, Foundational, une par User Story avec sa priorité `P1/P2/P3`, Polish) et
  peuvent contenir des **emoji** (🎯 ⚠️) à retirer des titres.
- **Titre descriptif** (obligatoire) : jamais le nom générique brut ("Setup"). Enrichir depuis les
  tâches de la phase ; pour une phase "User Story N - <titre>", reprendre l'intitulé de la story.
- **Créer le sous-ticket** :
  `save_issue({team, title, parentId: "<issue_id UUID du ticket Feature>", labelIds: ["<UUID Task>"],
  description: "<résumé 1 ligne>", state: <Backlog>})`. Le **`parentId` est l'UUID interne**
  (`issue_id`) du ticket `Feature`, **pas** l'`identifier` (`ENG-123`). **State = Backlog.** La
  **description est un résumé d'une ligne** (pas d'énumération des `Txxx`).
- **Rattraper le label `Feature`** sur le ticket de feature sans écraser ses labels : `get_issue({id})`
  -> union des `labelIds` existants + `Feature` -> `save_issue({id, labelIds: <union>})`.
- Récupérer `issue_id` / `identifier` / `url` et consigner dans `linear.issues[].sub_issues[]`.

## Mettre à jour un ticket (statut / cases à cocher)
Pour `update-issue-linear`. Un seul outil `save_issue` **crée ou met à jour** : passer un **`id`**
(l'`identifier`, ex. `LIN-123`) déclenche la **mise à jour** (le `team` n'est requis qu'à la création).

- **Trouver le ticket** : `list_issues({query: "<mots-clés du titre>", team})` (la recherche porte sur
  titre + description) ; ou `get_issue({id})` si l'`identifier` est déjà connu (retourne aussi l'état
  courant, la `description`, et le `branchName` git - utile pour recouper avec la branche courante).
- **Résoudre l'état** : `list_issue_statuses({team})` renvoie les états de l'équipe avec leur **type**
  (`backlog` / `unstarted` / `started` / `completed` / `canceled` / `triage`). Pour "terminé", viser
  le type **`completed`** ; "en cours" -> `started`.
- **Changer l'état** : `save_issue({id, state})` - `state` accepte le **nom** (`"Done"`), le **type**
  (`completed`) ou l'**UUID** de l'état. Ex. : `save_issue({id: "LIN-123", state: "Done"})`.
- **Cocher une case** (sous-partie d'une grosse feature) : lire la `description` via `get_issue`,
  passer la ligne `- [ ] ...` visée à `- [x] ...`, puis `save_issue({id, description: "<MAJ>"})`.
- **Idempotence** : lire l'état courant (`get_issue`) **avant** d'écrire ; s'il est déjà celui visé,
  ne rien faire. **L'état courant vit dans Linear** - ne **rien consigner** dans le manifeste committé
  (l'avancement de fabrication n'y va pas : deux développeurs sur deux branches le réécriraient en
  parallèle -> conflit de merge).
- **Pas de commentaire** par défaut (on ne change que l'état / la case). `save_comment({issueId, body})`
  existe mais n'est pas utilisé ici.

## Idempotence (bloc manifeste `linear` = carte amont figée seulement)
Le manifeste committé porte **uniquement la carte amont figée** : les tickets `Feature` et leurs
sous-tickets `Task` **par FR**, posés **une seule fois** par `premier-alimente-linear` (phase
single-owner, **avant tout branchement** - aucune concurrence). Avant de créer, lire `linear.issues` :
une feature déjà consignée avec un `issue_id` est **déjà créée** -> ne pas recréer.

**Ce qui n'est PLUS dans le manifeste (vit dans Linear) :** les sous-tickets **par phase**
(`creation-task-linear`) et l'**état d'avancement** (`update-issue-linear`). L'avancement de fabrication
est concurrent (une branche par développeur) ; l'écrire dans le fichier committé unique provoquerait des
conflits de merge. **Linear est la source de vérité** : idempotence via `list_issues({parentId})` + le
jeton `Phase N -` en tête de titre.
Vue d'ensemble des règles multi-développeurs (numérotation, couplage, merge, constitution) :
`fabrication-parallele.md`.
Bloc :
```json
"linear": {
  "phase": "init", "team": null, "project": null,
  "issues": [
    { "id": "001", "ucs": ["UC2"], "name": "...",
      "issue_id": "...", "identifier": "ENG-123", "url": "https://linear.app/...",
      "status": "created",
      "sub_issues": [
        { "fr": "FR-001", "title": "FR-001 - Recherche en langage naturel",
          "issue_id": "...", "identifier": "ENG-124", "url": "https://linear.app/...", "status": "created" }
      ]
    }
  ],
  "all_issues_created": false
}
```
Statuts (ticket **et** sous-ticket FR) : `created` (posé, exige `issue_id`), `skipped` (écarté en
session), `merged` (fusionné). Dans le manifeste, `sub_issues[]` ne porte **qu'une nature**, en **Backlog** :
- **`{fr, ...}`** - un par Functional Requirement, posé par **`premier-alimente-linear`** (clé stable =
  `id` de feature + `fr`).

Les sous-tickets **`{phase, ...}`** (posés par `creation-task-linear`) et l'état d'avancement vivent
**dans Linear**, jamais dans ce bloc. Écriture **silencieuse** (read-modify-write + revalidation JSON),
jamais narrée.
