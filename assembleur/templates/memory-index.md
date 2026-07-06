# MEMORY.md — index mémoire projet

<!-- Livré en `assembleur-out/memory/MEMORY.md`. Index concis (≤ 200 lignes) : des POINTEURS, pas
     de contenu dupliqué. L'équipe le copie (avec le reste du paquet) dans le repo de fabrication.
     Les fichiers thématiques sont chargés à la demande. Contenu seul. -->

## Le projet en une phrase
[Ce que fait le produit.]

## Contrats (3 faces) — où regarder
- **Fonctionnel** : les graines `features/<id>-…spec-seed.md` (User Scenarios + FR) ; langage = `memory/domain.md`.
- **Technique** : `technical-context.md` + `memory/architecture.md` (stack, composants, ADR, conventions).
- **Design** : `memory/design.md` (design system synchronisé + états + erreurs + a11y).

## Constitution
`pre-constitution.md` — principes non négociables (P1..Pn) + gouvernance. (Donnée à `/speckit.constitution`.)

## Découpage
`feature-map.md` — séquence, couplage/dépendances, walking skeleton (feature `001`).

## Fichiers mémoire (chargés à la demande)
- `memory/domain.md` — langage ubiquitaire & entités.
- `memory/architecture.md` — stack, composants, décisions, conventions, qualité.
- `memory/design.md` — design system, états, accessibilité.
- `memory/features.md` — séquence & 3 faces par feature.
- `technical-context.md` (à la racine) — contexte technique SpecKit (input `/speckit.plan`).
