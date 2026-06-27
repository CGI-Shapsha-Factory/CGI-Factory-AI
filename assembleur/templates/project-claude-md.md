<!-- CLAUDE.md du PROJET (repo SpecKit). La section entre les marqueurs est gérée par SpecKit
     (update-agent-context) — ne pas l'éditer à la main. Hors marqueurs = guidance factory. -->

# <PROJECT_NAME>

[Une phrase : ce que fait le produit.] (src: cadrage/product-brief)

<!-- SPECKIT START -->
<!-- Section gérée automatiquement par SpecKit. -->
<!-- SPECKIT END -->

## Contrats (3 faces)
- **Fonctionnel** : briefs par feature dans `specs/` ; langage = `GLOSSARY.md`.
- **Technique** : stack [..] ; style/format/nommage dans `conventions/` ; ADR de référence.
- **Design** : design system `design-system/` (tokens DTCG) ; accessibilité **WCAG 2.2 AA**.

## Où vit quoi
- `.specify/memory/constitution.md` — principes non négociables (opposables).
- `specs/NNN-feature/spec.md` — une feature = 3 faces (fonctionnel + technique + design).
- `GLOSSARY.md` — langage ubiquitaire. `MEMORY.md` — index des contrats & décisions.

## Lancer SpecKit
Voir le plan d'attaque : `specify init --ai claude`, puis `/speckit.specify` par feature
(**walking skeleton d'abord**) → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`.
La *Constitution Check* du `plan.md` est **opposable**.

## Règles clés (invariants des 3 contrats)
- [ex. refus d'inventer / réponses sourcées] (fonctionnel)
- [ex. filtrage par droits, requêtes paramétrées] (technique)
- [ex. aucune valeur de couleur brute, états vide/chargement/erreur traités, AA] (design)
