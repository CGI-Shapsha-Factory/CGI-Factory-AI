# Plan d'attaque — fabrication SpecKit

> Livré en `assembleur-out/attack-plan.md`. **L'équipe l'exécute** : l'assembleur ne lance pas
> SpecKit, il fournit le paquet. Contenu seul (aucune provenance).

## 0. Mettre le paquet en place
- `CLAUDE.md` et `memory/` sont **déjà déployés dans `.claude/`** par la convergence — actifs sans
  copie manuelle. Le reste du paquet (constitution, graines, carte des features, contexte technique)
  reste dans `assembleur-out/` et sert de matière aux `/speckit.*`.
- Initialiser SpecKit : `specify init --here --integration claude` dans le repo (automatisable via
  `/assembleur:install-speckit` — installe `uv`/le CLI et joue `specify init` sans manip).

## 1. Constitution
`/speckit.constitution` en fournissant `pre-constitution.md` — les principes non négociables sont déjà
rédigés ; il ne reste qu'à les graver.

## 2. Séquence des features (ordre des dépendances)
| Ordre | Feature | Walking skeleton | Parallélisable | Dépend de |
|-------|---------|------------------|----------------|-----------|
| 1 | 001 — [..] | oui | non | — |
| 2 | 002 — [..] | non | [oui/non] | 001 |

> Ordre et couplage : voir `feature-map.md`. Le **walking skeleton** (001) d'abord.

## 3. Par feature (numérotation canonique `NNN-slug`, une branche = une feature = un développeur)
Prendre `NNN-slug` dans `feature-map.md` (colonne « Répertoire / branche SpecKit ») — c'est l'`id` du
registre de l'architecte, **jamais** un numéro auto-généré. Enchaîner :

1. **Claim** : s'assigner le ticket `Feature` Linear de `NNN` et le passer *In Progress* (ne jamais
   prendre une feature déjà assignée).
2. `git checkout main && git pull` puis **`git checkout -b NNN-slug`**.
3. **`/speckit.specify`** en fournissant explicitement **`SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug`**
   (+ la matière de la graine `features/NNN-slug.md`). Ceci fige le répertoire **et** le numéro :
   pas d'auto-numérotation, donc pas de collision entre développeurs.
4. `/speckit.plan` (Technical Context dans `technical-context.md`) → `/speckit.tasks` →
   **`/assembleur:creation-task-linear`** (un sous-ticket `Task` par phase, rattaché au ticket
   `Feature`) → `/speckit.implement`.

> Le numéro `NNN` = l'`id` du registre ; `SPECIFY_FEATURE_DIRECTORY` fige le répertoire, la branche fige
> l'attribution des coûts et le recoupement Linear. Le garde-fou `.claude/hooks/check_speckit_alignment.py`
> vérifie l'alignement à chaque édition d'un `spec.md`, et en CI (`python .claude/hooks/check_speckit_alignment.py check`).

## 4. Règles multi-développeurs
- **Numérotation** : `NNN` vient **toujours** de `feature-map.md` ; jamais d'auto-numérotation SpecKit
  (sinon deux devs partis de `main` produisent le même numéro). Le timestamp est **banni** (l'attribution
  des coûts et la sync Linear lisent `^\d{3}-`).
- **Suivi dans Linear** : l'avancement (sous-tickets de phase, état des tickets) vit **directement dans
  Linear** (l'application), **pas** dans le manifeste committé — pas de conflit de merge sur `manifest.json`.
- **Composants partagés** : les features en **écriture concurrente** sur un même composant (voir la table
  « Couplage / états partagés » de `feature-map.md`, et les relations `blockedBy` dans Linear) se font
  **en séquence**, pas en parallèle.
- **Artefacts figés en amont** : `/speckit.constitution` (depuis `pre-constitution.md`) se lance **une
  seule fois** puis on **committe** `.specify/memory/constitution.md` ; `CLAUDE.md` + `memory/` sont déjà
  déployés et committés par la convergence. **Ne pas les régénérer** par feature/branche.
