# Guide Linear — création des tickets via le MCP linear-prism (assembleur)

Référence d'usage pour `init-issues-linear`. La création passe par le **MCP du plugin
`linear-prism`** (serveur hébergé `https://mcp.linear.app/mcp`, authentifié en OAuth via `/mcp` —
**aucune clé API** à gérer). Ce plugin est **externe à la Factory** : le skill le détecte et,
s'il est absent, bascule en **mode brouillon**.

## Détection (avant tout)
Sonder `mcp__plugin_linear-prism_linear__list_teams`.
- **Répond** (liste d'équipes) → le MCP est prêt, continuer.
- **Échoue / indisponible** → dire en clair : « La création de tickets Linear a besoin du plugin
  `linear-prism` et d'une authentification (`/mcp`). Installe-le puis relance — ou je te prépare
  les tickets en **brouillon** (`assembleur-out/linear-drafts.md`) à coller à la main. » **Ne
  jamais bloquer** : proposer le mode brouillon.

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
- **`labels`** — `feature:<id>` (toujours) + `walking-skeleton` (si la feature 001 / le walking
  skeleton). **Jamais de label `MVP`** — l'architecture n'a **aucune notion de MVP**. Si un label
  n'existe pas, le créer via `create_issue_label` ou l'omettre (best-effort, ne pas bloquer).
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
      "status": "created" }
  ],
  "all_issues_created": false
}
```
Statuts : `created` (ticket posé, exige `issue_id`), `skipped` (écartée en session), `merged`
(fusionnée dans une autre feature), `draft` (mode brouillon). Écriture **silencieuse**
(read-modify-write + revalidation JSON), jamais narrée.

## Mode brouillon (repli, MCP absent)
Écrire `assembleur-out/linear-drafts.md` : une section par feature avec **titre**, **description
(1 ligne)**, et — si volumineuse — la **checklist** en cases Markdown `- [ ]` (les futurs
sous-tickets). L'équipe les crée ensuite à la main (ou relance quand `linear-prism` est prêt).
Consigner ces features avec `status: "draft"` dans le manifeste.
