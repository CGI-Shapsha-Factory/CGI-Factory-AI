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
- **Design** : design system **synchronisé depuis Claude Design via `/design-sync`** ; guidelines
  (états, patterns d'erreur, socle a11y) dans le handoff design ; accessibilité au niveau visé.

## Où vit quoi
- `.specify/memory/constitution.md` — principes non négociables (opposables).
- `specs/NNN-feature/spec.md` — une feature = 3 faces (fonctionnel + technique + design).
- `GLOSSARY.md` — langage ubiquitaire. `MEMORY.md` — index des contrats & décisions.

## Lancer SpecKit
Le repo est **déjà initialisé** (`specify init --ai claude`, précondition de la convergence) et la
constitution finale convergée est en place. Voir le plan d'attaque : `/speckit.specify` par feature
(**walking skeleton d'abord**) → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`.
La *Constitution Check* du `plan.md` est **opposable**. **Ne pas relancer `specify init`** (il
écraserait la constitution).

## Design (design-sync) — §6, opposable
- **Exécuter `/design-sync` au démarrage** ; ne construire qu'à partir des **tokens et composants
  synchronisés** (le design system vit dans Claude Design).
- **Checklist des états par écran** : chargement, vide, erreur, succès.
- **Patterns d'erreur** : validation à la sortie du champ ; format d'erreur API → messages par champ.
- **Socle d'accessibilité** : niveau visé (ex. WCAG 2.2 AA) — contraste, focus visible, clavier.

## Règles clés (invariants des 3 contrats)
- [ex. refus d'inventer / réponses sourcées] (fonctionnel)
- [ex. filtrage par droits, requêtes paramétrées] (technique)
- **aucune valeur de style en dur** (tokens uniquement) ; états vide/chargement/erreur/succès traités ;
  erreurs selon le contrat ; accessibilité au niveau visé (design)
