# MEMORY.md — index mémoire projet

<!-- Livré en `assembleur-out/memory/MEMORY.md`. Index concis (≤ 200 lignes) : des POINTEURS
     cliquables (liens Markdown `[titre](chemin) — accroche`), jamais de contenu dupliqué.
     Chemins RELATIFS à ce fichier (memory/MEMORY.md) : un voisin de memory/ s'écrit `domain.md`
     (jamais `memory/domain.md`) ; un fichier du paquet à la racine s'écrit `../feature-map.md`.
     L'équipe copie le paquet dans le repo de fabrication ; les thématiques sont lues à la demande.
     Contenu seul. -->

## Le projet en une phrase
[Ce que fait le produit.]

## Contrats (3 faces) — où regarder
- **Fonctionnel** : les graines [features/](../features/) (User Scenarios + FR) ; langage = [domaine](domain.md).
- **Technique** : [contexte technique](../technical-context.md) + [architecture](architecture.md) (stack, composants, ADR, conventions).
- **Design** : [design](design.md) (design system synchronisé + états + erreurs + a11y).

## Constitution
[Pré-constitution](../pre-constitution.md) — principes non négociables (P1..Pn) + gouvernance (donnée à `/speckit.constitution`).

## Découpage
[Carte des features](../feature-map.md) — séquence, couplage/dépendances, walking skeleton.

## Fichiers thématiques — lus par Claude au besoin
- [Domaine](domain.md) — langage ubiquitaire & entités.
- [Architecture](architecture.md) — stack, composants, décisions (ADR), conventions, qualité.
- [Design](design.md) — design system, états, accessibilité.
- [Features](features.md) — séquence & 3 faces par feature.
- [Contexte technique](../technical-context.md) — Technical Context SpecKit (input `/speckit.plan`).
