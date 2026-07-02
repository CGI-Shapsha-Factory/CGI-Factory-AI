# Plan d'attaque — fabrication SpecKit

> Livré en `assembleur-out/attack-plan.md`. **L'équipe l'exécute** : l'assembleur ne lance pas
> SpecKit, il fournit le paquet. Contenu seul (aucune provenance).

## 0. Mettre le paquet en place
- Copier le contenu de `assembleur-out/` à la racine du repo de fabrication (constitution, graines,
  carte des features, contexte technique, `CLAUDE.md`, `memory/`).
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

## 3. Par feature (sur la branche `NNN-feature`)
La graine `features/<id>-…spec-seed.md` fournit la matière. Enchaîner :
`/speckit.specify` (compléter à partir de la graine) → `/speckit.plan` (Technical Context dans
`technical-context.md`) → `/speckit.tasks` → `/speckit.implement`.
