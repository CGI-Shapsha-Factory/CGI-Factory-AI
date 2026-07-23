---
name: premier-alimente-linear
description: Première alimentation de Linear - transforme les features approuvées en tickets Linear (un ticket Feature par feature + un sous-ticket Task par Functional Requirement, tout en Backlog, label Feature seul), avec confirmation ticket par ticket, via le MCP linear-prism - juste avant install-speckit. Les sous-tickets par phase (label Task) restent créés plus tard par creation-taches-par-phase-de-spec, après /speckit.tasks.
---

# premier-alimente-linear

**Pont vers Linear.** À lancer **après `assembleur-convergence`** (le paquet est produit, la
cohérence validée, les features **déjà approuvées**) et **avant `install-speckit`**. Ce skill lit
la liste des features, la présente en **tableau de revue**, puis - **ticket par ticket, avec
confirmation** - crée **un ticket `Feature` par feature** et, sous chacun, **un sous-ticket `Task`
par Functional Requirement**, pour que l'équipe pilote la fabrication SpecKit feature par feature.

> **Point de gel du registre de features.** Peupler Linear **fige** le découpage : à partir d'ici,
> `architecture.feature_sequence` est **immuable** (plus de découpage/fusion, plus de renumérotation).
> Tout **arbitrage** (split/merge) doit avoir eu lieu **avant**, dans `assembleur-convergence`, qui a
> l'autorité finale sur le registre. Ensuite, le garde-fou `check_speckit_alignment.py` impose
> l'alignement `specs/NNN-slug` <-> registre pour toute la fabrication.

## Objectif
Créer, dans Linear, pour **chaque feature approuvée** :
- **un ticket `Feature`** - un **titre** (intitulé métier), une **description d'une ligne**, le label
  **`Feature`** (seul ; **jamais** `feature:<id>` ni un label de numérotation - l'identifiant Linear
  `<TEAM>-<n>` porte déjà le numéro) (+ `walking-skeleton` si concernée) ;
- **un sous-ticket `Task` par Functional Requirement** (`FR-xxx`) de la graine, **rattaché** à la
  Feature (`parentId`), label **`Task`**.

**Tout est créé en Backlog** (features **et** tasks). Chaque ticket est **confirmé avant création**.
Idempotent : on ne recrée jamais un ticket (feature ou task) déjà posé. **Plus de checklist dans la
description** - chaque "chose à faire" est un vrai sous-ticket `Task`.

## Frontière (exception assumée)
L'assembleur ne produit que son paquet (`assembleur-out/`) et **n'écrit jamais dans le repo cible**.
Créer des tickets Linear est une **exception explicitement bornée** à "pas de Linear" : Linear est
un **système externe** (pas le repo cible, pas un fichier que SpecKit génère). La seule écriture
propre à la Factory est le bloc `linear` du manifeste - **configuration seule** (équipe, projet) :
**les tickets eux-mêmes ne sont jamais consignés dans le manifeste**, Linear est leur unique source
de vérité. La création passe par le **MCP du plugin `linear-prism`** (externe à la Factory) - voir
`references/linear-guide.md`.

## Pré-requis (vérification silencieuse)
Lire `manifest.json` **sans l'annoncer** :
- la convergence a tourné et la **cohérence est validée**, et le paquet est présent
  (`assembleur-out/feature-map.md` + au moins une graine `assembleur-out/features/*.md`) ;
- sinon -> le dire en clair et orienter vers `/assembleur:assembleur-convergence` :
  > "Les tickets ne peuvent pas être créés : il faut d'abord la convergence terminée et la
  > cohérence validée (le paquet de features approuvées)."

Le registre des features est `architecture.feature_sequence` (`{id, ucs, name}` + le
`walking_skeleton`). **Ne rien inventer** : on ne crée de ticket que pour les features approuvées.

## Étape 1 : Détecter Linear (MCP linear-prism)
Sonder `mcp__plugin_linear-prism_linear__list_teams` (cf. `references/linear-guide.md`).
- Disponible -> continuer.
- Indisponible -> **ne rien créer** : refuser en clair ("Je ne peux pas créer de tickets Linear :
  le MCP `linear-prism` n'est pas disponible.") et afficher les **instructions d'installation**
  (section "Installation du plugin linear-prism" de `references/linear-guide.md` : marketplace,
  `/plugin install`, redémarrage, `/mcp`). Installer puis **relancer** une fois authentifié.

## Étape 2 : Charger et présenter les features (tableau de revue)
Lire `architecture.feature_sequence`, `assembleur-out/feature-map.md` (ordre, couplage, **Dépend
de**, parallélisable) et chaque graine `assembleur-out/features/<id>-*.md` (User Stories,
`FR-xxx`, `SC-xxx`, cas limites). Afficher **un tableau de revue unique** (c'est l'exception au
"pas de tableau" - une revue, comme `feature-map.md`) :

| Ordre | Feature | Use cases | Walking skeleton | Dépend de | Titre proposé | Description (1 ligne) | # FR (Tasks) |
|-------|---------|-----------|------------------|-----------|---------------|-----------------------|--------------|

(La colonne **# FR (Tasks)** = le nombre de Functional Requirements de la graine -> autant de
sous-tickets `Task` qui seront créés sous la Feature.)

Puis **demander avec `AskUserQuestion` : "Créer un ticket Feature par feature, avec ses
sous-tickets Task ?"** - deux options, "créer les tickets" (recommandé) et "ajuster d'abord le
découpage" ; le refus reste cliquable.
- **Créer** -> passer à l'Étape 3.
- **Ajuster** -> **boucle d'ajustement** (un appel `AskUserQuestion` par point, cf.
  `references/interactive-loop.md` : recommandée + alternative) : quelles features **fusionner / renommer / écarter /
  réordonner** ? Refléter chaque décision dans le tableau (une feature écartée ou fusionnée n'aura
  simplement **pas de ticket** - la décision se prend et se confirme **en session**), **réafficher**
  le tableau, et **confirmer l'ensemble** avant de créer.

## Étape 3 : Cible Linear (une seule fois)
Choisir l'**équipe** (`list_teams` -> **avec `AskUserQuestion`**, deux options : la recommandée et
l'alternative la plus proche) et, optionnellement, le
**projet** (`list_projects`).

**État initial = Backlog (impératif absolu).** `list_issue_statuses({team})` -> repérer l'état dont le
**type** est `backlog` et **retenir son `name`** (il varie selon l'équipe). C'est ce **nom** qui sera
passé à `save_issue`, **jamais le type** : le MCP résout l'état **par nom seulement** et **échoue en
silence** sur une valeur inconnue (les tickets atterriraient dans l'état par défaut de l'équipe, sans
la moindre erreur). **Toute** issue créée par ce skill - Feature **comme** Task - part en **Backlog**,
jamais en Todo. Si **aucun** état de type `backlog` n'est résolvable : **ne rien créer**, le dire en
clair et demander **avec `AskUserQuestion`** quel état de l'équipe fait office de backlog (deux
options : l'état le plus probable de la liste, recommandé, et l'alternative la plus proche). **Jamais**
de repli sur l'état par défaut.

Résoudre aussi les labels **`Feature`** et **`Task`** par nom (`list_issue_labels`, insensible à la
casse ; ne pas les créer). Consigner `team`/`project` dans le manifeste **en silence** (configuration
seule - jamais de tickets). Puis **relever l'existant dans Linear** (base d'idempotence) :
`list_issues({team, label Feature})` -> la liste des tickets `Feature` déjà présents, comparés par
**titre exact**. Détails : `references/linear-guide.md`.

## Étape 4 : Boucle par feature : la Feature puis ses Task (confirmation obligatoire)
Pour **chaque** feature retenue, **dans l'ordre** :
1. **Préparer** :
   - la **Feature** : un **titre** (intitulé métier, ex. `001 - Recherche Q&A sourcée`) et une
     **description d'une ligne** (parcours principal / rôle de la feature, depuis la graine) ;
   - la **liste des `Task`** : **un par Functional Requirement** de la graine
     `assembleur-out/features/<id>-*.md` (§Functional Requirements). Pour chaque `FR-xxx` : **titre**
     = `FR-00x - <intitulé fonctionnel court>` ; **description d'une ligne** = l'énoncé du FR.
2. **Confirmer avec `AskUserQuestion`** : le **titre** + **description** de la Feature **et
   la liste des Task (FR)** - deux options, "créer tel que proposé" (recommandé) et "ajuster",
   la saisie libre recevant les corrections. **Ne rien créer** tant que ce n'est pas approuvé ;
   "ajuster" corrige en place.
3. **Réconcilier avec Linear avant de créer** : si un ticket `Feature` au **titre exact** existe déjà
   dans le relevé de l'Étape 3 (relancer `list_issues({team, label Feature})` au besoin), **l'adopter**
   (récupérer son `identifier` / `url` - l'`identifier` servira de `parentId`) et **ne pas le
   recréer** ; sinon **créer la Feature** (cf. `references/linear-guide.md`) : `save_issue({team, title, description,
   labels:["Feature"(+"walking-skeleton" si 001/walking skeleton)], state:"<nom de l'état Backlog>"})`
   -> récupérer `identifier` / `url`. **Sur la toute première création**, relire le ticket
   (`get_issue({id})`) et vérifier qu'il est bien en **Backlog** ; s'il ne l'est pas, **s'arrêter
   immédiatement** et le dire en clair (ne jamais enchaîner N créations mal placées). Poser les
   **relations bloquantes** (`blockedBy`) d'après
   "Dépend de" (la dépendance est une feature **antérieure**, déjà créée). Label **`Feature` seul** -
   **jamais** `feature:<id>`, **jamais** `MVP`.
4. **Créer chaque Task** (sous-ticket de la Feature) : d'abord `list_issues({parentId:<identifier
   de la Feature>})` -> un Task dont le titre commence par le **jeton `FR-00x -`** existe déjà ->
   **ne pas le recréer**. Sinon `save_issue({team, title:"FR-00x - ...",
   parentId:<identifier de la Feature>, labels:["Task"], description:"<énoncé du FR>",
   state:"<nom de l'état Backlog>"})`. Le **`parentId` est l'`identifier`** de la Feature (ex.
   `ENG-123`) : le MCP **accepte les identifiants** et **ne retourne aucun UUID interne** - ne pas
   chercher d'`issue_id`.
5. **Passer à la feature suivante.** **Répéter jusqu'à ce que toutes soient traitées.** **Rien n'est
   consigné dans le manifeste** : ni ticket, ni sous-ticket, ni statut - **Linear est la seule source
   de vérité** de la carte des tickets.

**Idempotence (via Linear, jamais via le manifeste)** : une Feature est ré-identifiée par son **titre
exact** dans `list_issues({team, label Feature})` ; un Task par le **jeton `FR-00x -`** dans
`list_issues({parentId})`. Un ticket trouvé est **adopté**, jamais recréé - y compris si le skill est
relancé par un autre développeur ou depuis un autre clone (le manifeste ne porte aucune carte de
tickets à désynchroniser).

## Vérification avant de conclure
- Chaque feature approuvée a **son ticket `Feature`** (ou a été explicitement écartée/fusionnée en
  session), en **Backlog**, label **`Feature`** (sans `feature:<id>`) ; les **dépendances**
  (`blockedBy`) sont posées.
- Chaque `Feature` porte **un sous-ticket `Task` par FR** (rattaché par `parentId`), en **Backlog**,
  label `Task`.
- **Vérifier dans Linear** (pas dans le manifeste) : relancer `list_issues({team, label Feature})` et
  confirmer que chaque feature retenue a son ticket ; contrôler quelques `list_issues({parentId})` au
  hasard pour les Task par FR.
- **Contrôle d'état (obligatoire)** : sur ce relevé, vérifier que **tous** les tickets créés - Feature
  **et** Task - sont bien en **Backlog**. Un seul ticket ailleurs = l'état n'a pas été résolu par son
  nom : le dire en clair et corriger (`save_issue({id, state:"<nom Backlog>"})`) avant de conclure.
- Lancer le garde-fou (il valide la **configuration** du bloc `linear` - équipe posée - pas les
  tickets, qui vivent dans Linear). La variable de plugin **ne s'expanse pas pareil selon le
  shell** - prendre la forme du shell utilisé :
  - Bash : `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_linear.py" <racine>/manifest.json`
  - PowerShell : `python "$env:CLAUDE_PLUGIN_ROOT/scripts/check_linear.py" <racine>/manifest.json`
    (en PowerShell, `${CLAUDE_PLUGIN_ROOT}` désigne une variable de session, **pas**
    l'environnement : le chemin serait vide et la commande échouerait)
- Le bloc `linear` du manifeste **reparse sans erreur** ; restitution **en prose** ("j'ai créé N
  tickets Feature et M sous-tickets Task, en Backlog"), manifeste mis à jour **en silence**.

## Règles invariantes
- **Exception Linear bornée.** On n'écrit que dans Linear (externe) + le bloc `linear` du manifeste ;
  jamais dans le repo cible.
- **Confirmer avant de créer.** Chaque ticket est validé par l'humain avant création (action
  externe, difficile à défaire).
- **Un point à la fois.** Questions et confirmations **avec `AskUserQuestion`**, un appel chacune (cf.
  `interactive-loop.md`) ; le seul tableau autorisé est le tableau de revue de l'Étape 2.
- **Idempotent.** On ne crée jamais deux fois le même ticket.
- **Rien d'inventé.** Seulement les features approuvées par la convergence.
- **Manifeste en silence.** Aucun nom de clé à l'écran ; restitution en prose.

Étape suivante : `/assembleur:install-speckit` - poser SpecKit dans le repo, puis fabriquer feature par feature (chaque ticket Linear pilote un cycle `/speckit.specify` -> `/speckit.plan` -> `/speckit.tasks` -> `/speckit.implement`). **Après `/speckit.tasks`** (une fois `specs/<feature>/tasks.md` produit), lancer `/assembleur:creation-taches-par-phase-de-spec` pour créer un **sous-ticket par phase** (label `Task`) rattaché au ticket `Feature` de chaque feature.
