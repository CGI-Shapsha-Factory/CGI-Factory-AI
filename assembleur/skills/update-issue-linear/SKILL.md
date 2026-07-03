---
name: update-issue-linear
description: Met à jour l'état d'un ticket Linear quand l'utilisateur signale qu'une tâche est terminée (ou avancée) — retrouve le ticket par son nom, ou le déduit des derniers changements de code, puis change son état (ou coche une case), via le MCP linear-prism.
---

# update-issue-linear

**Pont vers Linear (mise à jour).** À lancer **à la demande**, pendant la fabrication (après
`install-speckit`, quand l'équipe fabrique feature par feature) : **chaque fois qu'une tâche avance
ou est terminée**. Ce skill lit le **message de l'utilisateur comme indice** (« j'ai terminé la
recherche Q&A sourcée », « j'ai fini FR-004 », « j'ai commencé 002 »…), retrouve le **ticket Linear
concerné**, et **met à jour son état** — après confirmation. **Non gaté** : ce n'est pas une étape de
la chaîne, on l'invoque quand on veut.

## Objectif
À partir de l'indice, **passer un ticket Linear dans le bon état** (terminé par défaut, sinon en
cours / bloqué) — ou, si l'indice vise une **sous-partie** d'une grosse feature, **cocher la case**
correspondante dans la description. Le ticket est **toujours confirmé avant d'écrire**. Idempotent :
si le ticket est déjà dans l'état visé, on ne réécrit rien.

## Frontière (exception assumée)
L'assembleur **n'écrit jamais dans le repo cible** : tout sort dans `assembleur-out/`. Mettre à jour
un ticket Linear est la **même exception bornée** que `premier-alimente-linear` : Linear est un **système
externe** (pas le repo cible, pas un fichier que SpecKit génère). La seule écriture propre à la
Factory est le bloc `linear` du manifeste. Le dialogue passe par le **MCP du plugin `linear-prism`**
(externe à la Factory) — voir `references/linear-guide.md`.

## Pré-requis (vérification silencieuse)
Lire `.factory/manifest.json` **sans l'annoncer** : le bloc `linear` liste les tickets déjà créés
(`issues[]` : `identifier`, `id` de feature, `name`, `url`).
- **Des tickets existent** → s'en servir comme index (résolution rapide et précise).
- **Aucun ticket / pas de bloc `linear`** → **ne pas bloquer** : on peut chercher directement dans
  Linear ; mais si l'équipe n'a jamais créé de tickets, l'orienter en clair vers
  `/assembleur:premier-alimente-linear` (« il n'y a pas encore de tickets à mettre à jour »).

## Étape 1 — Détecter Linear (MCP linear-prism)
Sonder `mcp__plugin_linear-prism_linear__list_teams` (cf. `references/linear-guide.md`).
- **Disponible** → continuer.
- **Indisponible** → **ne pas bloquer** : afficher les **instructions d'installation** (section
  « Installation du plugin linear-prism » de `references/linear-guide.md` : ajout de la marketplace,
  `/plugin install`, redémarrage, `/mcp` pour l'authentification OAuth). Expliquer en clair qu'une
  **mise à jour a besoin du MCP** (contrairement à la création, il n'y a pas de mode brouillon utile
  ici) : installer puis **relancer** la même phrase.

## Étape 2 — Lire l'indice (le message de l'utilisateur)
Le **message qui déclenche le skill** (et, le cas échéant, les arguments passés à
`/assembleur:update-issue-linear`) est l'**indice**. En extraire deux choses :
- **La tâche visée** : un nom en clair (« recherche Q&A sourcée »), un identifiant (`LIN-123`), un
  `id` de feature (`001`), un `FR-xxx`, ou **rien** (« j'ai terminé la tâche »).
- **L'action voulue** : **terminé** (« fini / terminé / done / bouclé »), **en cours** (« commencé /
  en cours / je bosse dessus »), **bloqué** (« bloqué / en attente »), ou une **sous-partie** d'une
  grosse feature (un `FR-xxx` / un item de la liste de contrôle) → **cocher une case**. En l'absence
  de verbe clair, supposer **terminé** (usage principal), mais **confirmer**.

## Étape 3 — Identifier le ticket
- **Tâche nommée** → chercher d'abord dans `linear.issues[]` (par `identifier`, `id` de feature, ou
  mot-clé du `name`) ; **et aussi dans les sous-tickets** `linear.issues[].sub_issues[]` (par
  `identifier`, `phase`/`phase_name`, ou mot-clé du `title`) quand l'indice vise une **phase**
  (« phase 2 », « la partie tests », un titre de phase) ; sinon interroger Linear :
  `list_issues({query: "<mots-clés>", team})` (la recherche porte sur titre + description).
- **Tâche non nommée** → **déduire des derniers changements de code** (le repo cible est souvent un
  dépôt git), best-effort :
  - **branche courante** `git rev-parse --abbrev-ref HEAD` — les branches Linear encodent souvent
    l'`identifier` (ex. `lin-123-…`) : signal fort ;
  - `git log -1 --format=%s%n%b` (dernier commit), `git diff --name-only` et `git status --porcelain`
    (fichiers récemment touchés) → en extraire des mots-clés ;
  - croiser ces mots-clés avec `linear.issues[]` (et au besoin `list_issues`) → **candidats**.
  - Pas de git ou rien de sûr → **proposer une courte liste** (tickets ouverts : `list_issues`
    `assignee: "me"`, états `unstarted`/`started`) et **demander** lequel (un point à la fois).
- `get_issue({id})` pour lire l'**état courant** et la **description** (nécessaire pour les cases).
- **Confirmer le ticket** — nom + intitulé — **avant toute écriture** (recommandé + « ce n'est pas
  celui-là » + « saisir »). **Ne jamais écrire sur une simple déduction.**

## Étape 4 — Déterminer la mise à jour (depuis l'indice)
- **Terminé** → résoudre l'état cible via `list_issue_statuses({team})` : viser l'état de **type
  `completed`** (« Done » / « Terminé » selon l'équipe). En cours → type `started` ; bloqué → l'état
  ou le label que l'équipe utilise pour « bloqué » s'il existe (best-effort ; sinon le dire en clair).
- **Sous-partie** (un `FR-xxx` / item de checklist) → dans la `description` du ticket, passer la ligne
  `- [ ] …` correspondante à `- [x] …`. Si **toutes** les cases deviennent cochées, **proposer** de
  passer aussi le ticket à terminé.
- **Idempotence** : si `get_issue` montre que le ticket est **déjà** dans l'état visé (ou la case déjà
  cochée), **le dire en clair et ne rien écrire**.

## Étape 5 — Confirmer puis appliquer
1. **Confirmer l'action** en clair (recommandé + ajuster + saisir) : « passer *&lt;ticket&gt;* à
   *terminé* » ou « cocher *&lt;item&gt;* dans *&lt;ticket&gt;* ». **Ne rien écrire** tant que ce n'est pas
   approuvé ; « ajuster » / « saisir » corrige en place.
2. **Appliquer** (cf. `references/linear-guide.md`) :
   - état : `save_issue({id, state: "<nom ou type de l'état résolu>"})` ;
   - case : `save_issue({id, description: "<description avec la case cochée>"})`.
   - **Pas de commentaire** (on ne change que l'état / la case).
3. **Consigner en silence** dans `linear.issues[]` le dernier état posé (champ `workflow_state`,
   distinct du `status` d'action Factory), puis restituer en prose.

## Vérification avant de conclure
- `get_issue` reflète le **nouvel état** (ou la case cochée) ; le ticket **existe** et l'écriture a
  réussi.
- Le bloc `linear` du manifeste **reparse sans erreur** ; mise à jour **en silence**.
- Restitution **en prose** (« j'ai passé *Recherche Q&A sourcée* à *Terminé* »), **une** phrase de suite.

## Règles invariantes
- **Exception Linear bornée.** On n'écrit que dans Linear (externe) + le bloc `linear` du manifeste ;
  jamais dans le repo cible.
- **Confirmer avant d'écrire.** Toute mise à jour est validée par l'humain (action externe, difficile
  à défaire) ; on ne se fie **jamais** à une déduction seule.
- **Un point à la fois.** Questions et confirmations en prose, une par une (cf. `interactive-loop.md`) ;
  pas de tableau.
- **Idempotent.** `get_issue` **avant** d'écrire ; si l'état est déjà bon, ne rien faire.
- **Rien d'inventé.** On ne met à jour qu'un ticket **confirmé** ; jamais un état non demandé.
- **Manifeste en silence.** Aucun nom de clé ni statut brut à l'écran ; restitution en prose.

Étape suivante : reprendre la fabrication de la feature suivante (le cycle SpecKit `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`), et relancer ce skill dès qu'une tâche avance.
