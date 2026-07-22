---
name: update-issue-linear
description: Met à jour l'état d'un ticket Linear quand l'utilisateur signale qu'une tâche est terminée (ou avancée) - retrouve le ticket (feature ou sous-ticket) par son nom, ou le déduit des derniers changements de code, puis change son état, via le MCP linear-prism.
---

# update-issue-linear

**Pont vers Linear (mise à jour).** À lancer **à la demande**, pendant la fabrication (après
`install-speckit`, quand l'équipe fabrique feature par feature) : **chaque fois qu'une tâche avance
ou est terminée**. Ce skill lit le **message de l'utilisateur comme indice** ("j'ai terminé la
recherche Q&A sourcée", "j'ai fini FR-004", "j'ai commencé 002"...), retrouve le **ticket Linear
concerné**, et **met à jour son état** - après confirmation. **Non gaté** : ce n'est pas une étape de
la chaîne, on l'invoque quand on veut.

## Objectif
À partir de l'indice, **passer un ticket Linear dans le bon état** (terminé par défaut, sinon en
cours / bloqué). Si l'indice vise une **sous-partie** d'une feature (un `FR-xxx`, une phase), la cible
est le **sous-ticket** correspondant, pas le parent : **il n'existe aucune case à cocher** dans les
descriptions - chaque chose à faire est un **vrai sous-ticket** (`Task` par FR posé par
`premier-alimente-linear`, `Task` par phase posé par `creation-tasks-linear`). Le ticket est
**toujours confirmé avant d'écrire**. Idempotent : si le ticket est déjà dans l'état visé, on ne
réécrit rien.

## Frontière (exception assumée)
L'assembleur **n'écrit jamais dans le repo cible** : tout sort dans `assembleur-out/`. Mettre à jour
un ticket Linear est la **même exception bornée** que `premier-alimente-linear` : Linear est un **système
externe** (pas le repo cible, pas un fichier que SpecKit génère). **L'état d'avancement vit dans Linear**
- ce skill **n'écrit rien dans le manifeste committé** (deux développeurs mettant à jour en parallèle
réécriraient le même registre committé -> conflit de merge). Le dialogue passe par le **MCP du plugin
`linear-prism`** (externe à la Factory) - voir `references/linear-guide.md`.

## Pré-requis (vérification silencieuse)
Lire `manifest.json` **sans l'annoncer** : le bloc `linear` fournit la configuration (`team`,
`project`). **Les tickets vivent dans Linear** (aucune carte dans le manifeste) : toute résolution
passe par `list_issues` / `get_issue`.
- **Pas de bloc `linear`** -> **ne pas bloquer** : on peut chercher directement dans Linear
  (`list_teams` puis `list_issues`) ; mais si l'équipe n'a jamais créé de tickets, l'orienter en
  clair vers `/assembleur:premier-alimente-linear` ("il n'y a pas encore de tickets à mettre à jour").

## Étape 1 : Détecter Linear (MCP linear-prism)
Sonder `mcp__plugin_linear-prism_linear__list_teams` (cf. `references/linear-guide.md`).
- **Disponible** -> continuer.
- **Indisponible** -> **ne rien mettre à jour** : refuser en clair ("Je ne peux pas mettre à jour
  de ticket Linear : le MCP `linear-prism` n'est pas disponible.") et afficher les **instructions
  d'installation** (section "Installation du plugin linear-prism" de `references/linear-guide.md` :
  ajout de la marketplace, `/plugin install`, redémarrage, `/mcp` pour l'authentification OAuth).
  Installer puis **relancer** la même phrase.

## Étape 2 : Lire l'indice (le message de l'utilisateur)
Le **message qui déclenche le skill** (et, le cas échéant, les arguments passés à
`/assembleur:update-issue-linear`) est l'**indice**. En extraire deux choses :
- **La tâche visée** : un nom en clair ("recherche Q&A sourcée"), un identifiant (`LIN-123`), un
  `id` de feature (`001`), un `FR-xxx`, ou **rien** ("j'ai terminé la tâche").
- **L'action voulue** : **terminé** ("fini / terminé / done / bouclé"), **en cours** ("commencé /
  en cours / je bosse dessus"), **bloqué** ("bloqué / en attente"). En l'absence de verbe clair,
  supposer **terminé** (usage principal), mais **confirmer**.
- **Le niveau visé** : la **feature entière**, ou une **sous-partie** (un `FR-xxx`, une phase) - qui
  est alors un **sous-ticket** à part entière, cible directe de la mise à jour.

## Étape 3 : Identifier le ticket
- **Tâche nommée** -> chercher **dans Linear** : `get_issue({id})` si un `identifier` (`LIN-123`) est
  donné, sinon `list_issues({query: "<mots-clés>", team})` (titre + description ; les tickets Feature
  portent l'id `001...` en tête de titre). Quand l'indice vise une **phase** ("phase 2",
  "la partie tests", un titre de phase), les sous-tickets de phase **vivent dans Linear** (pas dans le
  manifeste) : les retrouver via `list_issues({parentId: "<identifier de la Feature>"})` (jeton
  `Phase N -` en tête de titre) ou `list_issues({query: "<mots-clés>", team})` (titre + description).
- **Tâche non nommée** -> **déduire des derniers changements de code** (le repo cible est souvent un
  dépôt git), best-effort :
  - **branche courante** `git rev-parse --abbrev-ref HEAD` - les branches Linear encodent souvent
    l'`identifier` (ex. `lin-123-...`) : signal fort ;
  - `git log -1 --format=%s%n%b` (dernier commit), `git diff --name-only` et `git status --porcelain`
    (fichiers récemment touchés) -> en extraire des mots-clés ;
  - croiser ces mots-clés avec `list_issues({query, team})` -> **candidats**.
  - Pas de git ou rien de sûr -> **demander avec `AskUserQuestion`** lequel : deux tickets ouverts
    (`list_issues` `assignee: "me"`, états `unstarted`/`started`), le plus probable en premier, la
    saisie libre pour un autre.
- `get_issue({id})` pour lire l'**état courant** du ticket visé.
- **Confirmer le ticket avec `AskUserQuestion`** - nom + intitulé - **avant toute écriture** :
  deux options, le ticket déduit (recommandé) et "ce n'est pas celui-là", la saisie libre pour en
  désigner un autre. **Ne jamais écrire sur une simple déduction.**

## Étape 4 : Déterminer la mise à jour (depuis l'indice)
- **Terminé** -> résoudre l'état cible via `list_issue_statuses({team})` : repérer l'état de **type
  `completed`** et **retenir son `name`** ("Done" / "Terminé" selon l'équipe) - c'est ce **nom** qui
  est passé à `save_issue`, jamais le type. En cours -> l'état de type `started` (même règle) ;
  bloqué -> l'état ou le label que l'équipe utilise pour "bloqué" s'il existe (best-effort ; sinon
  le dire en clair).
- **Sous-partie** (un `FR-xxx`, une phase) -> la cible est le **sous-ticket**, pas le parent : le
  retrouver via `list_issues({parentId: "<identifier de la Feature>"})` (jeton `FR-00x -` ou
  `Phase N -` en tête de titre) et lui appliquer le changement d'état ci-dessus. **Ne jamais éditer
  la `description` du parent** pour signifier un avancement : les descriptions ne portent **aucune
  case à cocher** (chaque chose à faire est un vrai sous-ticket). Si, après cette mise à jour,
  **tous** les sous-tickets de la Feature sont terminés, **demander avec `AskUserQuestion`** s'il
  faut passer aussi la Feature à terminé ("passer la feature à terminé" en recommandé / "laisser le
  statut tel quel").
- **Idempotence** : si `get_issue` montre que le ticket visé est **déjà** dans l'état voulu, **le
  dire en clair et ne rien écrire**.

## Étape 5 : Confirmer puis appliquer
1. **Confirmer l'action avec `AskUserQuestion`** : "passer *&lt;ticket&gt;* à *terminé*" - deux
   options, l'action proposée (recommandé) et "ne rien changer" ; le refus reste cliquable. **Ne
   rien écrire** tant que ce n'est pas approuvé ; la saisie libre corrige en place.
2. **Appliquer** (cf. `references/linear-guide.md`) : `save_issue({id, state: "<nom de l'état
   résolu>"})` - le **nom**, jamais le type : le MCP résout l'état **par nom seulement** et **échoue
   en silence** sur une valeur inconnue. **Pas de commentaire** (on ne change que l'état).
3. **Ne rien écrire dans le manifeste** : l'état courant vit **dans Linear** (`get_issue` fait foi).
   Restituer en prose.

## Vérification avant de conclure
- `get_issue` reflète le **nouvel état** ; le ticket **existe** et l'écriture a réussi. Si l'état
  n'a **pas** changé, l'écriture a échoué en silence (état résolu par type au lieu du nom) : le dire
  en clair, ne jamais annoncer une mise à jour non constatée.
- **Aucune écriture manifeste** : l'état d'avancement vit dans Linear (pas de conflit multi-dev).
- Restitution **en prose** ("j'ai passé *Recherche Q&A sourcée* à *Terminé*"), **une** phrase de suite.

## Règles invariantes
- **Exception Linear bornée.** On n'écrit **que dans Linear** (externe) ; **jamais** dans le manifeste
  committé (conflit multi-dev) ni dans le repo cible.
- **Confirmer avant d'écrire.** Toute mise à jour est validée par l'humain (action externe, difficile
  à défaire) ; on ne se fie **jamais** à une déduction seule.
- **Un point à la fois.** Questions et confirmations **avec `AskUserQuestion`**, un appel chacune (cf. `interactive-loop.md`) ;
  pas de tableau.
- **Idempotent.** `get_issue` **avant** d'écrire ; si l'état est déjà bon, ne rien faire.
- **Rien d'inventé.** On ne met à jour qu'un ticket **confirmé** ; jamais un état non demandé.
- **Rien dans le manifeste.** L'état vit dans Linear ; restitution en prose (aucun statut brut à l'écran).

Étape suivante : reprendre la fabrication de la feature suivante (le cycle SpecKit `/speckit.specify` -> `/speckit.plan` -> `/speckit.tasks` -> `/speckit.implement`), et relancer ce skill dès qu'une tâche avance.
