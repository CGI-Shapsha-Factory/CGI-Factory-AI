---
name: assembleur-amorce
description: Amorce l'environnement de fabrication (CI, checks) et initialise Linear avec les features, après validation humaine de l'équipe.
---

# assembleur-amorce

Dernière étape de la phase convergence : **amorce l'environnement de fabrication** et
**initialise Linear**. **Porte humaine : la validation de l'équipe** (def : « l'équipe
arbitre le découpage en feature, les briefs par feature, le walking skeleton ; si
validation : initialisation de Linear avec les features définies »).

## Porte d'entrée
Le skill `assembleur` a produit le pack (`assembly.phase = "converge"`) et le rapport de
cohérence a été **validé par l'humain** (`assembly.coherence_validated = true`). Sinon,
orienter en clair vers `/assembleur:assembleur` (ou rappeler que la cohérence doit d'abord
être validée).

## Entrées
Le bloc `assembly` (faces, plan d'attaque), `assembleur-out/coherence-report.md`,
`attack-plan.md`, la `feature_sequence` (architecte) ; `references/linear-guide.md`.

## Procédure

### Étape 1 — CI & checks (génération), dont les contrôles design-sync (§6)
Écrire `<target_repo>/.github/workflows/factory-checks.yml` : câble les garde-fous
déterministes (`check_discovery.py`, `check_architecture.py`, `check_design.py`,
`check_assembly.py`) + les linters de `conventions/`. **Rendre le contrat de design opposable
(§6 spec designer)** — câbler aussi :
- une **règle de lint qui interdit les valeurs de style en dur** (couleurs/tailles/espacements
  littéraux) → **force l'usage des tokens** du design system synchronisé ;
- un **point de contrôle de revue** : l'écran implémente-t-il ses **états requis** (chargement, vide,
  erreur, succès) et ses **patterns d'erreur** ? (porté par l'agent reviewer comme un check) ;
- l'**amorçage inclut le `design-sync` initial** : exécuter `/design-sync` au démarrage du projet pour
  que le design system soit présent dès le départ.
**Génération seulement** : l'équipe commit et active. MAJ `assembly.ci_generated = true`.

### Étape 2 — Finaliser le plan d'attaque
Confirmer l'ordre des `/speckit.specify` (walking skeleton d'abord) et les features
parallélisables. **Ne pas relancer `specify init`** : le repo a été initialisé **avant** la
convergence (précondition `assembleur-init`) et la constitution convergée y est déjà en place ;
relancer init l'écraserait.

### Étape 3 — Porte humaine : l'équipe arbitre le découpage
Le **découpage en features** est le **registre canonique** `architecture.feature_sequence`
(objets `{id, ucs, name}` ; `ucs` = liste de use cases ; walking skeleton = l'`id` `001`).
Restituer en chat, **par feature** : `id` + `ucs` + nom, dépendances, et le brief
3-faces. Demander à
l'équipe d'**arbitrer** — deux issues possibles :
- **Valider tel quel** → poser `assembly.team_validated = true` (**geste humain**, jamais auto).
- **Demander un changement de découpage** (fusion / scission / réordonnancement d'une feature,
  walking skeleton différent) → **ne pas initialiser Linear** ; renvoyer vers
  `/architecte:architecte-contrat` pour **re-figer le registre**, puis `/assembleur:assembleur` pour
  **re-coudre** (un simple ajustement de brief se corrige via `/assembleur:assembleur`).
**Sans `team_validated`, ne pas toucher à Linear.**

### Étape 4 — Suivi Linear « Todo → En cours » (hook aval + filet natif)
Amorcer le **pilotage automatique du statut** (def : « statut tenu à jour automatiquement par
l'activité git ; la mise à jour au niveau de la tâche est assurée par Claude Code (Hook) »). **Génération
seulement** (l'équipe active) :
- **Hook Claude Code** : copier `templates/linear-start-hook.py` → `<target_repo>/.claude/hooks/linear-start.py`
  et fusionner `templates/claude-settings-hook.json` dans `<target_repo>/.claude/settings.json` (hook
  **`PostToolUse`** matcher `Edit|Write|MultiEdit`). À la **1re édition de code** d'une feature, le hook
  passe son issue Linear **Todo → En cours** (clé `.env`, **idempotent**, **fail-safe** — ne bloque jamais,
  n'affiche jamais la clé). Résolution via la branche + `<target_repo>/.claude/linear-map.json` (écrit par
  `init-linear`). Ajouter `.claude/.linear-started.json` au `.gitignore`.
- **Filet natif Linear** (zéro code, à documenter dans `attack-plan.md`) : connecter **GitHub↔Linear**,
  activer **PR ouverte → En cours**, **merge → Terminé**, *magic words* `Fixes <identifier>` ; couvre le
  reste du cycle et le code écrit **hors** Claude Code. Convention de branche : `<identifier>-<slug>`.

### Étape 5 — Initialisation de Linear (skill dédié)
**Ne pas écrire dans Linear ici.** L'initialisation des features dans Linear est confiée au skill
dédié **`/assembleur:init-linear`** (clé API dans `.env`, dédup d'un projet existant, défauts
**Todo/non-assigné**, carte issue↔feature, traçabilité). Une fois `assembly.team_validated` posé
(étape 3), orienter l'utilisateur :
> Étape suivante : `/assembleur:init-linear` — créer le projet et les features dans Linear.

## Porte de sortie
- CI `factory-checks.yml` généré dans le repo cible ; plan d'attaque finalisé.
- **Hook Linear** (`.claude/hooks/linear-start.py` + `settings.json`) généré dans le repo cible ; filet
  natif documenté.
- `assembly.team_validated` posé **par l'humain** (ou découpage renvoyé à l'architecte).
- L'init Linear est **déléguée** à `/assembleur:init-linear` (pas faite ici).

## Mise à jour du manifeste
- `assembly.ci_generated`, `assembly.team_validated` (**par l'humain**), `assembly.phase`.
- (L'init Linear — `linear_initialized`, `linear_issues[]`, `linear_project` — est posée par
  `/assembleur:init-linear`, pas ici.)

## Règles invariantes
- **L'équipe valide.** Le découpage n'est jamais auto-validé ; Linear n'est jamais touché
  avant `team_validated`.
- **Effets de bord maîtrisés.** L'assembleur ne lance pas `specify init` (équipe) ; le seul
  effet live est Linear, **après la porte**.
- **Marquer, ne pas inventer.** Pas de MCP Linear → fichier d'import, pas d'écriture fantôme.
- **Pas de fuite de champ** en sortie utilisateur.

Étape suivante : `/assembleur:init-linear` — créer les features dans Linear (après ta validation) ; puis l'équipe enchaîne les `/speckit.specify` selon le plan d'attaque (le repo est déjà initialisé, constitution convergée en place).
