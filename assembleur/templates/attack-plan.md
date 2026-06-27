# Plan d'attaque — fabrication SpecKit

> Généré par l'assembleur. **L'équipe l'exécute** dans le repo cible (l'assembleur ne lance
> pas `specify init` lui-même). (src: architecte/feature_sequence)

## 0. Prérequis (déjà fait AVANT la convergence)
- Le repo cible a **déjà** été initialisé : `specify init --ai claude` a été lancé **avant**
  l'assembleur (précondition vérifiée par `assembleur-init`). L'assembleur a donc écrit **après**
  init : sa **constitution finale convergée** a **remplacé** le gabarit de SpecKit dans
  `.specify/memory/constitution.md` (bon ordre, pas de clobber).
- **Ne pas relancer `specify init`** ici : il réécraserait la constitution convergée. La raffiner
  via `/speckit.constitution` seulement si besoin.

## 1. Séquence des features (ordre des dépendances)
| Ordre | Feature | Walking skeleton | Parallélisable | Dépend de |
|-------|---------|------------------|----------------|-----------|
| 1 | 001 — [..] | oui | non | — |
| 2 | 002 — [..] | non | [oui/non] | 001 |

## 2. Par feature (sur la branche `NNN-feature`)
Le seed `specs/NNN-feature/spec.md` est déjà posé. Enchaîner :
`/speckit.specify` (compléter/clarifier) → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`.

## 3. CI
Activer `.github/workflows/factory-checks.yml` (garde-fous déterministes + linters `conventions/`).

## 4. Linear (après validation de l'équipe)
`/assembleur:assembleur-amorce` crée le projet Linear + **une issue par feature** (via MCP),
**uniquement** après la validation du découpage par l'équipe.
