# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Nature du dépôt
Ce dépôt n'est **pas un projet applicatif** : c'est une **collection de plugins Claude Code** formant une « Factory IA » (fabrique logicielle à forte assistance IA). Les livrables sont des **skills Markdown** + un `plugin.json` par plugin. **Ni build, ni lint, ni tests** — la seule « compilation » est la validité JSON des manifestes.

- Dépôt : `github.com/NASSWIEL/Factory-IA` (public), branche `main`. Documents de conception dans le parent (`../context-complet.txt`, `../architecture.md`).
- Distribution : les plugins sont publiés via une **marketplace `git-subdir`** (`.claude-plugin/marketplace.json`) pointant ce dépôt ; marketplace de référence : **Shapsha-Factory**. Les remotes (origin public + remote pro privé) et le mécanisme de **snapshot** (réinjection `README.md` + `marketplace.json`) sont consignés dans la **mémoire projet interne** — pas dans l'arbre versionné. Côté utilisateur : `/plugin marketplace update Shapsha-Factory`.
- Installeur (façon BMAD) : **`install.py`** à la racine = un menu interactif (cases à cocher, choix libre des modules) qui enrobe `claude plugin install` ; flags non-interactifs `--modules`/`--all`/`--scope`/`--dry-run`. Doc : **`INSTALL.md`**. La marketplace expose aussi `category`/`tags` par plugin (groupement par rôle dans `/plugin` Discover).
- Git : branche `main`, email `naifsaleem20@gmail.com`. Commit/push uniquement sur demande.

## Les plugins (phase amont = 4 contrats)
| Dossier | Rôle | État | Détail |
|---------|------|------|--------|
| `cadrage/` | Contrat **fonctionnel** (captation → pack SpecKit) | **construit** | voir `cadrage/CLAUDE.md` |
| `architecte/` | Contrat **technique** (drivers, attributs qualité, composants, stack, ADR, walking skeleton, conventions/linters, diagrammes) | **construit** | voir `architecte/CLAUDE.md` |
| `designer/` | Contrat **design** (design system exécutable : tokens DTCG, fondations, composants & états, parcours, accessibilité WCAG 2.2) | **construit** | voir `designer/CLAUDE.md` |
| `assembleur/` | Convergence des 3 contrats par feature + amorçage repo SpecKit (constitution, CLAUDE.md, briefs 3-faces, glossaire consolidé, MEMORY.md, seeds spec.md, CI, Linear) | **construit** | voir `assembleur/CLAUDE.md` |

Chaque plugin a (ou aura) son propre **`<plugin>/CLAUDE.md`** détaillé. Pour travailler sur `cadrage`, lire **`cadrage/CLAUDE.md`** en premier.

**Vue d'ensemble utilisateur** de toute la chaîne (4 phases, ordre des skills, portes humaines) : le skill **`/cadrage:help-factory`** ; détail de la phase amont : `/cadrage:help-cadrage`.

## Principe transverse
- **L'IA propose, l'humain tranche.** Aucune gate structurante n'est franchie par l'IA.
- **Figer les contrats en amont**, automatiser l'hygiène en aval par des hooks déterministes (socle à venir).
- Les sorties de cadrage + architecte + designer convergent dans l'**assembleur** ; `cadrage` produit une **pré-constitution** (face fonctionnelle), et l'**assembleur écrit la constitution finale convergée** (3 faces) consommée par SpecKit.

## Conventions communes
- Skills : `<plugin>/skills/<nom>/SKILL.md`, frontmatter `name:` + `description:` (une phrase courte anglaise). Corps des skills en **français** (instructions).
- Langue : **tout en français** (skills, templates, artefacts, interaction) ; seuls les identifiants/valeurs machine du manifeste et noms d'outils/formats restent tels quels.
- Workspace runtime d'un projet client : `factory-docs/{manifest.json, templates/, work/}` (plat) + `factory-prompts/`.
- **Identité des features (clé de jointure inter-plugins)** : le **use case** du cadrage (ex. `UC2`) est l'identifiant fonctionnel **stable** qui traverse les 4 plugins. L'architecte fige le **registre canonique** `architecture.feature_sequence` = objets `{id, ucs, name, mvp}` où `ucs` est une **liste** (l'`id` `001…` = ordre de fabrication ; une feature peut **bundler plusieurs use cases** en cas de fusion) ; designer (`journeys_coverage[].uc`) et assembleur joignent les 3 faces **par use case**. Composants : services = `components.md` (architecte) ; UI = `design-components.md` (designer).
- Marketplace : ajouter un plugin = une entrée `git-subdir` dans le `marketplace.json` de la marketplace Shapsha-Factory (`url` = ce dépôt Factory-IA, `path` = dossier du plugin).
