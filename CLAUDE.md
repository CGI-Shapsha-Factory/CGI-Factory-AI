# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du dépôt
Ce dépôt n'est **pas un projet applicatif** : c'est une **collection de plugins Claude Code** formant une « Factory IA » (fabrique logicielle à forte assistance IA). Les livrables sont des **skills Markdown** + un `plugin.json` par plugin. **Ni build, ni lint, ni tests** — la seule « compilation » est la validité JSON des manifestes.

- Dépôt : `github.com/NASSWIEL/Factory-IA` (**privé depuis 2026-06-26**), branche `main`. Documents de conception dans le parent (`../context-complet.txt`, `../architecture.md`).
- Distribution : marketplace **`git-subdir`** (`.claude-plugin/marketplace.json`) → **Shapsha-Factory**. Le repo pro CGI (`CGI-Shapsha-Factory/CGI-Factory-AI`) reçoit les évolutions par **workflow PR** (branche depuis `cgi/main` + réinjection `README.md` / `marketplace.json` / `docs/factory-ia.png`, puis PR + merge — **plus de force-push**). Détails (remotes, recette PR, token) en **mémoire projet interne**, pas dans l'arbre versionné. Côté utilisateur : `/plugin marketplace update Shapsha-Factory`.
- Installation : **uniquement via la marketplace** (`.claude-plugin/marketplace.json` → Shapsha-Factory). Côté utilisateur : `/plugin marketplace add` puis `/plugin install <plugin>@Shapsha-Factory`. La marketplace expose aussi `category`/`tags` par plugin (groupement par rôle dans `/plugin` Discover). *(L'ancien installeur façon BMAD — `install.py` / wrapper npx / `INSTALL.md` — a été retiré : la marketplace suffit.)*
- Git : branche `main`, email `naifsaleem20@gmail.com`. Commit/push uniquement sur demande.

## Les plugins (phase amont = 4 contrats)
| Dossier | Rôle | État | Détail |
|---------|------|------|--------|
| `cadrage/` | Contrat **fonctionnel** (captation → pack repris par l'architecte) | **construit** | voir `cadrage/CLAUDE.md` |
| `architecte/` | Contrat **technique** (drivers, attributs qualité, composants, stack, ADR, walking skeleton, conventions/linters, diagrammes) | **construit** | voir `architecte/CLAUDE.md` |
| `designer/` | Contrat **design** — **atelier de couverture** (checklist fondation/expérience/technique pré-remplie par les handoffs) qui produit le **prompt Claude Design** + rapport de couverture + handoff ; le design system naît dans **Claude Design** (`/design-sync`), pas généré par le plugin | **construit** | voir `designer/CLAUDE.md` |
| `assembleur/` | Convergence des 3 contrats par feature + amorçage repo SpecKit (constitution, CLAUDE.md, briefs 3-faces, glossaire consolidé, MEMORY.md, seeds spec.md, CI, Linear) | **construit** | voir `assembleur/CLAUDE.md` |

Chaque plugin a (ou aura) son propre **`<plugin>/CLAUDE.md`** détaillé. Pour travailler sur `cadrage`, lire **`cadrage/CLAUDE.md`** en premier.

**Vue d'ensemble utilisateur** de toute la chaîne (4 phases, ordre des skills, portes humaines) : le skill **`/cadrage:help-factory`** — l'**aide unique** (statique, un tableau par plugin).

## Principe transverse
- **L'IA propose, l'humain tranche.** Aucune gate structurante n'est franchie par l'IA.
- **Figer les contrats en amont**, automatiser l'hygiène en aval par des hooks déterministes (socle à venir).
- Les sorties de cadrage + architecte + designer convergent dans l'**assembleur** ; il produit un **paquet de handoff** dans `assembleur-out/` — dont une **pré-constitution** (au format `constitution.md`, dérivée des 3 contrats) et des **graines spec** par feature — que **l'équipe** donne à SpecKit. L'assembleur **n'écrit jamais** dans le repo cible. Il n'y a plus de skill handoff côté cadrage.

## Conventions communes
- Skills : `<plugin>/skills/<nom>/SKILL.md`, frontmatter `name:` + `description:` (une phrase courte anglaise). Corps des skills en **français** (instructions).
- Langue : **tout en français** (skills, templates, artefacts, interaction) ; seuls les identifiants/valeurs machine du manifeste et noms d'outils/formats restent tels quels.
- Workspace runtime d'un projet client : `.factory/{manifest.json, templates/}` (mécanique cachée) + un dossier de sortie par plugin à la racine (`cadrage-out/`, `architecte-out/`, `designer-out/`, `assembleur-out/`) + `prompts/<plugin>/` (prompts Claude Design par plugin : `prompts/cadrage/`, `prompts/designer/`, en fichiers plats).
- **Identité des features (clé de jointure inter-plugins)** : le **use case** du cadrage (ex. `UC2`) est l'identifiant fonctionnel **stable**. L'architecte fige le **registre canonique** `architecture.feature_sequence` = objets `{id, ucs, name}` où `ucs` est une **liste** (l'`id` `001…` = ordre de fabrication ; une feature peut **bundler plusieurs use cases** en cas de fusion ; **aucune notion de MVP** nulle part — l'ordre est purement technique) ; l'assembleur joint les faces **fonctionnelle** (briefs cadrage) et **technique** (composants/ADR architecte) **par use case**. La **face design est globale** (pas de jointure par feature) : le designer produit un **handoff** (réf. du design system Claude Design synchronisé via `/design-sync` + guidelines) appliqué à tous les écrans. Composants : services **+ application front-end** = `components.md` (architecture technique, architecte) ; le **design system visuel** naît dans Claude Design (`/design-sync`).
- Marketplace : ajouter un plugin = une entrée `git-subdir` dans le `marketplace.json` de la marketplace Shapsha-Factory (`url` = ce dépôt Factory-IA, `path` = dossier du plugin).

## Flux d'artefacts (contrat I/O explicite, déterministe)
La **mécanique partagée** vit dans `.factory/{manifest.json, templates/}` (dossier caché, créé par `cadrage-init`). Les **documents générés** vont dans un dossier de sortie **par plugin** à la racine : `cadrage-out/`, `architecte-out/`, `designer-out/`, `assembleur-out/` (+ `prompts/<plugin>/` pour les prompts, en **fichiers plats** `<NNN>-<JJ-MM>-<nom>.md`). Le **manifeste** est le contrat machine ; chaque plugin **écrit dans son `-out/`** et **lit directement** ceux de l'amont (pas d'hypothèse implicite). Contrat de consommation strict : **architecte ⊂ cadrage** ; **designer ⊂ cadrage + architecte** ; **assembleur ⊂ les trois**. **Plus de skill handoff** côté cadrage : la convergence est le rôle de l'**assembleur**, qui produit un **paquet** (il n'écrit jamais dans le repo cible).

| Plugin | Consomme (entrées) | Produit (sorties) | Bloc manifeste |
|---|---|---|---|
| **cadrage** | matière brute (transcripts/docs) | `cadrage-out/`: capture-brute, project-frame, product-brief, glossaire, spec-index, coupling-map, completude-report, `features-fonctionnels-brief/<feature>.brief.md` ; `prompts/cadrage/` | `artifacts`, `demonstrateur`, `discovery`, `definition_of_ready` |
| **architecte** | `cadrage-out/`: product-brief, glossaire, spec-index, project-frame, briefs | `architecte-out/`: drivers-quality, components, tech-stack, standards, diagrams (+ `diagrammes/*.png`), risks, **design-impact**, `decisions/ADR-*.md` ; `conventions/` (racine) | `architecture` |
| **designer** | `cadrage-out/` (product-brief, glossaire, spec-index, démonstrateur) **+** `architecte-out/design-impact.md` | `designer-out/`: coverage-report, design-guidelines ; `prompts/designer/<NNN>-<JJ-MM>-claude-design.md` | `design` |
| **assembleur** | `cadrage-out/` + `architecte-out/` (tech-stack, components, standards, decisions/, drivers-quality) + `designer-out/` (design-guidelines, coverage-report) | `assembleur-out/` (paquet de handoff, **rien dans le repo cible**) : `pre-constitution.md`, `features/<id>-*.spec-seed.md`, `feature-map.md`, `technical-context.md`, `CLAUDE.md`, `memory/{MEMORY,domain,architecture,design,features}.md`, `coherence-report.md`, `attack-plan.md` | `assembly` |

**Enforcement** (3 couches, déjà en place) : (1) **portes d'entrée** de chaque `-init` (refusent si la phase amont n'est pas validée + vérifient la présence des fichiers attendus dans les `-out/` amont) ; (2) **garde-fous déterministes** `check_discovery`/`check_ready`/`check_architecture`/`check_design`/`check_assembly` (défaut `.factory/manifest.json`) ; (3) **manifeste** (jointure par use case). **Frontière SpecKit** : l'assembleur produit un **paquet** dans `assembleur-out/` (pré-constitution, graines spec, carte des features, contexte technique, CLAUDE.md, mémoire) ; **c'est l'équipe** qui lance `specify init` puis `/speckit.constitution` (depuis `pre-constitution.md`) et les `/speckit.specify`. L'assembleur **n'écrit jamais** `.specify/`, `specs/NNN/spec.md`, ni aucun fichier que SpecKit génère.
