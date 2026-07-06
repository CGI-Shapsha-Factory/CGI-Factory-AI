# CLAUDE.md — plugin `assembleur`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`assembleur` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`assembleur` = **phase 4** de la Factory (convergence). Il **lit les 3 contrats**
(fonctionnel = cadrage, technique = architecte, design = designer), les **converge**, et
**produit un paquet de handoff** que l'équipe donne à SpecKit. **Il n'écrit jamais dans un
repo cible** : tout sort dans **`assembleur-out/`**. Pas de constitution dans `.specify/`,
pas de `specs/NNN/spec.md`, pas de GLOSSARY.md ; le seul CI produit est un
**garde-fou de test** (`ci/tests.yml`) livré **dans le paquet** (jamais posé dans le repo cible — c'est
l'équipe qui le pose en *required status check*). Ce sont des **skills Markdown** ; pas de build/test.
**Trois exceptions bornées** à « ne rien écrire hors du paquet » : `premier-alimente-linear` **et
`update-issue-linear`** créent et mettent à jour des tickets **Linear** (système externe, pas le repo
cible) ; `install-speckit` invoque `specify init` (c'est SpecKit qui génère `.specify/`) ; et
`create-cowork-md` écrit **`init-cowork.md` à la racine** (document de contexte de supervision pour
le PO/Quark, pas un artefact SpecKit ni le repo cible SpecKit).

## Langue & invocation
- **Tout en français** (skills, templates, artefacts, interaction). Seuls les
  identifiants/valeurs machine et noms d'outils/formats (`spec.md`, `constitution.md`,
  SpecKit, `/design-sync`) restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/assembleur:<skill>` + auto par le modèle.

## Les 7 skills
- `assembleur-init` — setup (zéro décision) : installe les gabarits, crée `assembleur-out/`, étend le
  manifeste (bloc `assembly` allégé). **Jamais bloquant** : pose le terrain de convergence **toujours**,
  puis **signale** (sans refuser) si l'un des 3 dossiers de sortie amont (`cadrage-out/`,
  `architecte-out/`, `designer-out/`) est **absent, vide ou incomplet** — **sans** lire de statut de
  validation (validé ou non n'est pas le problème de l'assembleur). **Aucun repo cible à capturer, aucun
  hook à poser** (l'enforcement est posé en amont par `architecte-init`).
- `assembleur-convergence` — **lit les 3 contrats en parallèle** (5 sous-agents `contract-reader`,
  map-reduce), converge, **produit le paquet** dans `assembleur-out/`, **résout les marqueurs en
  session**, et fait la cohérence (porte humaine : *garant de cohérence*).
- `premier-alimente-linear` — **première alimentation de Linear** : lit les features approuvées, les
  présente en tableau, puis crée **un ticket Linear par feature** (label **`Feature`** résolu par nom
  + `feature:<id>` clé de jointure ; via le MCP **`linear-prism`**, confirmation ticket par ticket,
  **liste de contrôle** dans la description pour les grosses features, `blockedBy` pour les
  dépendances), bloc manifeste `linear`. **Exception bornée** à « pas de Linear » (Linear est
  externe). Repli **brouillon** (`assembleur-out/linear-drafts.md`) si le MCP est absent. Voir
  `references/linear-guide.md`.
- `creation-task-linear` — **sous-tickets par phase** : à lancer **après `/speckit.tasks`** (quand
  `specs/<feature>/tasks.md` existe). Pour chaque feature, parse les phases (`## Phase N:`) de son
  `tasks.md` et crée **un sous-ticket Linear par phase** (label **`Task`**, `parentId` = ticket
  `Feature`, **titre descriptif** généré — jamais le nom générique brut « Setup »), après
  confirmation. Labels `Feature`/`Task` **résolus par nom** (`list_issue_labels`), jamais créés. Bloc
  manifeste `linear.issues[].sub_issues[]`. Repli **brouillon** si le MCP est absent. Voir
  `references/linear-guide.md`.
- `update-issue-linear` — **mise à jour Linear** : à partir du message de l'utilisateur (« j'ai
  terminé la tâche … »), retrouve le ticket (par nom, ou **déduit des derniers changements de code**)
  et **met à jour son état** (terminé / en cours ; ou **coche une case** d'une grosse feature), après
  confirmation, via le MCP **`linear-prism`**. **Non gaté**, invoqué à la demande pendant la
  fabrication ; champ manifeste silencieux `workflow_state`. Voir `references/linear-guide.md`.
- `create-cowork-md` — **contexte de supervision (Quark)** : détecte le **dépôt GitHub**
  (`git remote get-url origin`, repli `gh repo view`) et le **projet Linear** (MCP `linear-prism`
  + bloc `linear`), rassemble le contexte des **3 contrats**, et génère **`init-cowork.md` à la
  racine** — le document unique que le PO donne à Quark. **Ne contient rien d'aval** (pas de
  workflow SpecKit / fabrication / avancement : ils n'existent pas encore) ; seuls les **liens**
  GitHub/Linear renvoient à l'état vivant. **3ᵉ exception bornée** à « paquet seul » (écrit à la
  racine — fichier de supervision, pas un artefact SpecKit). Bloc manifeste `cowork`. Non gaté,
  à la demande (idéalement après `premier-alimente-linear`). Voir `references/linear-guide.md`.
- `install-speckit` — **pont vers SpecKit** : pose SpecKit dans le repo cible via
  `scripts/install_speckit.py` (auto-install `uv` sans admin, introspection des flags de `specify
  init`, `specify init` non-interactif, test de fumée, bloc manifeste `speckit`). **Seule exception
  bornée** à « n'écrit jamais dans le repo cible » : c'est `specify init` qui génère `.specify/`,
  jamais ce skill.

## Le paquet `assembleur-out/`
```
assembleur-out/
├── pre-constitution.md        # principes non négociables, format constitution.md (→ /speckit.constitution)
├── features/NNN-…spec-seed.md  # une graine par feature, format spec.md (→ /speckit.specify)
├── feature-map.md             # séquence + couplage/dépendances + walking skeleton
├── technical-context.md       # Technical Context (→ /speckit.plan)
├── CLAUDE.md                  # CLAUDE.md projet (< 200 lignes, @import memory/MEMORY.md — jamais backtiqué)
├── ci/tests.yml               # backstop CI diff-coverage (required status check ; non contournable)
├── memory/{MEMORY,domain,architecture,design,features}.md
├── coherence-report.md
└── attack-plan.md
```
Le manifeste et les gabarits vivent dans `.factory/`. Écriture = read-modify-write + revalidation JSON.

**Déploiement mémoire (important).** L'équipe pose `CLAUDE.md` **et** le dossier `memory/` **à la
racine** du repo de fabrication (les `@imports` du CLAUDE.md sont relatifs à ce fichier). Le
`CLAUDE.md` **importe l'index** via une ligne `@memory/MEMORY.md` **jamais entre backticks** (un
`@import` backtiqué = texte littéral, non importé) ; l'index (chargé chaque session) pointe vers les
thématiques, lues à la demande. **Ce n'est PAS l'auto-mémoire native** de Claude Code
(`~/.claude/projects/<projet>/memory/`, machine-locale et non commitée) : ici la mémoire est
**commitée et partagée** avec l'équipe, chargée par l'`@import`.

## Lecture parallèle (map-reduce)
`assembleur-convergence` est l'orchestrateur ; il dispatche **5 lecteurs** (`agents/contract-reader.md`)
en parallèle (fonctionnel, domaine, technique, décisions, design), chacun avec un schéma de sortie,
puis synthétise. Cadrage : 3–5 sous-agents, objectif/format/limites clairs (Explore ne lit que des
extraits → on utilise un agent dédié à lecture complète).

## Convergence (mapping 3 faces → SpecKit)
Voir `references/speckit-mapping.md`. **Clé de jointure = le use case** (registre canonique
`architecture.feature_sequence` = objets `{id, ucs, name}`). Fonctionnel + technique joints **par use
case** ; design **global** (système synchronisé via `/design-sync` + guidelines). La pré-constitution
converge les **principes non négociables** des 3 contrats (dont la règle design-sync : tout écran
dérive du design system synchronisé, aucune valeur de style en dur, états couverts, contrat d'erreur ;
et le **principe de test** : tests écrits avec le code, intégration mockée, **backstop CI diff-coverage requis**).

## Conventions partagées
`references/interactive-loop.md`, `references/ux-conventions.md`, `references/speckit-mapping.md`,
`references/linear-guide.md` (usage du MCP linear-prism : détection, installation, `save_issue`
création **et mise à jour d'état**, `list_issue_statuses`, `blockedBy`, mode brouillon).
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
python scripts/check_assembly.py <projet>/.factory/manifest.json
```

## Invariants
**Paquet seul** (n'écrit que dans `assembleur-out/`, jamais un fichier que SpecKit génère — **trois
exceptions bornées : `premier-alimente-linear` et `update-issue-linear`, qui créent et mettent à jour des
tickets Linear (système externe, jamais le repo cible) ; `install-speckit`, qui invoque `specify
init` pour que SpecKit génère lui-même `.specify/`, sans jamais le rédiger à la main ; et
`create-cowork-md`, qui écrit `init-cowork.md` à la racine (contexte de supervision PO/Quark, pas un
artefact SpecKit)**) ; proposer/pas décider (cohérence validée par l'humain) ; **rien laissé indéfini** (tout marqueur
résolu en session, en place) ; **contenu seul** (aucune `(src:)`, horodatage, nom de personne) ;
restitutions en prose, manifeste mis à jour en silence.
