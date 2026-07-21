---
name: creation-task-linear
description: Après /speckit.tasks, crée un sous-ticket Linear par phase de specs/<feature>/tasks.md (label Task, titre descriptif, rattaché au ticket Feature de la feature) via le MCP linear-prism, avec confirmation phase par phase.
---

# creation-task-linear

**Deuxième niveau de tâches Linear (par phase d'implémentation).** À lancer **pendant la fabrication**,
**après `/speckit.tasks`** - c'est-à-dire une fois que SpecKit a produit `specs/<feature>/tasks.md`. Ce
skill lit les **phases** de chaque `tasks.md` et crée, dans Linear, **un sous-ticket par phase** (label
`Task`, en **Backlog**) **rattaché** (`parentId`) au ticket `Feature` déjà créé par
`premier-alimente-linear`.

> **Coexistence assumée (deux niveaux de Task).** `premier-alimente-linear` a déjà posé, sous chaque
> Feature, **un `Task` par Functional Requirement** (niveau fonctionnel). Ce skill ajoute, sous la même
> Feature, **un `Task` par phase** (niveau implémentation). Les Task par FR sont consignés dans le
> manifeste (carte amont figée, single-owner) ; les Task **par phase vivent uniquement dans Linear** -
> l'avancement de fabrication ne s'écrit **jamais** dans le manifeste committé (deux développeurs sur
> deux branches réécriraient le même registre committé -> conflit de merge).

> **Déclenchement automatique (hook).** Le hook `PostToolUse` `tasks_linear_hook.py` (posé par
> `install-speckit` dans `.claude/hooks/`) détecte **chaque édition d'un `specs/<feature>/tasks.md`** et,
> s'il repère une **phase sans sous-ticket** consigné, **pousse l'agent à lancer ce skill** (le hook ne
> parle jamais à Linear). Ce skill est donc la **sync** : il **vérifie** que chaque phase a son sous-ticket
> `Task` (label `Task`, **Backlog**, `parentId` = ticket `Feature`), **crée uniquement les manquants**
> (après confirmation groupée), et **ne modifie jamais** un sous-ticket déjà existant (ni état, ni label -
> "ce n'est pas son business").

## Objectif
Pour chaque feature dont le `tasks.md` existe : parcourir ses **phases** (`## Phase N: ...`) et créer
**un sous-ticket Linear par phase** avec :
- un **titre spécifique et descriptif** - **jamais** le nom générique brut de la phase ("Setup",
  "Foundational", "Polish", "Backend") : enrichir en lisant les tâches de la phase (ex.
  `Setup` -> "Mise en place : scaffolding, outillage & dépendances (Ingestion)") ; pour une phase
  "User Story N", reprendre l'intitulé de la story (déjà descriptif), nettoyé des emoji ;
- le label **`Task`** ;
- le **`parentId`** = le ticket `Feature` de la feature ;
- une **description d'une ligne** (résumé du but de la phase) - **pas de liste de tâches** dans le corps.

Chaque sous-ticket est **confirmé avant création**. Idempotent : une phase qui a **déjà son sous-ticket
dans Linear** (vérifié par `parentId`) n'est **pas recréée**.

## Frontière (exception assumée)
Comme `premier-alimente-linear` : créer des tickets Linear est une **exception explicitement bornée**
à "pas de Linear". Linear est un **système externe** (pas le repo cible, pas un fichier que SpecKit
génère). **Les sous-tickets de phase vivent uniquement dans Linear** - ce skill **n'écrit rien dans le
manifeste committé** : l'avancement de fabrication n'y est jamais consigné (deux développeurs sur deux
branches réécriraient le même registre committé -> conflit). On **lit** `specs/<feature>/tasks.md`
(fichier généré par SpecKit) **sans jamais le modifier**.

## Pré-requis (vérification silencieuse)
Lire `manifest.json` **sans l'annoncer** :
- `premier-alimente-linear` a tourné : le bloc `linear` porte la configuration (`team`) - les tickets
  `Feature` eux-mêmes se vérifient **dans Linear** (`list_issues({team, label Feature})`), jamais dans
  le manifeste ;
- au moins un `specs/<feature>/tasks.md` existe dans le repo de fabrication ;
- sinon -> le dire en clair et orienter :
  > "Les sous-tickets de phase ne peuvent pas être créés : il faut d'abord les tickets par feature
  > (`/assembleur:premier-alimente-linear`) **et** avoir lancé `/speckit.tasks` (le `tasks.md` de la
  > feature)."

**Ne rien inventer** : on ne crée un sous-ticket que pour une phase réellement présente dans un
`tasks.md`.

## Étape 1 : Détecter Linear (MCP linear-prism)
Sonder `mcp__plugin_linear-prism_linear__list_teams` (cf. `references/linear-guide.md`).
- Disponible -> continuer.
- Indisponible -> **ne rien créer** : refuser en clair ("Je ne peux pas créer de sous-tickets
  Linear : le MCP `linear-prism` n'est pas disponible.") et afficher les **instructions
  d'installation** (section "Installation du plugin linear-prism" de `references/linear-guide.md`).
  Installer puis **relancer** une fois authentifié.

## Étape 2 : Résoudre les labels et l'équipe (une seule fois)
- **Équipe** : réutiliser `linear.team` du manifeste (posé par `premier-alimente-linear`). Ne pas
  redemander.
- **Labels `Feature` / `Task`** : les **résoudre par nom** via
  `mcp__plugin_linear-prism_linear__list_issue_labels` (comparaison **insensible à la casse** - les
  labels s'appellent `Feature` / `Task`). Retenir leurs **UUID** pour la session. **Ne pas les créer**
  (ils préexistent dans l'espace de travail). Si l'un manque -> le dire en clair et proposer soit de le
  créer (`create_issue_label`, best-effort), soit de l'omettre. Détails :
  `references/linear-guide.md`.

## Étape 3 : Rattraper le label `Feature` sur les tickets de feature (additif)
Pour chaque ticket de feature (relevé via `list_issues({team, label Feature})`, complété au besoin
d'une recherche par titre pour les tickets sans label), s'assurer qu'il porte le label
`Feature` **sans perdre ses labels existants** : lire ses labels via `get_issue({id})`, puis
`save_issue({id, labelIds: <union des labelIds existants + Feature>})`. **Additif** : ne jamais
retirer un label existant (ex. `walking-skeleton`). Idempotent : si `Feature` est déjà présent, ne
rien écrire.

## Étape 4 : Boucle par feature puis par phase (confirmation obligatoire)
Pour **chaque** feature qui a un `specs/<feature>/tasks.md` :

1. **Rattacher** : retrouver le ticket `Feature` de la feature **dans Linear** -
   `list_issues({team, label Feature})` (ou `list_issues({query})`) et jointure par **titre** (l'id
   `001...` figure en tête du titre, ex. `001 - ...`) ou par nom de dossier/branche `NNN-slug`.
   Récupérer son **`issue_id` (UUID)** = le futur `parentId`. Si aucun ticket `Feature` ne
   correspond -> le signaler et passer (ne pas créer d'orphelin).
2. **Lister l'existant DANS Linear (autorité d'idempotence)** : `list_issues({parentId: "<issue_id>"})`
   pour récupérer les sous-tickets `Task` déjà créés sous cette Feature. **Linear est la source de
   vérité** (pas le manifeste - l'avancement de fabrication n'y est jamais écrit). La ré-identification
   d'une phase se fait sur le **jeton stable `Phase N -`** en tête de titre (voir étape 6).
3. **Parser `tasks.md`** (lecture seule) :
   - phases : lignes `^## Phase (\d+): (.+)$` (le titre suit le numéro) ;
   - tâches d'une phase : lignes `^- \[[ xX]\] (T\d{3})(?: \[P\])?(?: \[US\d+\])? (.+)$`, groupées
     sous la phase courante (les IDs `T001...` sont **séquentiels sur tout le fichier**) ;
   - **retirer les emoji** (🎯 ⚠️ ...) des titres de phase, puis **collapser les espaces** doublés.
3bis. **Écarter les phases déjà possédées par un ticket de maintenance.** Une phase née d'une anomalie ou
   d'une évolution **nomme son ticket propriétaire dans son titre** :
   `^\s*(Évolution|Evolution|Anomalie)\s+(<identifiant>)\b` - ex.
   `## Phase 7: Évolution RAG-12 - Ingestion des pièces PNG`. Ce travail **est déjà suivi** par ce
   ticket ; lui créer un sous-ticket `Task` produirait un **doublon** (frère du ticket d'origine sous
   la même Feature, deux états à synchroniser, et "Linear est la seule source de vérité" tombe).
   **Deux conditions, jamais une seule** : le marqueur est présent **et** l'identifiant **résout** via
   `get_issue`. Si les deux tiennent -> **énoncer** en clair ("Phase 7 déjà suivie par RAG-12, rien à
   créer") et passer à la phase suivante : **ne jamais la proposer, ne jamais poser la question**. Si le
   marqueur est là mais que l'identifiant **ne résout pas** (marqueur erroné) -> **c'est le seul cas à
   remonter à l'humain** ; ne jamais créer en silence sur un marqueur douteux.
   *(Le mot littéral `Évolution`/`Anomalie` est **obligatoire** avant l'identifiant : un motif large
   `[A-Z]+-\d+` matcherait `FR-006`, `ADR-010`, `SC-001`, `TC-001` et ferait disparaître en silence les
   sous-tickets de phases de fabrication normales.)*
4. **Par phase manquante** (celles sans sous-ticket dans Linear **et** non écartées en 3bis, dans
   l'ordre), préparer :
   - un **titre** = **jeton stable `Phase N - `** + intitulé **descriptif** (voir Objectif) - enrichir
     les phases génériques à partir de leurs tâches ; reprendre l'intitulé des phases "User Story N" ;
     suffixer par le nom de la feature pour lever l'ambiguïté. Ex. `Phase 1 - Mise en place :
     scaffolding & outillage (Ingestion)`. Le jeton `Phase N -` est ce qui permet de ré-apparier sans
     manifeste ;
   - une **description d'une ligne** (le but de la phase, déduit de ses tâches) - **sans** énumérer
     les tâches `Txxx`.
5. **Confirmer** (recommandé + ajuster + saisir, cf. `references/interactive-loop.md`) : le **titre**
   et la **description d'une ligne** de chaque phase manquante. **Ne rien créer** tant que ce n'est pas
   approuvé. (Astuce : présenter d'un coup la liste des phases manquantes d'une feature pour validation
   groupée, puis créer.)
6. **Créer** (cf. `references/linear-guide.md`) :
   `save_issue({team, title: "Phase N - <intitulé descriptif>", parentId: "<issue_id UUID du ticket
   Feature>", labelIds: ["<UUID Task>"], description: "<résumé 1 ligne>", state: <Backlog>})`.
   **State = Backlog.** **Ne rien consigner dans le manifeste** : le sous-ticket **est** la trace, et il
   vit dans Linear. Passer à la phase suivante, puis à la feature suivante.

**Idempotence (via Linear).** Une phase dont le sous-ticket existe **déjà dans Linear** (jeton
`Phase N -` présent sous le bon `parentId`) n'est **pas recréée**. On ne s'appuie **pas** sur le
manifeste : l'avancement de fabrication n'y est jamais écrit (multi-développeurs, sans conflit).
**Une phase qui nomme son ticket propriétaire** (`Évolution <id> -`, `Anomalie <id> -`) n'est **ni
recréée ni proposée** : son travail est déjà suivi par ce ticket (cf. étape 3bis).

## Vérification avant de conclure
- Chaque feature avec un `tasks.md` a **un sous-ticket par phase dans Linear** (ou une phase
  explicitement écartée) ; chaque sous-ticket porte le label `Task`, le jeton `Phase N -`, et pointe
  (`parentId`) vers son ticket `Feature`. Vérifier via `list_issues({parentId})`.
- Lancer le garde-fou : `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_linear.py" <racine>/manifest.json`
  (il valide la **carte amont figée** - tickets `Feature` + `Task` par FR ; les sous-tickets **de phase
  vivent dans Linear** et ne sont **pas** exigés dans le manifeste).
- **Aucune écriture manifeste** par ce skill ; restitution **en prose** ("j'ai créé N sous-tickets de
  phase sous M features").

## Règles invariantes
- **Exception Linear bornée.** On n'écrit **que dans Linear** (externe) ; **jamais** dans le manifeste
  committé (l'avancement de fabrication n'y va pas - conflit multi-dev) ni dans le repo cible. `tasks.md`
  est **lu**, jamais modifié.
- **Titre descriptif + jeton.** Toujours `Phase N - <intitulé enrichi>` ; jamais le nom générique brut.
- **Confirmer avant de créer.** Chaque sous-ticket est validé par l'humain avant création.
- **Rattachement réel.** `parentId` = l'**UUID** (`issue_id`) du ticket `Feature`, jamais l'identifier
  (`ENG-123`).
- **Labels résolus, pas inventés.** `Feature`/`Task` sont résolus par nom ; jamais recréés.
- **Idempotent via Linear.** On liste les sous-tickets existants (`parentId`) avant de créer ; jamais
  deux fois la même phase.
- **Un travail, un ticket, un propriétaire.** Une phase qui **nomme son ticket propriétaire**
  (`Évolution <id> -`, `Anomalie <id> -`) est **déjà suivie** : on ne la recrée pas, et surtout **on ne
  la propose pas**. On l'énonce et on passe. La seule question légitime est un marqueur qui **ne résout
  pas** dans Linear.
- **Restitution en prose.** Aucun nom de clé à l'écran.

Étape suivante : reprendre la fabrication SpecKit de la feature (`/speckit.implement`), puis
`/assembleur:update-issue-linear` pour faire avancer l'état d'un ticket `Feature` ou d'un sous-ticket
`Task` quand une phase est terminée.
