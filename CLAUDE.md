# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du dépôt
Ce dépôt n'est **pas un projet applicatif** : c'est une **collection de plugins Claude Code** formant une « Factory IA » (fabrique logicielle à forte assistance IA). Les livrables sont des **skills Markdown** + un `plugin.json` par plugin. **Ni build, ni lint, ni tests** — la seule « compilation » est la validité JSON des manifestes.

- Dépôt : `github.com/NASSWIEL/Factory-IA` (**privé depuis 2026-06-26**), branche `main`. Documents de conception dans le parent (`../context-complet.txt`, `../architecture.md`).
- Distribution : marketplace **`git-subdir`** (`.claude-plugin/marketplace.json`) → **Shapsha-Factory**. Le repo pro CGI (`CGI-Shapsha-Factory/CGI-Factory-AI`) reçoit les évolutions par **workflow PR** (branche depuis `cgi/main` + réinjection `README.md` / `marketplace.json` / `docs/factory-ia.png`, puis PR + merge — **plus de force-push**). Détails (remotes, recette PR, token) en **mémoire projet interne**, pas dans l'arbre versionné. Côté utilisateur : `/plugin marketplace update Shapsha-Factory`.
- Installeur (façon BMAD) : **`install.py`** (Python) **+ wrapper npx** (`package.json` + `bin/factory-install.mjs`) = un menu interactif (cases à cocher, **choix libre** des modules) qui enrobe `claude plugin install` ; flags `--modules`/`--all`/`--scope`/`--yes`/`--dry-run`. Doc : **`INSTALL.md`**. La marketplace expose aussi `category`/`tags` par plugin (groupement par rôle dans `/plugin` Discover).
- Git : branche `main`, email `naifsaleem20@gmail.com`. Commit/push uniquement sur demande.

## Les plugins (phase amont = 4 contrats)
| Dossier | Rôle | État | Détail |
|---------|------|------|--------|
| `cadrage/` | Contrat **fonctionnel** (captation → pack SpecKit) | **construit** | voir `cadrage/CLAUDE.md` |
| `architecte/` | Contrat **technique** (drivers, attributs qualité, composants, stack, ADR, walking skeleton, conventions/linters, diagrammes) | **construit** | voir `architecte/CLAUDE.md` |
| `designer/` | Contrat **design** — **atelier de couverture** (checklist fondation/expérience/technique pré-remplie par les handoffs) qui produit le **prompt Claude Design** + rapport de couverture + handoff ; le design system naît dans **Claude Design** (`/design-sync`), pas généré par le plugin | **construit** | voir `designer/CLAUDE.md` |
| `assembleur/` | Convergence des 3 contrats par feature + amorçage repo SpecKit (constitution, CLAUDE.md, briefs 3-faces, glossaire consolidé, MEMORY.md, seeds spec.md, CI, Linear) | **construit** | voir `assembleur/CLAUDE.md` |

Chaque plugin a (ou aura) son propre **`<plugin>/CLAUDE.md`** détaillé. Pour travailler sur `cadrage`, lire **`cadrage/CLAUDE.md`** en premier.

**Vue d'ensemble utilisateur** de toute la chaîne (4 phases, ordre des skills, portes humaines) : le skill **`/cadrage:help-factory`** — l'**aide unique** (statique, un tableau par plugin).

## Principe transverse
- **L'IA propose, l'humain tranche.** Aucune gate structurante n'est franchie par l'IA.
- **Figer les contrats en amont**, automatiser l'hygiène en aval par des hooks déterministes (socle à venir).
- Les sorties de cadrage + architecte + designer convergent dans l'**assembleur** ; `cadrage` produit une **pré-constitution** (face fonctionnelle), et l'**assembleur écrit la constitution finale convergée** (3 faces) consommée par SpecKit.

## Conventions communes
- Skills : `<plugin>/skills/<nom>/SKILL.md`, frontmatter `name:` + `description:` (une phrase courte anglaise). Corps des skills en **français** (instructions).
- Langue : **tout en français** (skills, templates, artefacts, interaction) ; seuls les identifiants/valeurs machine du manifeste et noms d'outils/formats restent tels quels.
- Workspace runtime d'un projet client : `factory-docs/{manifest.json, templates/, work/}` (plat) + `factory-prompts/`.
- **Identité des features (clé de jointure inter-plugins)** : le **use case** du cadrage (ex. `UC2`) est l'identifiant fonctionnel **stable**. L'architecte fige le **registre canonique** `architecture.feature_sequence` = objets `{id, ucs, name, mvp}` où `ucs` est une **liste** (le champ `mvp` est une décision **d'architecture** — le cadrage ne porte plus de notion de MVP) (l'`id` `001…` = ordre de fabrication ; une feature peut **bundler plusieurs use cases** en cas de fusion) ; l'assembleur joint les faces **fonctionnelle** (briefs cadrage) et **technique** (composants/ADR architecte) **par use case**. La **face design est globale** (pas de jointure par feature) : le designer produit un **handoff** (réf. du design system Claude Design synchronisé via `/design-sync` + guidelines) appliqué à tous les écrans. Composants : services = `components.md` (architecte) ; l'UI naît dans Claude Design.
- Marketplace : ajouter un plugin = une entrée `git-subdir` dans le `marketplace.json` de la marketplace Shapsha-Factory (`url` = ce dépôt Factory-IA, `path` = dossier du plugin).

## Flux d'artefacts (contrat I/O explicite, déterministe)
Tous les plugins partagent **un seul workspace** `factory-docs/{manifest.json, templates/, work/}` (+ `factory-prompts/`), créé par `cadrage-init` à la racine du projet. Le **manifeste** est le contrat machine ; les artefacts sont des **fichiers nommés** dans `factory-docs/work/` (à plat). Chaque plugin a une **liste d'entrées et de sorties déterministe** — il sait exactement où chercher (pas d'hypothèse implicite). Contrat de consommation strict : **architecte ⊂ cadrage** ; **designer ⊂ cadrage + architecte** ; **assembleur ⊂ les trois**.

| Plugin | Consomme (entrées) | Produit (sorties) | Bloc manifeste |
|---|---|---|---|
| **cadrage** | matière brute (transcripts/docs) | `work/`: capture-brute, project-frame, product-brief, glossaire, spec-index, coupling-map, `00X-*.brief.md`, pre-constitution, completude-report ; `factory-prompts/` | `artifacts`, `demonstrateur`, `discovery`, `definition_of_ready` |
| **architecte** | cadrage : product-brief, glossaire, spec-index, project-frame, `*.brief.md`, pre-constitution | `work/`: drivers-quality, components, tech-stack, standards, diagrams, risks, **design-impact**, `decisions/ADR-*.md` ; `conventions/` (racine) | `architecture` |
| **designer** | cadrage : product-brief, glossaire, spec-index, démonstrateur **+** architecte : `design-impact.md` | `work/`: coverage-report, design-guidelines ; `factory-prompts/<NNN>-claude-design/prompt.md` | `design` |
| **assembleur** | cadrage + architecte (tech-stack, components, standards, decisions/, drivers-quality) + designer (design-guidelines, coverage-report) | `work/`: briefs/, guidelines/, coherence-report, attack-plan **+ `<target_repo>/`** : `.specify/memory/constitution.md`, CLAUDE.md, GLOSSARY.md, MEMORY.md, specs/NNN/spec.md, CI, hook Linear | `assembly` |

**Enforcement** (3 couches, déjà en place) : (1) **portes d'entrée** de chaque `-init` (refusent si la phase amont n'est pas validée + vérifient la présence des fichiers attendus) ; (2) **garde-fous déterministes** `check_discovery`/`check_ready`/`check_architecture`/`check_design`/`check_assembly` ; (3) **manifeste** (jointure par use case). **Frontière SpecKit** : `specify init` (runtime + commandes `/speckit.*`) est lancé **avant** la convergence ; l'assembleur écrit **ensuite** dans `<target_repo>` et **remplace** le gabarit de constitution (jamais l'inverse — sinon clobber).
