# Plan d'attaque — fabrication SpecKit

> Généré par l'assembleur. **L'équipe l'exécute** dans le repo cible (l'assembleur ne lance
> pas `specify init` lui-même). (src: architecte/feature_sequence)

## 0. Initialisation
- Lancer `specify init --ai claude` dans `<target_repo>` (si pas déjà initialisé).
- La constitution est **déjà fournie** (`.specify/memory/constitution.md`). La raffiner via
  `/speckit.constitution` seulement si besoin (ne pas écraser sans raison).

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
