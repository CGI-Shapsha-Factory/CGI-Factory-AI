# CLAUDE.md : plugin `assembleur`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`assembleur` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`assembleur` = **phase 4** de la Factory (convergence). Il **lit les 3 contrats**
(fonctionnel = cadrage, technique = architecte, design = designer), les **converge**, et
**produit un paquet de handoff** que l'équipe donne à SpecKit. **Il n'écrit jamais dans un
repo cible** : tout sort dans **`assembleur-out/`**. Pas de constitution dans `.specify/`,
pas de `specs/NNN/spec.md`, pas de GLOSSARY.md. Ce sont des **skills Markdown** ; pas de build/test.
**Quatre exceptions bornées** à "ne rien écrire hors du paquet" : `premier-alimente-linear` **et
`update-issue-linear`** créent et mettent à jour des tickets **Linear** (système externe, pas le repo
cible) ; `install-speckit` invoque `specify init` (c'est SpecKit qui génère `.specify/`) ;
`create-cowork-md` écrit **`init-cowork.md` à la racine** (document de contexte de supervision pour
le PO/Quark) ; et `assembleur-convergence` écrit **`CLAUDE.md` + `memory/` dans le `.claude/` du
projet** (déploiement, pour qu'ils soient actifs sans copie manuelle).

## Langue & invocation
- **Tout en français** (skills, templates, artefacts, interaction). Seuls les
  identifiants/valeurs machine et noms d'outils/formats (`spec.md`, `constitution.md`,
  SpecKit) restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/assembleur:<skill>` + auto par le modèle.

## Les 8 skills
- `assembleur-init` - setup (zéro décision) : installe les gabarits, crée `assembleur-out/`, étend le
  manifeste (bloc `assembly` allégé). **Jamais bloquant** : pose le terrain de convergence **toujours**,
  puis **signale** (sans refuser) si l'un des 3 dossiers de sortie amont (`cadrage-out/`,
  `architecte-out/`, `designer-out/`) est **absent, vide ou incomplet** - **sans** lire de statut de
  validation (validé ou non n'est pas le problème de l'assembleur). **Aucun repo cible à capturer, aucun
  hook à poser** (l'enforcement est posé en amont par `architecte-init`).
- `assembleur-convergence` - **lit les 3 contrats en parallèle** (5 sous-agents `contract-reader`,
  map-reduce), converge, **arbitre le registre de features** (autorité finale : découpe/fusionne,
  **réécrit `architecture.feature_sequence`**, figé ensuite à l'init Linear), **produit le paquet** dans `assembleur-out/` **+ déploie `CLAUDE.md` et
  `memory/` directement dans le `.claude/` du projet** (actifs sans copie manuelle), **résout les
  marqueurs en session**, et fait la cohérence (porte humaine : *garant de cohérence*).
- `premier-alimente-linear` - **première alimentation de Linear** (**point de gel** du registre de
  features : après, `architecture.feature_sequence` est immuable) : lit les features approuvées, les
  présente en tableau, puis crée **un ticket `Feature` par feature + un sous-ticket `Task` par
  Functional Requirement** (`parentId`), **tout en Backlog** (label **`Feature`** seul, résolu par nom -
  **jamais** `feature:<id>` ni un label de numérotation, l'identifiant Linear porte déjà le numéro ;
  `Task` pour les sous-tickets ; via le MCP **`linear-prism`**, confirmation ticket par ticket,
  `blockedBy` pour les dépendances), bloc manifeste `linear`. **Exception bornée** à "pas de Linear" (Linear est
  externe). Si le MCP `linear-prism` est **absent**, **ne rien créer** : refuser en clair et
  afficher les **instructions d'installation** (section "Installation du plugin linear-prism").
  Voir `references/linear-guide.md`.
- `creation-task-linear` - **sous-tickets par phase (2ᵉ niveau de Task)** : à lancer **après
  `/speckit.tasks`** (quand `specs/<feature>/tasks.md` existe). Pour chaque feature, parse les phases
  (`## Phase N:`) de son `tasks.md` et crée **un sous-ticket Linear par phase** (label **`Task`**, en
  **Backlog**, `parentId` = ticket `Feature`, **titre descriptif** généré - jamais le nom générique
  brut "Setup"), après confirmation. **Coexiste** avec les Task par FR posés en amont par
  `premier-alimente-linear`. Labels `Feature`/`Task` **résolus par nom** (`list_issue_labels`), jamais
  créés. **Idempotence via Linear** (`list_issues({parentId})`, jeton `Phase N -` en tête de titre) : les
  sous-tickets **par phase vivent uniquement dans Linear** - **aucune écriture dans le manifeste
  committé** (l'avancement de fabrication est concurrent, une branche par dev ; le fichier unique
  committé entrerait en conflit). Si le MCP `linear-prism` est **absent**, **ne rien créer** : refuser en
  clair et afficher les **instructions d'installation**. Voir `references/linear-guide.md`.
- `update-issue-linear` - **mise à jour Linear** : à partir du message de l'utilisateur ("j'ai
  terminé la tâche ..."), retrouve le ticket (par nom, ou **déduit des derniers changements de code**)
  et **met à jour son état** (terminé / en cours ; ou **coche une case** d'une grosse feature), après
  confirmation, via le MCP **`linear-prism`**. **Non gaté**, invoqué à la demande pendant la
  fabrication ; **l'état vit dans Linear** - **aucune écriture manifeste**. Voir `references/linear-guide.md`.
- `create-cowork-md` - **contexte de supervision (Quark)** : détecte le **dépôt GitHub**
  (`git remote get-url origin`, repli `gh repo view`) et le **projet Linear** (MCP `linear-prism`
  + bloc `linear`), rassemble le contexte des **3 contrats**, et génère **`init-cowork.md` à la
  racine** - le document unique que le PO donne à Quark. **Ne contient rien d'aval** (pas de
  workflow SpecKit / fabrication / avancement : ils n'existent pas encore) ; seuls les **liens**
  GitHub/Linear renvoient à l'état vivant. **3ᵉ exception bornée** à "paquet seul" (écrit à la
  racine - fichier de supervision, pas un artefact SpecKit). Bloc manifeste `cowork`. Non gaté,
  à la demande (idéalement après `premier-alimente-linear`). Voir `references/linear-guide.md`.
- `install-speckit` - **pont vers SpecKit** : pose SpecKit dans le repo cible via
  `scripts/install_speckit.py` (auto-install `uv` sans admin, introspection des flags de `specify
  init`, `specify init` non-interactif, test de fumée, **pose le registre de hooks
  `.specify/extensions.yml`** depuis `references/speckit-extensions.yml` - config d'équipe **non
  générée par `specify init`** qui branche les automations Linear de la Factory en **hooks optionnels**
  (`after_tasks`->`creation-task-linear`, `after_implement`->`update-issue-linear`) -, **pose le hook
  `PostToolUse` `tasks_linear_hook.py`** (`references/linear-sync/`) dans `.claude/` du repo cible : il
  détecte toute édition d'un `specs/<feature>/tasks.md` et **pousse l'agent** (`decision:block`) à lancer
  `creation-task-linear` s'il manque un sous-ticket `Task` pour une phase - **le hook ne parle jamais à
  Linear** (MCP côté skill) -, bloc manifeste `speckit`). **Exceptions bornées** à "n'écrit jamais dans le repo cible" : `specify init` génère
  `.specify/` (jamais ce skill à la main) ; le registre `extensions.yml` et le bloc manifeste sont de la
  config Factory.
- `revue-gemini` - **revue de code indépendante (API Gemini) avant PR/merge** : contre l'**exces de
  confiance de Claude** par un relecteur **externe non biaisé**. Calcule le **diff de branche**
  (`git diff <base>...HEAD`, temporaire git-ignoré), **fan-out 6 sous-agents `gemini-reviewer` en
  parallèle** (un par dimension : `security`, `correctness`, `performance`, `architecture`, `quality`,
  `testing` - chacun lance `scripts/gemini_review.py` sur sa dimension), puis **agrège** (dedup, conflits
  conservés, classement par sévérité) et **restitue un tableau en session** (aucun fichier de sortie).
  **Consultatif** (l'humain tranche) ; **jamais bloquant** sur cle/quota/reseau. **Exception bornée** à
  "pas d'API externe" (Gemini est externe) ; la cle vit dans `.env` (git-ignoré, convention architecte).
  Agent : `agents/gemini-reviewer.md`. La **revue est faite par Gemini, jamais par Claude**.

## Le paquet `assembleur-out/` + déploiement `.claude/`
```
assembleur-out/
├── pre-constitution.md        # principes non négociables, format constitution.md (-> /speckit.constitution)
├── features/NNN-....md          # une graine par feature, format spec.md (-> /speckit.specify)
├── feature-map.md             # séquence + couplage/dépendances + walking skeleton
├── technical-context.md       # Technical Context (-> /speckit.plan)
├── coherence-report.md
└── attack-plan.md

.claude/                       # ÉCRIT DIRECTEMENT dans le projet (actif sans copie manuelle)
├── CLAUDE.md                  # CLAUDE.md projet (< 200 lignes, @import memory/MEMORY.md - jamais backtiqué)
└── memory/{MEMORY,domain,architecture,design,features}.md
```
Les **gabarits** vivent dans `.factory/assembleur/` (git-ignoré) ; le **manifeste** est **committé** dans `manifest.json`. Écriture = read-modify-write + revalidation JSON.

**Déploiement mémoire (important).** `CLAUDE.md` **et** le dossier `memory/` ne sont **pas** posés dans
`assembleur-out/` : `assembleur-convergence` les écrit **directement dans le `.claude/` du projet**
(racine du dossier courant), pour qu'ils soient **actifs dès la session suivante** sans copie manuelle.
C'est la **seule exception** au "paquet seul" (en plus de Linear / `specify init` / `init-cowork.md`).
Le `CLAUDE.md` **importe l'index** via une ligne `@memory/MEMORY.md` **jamais entre backticks** (un
`@import` backtiqué = texte littéral, non importé) ; `CLAUDE.md` et `memory/` sont **co-localisés dans
`.claude/`**, donc l'`@import` et les liens de `MEMORY.md` résolvent en relatif. `MEMORY.md` ne **lie en
dur** que ses **voisins de `memory/`** (qui voyagent avec lui) ; les fichiers du paquet `assembleur-out/`
y sont cités **en texte simple** (pas de lien `../` cassable). **Ce n'est PAS l'auto-mémoire native** de
Claude Code (`~/.claude/projects/<projet>/memory/`, machine-locale et non commitée) : ici la mémoire est
**commitée et partagée** avec l'équipe, chargée par l'`@import`.

## Lecture parallèle (map-reduce)
`assembleur-convergence` est l'orchestrateur ; il dispatche **5 lecteurs** (`agents/contract-reader.md`)
en parallèle (fonctionnel, domaine, technique, décisions, design), chacun avec un schéma de sortie,
puis synthétise. Cadrage : 3-5 sous-agents, objectif/format/limites clairs (Explore ne lit que des
extraits -> on utilise un agent dédié à lecture complète).

## Convergence (mapping 3 faces -> SpecKit)
Voir `references/speckit-mapping.md`. **Clé de jointure = le use case** (registre
`architecture.feature_sequence` = objets `{id, ucs, name}` - **proposé par l'architecte, finalisé
(split/merge) et figé à l'init Linear par l'assembleur**). Fonctionnel + technique joints **par use
case** ; design **global** (export committé du design system + guidelines). La pré-constitution
converge les **principes non négociables** des 3 contrats (dont la règle design : tout écran
dérive de l'export committé du design system, aucune valeur de style en dur, états couverts, contrat d'erreur ;
et le **principe de test** : tests écrits avec le code, intégration mockée).

## Conventions partagées
`references/interactive-loop.md`, `references/ux-conventions.md`, `references/speckit-mapping.md`,
`references/fabrication-parallele.md` (règles multi-développeurs consolidées - numérotation, Linear,
couplage, merge, constitution ; **couche autour de SpecKit, jamais de réécriture**),
`references/linear-guide.md` (usage du MCP linear-prism : détection, installation, `save_issue`
création **et mise à jour d'état**, `list_issue_statuses`, `blockedBy`, refus + instructions
d'installation si le MCP est absent).
Garde-fous déterministes : `scripts/check_assembly.py` (présence du paquet + aucun marqueur résiduel +
couverture des features), `scripts/check_linear.py` (une feature = un ticket ou une décision
explicite, tickets créés porteurs d'identifiant) et `scripts/check_cowork.py` (bloc `cowork` +
`init-cowork.md` à la racine exposant une section GitHub et une section Linear). Gabarit :
`templates/init-cowork.md`. Installeur : `scripts/install_speckit.py` (pose
SpecKit dans le repo, best-effort, timeouts, PATH rafraîchi en cours de processus, flags version-proof
par introspection). Agent : `agents/contract-reader.md`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python scripts/check_assembly.py <projet>/manifest.json
```

## Invariants
**Paquet seul** (n'écrit que dans `assembleur-out/`, jamais un fichier que SpecKit génère - **quatre
exceptions bornées : `premier-alimente-linear` et `update-issue-linear`, qui créent et mettent à jour des
tickets Linear (système externe, jamais le repo cible) ; `install-speckit`, qui invoque `specify
init` pour que SpecKit génère lui-même `.specify/`, sans jamais le rédiger à la main ;
`create-cowork-md`, qui écrit `init-cowork.md` à la racine (contexte de supervision PO/Quark, pas un
artefact SpecKit) ; et `assembleur-convergence`, qui écrit `CLAUDE.md` + `memory/` dans le `.claude/`
du projet (déploiement, actif sans copie manuelle)**) ; proposer/pas décider (cohérence validée par l'humain) ; **rien laissé indéfini** (tout marqueur
résolu en session, en place) ; **contenu seul** (aucune `(src:)`, horodatage, nom de personne) ;
restitutions en prose, manifeste mis à jour en silence ; **typographie humaine** : aucun glyphe de style IA dans les artefacts/prompts (pas de tiret cadratin, de points de suspension unicode, de flèches unicode, de guillemets à chevrons, ni de coche/croix ; équivalents clavier, cf. la section Typographie de `references/ux-conventions.md`).
