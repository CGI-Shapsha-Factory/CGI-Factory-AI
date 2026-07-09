---
name: creation-task-linear
description: Après /speckit.tasks, crée un sous-ticket Linear par phase de specs/<feature>/tasks.md (label Task, titre descriptif, rattaché au ticket Feature de la feature) via le MCP linear-prism, avec confirmation phase par phase.
---

# creation-task-linear

**Deuxième alimentation de Linear (niveau tâches).** À lancer **pendant la fabrication**, **après
`/speckit.tasks`** — c'est-à-dire une fois que SpecKit a produit `specs/<feature>/tasks.md`. Ce skill
lit les **phases** de chaque `tasks.md` et crée, dans Linear, **un sous-ticket par phase** (label
`Task`) **rattaché** (`parentId`) au ticket `Feature` déjà créé par `premier-alimente-linear`.

## Objectif
Pour chaque feature dont le `tasks.md` existe : parcourir ses **phases** (`## Phase N: …`) et créer
**un sous-ticket Linear par phase** avec :
- un **titre spécifique et descriptif** — **jamais** le nom générique brut de la phase (« Setup »,
  « Foundational », « Polish », « Backend ») : enrichir en lisant les tâches de la phase (ex.
  `Setup` → « Mise en place : scaffolding, outillage & dépendances (Ingestion) ») ; pour une phase
  « User Story N », reprendre l'intitulé de la story (déjà descriptif), nettoyé des emoji ;
- le label **`Task`** ;
- le **`parentId`** = le ticket `Feature` de la feature ;
- une **description d'une ligne** (résumé du but de la phase) — **pas de liste de tâches** dans le corps.

Chaque sous-ticket est **confirmé avant création**. Idempotent : une phase déjà consignée avec un
`issue_id` n'est **pas recréée**.

## Frontière (exception assumée)
Comme `premier-alimente-linear` : créer des tickets Linear est une **exception explicitement bornée**
à « pas de Linear ». Linear est un **système externe** (pas le repo cible, pas un fichier que SpecKit
génère). La seule écriture propre à la Factory est le bloc `linear` du manifeste. On **lit**
`specs/<feature>/tasks.md` (fichier généré par SpecKit) **sans jamais le modifier**.

## Pré-requis (vérification silencieuse)
Lire `manifest.json` **sans l'annoncer** :
- `premier-alimente-linear` a tourné : `linear.issues[]` contient des tickets `Feature` avec un
  `issue_id` (l'UUID interne, nécessaire comme `parentId`) ;
- au moins un `specs/<feature>/tasks.md` existe dans le repo de fabrication ;
- sinon → le dire en clair et orienter :
  > « Les sous-tickets de phase ne peuvent pas être créés : il faut d'abord les tickets par feature
  > (`/assembleur:premier-alimente-linear`) **et** avoir lancé `/speckit.tasks` (le `tasks.md` de la
  > feature). »

**Ne rien inventer** : on ne crée un sous-ticket que pour une phase réellement présente dans un
`tasks.md`.

## Étape 1 — Détecter Linear (MCP linear-prism)
Sonder `mcp__plugin_linear-prism_linear__list_teams` (cf. `references/linear-guide.md`).
- Disponible → continuer.
- Indisponible → **ne rien créer** : refuser en clair (« Je ne peux pas créer de sous-tickets
  Linear : le MCP `linear-prism` n'est pas disponible. ») et afficher les **instructions
  d'installation** (section « Installation du plugin linear-prism » de `references/linear-guide.md`).
  Installer puis **relancer** une fois authentifié.

## Étape 2 — Résoudre les labels et l'équipe (une seule fois)
- **Équipe** : réutiliser `linear.team` du manifeste (posé par `premier-alimente-linear`). Ne pas
  redemander.
- **Labels `Feature` / `Task`** : les **résoudre par nom** via
  `mcp__plugin_linear-prism_linear__list_issue_labels` (comparaison **insensible à la casse** — les
  labels s'appellent `Feature` / `Task`). Retenir leurs **UUID** pour la session. **Ne pas les créer**
  (ils préexistent dans l'espace de travail). Si l'un manque → le dire en clair et proposer soit de le
  créer (`create_issue_label`, best-effort), soit de l'omettre. Détails :
  `references/linear-guide.md`.

## Étape 3 — Rattraper le label `Feature` sur les tickets de feature (additif)
Pour chaque ticket de feature (`linear.issues[]` avec `issue_id`), s'assurer qu'il porte le label
`Feature` **sans perdre ses labels existants** : lire ses labels via `get_issue({id})`, puis
`save_issue({id, labelIds: <union des labelIds existants + Feature>})`. **Additif** : ne jamais
retirer `feature:<id>` ni `walking-skeleton`. Idempotent : si `Feature` est déjà présent, ne rien
écrire.

## Étape 4 — Boucle par feature puis par phase (confirmation obligatoire)
Pour **chaque** feature qui a un `specs/<feature>/tasks.md` :

1. **Rattacher** : retrouver le ticket `Feature` de la feature dans `linear.issues[]` — jointure par
   `id` (`001…`) et par nom de dossier/branche `NNN-feature`. Récupérer son **`issue_id` (UUID)** =
   le futur `parentId`. Si aucun ticket `Feature` ne correspond → le signaler et passer (ne pas créer
   d'orphelin).
2. **Parser `tasks.md`** (lecture seule) :
   - phases : lignes `^## Phase (\d+): (.+)$` (le titre suit le numéro) ;
   - tâches d'une phase : lignes `^- \[[ xX]\] (T\d{3})(?: \[P\])?(?: \[US\d+\])? (.+)$`, groupées
     sous la phase courante (les IDs `T001…` sont **séquentiels sur tout le fichier**) ;
   - **retirer les emoji** (🎯 ⚠️ …) des titres de phase, puis **collapser les espaces** doublés.
3. **Par phase** (dans l'ordre), préparer :
   - un **titre descriptif** (voir Objectif) — enrichir les phases génériques à partir de leurs
     tâches ; reprendre l'intitulé des phases « User Story N » ; suffixer par le nom de la feature
     pour lever l'ambiguïté ;
   - une **description d'une ligne** (le but de la phase, déduit de ses tâches) — **sans** énumérer
     les tâches `Txxx`.
4. **Confirmer** (recommandé + ajuster + saisir, cf. `references/interactive-loop.md`) : le **titre**
   et la **description d'une ligne** de chaque phase. **Ne rien créer** tant que ce n'est pas approuvé.
   (Astuce : présenter d'un coup la liste des phases d'une feature pour validation groupée, puis
   créer.)
5. **Créer** (cf. `references/linear-guide.md`) :
   `save_issue({team, title, parentId: "<issue_id UUID du ticket Feature>", labelIds: ["<UUID Task>"],
   description: "<résumé 1 ligne>", state: <Todo/unstarted si résolu>})` → récupérer `issue_id` /
   `identifier` / `url`.
6. **Consigner** dans `linear.issues[].sub_issues[]` (en silence) : `{phase, phase_name, title,
   issue_id, identifier, url, status: "created"}`, puis phase suivante. **Répéter** jusqu'à épuisement
   des phases, puis feature suivante.

**Idempotence** : une phase déjà consignée (même `id` de feature + même numéro de phase) avec un
`issue_id` n'est **pas recréée**.

## Vérification avant de conclure
- Chaque feature avec un `tasks.md` a **un sous-ticket par phase** (ou une décision `skipped`) ;
  chaque sous-ticket porte le label `Task` et pointe (`parentId`) vers son ticket `Feature`.
- Lancer le garde-fou : `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_linear.py" <racine>/manifest.json`.
- Le bloc `linear` du manifeste **reparse sans erreur** ; restitution **en prose** (« j'ai créé N
  sous-tickets de phase sous M features »), manifeste mis à jour **en silence**.

## Règles invariantes
- **Exception Linear bornée.** On n'écrit que dans Linear (externe) + le bloc `linear` du manifeste ;
  jamais dans le repo cible. `tasks.md` est **lu**, jamais modifié.
- **Titre descriptif obligatoire.** Jamais le nom générique brut d'une phase ; toujours enrichi.
- **Confirmer avant de créer.** Chaque sous-ticket est validé par l'humain avant création.
- **Rattachement réel.** `parentId` = l'**UUID** (`issue_id`) du ticket `Feature`, jamais l'identifier
  (`ENG-123`).
- **Labels résolus, pas inventés.** `Feature`/`Task` sont résolus par nom ; jamais recréés.
- **Idempotent.** On ne crée jamais deux fois le même sous-ticket.
- **Manifeste en silence.** Aucun nom de clé à l'écran ; restitution en prose.

Étape suivante : reprendre la fabrication SpecKit de la feature (`/speckit.implement`), puis
`/assembleur:update-issue-linear` pour faire avancer l'état d'un ticket `Feature` ou d'un sous-ticket
`Task` quand une phase est terminée.
