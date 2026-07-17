# Fabrication en parallèle : coordination d'équipe autour de SpecKit

Référence lue par les skills de l'assembleur (et distillée dans `attack-plan.md`, le `CLAUDE.md`
projet, `feature-map.md`). Elle **consolide** les règles de fabrication à plusieurs développeurs,
autrement dispersées dans `speckit-mapping.md`, `linear-guide.md`, `feature-map.md`, `attack-plan.md`
et les garde-fous. Contenu seul.

## Principe : une couche *autour* de SpecKit (jamais de réécriture)
La Factory **n'ajoute pas d'instructions dans SpecKit** : elle pose une **couche de coordination
d'équipe autour** de lui.
- On n'écrit **jamais** dans `.specify/`, on ne modifie **aucune** commande `/speckit.*` ni sa séquence,
  on n'injecte rien dans les skills/commandes SpecKit.
- On **s'adapte** aux mécanismes natifs : l'override `SPECIFY_FEATURE_DIRECTORY` (honoré par
  `/speckit.specify`, chemin résolu persisté dans `.specify/feature.json`), `.specify/init-options.json`
  (`feature_numbering`), et le garde-fou d'alignement.
- Les commandes SpecKit natives sont **citées en rappel optionnel**, jamais insérées comme étapes.

## Le problème que SpecKit ne résout pas seul
SpecKit est **centré sur un développeur unique** ; ses docs sont muettes sur l'équipe.
- **Collision de numéro.** `/speckit.specify` (via `create-new-feature.sh`) calcule `NNN` en scannant le
  `specs/` **local** : deux développeurs partis de `main` obtiennent **le même numéro** -> collision au
  merge.
- **Pas de détection de conflit inter-spec.** SpecKit isole les *documents* par feature (`specs/NNN/`)
  mais **ne vérifie pas** que deux features touchant le **même code/contrat** restent compatibles.
- **Fichiers partagés.** `.specify/` (constitution, templates, scripts) est commun à toutes les
  features : édité en parallèle, il entre en conflit.

## Ce que la Factory garantit déjà (acquis : ne pas défaire)
- **Numérotation gelée.** `NNN` = `id` du registre `architecture.feature_sequence` (figé à l'init
  Linear). Imposée via `SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug` ; **jamais** d'auto-numérotation.
  Timestamp **banni** (l'attribution des coûts et la sync Linear lisent `^\d{3}-`). Garde-fou
  `check_speckit_alignment.py` (doublon / timestamp / numéro hors registre = échec). Voir
  `speckit-mapping.md`.
- **Linear = source de vérité de l'avancement.** Les sous-tickets **par phase** (`creation-task-linear`)
  et l'**état** (`update-issue-linear`) vivent **dans Linear**, jamais dans `manifest.json` committé -
  pas de conflit de merge sur l'état. Voir `linear-guide.md`.
- **Artefacts amont figés** une fois (constitution, `.claude/CLAUDE.md`, `memory/`) - jamais régénérés
  par feature.

## Les règles (par sujet)

**1. Une feature = une branche = un développeur.** `git checkout -b NNN-slug` (le `NNN-slug` du
registre). Le répertoire `specs/NNN-slug/` est **parallèle-safe** : isolé, il n'entre pas en conflit.

**2. Claim avant de démarrer.** S'assigner le ticket `Feature` Linear et le passer *In Progress* ; ne
jamais prendre une feature déjà assignée.

**3. Suivi dans Linear.** L'avancement s'écrit **dans Linear**, jamais dans le manifeste committé.

**4. Couplage & code partagé -> en séquence.** Les features qui écrivent le **même composant/état** (table
"Couplage / états partagés" de `feature-map.md`, relations `blockedBy` Linear) se traitent **l'une
après l'autre**. SpecKit ne détecte pas ces conflits : **assigner des zones de code disjointes**.

**5. `.specify/` partagé = point chaud.** Constitution, templates, scripts, `init-options.json` :
**ne jamais les éditer dans une branche de feature**.

**6. Constitution - un seul intendant.** On **respecte le modèle SpecKit** : amendée uniquement via
`/speckit.constitution` (jamais à la main), par **une seule** personne ; versionnée par SpecKit
(MAJOR/MINOR/PATCH + *Sync Impact Report*). Lancée **une fois** depuis `pre-constitution.md`, puis
`.specify/memory/constitution.md` est committé ; **jamais** modifiée en branche de feature.

**7. Portes de cohérence natives (optionnel - on ne réordonne rien).** SpecKit fournit `/speckit.clarify`
(lever les ambiguïtés), `/speckit.analyze` (cohérence spec <-> plan <-> tasks) et `/speckit.checklist`. À la
main de l'équipe, en complément - **jamais** insérées de force dans la séquence, jamais redéfinies.

**8. Intégration / merge.** Wrapper git/Linear/Factory (ne touche pas SpecKit) :
- le **walking skeleton** (`001`) est mergé **en premier** (dé-risque la stack pour tous) ;
- **avant la PR** : `/assembleur:revue-gemini` (consultatif) + `python .claude/hooks/check_speckit_alignment.py check` ;
- **committer `specs/NNN-slug/` avec le code** (la spec voyage avec l'implémentation) ;
- **rebase sur `main`** avant le merge (historique linéaire ; révèle tôt une dérive sur `.specify/`) ;
- **après le merge** : supprimer la branche + `/assembleur:update-issue-linear`.
- La **protection de branche** (PR obligatoire, revue, CI verte, pas de force-push) est un **ruleset
  GitHub côté serveur** - hors périmètre Factory, seul garde-fou multi-personnes non contournable.

## À ne pas faire
- Laisser SpecKit **auto-numéroter** (ou numéroter par timestamp).
- Lancer `/speckit.specify` **sur `main`** (toujours sur la branche `NNN-slug`).
- Éditer la **constitution** (ou tout `.specify/` partagé) **dans une branche de feature**.
- Écrire l'**avancement** dans `manifest.json` (il vit dans Linear).
- Prendre une feature **déjà claim**.
- **Paralléliser** deux features qui écrivent le même composant.
- **Modifier** une commande `/speckit.*` ou un fichier généré sous `.specify/`.

## Où ces règles sont distillées
- `attack-plan.md` (playbook que l'équipe exécute) - §3 boucle par feature, §4 règles multi-dev, §5
  intégration, §6 constitution, §7 anti-patterns.
- `project-claude-md.md` -> `.claude/CLAUDE.md` du projet - rappel imposé.
- `feature-map.md` - couplage / états partagés + `blockedBy`.
- `linear-guide.md` - Linear source de vérité ; `speckit-mapping.md` - numérotation.
