<!-- CLAUDE.md du PROJET, livré en `assembleur-out/CLAUDE.md`. L'équipe le place à la racine du repo
     de fabrication. < 200 lignes, concis. Instructions durables + @imports vers les fichiers mémoire.
     Contenu seul. -->

# <PROJECT_NAME>

[Une phrase : ce que fait le produit.]

## Contrats (3 faces) — où regarder
- **Fonctionnel** : les graines de feature (`features/<id>-…spec-seed.md`) ; langage = `@memory/domain.md`.
- **Technique** : `@technical-context.md` et `@memory/architecture.md` (stack, composants, ADR, conventions).
- **Design** : `@memory/design.md` (design system synchronisé + états + erreurs + a11y).

## Constitution (opposable)
`pre-constitution.md` porte les **principes non négociables**. À donner à `/speckit.constitution` au
démarrage de SpecKit ; chaque `plan.md` passe ensuite la *Constitution Check*.

## Lancer SpecKit
Voir `attack-plan.md` : `specify init` → `/speckit.constitution` (depuis `pre-constitution.md`) →
`/speckit.specify` par feature **dans l'ordre du `feature-map.md`** (walking skeleton d'abord) →
`/speckit.plan` → `/speckit.tasks` → `/speckit.implement`.

## Design (design-sync) — non négociable
- **Exécuter `/design-sync`** ; ne construire qu'à partir des **tokens et composants synchronisés** —
  **aucune valeur de style en dur**.
- **États par écran** : chargement, vide, erreur, succès.
- **Patterns d'erreur** : le format d'erreur de l'API se projette en messages par champ.
- **Accessibilité** : au niveau visé (ex. WCAG 2.2 AA) — contraste, focus visible, clavier.

## Règles clés (invariants des 3 contrats)
- [ex. règle fonctionnelle non négociable]
- [ex. règle technique : filtrage par droits, requêtes paramétrées]
- **aucune valeur de style en dur** (tokens uniquement) ; états couverts ; erreurs selon le contrat ;
  accessibilité au niveau visé.

## Commandes
[Build / test / lint, dérivées de la stack — ex. `uv run pytest`, `npm test`.]
