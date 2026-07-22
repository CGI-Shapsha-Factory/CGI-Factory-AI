<!-- CLAUDE.md du PROJET, écrit directement dans `.claude/CLAUDE.md` du projet (co-localisé avec
     `.claude/memory/`). Actif dès la session suivante, sans copie manuelle. < 200 lignes, concis.
     Instructions durables + @import vers l'index mémoire. Contenu seul. -->

# <PROJECT_NAME>

[Une phrase : ce que fait le produit.]

<!-- NE JAMAIS mettre un @import entre backticks : Claude Code le traiterait comme du TEXTE LITTÉRAL
     et ne l'importerait pas (cf. doc mémoire). Le dossier s'appelle `memory` ; le `@` est seulement
     l'opérateur d'import. La ligne `@memory/MEMORY.md` ci-dessous DOIT rester sans backticks. -->
## Mémoire projet (index chargé à chaque session)
@memory/MEMORY.md

L'index `memory/MEMORY.md` (chargé à chaque session) pointe vers les fichiers thématiques
(`memory/domain.md`, `memory/architecture.md`, `memory/design.md`, `memory/features.md`), que Claude
lit **à la demande**.

## Contrats (3 faces) : où regarder
- **Fonctionnel** : les graines de feature (`assembleur-out/features/<id>-<slug>.md`) ; langage = `memory/domain.md`.
- **Technique** : `assembleur-out/technical-context.md` et `memory/architecture.md` (stack, composants, ADR, conventions).
- **Design** : `memory/design.md` (design system synchronisé + états + erreurs + a11y).

## Constitution (opposable)
`assembleur-out/pre-constitution.md` porte les **principes non négociables**. À donner à `/speckit.constitution` au
démarrage de SpecKit ; chaque `plan.md` passe ensuite la *Constitution Check*.

## Lancer SpecKit
Voir `assembleur-out/attack-plan.md` : `specify init` -> `/speckit.constitution` (depuis `assembleur-out/pre-constitution.md`) ->
`/speckit.specify` par feature **dans l'ordre du `assembleur-out/feature-map.md`** (walking skeleton d'abord) ->
`/speckit.plan` -> `/speckit.tasks` -> `/speckit.implement`.
Au `/speckit.plan` d'une feature, **relire sa graine** `assembleur-out/features/<id>-<slug>.md` (annexes
Face technique / Face design) en plus de `assembleur-out/technical-context.md` : le `spec.md` généré
ne reprend pas les annexes.

## Numérotation SpecKit : imposée (multi-développeurs)
- **Une feature = une branche = un développeur.** Le numéro `NNN-slug` est **déjà fixé** dans
  `assembleur-out/feature-map.md` (colonne "Répertoire / branche SpecKit") - c'est l'`id` du registre
  de l'architecte, pas un numéro à recalculer.
- Pour chaque feature : `git checkout -b NNN-slug`, **puis** `/speckit.specify` en fournissant
  explicitement **`SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug`**. **Ne jamais** laisser SpecKit
  auto-numéroter - deux développeurs partis de `main` collisionneraient le même numéro. Le garde-fou
  `.claude/hooks/check_speckit_alignment.py` bloque toute dérive (doublon, timestamp, numéro hors registre).
- **Claim.** Avant de démarrer `NNN`, s'assigner son ticket `Feature` Linear et le passer *In Progress* ;
  ne jamais prendre une feature déjà assignée. L'**avancement vit dans Linear** (l'application), pas dans le repo.
- **Features couplées -> en séquence.** Deux features qui écrivent le même composant/état (voir "Couplage /
  états partagés" de `assembleur-out/feature-map.md`, relations `blockedBy` Linear) se font **l'une après
  l'autre**, jamais en parallèle - SpecKit ne détecte pas les conflits de code/contrat partagé.
- **Constitution - un seul intendant.** `.specify/memory/constitution.md` n'est amendée que via
  `/speckit.constitution` (jamais à la main), par une seule personne ; **jamais** dans une branche de feature.
- **Portes de cohérence natives (optionnel).** SpecKit fournit `/speckit.clarify`, `/speckit.analyze`,
  `/speckit.checklist` - à la main de l'équipe. La séquence `/speckit.*` reste inchangée.
- **Playbook complet** de fabrication parallèle : `assembleur-out/attack-plan.md`.

## Design : non négociable
- **Le design system committé** (`designer-out/maquette-de-claude-design/`) est la **source** ; ne
  construire qu'à partir de ses **tokens et composants** - **aucune valeur de style en dur**.
- **États par écran** : chargement, vide, erreur, succès.
- **Patterns d'erreur** : le format d'erreur de l'API se projette en messages par champ.
- **Accessibilité** : au niveau visé (ex. WCAG 2.2 AA) - contraste, focus visible, clavier.

## Règles clés (invariants des 3 contrats)
- [ex. règle fonctionnelle non négociable]
- [ex. règle technique : filtrage par droits, requêtes paramétrées]
- **aucune valeur de style en dur** (tokens uniquement) ; états couverts ; erreurs selon le contrat ;
  accessibilité au niveau visé.
- **Tests écrits en même temps que le code** : toute fonction métier a son test (cas passant / échec /
  limite) dans le même changement ; intégration API/front/batch avec dépendances **mockées**. Garde-fous :
  hooks `.claude/` + pre-commit.

## Commandes
[Build / test / lint, dérivées de la stack - ex. `uv run pytest`, `npm test`.]
