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
- **Équipe** (obligatoire pour créer) : `list_teams` -> demander **avec `AskUserQuestion`** : deux
  options, celle qui correspond au projet / à l'organisation (recommandé) et l'alternative la plus
  proche ; la saisie libre pour une autre équipe. Retenir le
  `team` (nom ou id).
- **Projet** (optionnel) : `list_projects({team})` -> demander **avec `AskUserQuestion`** : un
  projet existant (recommandé) ou en créer un au
  nom du produit. Retenir le `project`.
- **État initial = Backlog (impératif absolu)** : `list_issue_statuses({team})` -> repérer l'état dont
  le **type** est `backlog` et **retenir son `name`** (il varie selon l'équipe : "Backlog",
  "Icebox"...). C'est ce **nom** qui est passé à `save_issue`, **jamais le type** : le MCP
  `linear-prism` résout l'état **par nom seulement** et **échoue en silence** sur une valeur
  inconnue - passer `state: "backlog"` (le type) laisse le ticket dans l'état par défaut de
  l'équipe, sans la moindre erreur. **Toute nouvelle issue** (Feature comme Task, tous niveaux
  confondus) est créée en **Backlog**, jamais en Todo, tickets **non assignés**.
  - **Aucun repli silencieux.** Si aucun état de type `backlog` n'est résolvable, **ne rien créer** :
    le dire en clair et demander à l'humain quel état de l'équipe fait office de backlog. Ne
    **jamais** "laisser l'état par défaut de l'équipe".
  - **Contrôle après le premier ticket** : dès la **première** création, relire le ticket via
    `get_issue({id})` et vérifier que son état est bien celui visé. S'il ne l'est pas, **s'arrêter
    immédiatement** et le dire en clair - plutôt que de poser N tickets au mauvais endroit.

## Créer un ticket (par feature)
`mcp__plugin_linear-prism_linear__save_issue` - création quand on ne passe **pas** d'`id` :
- **`team`** (obligatoire) - l'équipe retenue.
- **`title`** (obligatoire) - l'intitulé métier en clair (ex. `001 - Recherche Q&A sourcée`).
- **`description`** - **Markdown** (newlines littéraux, pas d'échappement) : la description d'une
  ligne + un court contexte (parcours principal, critère de succès clé). Voir la face fonctionnelle
  de la graine `assembleur-out/features/<id>-*.md`.
- **`project`** - si retenu. **`state`** - le **nom** de l'état Backlog résolu ci-dessus (jamais le
  type).
- **`labels`** - le label plat **`Feature`** (taxonomie) **seul** (+ `walking-skeleton` si la feature
  001 / le walking skeleton). **Jamais** de label de numérotation **`feature:<id>`** / `Issue:<id>`
  (l'`identifier` Linear `<TEAM>-<n>` porte déjà le numéro), **jamais** `MVP`. Les labels plats
  **`Feature`** / **`Task`** **préexistent** dans l'espace de travail : les **résoudre par nom** via
  `list_issue_labels` (comparaison **insensible à la casse**) pour vérifier qu'ils existent, puis les
  passer **par nom** dans le paramètre **`labels`** - **ne pas les créer**. Un label absent : le créer
  via `create_issue_label` ou l'omettre (best-effort, ne pas bloquer).
  **Attention, le paramètre est `labels` (tableau de noms ou d'ids), pas `labelIds`** - et sur une
  **mise à jour** il **remplace l'ensemble des labels** du ticket : ne jamais le passer en mise à jour
  sans avoir d'abord **fusionné les labels existants** (sinon on efface `walking-skeleton` et les
  autres).
- Récupérer dans la réponse : l'**`identifier`** (ex. `ENG-123`) et l'**`url`**. L'`identifier` est
  la **clé de rattachement** utilisée ensuite comme `parentId` (voir ci-dessous) ; le MCP ne
  retourne **pas** d'UUID interne - ne pas en chercher un.

## Sous-tickets Task par Functional Requirement (`premier-alimente-linear`)
Chaque "chose à faire" d'une feature est un **vrai sous-ticket `Task`** (pas une checkbox dans la
description). `premier-alimente-linear` crée **un `Task` par Functional Requirement** (`FR-xxx`) de la
graine `assembleur-out/features/<id>-*.md`, **rattaché** à la Feature :

`save_issue({team, title: "FR-00x - <intitulé fonctionnel court>", parentId: "<identifier de la
Feature>", labels: ["Task"], description: "<énoncé du FR, 1 ligne>", state: "<nom Backlog>"})`

- **`parentId` = l'`identifier` de la Feature** (ex. `ENG-123`). Le MCP `linear-prism` **accepte les
  identifiants** et **ne retourne aucun UUID interne** : ne pas chercher d'`issue_id`.
- **State = le nom de l'état Backlog** (comme la Feature). Label **`Task`** seul.
- **Idempotence via Linear** : avant de créer, `list_issues({parentId})` - un Task dont le titre
  commence par le jeton **`FR-00x -`** existe déjà -> ne pas recréer. **Rien n'est consigné dans le
  manifeste.**

*(Niveau distinct, plus tard : `creation-taches-par-phase-de-spec` crée en plus un `Task` par **phase** de
`tasks.md` après SpecKit - voir ci-dessous. Les deux niveaux coexistent sous la même Feature,
distingués par leur jeton de titre : `FR-00x -` vs `Phase N -`.)*

## Dépendances entre features -> relations bloquantes
La carte `assembleur-out/feature-map.md` porte la colonne **"Dépend de"**. Les features sont
traitées **dans l'ordre** (001, 002, ...) ; une dépendance pointe vers une feature **antérieure**,
donc **déjà créée**. Sur le ticket parent de la feature dépendante, poser :
`save_issue({id: "<identifier de la feature>", blockedBy: ["<identifier de la dépendance>"]})`
(ou passer `blockedBy` dès la création). `blocks`/`blockedBy` sont **append-only**.

## Sous-tickets par phase (`tasks.md`) -> pour `creation-taches-par-phase-de-spec`
Après `/speckit.tasks`, chaque feature a un `specs/<feature>/tasks.md`. On crée **un vrai sous-ticket
par phase** - comme partout ici, jamais une checkbox dans une description.

- **Parser `tasks.md`** (lecture seule) : phases = lignes `^## Phase (\d+): (.+)$` ; tâches d'une
  phase = lignes `^- \[[ xX]\] (T\d{3})(?: \[P\])?(?: \[US\d+\])? (.+)$`. Les phases sont
  **séquentielles** (Setup, Foundational, une par User Story avec sa priorité `P1/P2/P3`, Polish) et
  peuvent contenir des **emoji** (🎯 ⚠️) à retirer des titres.
- **Titre descriptif** (obligatoire) : jamais le nom générique brut ("Setup"). Enrichir depuis les
  tâches de la phase ; pour une phase "User Story N - <titre>", reprendre l'intitulé de la story.
- **Créer le sous-ticket** :
  `save_issue({team, title, parentId: "<identifier du ticket Feature>", labels: ["Task"],
  description: "<résumé 1 ligne>", state: "<nom Backlog>"})`. Le **`parentId` est l'`identifier`**
  du ticket `Feature` (ex. `ENG-123`) - le MCP l'accepte et ne retourne aucun UUID interne.
  **State = le nom de l'état Backlog.** La **description est un résumé d'une ligne** (pas
  d'énumération des `Txxx`).
- **Rattraper le label `Feature`** sur le ticket de feature sans écraser ses labels : `get_issue({id})`
  -> **union des labels existants + `Feature`** -> `save_issue({id, labels: <union des noms>})`. Le
  paramètre `labels` **remplace tout** : sans l'union, on efface les labels déjà posés.
- **Rien n'est consigné dans le manifeste** : la ré-identification passe par `list_issues({parentId})`
  + le jeton `Phase N -` en tête de titre.

## Mettre à jour un ticket (statut)
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
- **Faire avancer une sous-partie d'une feature** : il n'y a **aucune case à cocher** dans les
  descriptions - chaque "chose à faire" est un **vrai sous-ticket** (`Task` par FR posé par
  `premier-alimente-linear`, `Task` par phase posé par `creation-taches-par-phase-de-spec`). On met donc à jour
  **le sous-ticket lui-même** : le retrouver via `list_issues({parentId: "<identifier de la
  Feature>"})` (jeton `FR-00x -` ou `Phase N -` en tête de titre), puis `save_issue({id, state})`
  sur **ce sous-ticket**. Ne jamais éditer la `description` du parent pour signifier un avancement.
- **Idempotence** : lire l'état courant (`get_issue`) **avant** d'écrire ; s'il est déjà celui visé,
  ne rien faire. **L'état courant vit dans Linear** - ne **rien consigner** dans le manifeste committé
  (l'avancement de fabrication n'y va pas : deux développeurs sur deux branches le réécriraient en
  parallèle -> conflit de merge).
- **Pas de commentaire** par défaut (on ne change que l'état / la case). `save_comment({issueId, body})`
  existe mais n'est pas utilisé ici.

## Idempotence (Linear est la seule source de vérité des tickets)
**Aucun ticket n'est consigné dans le manifeste committé** - ni Feature, ni Task, ni statut. La carte
des tickets et l'état d'avancement vivent **dans Linear** ; le manifeste ne porte que la
**configuration** du pont Linear (équipe, projet). Raison : la fabrication est concurrente (une
branche par développeur) et un registre de tickets dans le fichier committé unique se désynchronise
et provoque des conflits de merge.

Ré-identification (avant toute création) :
- **Feature** : `list_issues({team, label Feature})` -> comparaison par **titre exact** ; un ticket
  trouvé est **adopté** (réutiliser son `identifier` comme `parentId`), jamais recréé.
- **Task par FR** (`premier-alimente-linear`) : `list_issues({parentId})` + jeton **`FR-00x -`** en
  tête de titre.
- **Task par phase** (`creation-taches-par-phase-de-spec`) : `list_issues({parentId})` + jeton **`Phase N -`** en
  tête de titre.
- **État d'avancement** (`update-issue-linear`) : `get_issue({id})` avant d'écrire.

### Phase déjà possédée par un ticket de maintenance (4e clé de jointure)
Les trois clés ci-dessus rattachent un objet à un sous-ticket **que la fabrication a créé**. Il manquait
la clé inverse : une phase dont le travail est **déjà suivi par un ticket d'anomalie ou d'évolution**,
créé en aval par `maintenance`. Sans elle, `creation-taches-par-phase-de-spec` voit la phase comme manquante et crée un
**doublon** - frère du ticket d'origine sous la même Feature, deux états à synchroniser, et la source de
vérité unique tombe.

Clé : la phase **nomme son propriétaire dans son titre**, dans `tasks.md`.

```
## Phase 7: Évolution RAG-12 - Ingestion des pièces scannées au format PNG
## Phase 8: Anomalie RAG-31 - Correction du chevauchement de réservations
```

Motif : `^\s*(Évolution|Evolution|Anomalie)\s+([A-Za-z][A-Za-z0-9]*-\d+)\b` appliqué au titre qui suit
`## Phase N:`. Le mot littéral est **obligatoire** avant l'identifiant - un motif large `[A-Z]+-\d+`
matcherait `FR-006`, `ADR-010`, `SC-001`, `TC-001` et supprimerait en silence des sous-tickets légitimes.

Règle : une phase marquée **et** dont l'identifiant **résout** (`get_issue`) n'est **ni créée ni
proposée** - elle est énoncée ("Phase 7 déjà suivie par RAG-12"). Un marqueur qui ne résout pas est le
seul cas à remonter à l'humain. Posé par `maintenance` (`realisation-evolution`, `correction-anomalie`), lu
par `creation-taches-par-phase-de-spec` et par le hook `linear-sync/tasks_linear_hook.py` (qui, lui, ne peut que
reconnaître le motif : il ne parle jamais à Linear).

Vue d'ensemble des règles multi-développeurs (numérotation, couplage, merge, constitution) :
`fabrication-parallele.md`.
Bloc manifeste (configuration seule, écrit en silence par `premier-alimente-linear`) :
```json
"linear": {
  "phase": "init", "team": null, "project": null
}
```
Une feature écartée ou fusionnée pendant la revue n'a simplement **pas de ticket** (décision prise et
confirmée en session). Écriture **silencieuse** (read-modify-write + revalidation JSON), jamais narrée.
