# Plan d'attaque : fabrication SpecKit

> Livré en `assembleur-out/attack-plan.md`. **L'équipe l'exécute** : l'assembleur ne lance pas
> SpecKit, il fournit le paquet. Contenu seul (aucune provenance).

## 0. Mettre le paquet en place
- `CLAUDE.md` et `memory/` sont **déjà déployés dans `.claude/`** par la convergence - actifs sans
  copie manuelle. Le reste du paquet (constitution, graines, carte des features, contexte technique)
  reste dans `assembleur-out/` et sert de matière aux `/speckit.*`.
- Initialiser SpecKit : `specify init --here --integration claude` dans le repo (automatisable via
  `/assembleur:install-speckit` - installe `uv`/le CLI et joue `specify init` sans manip).

## 1. Constitution
`/speckit.constitution` en fournissant `pre-constitution.md` - les principes non négociables sont déjà
rédigés ; il ne reste qu'à les graver.

## 2. Séquence des features (ordre des dépendances)
| Ordre | Feature | Walking skeleton | Parallélisable | Dépend de |
|-------|---------|------------------|----------------|-----------|
| 1 | 001 - [..] | oui | non | - |
| 2 | 002 - [..] | non | [oui/non] | 001 |

> Ordre et couplage : voir `feature-map.md`. Le **walking skeleton** (001) d'abord.

> **Spikes / dé-risquage (avant ou pendant 001).** [Depuis le registre de risques architecte :
> risque -> spike/POC -> critère de levée.] Le walking skeleton (001) dé-risque la stack ; les spikes
> ciblent les risques résiduels avant de s'engager.

## 3. Par feature (numérotation canonique `NNN-slug`, une branche = une feature = un développeur)
Prendre `NNN-slug` dans `feature-map.md` (colonne "Répertoire / branche SpecKit") - c'est l'`id` du
registre de l'architecte, **jamais** un numéro auto-généré. Enchaîner :

1. **Claim** : s'assigner le ticket `Feature` Linear de `NNN` et le passer *In Progress* (ne jamais
   prendre une feature déjà assignée).
2. `git checkout main && git pull` puis **`git checkout -b NNN-slug`**.
3. **`/speckit.specify`** en fournissant explicitement **`SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug`**
   (+ la matière de la graine `features/NNN-slug.md`). Ceci fige le répertoire **et** le numéro :
   pas d'auto-numérotation, donc pas de collision entre développeurs.
4. `/speckit.plan` (Technical Context dans `technical-context.md` ; **relire aussi la graine**
   `features/NNN-slug.md` : ses annexes Face technique / Face design portent les composants, ADR
   et écrans propres à la feature, que le `spec.md` généré ne reprend pas) -> `/speckit.tasks` ->
   **`/assembleur:creation-tasks-linear`** (un sous-ticket `Task` par phase, rattaché au ticket
   `Feature`) -> `/speckit.implement`.

> Le numéro `NNN` = l'`id` du registre ; `SPECIFY_FEATURE_DIRECTORY` fige le répertoire, la branche fige
> l'attribution des coûts et le recoupement Linear. Le garde-fou `.claude/hooks/check_speckit_alignment.py`
> vérifie l'alignement à chaque édition d'un `spec.md`, et en CI (`python .claude/hooks/check_speckit_alignment.py check`).

> **Rappel (optionnel, natif SpecKit).** En complément, SpecKit fournit `/speckit.clarify` (après
> `specify`, pour lever les ambiguïtés), `/speckit.analyze` (avant `implement`, cohérence
> spec <-> plan <-> tasks) et `/speckit.checklist`. À la main de l'équipe - la séquence `/speckit.*` reste
> inchangée.

## 4. Règles multi-développeurs
- **Numérotation** : `NNN` vient **toujours** de `feature-map.md` ; jamais d'auto-numérotation SpecKit
  (sinon deux devs partis de `main` produisent le même numéro). Le timestamp est **banni** (l'attribution
  des coûts et la sync Linear lisent `^\d{3}-`).
- **Suivi dans Linear** : l'avancement (sous-tickets de phase, état des tickets) vit **directement dans
  Linear** (l'application), **pas** dans le manifeste committé - pas de conflit de merge sur `manifest.json`.
- **Composants partagés** : les features en **écriture concurrente** sur un même composant (voir la table
  "Couplage / états partagés" de `feature-map.md`, et les relations `blockedBy` dans Linear) se font
  **en séquence**, pas en parallèle.
- **Artefacts figés en amont** : `/speckit.constitution` (depuis `pre-constitution.md`) se lance **une
  seule fois** puis on **committe** `.specify/memory/constitution.md` ; `CLAUDE.md` + `memory/` sont déjà
  déployés et committés par la convergence. **Ne pas les régénérer** par feature/branche.

## 5. Intégration / merge (wrapper git/Linear : ne touche pas SpecKit)
- **Walking skeleton d'abord.** La feature `001` est mergée en premier : elle dé-risque la stack pour
  toutes les suivantes.
- **Avant la PR** : lancer `/assembleur:revue-gemini` (revue externe consultative) **et** le garde-fou
  `python .claude/hooks/check_speckit_alignment.py check`.
- **Committer `specs/NNN-slug/` avec le code** : la spec voyage avec l'implémentation.
- **Rebase sur `main`** avant le merge (historique linéaire ; révèle tôt une dérive sur un fichier
  partagé de `.specify/`).
- **Après le merge** : supprimer la branche, puis `/assembleur:update-issue-linear` (état du ticket).
- La **protection de branche** (PR obligatoire, revue, CI verte, pas de force-push) est un **ruleset
  GitHub côté serveur** - le seul garde-fou multi-personnes non contournable.

## 6. Constitution : un seul intendant
`/speckit.constitution` (depuis `pre-constitution.md`) se lance **une fois** ; ensuite la constitution
n'est amendée **que** via `/speckit.constitution`, par **une seule** personne, **jamais** à la main ni
dans une branche de feature (fichier partagé = point chaud de merge). SpecKit la versionne
(MAJOR/MINOR/PATCH + *Sync Impact Report*).

## 7. À ne pas faire
- Laisser SpecKit **auto-numéroter** (ou numéroter par timestamp).
- Lancer `/speckit.specify` **sur `main`** (toujours sur la branche `NNN-slug`).
- Éditer la **constitution** ou tout `.specify/` partagé **dans une branche de feature**.
- Écrire l'**avancement** dans `manifest.json` (il vit dans Linear).
- Prendre une feature **déjà assignée**.
- **Paralléliser** deux features qui écrivent le même composant (voir §4 "Composants partagés").
