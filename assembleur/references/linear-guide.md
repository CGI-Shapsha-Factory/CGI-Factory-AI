# Guide Linear — création et mise à jour des tickets via le MCP linear-prism (assembleur)

Référence d'usage pour `premier-alimente-linear` (création) et `update-issue-linear` (mise à jour). Le
dialogue passe par le **MCP du plugin `linear-prism`** (serveur hébergé `https://mcp.linear.app/mcp`,
authentifié en OAuth via `/mcp` — **aucune clé API** à gérer). Ce plugin est **externe à la Factory**
(voir « Installation » ci-dessous) : les skills le détectent et, s'il est absent, la création bascule
en **mode brouillon** (la mise à jour, elle, a besoin du MCP).

## Détection (avant tout)
Sonder `mcp__plugin_linear-prism_linear__list_teams`.
- **Répond** (liste d'équipes) → le MCP est prêt, continuer.
- **Échoue / indisponible** → dire en clair : « La création de tickets Linear a besoin du plugin
  `linear-prism` et d'une authentification (`/mcp`). Installe-le puis relance — ou je te prépare
  les tickets en **brouillon** (`assembleur-out/linear-drafts.md`) à coller à la main. » **Ne
  jamais bloquer** : proposer le mode brouillon.

## Installation du plugin linear-prism (si le MCP est absent)
`linear-prism` est un **plugin tiers** (externe à la Factory) qui **empaquette la configuration du
serveur MCP Linear hébergé** (`https://mcp.linear.app/mcp`, **OAuth — aucune clé API**). S'il n'est
pas détecté, guider l'utilisateur pas-à-pas :

1. **Ajouter la marketplace** : `/plugin marketplace add shinpr/linear-prism`
   (variante « bundle » si l'équipe le distribue ainsi : `/plugin marketplace add shinpr/claude-code-workflows`).
2. **Installer le plugin** : `/plugin install linear-prism@linear-prism`
   (ou `/plugin install linear-prism@claude-code-workflows` pour la variante bundle — le suffixe
   `@<marketplace>` doit correspondre à la marketplace ajoutée).
3. **Redémarrer Claude Code** (pour charger le serveur MCP du plugin).
4. **S'authentifier** : lancer **`/mcp`**, choisir le serveur `linear`, terminer le login OAuth dans
   le navigateur.

Revalider ensuite avec la **détection** ci-dessus (`list_teams` répond). Tant que ce n'est pas fait,
la **création** bascule en mode brouillon ; la **mise à jour** a besoin du MCP (relancer une fois
installé).

## Accès par clé API (Quark / environnement sans OAuth)
Le serveur MCP Linear s'authentifie en **OAuth** (défaut, ci-dessus) **ou** par **clé API**. Dans un
environnement où le flux OAuth `/mcp` n'est pas disponible (ex. le PO qui pilote depuis **Quark** et
demande une action en **écriture**), utiliser une **clé API personnelle** :
1. Linear → **Settings → Security & access → Personal API keys → New API key**.
2. Nommer la clé, lui donner un **accès en écriture** (*Write* / *Create issues* selon le besoin), la
   **restreindre à l'équipe** du projet, puis **Create**. La clé n'est **affichée qu'une fois** — la
   copier immédiatement (format `lin_api_…`).
3. La stocker dans un fichier **`.env`** (jamais commité, ajouté au `.gitignore`) : `LINEAR_API_KEY=lin_api_…`.
4. Le MCP `linear-prism` lit alors `LINEAR_API_KEY` pour s'authentifier (pas de login OAuth).

**Ne jamais** afficher, loguer ni committer la clé. C'est cette section que `create-cowork-md`
reprend dans `init-cowork.md` (« Accès Linear pour Quark »).

## Cible (une seule fois, avant la boucle)
- **Équipe** (obligatoire pour créer) : `list_teams` → présenter en 3 options (recommandée =
  celle qui correspond au projet / à l'organisation, alternative(s), « saisir »). Retenir le
  `team` (nom ou id).
- **Projet** (optionnel) : `list_projects({team})` → proposer un projet existant ou en créer un au
  nom du produit. Retenir le `project`.
- **État initial** (optionnel) : `list_issue_statuses({team})` → viser un état de type **Todo /
  unstarted** (jamais Backlog), tickets **non assignés**. Si l'état n'est pas résolvable
  proprement, laisser l'état par défaut de l'équipe.

## Créer un ticket (par feature)
`mcp__plugin_linear-prism_linear__save_issue` — création quand on ne passe **pas** d'`id` :
- **`team`** (obligatoire) — l'équipe retenue.
- **`title`** (obligatoire) — l'intitulé métier en clair (ex. `001 — Recherche Q&A sourcée`).
- **`description`** — **Markdown** (newlines littéraux, pas d'échappement) : la description d'une
  ligne + un court contexte (parcours principal, critère de succès clé). Voir la face fonctionnelle
  de la graine `assembleur-out/features/<id>-*.spec-seed.md`.
- **`project`** — si retenu. **`state`** — Todo/unstarted si résolu.
- **`labels`** — le label plat **`Feature`** (taxonomie) + `feature:<id>` (clé de jointure) +
  `walking-skeleton` (si la feature 001 / le walking skeleton). **Jamais de label `MVP`** —
  l'architecture n'a **aucune notion de MVP**. Les labels plats **`Feature`** / **`Task`**
  **préexistent** dans l'espace de travail : les **résoudre par nom** via `list_issue_labels`
  (comparaison **insensible à la casse**) et passer leurs **UUID** dans `labelIds` — **ne pas les
  créer**. Un label absent : le créer via `create_issue_label` ou l'omettre (best-effort, ne pas
  bloquer). Note : `save_issue` prend `labelIds` (UUID), pas des noms — d'où la résolution préalable.
- Récupérer dans la réponse : l'**id interne**, l'**identifier** (ex. `ENG-123`) et l'**url**.

## Liste de contrôle d'une grosse feature → checkboxes dans la description
Pour une feature **volumineuse** (bundle > 1 use case, **ou** ≥ 4 exigences fonctionnelles, **ou**
≥ 2 user stories dans la graine) : inclure la liste de contrôle **directement dans la `description`**
du ticket via la syntaxe Markdown `- [ ] item`. Linear les rend interactifs (cases cochables). Pas de
sous-ticket (`parentId`) — tout reste dans un seul ticket. Format de la description :

```markdown
Description en une ligne.

**Checklist :**
- [ ] FR-004 — Intitulé fonctionnel
- [ ] FR-005 — Intitulé fonctionnel
```

Dériver les items des `FR-xxx` / scénarios d'acceptation / `SC-xxx` de la graine.

## Dépendances entre features → relations bloquantes
La carte `assembleur-out/feature-map.md` porte la colonne **« Dépend de »**. Les features sont
traitées **dans l'ordre** (001, 002, …) ; une dépendance pointe vers une feature **antérieure**,
donc **déjà créée**. Sur le ticket parent de la feature dépendante, poser :
`save_issue({id: "<identifier de la feature>", blockedBy: ["<identifier de la dépendance>"]})`
(ou passer `blockedBy` dès la création). `blocks`/`blockedBy` sont **append-only**.

## Sous-tickets par phase (`tasks.md`) → pour `creation-task-linear`
Après `/speckit.tasks`, chaque feature a un `specs/<feature>/tasks.md`. On crée **un vrai sous-ticket
par phase** (contrairement à la checklist-dans-la-description du ticket de feature).

- **Parser `tasks.md`** (lecture seule) : phases = lignes `^## Phase (\d+): (.+)$` ; tâches d'une
  phase = lignes `^- \[[ xX]\] (T\d{3})(?: \[P\])?(?: \[US\d+\])? (.+)$`. Les phases sont
  **séquentielles** (Setup, Foundational, une par User Story avec sa priorité `P1/P2/P3`, Polish) et
  peuvent contenir des **emoji** (🎯 ⚠️) à retirer des titres.
- **Titre descriptif** (obligatoire) : jamais le nom générique brut (« Setup »). Enrichir depuis les
  tâches de la phase ; pour une phase « User Story N — <titre> », reprendre l'intitulé de la story.
- **Créer le sous-ticket** :
  `save_issue({team, title, parentId: "<issue_id UUID du ticket Feature>", labelIds: ["<UUID Task>"],
  description: "<résumé 1 ligne>", state})`. Le **`parentId` est l'UUID interne** (`issue_id`) du
  ticket `Feature`, **pas** l'`identifier` (`ENG-123`). La **description est un résumé d'une ligne**
  (pas d'énumération des `Txxx`).
- **Rattraper le label `Feature`** sur le ticket de feature sans écraser ses labels : `get_issue({id})`
  → union des `labelIds` existants + `Feature` → `save_issue({id, labelIds: <union>})`.
- Récupérer `issue_id` / `identifier` / `url` et consigner dans `linear.issues[].sub_issues[]`.

## Mettre à jour un ticket (statut / cases à cocher)
Pour `update-issue-linear`. Un seul outil `save_issue` **crée ou met à jour** : passer un **`id`**
(l'`identifier`, ex. `LIN-123`) déclenche la **mise à jour** (le `team` n'est requis qu'à la création).

- **Trouver le ticket** : `list_issues({query: "<mots-clés du titre>", team})` (la recherche porte sur
  titre + description) ; ou `get_issue({id})` si l'`identifier` est déjà connu (retourne aussi l'état
  courant, la `description`, et le `branchName` git — utile pour recouper avec la branche courante).
- **Résoudre l'état** : `list_issue_statuses({team})` renvoie les états de l'équipe avec leur **type**
  (`backlog` / `unstarted` / `started` / `completed` / `canceled` / `triage`). Pour « terminé », viser
  le type **`completed`** ; « en cours » → `started`.
- **Changer l'état** : `save_issue({id, state})` — `state` accepte le **nom** (`"Done"`), le **type**
  (`completed`) ou l'**UUID** de l'état. Ex. : `save_issue({id: "LIN-123", state: "Done"})`.
- **Cocher une case** (sous-partie d'une grosse feature) : lire la `description` via `get_issue`,
  passer la ligne `- [ ] …` visée à `- [x] …`, puis `save_issue({id, description: "<MAJ>"})`.
- **Idempotence** : lire l'état courant (`get_issue`) **avant** d'écrire ; s'il est déjà celui visé,
  ne rien faire. Consigner le dernier état posé dans `linear.issues[]` via un champ **`workflow_state`**
  (distinct de `status`, qui reste l'action Factory `created/skipped/merged/draft` — `check_linear.py`
  n'y touche pas et ignore `workflow_state`).
- **Pas de commentaire** par défaut (on ne change que l'état / la case). `save_comment({issueId, body})`
  existe mais n'est pas utilisé ici.

## Idempotence (bloc manifeste `linear`)
Avant de créer, lire `linear.issues` : une feature déjà consignée avec un `issue_id` est **déjà
créée** → ne pas recréer (proposer éventuellement une mise à jour via `save_issue({id, …})`).
Bloc :
```json
"linear": {
  "phase": "init", "team": null, "project": null,
  "issues": [
    { "id": "001", "ucs": ["UC2"], "name": "…",
      "issue_id": "…", "identifier": "ENG-123", "url": "https://linear.app/…",
      "status": "created",
      "sub_issues": [
        { "phase": 1, "phase_name": "Setup", "title": "Mise en place : scaffolding & outillage (Ingestion)",
          "issue_id": "…", "identifier": "ENG-131", "url": "https://linear.app/…", "status": "created" }
      ]
    }
  ],
  "all_issues_created": false, "all_sub_issues_created": false
}
```
Statuts (ticket **et** sous-ticket) : `created` (posé, exige `issue_id`), `skipped` (écarté en
session), `merged` (fusionné), `draft` (mode brouillon). `sub_issues[]` (posé par `creation-task-linear`)
: **une entrée par phase** du `tasks.md`, clé stable = `id` de feature + `phase`. Écriture
**silencieuse** (read-modify-write + revalidation JSON), jamais narrée.

## Mode brouillon (repli, MCP absent)
Écrire `assembleur-out/linear-drafts.md` : une section par feature avec **titre**, **description
(1 ligne)**, et — si volumineuse — la **checklist** en cases Markdown `- [ ]` (les futurs
sous-tickets). L'équipe les crée ensuite à la main (ou relance quand `linear-prism` est prêt).
Consigner ces features avec `status: "draft"` dans le manifeste. Pour `creation-task-linear`, ajouter
sous chaque feature la **liste des phases** (titre descriptif + résumé d'une ligne), consignées en
`sub_issues[]` avec `status: "draft"`.
