# Référence — Linear (clé API, GraphQL, défauts) pour `init-linear`

Détails consommés par `/assembleur:init-linear`. **L'écriture Linear n'a lieu qu'après la porte
humaine** (`assembly.team_validated == true`).

## Connexion : clé API personnelle dans `.env`
- L'utilisateur fournit une **clé API personnelle Linear** placée dans `.env` :
  `LINEAR_API_KEY=lin_api_…`.
- **Créer la clé** : Linear → **Settings** → **Security & access** → **Personal API keys** →
  **New API key** → nommer + choisir l'accès (≥ *Create issues* / *Write*) → **Create** → **copier**
  (affichée une seule fois).
- **Sécurité** : `.env` **gitignored** ; la clé n'est **jamais** affichée, loguée, ni commitée.

## API GraphQL
- Endpoint : `POST https://api.linear.app/graphql` · en-tête **`Authorization: <LINEAR_API_KEY>`**
  (sans « Bearer ») · `Content-Type: application/json`.
- **Équipe** : `query { teams { nodes { id name key } } }` (une issue appartient à une team).
- **Projets (dédup)** : `query { projects { nodes { id name url } } }` → comparer à `manifest.project`.
- **États** : `query { workflowStates { nodes { id name type } } }` → **« Todo » = state de type
  `unstarted`** (PAS `backlog`).
- **Créer le projet** : `mutation { projectCreate(input:{ name:"…", teamIds:["…"] }){ project { id url } } }`.
- **Créer une issue** : `mutation { issueCreate(input:{ title:"<id> — <nom>", description:"…",
  teamId:"…", projectId:"…", stateId:"<unstarted>" }){ issue { id identifier url } } }`.
  **Pas d'`assigneeId`** → issue **non assignée**. Tracer **`id` (uuid) ET `identifier` (ex. `ENG-123`)**.
- (Labels : résoudre/créer via `issueLabelCreate` / `labels`, puis `labelIds` ; dépendances via
  `issueRelationCreate` type `blocks`.)

## Transition d'état « Todo → En cours » (aval, hook Claude Code)
- **État courant + équipe d'une issue** : `query($id:String!){ issue(id:$id){ id identifier team{ id }
  state{ type } } }` (l'`id` accepte l'uuid **ou** la forme courte `ENG-123`).
- **État « En cours »** = workflow state de **type `started`** de l'équipe (jamais `unstarted`/`backlog`) :
  `query($t:String!){ team(id:$t){ states{ nodes{ id name type position } } } }`. ⚠️ Une équipe peut avoir
  **plusieurs** états `started` (ex. « In Progress » **et** « In Review ») → **préférer « In Progress »/
  « En cours »**, sinon le `started` de **plus petite `position`** ; **jamais « In Review »**.
- **Passer en cours** : `mutation($id:String!,$s:String!){ issueUpdate(id:$id, input:{stateId:$s}){ success } }`.
  (Assignee optionnel : `viewer{ id }` = porteur de la clé → `input:{ assigneeId }` pour coller à
  l'auto-assign Linear.)
- **Idempotent** : si l'état est déjà `started`/`completed`/`canceled`, ne rien faire.

## Convention de branche (clé de résolution hook + filet natif)
Brancher avec l'**identifiant Linear** embarqué : `<identifier>-<slug>` (ex. `eng-123-recherche-qa`).
Le hook retrouve l'issue par cet identifiant (ou par `feature:<id>` / `branch_slug` via
`<repo>/.claude/linear-map.json`). Le **filet natif** Linear (PR → En cours, merge → Terminé,
*magic words* `Fixes <identifier>`) repose sur la même convention.

## Détection d'un projet existant (dédup = Linear, pas le flag local)
Comparer `manifest.project` aux projets (nom normalisé : casse/espaces/accents + similarité +
tâches similaires). **Si un projet proche existe** → **informer** (nom, auteur, date, nb d'issues),
**donner le lien direct**, **conseiller**, puis **s'arrêter** — ne rien écrire. Clé de dédup des
issues (si réutilisation décidée par l'humain) : préfixe de titre `<id> —` ou label `feature:<id>`.

## Défauts à appliquer
Features **non assignées**, en **Todo** (`unstarted`) ; labels `feature:<id>` / `walking-skeleton`
(id `001`) / `MVP` (si `mvp`) ; dépendances en relations `blocks` ; ordre = séquence.

## Fallback (clé absente / API indisponible)
Produire `factory-docs/work/linear-features.json` (une entrée par feature), à importer manuellement.
**Pas d'écriture fantôme, pas de fausse confirmation.**

## Alternative
L'agent `linear-prism:task-decomposer-linear` peut être mobilisé s'il est disponible.
