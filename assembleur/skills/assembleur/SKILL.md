---
name: assembleur
description: Coud les 3 contrats par feature, vérifie la cohérence, et génère le pack SpecKit (constitution, CLAUDE.md, briefs 3-faces, glossaire, MEMORY.md, seeds spec.md).
---

# assembleur

Cœur de la phase convergence. **Coud les trois contrats par feature, garantit leur
cohérence, et génère le pack SpecKit consommable directement.** L'IA propose et structure ;
**l'humain tranche** — c'est le **garant de cohérence** : il vérifie que chaque feature part
avec ses **3 faces complètes et non contradictoires**.

## Porte d'entrée
`assembleur-init` a tourné (le manifeste contient le bloc `assembly` avec `target_repo`).
Sinon, orienter en clair vers `/assembleur:assembleur-init`.

## Entrées (les 3 contrats)
- **Fonctionnel (cadrage, `cadrage-out/`)** : `product-brief.md`, `glossaire.md`, `spec-index.md`
  (use cases), `features-fonctionnels-brief/*.brief.md`. *(Pas de pré-constitution : l'assembleur
  dérive lui-même la constitution convergée des fichiers bruts du cadrage — product-brief,
  project-frame, glossaire, spec-index, briefs.)*
- **Technique (architecte, `architecte-out/`)** : `tech-stack.md`, `components.md`, `standards.md`,
  `decisions/ADR-*.md`, `drivers-quality.md` (scénarios qualité QS) ; manifeste
  `architecture` (`feature_sequence`, `walking_skeleton`, `stack`).
- **Design (designer, `designer-out/`)** : `design-guidelines.md` (handoff : **réf. du design system validé/synchronisé**
  via `/design-sync` + guidelines — règles d'états, patterns d'erreur, socle a11y) + `coverage-report.md`.
  *(Le design system lui-même vit dans Claude Design ; pas de fichiers de tokens dans le repo factory.)*
- Conventions : `references/interactive-loop.md`, `references/ux-conventions.md`,
  `references/speckit-mapping.md`.

## Procédure — ordre imposé (chaque étape consomme la précédente)

### Étape 1 — Glossaire consolidé
Fusionner le langage ubiquitaire (glossaire cadrage + termes introduits par architecte/
designer), source unique, sans doublon ni contradiction. Écrire `<target_repo>/GLOSSARY.md`.
MAJ `assembly.glossary_consolidated = true`.

### Étape 2 — Couture 3-faces par feature (jointure par use case)
`architecture.feature_sequence` est le **registre canonique** : objets `{id, ucs, name}`
(`ucs` = liste de use cases ; une feature peut **bundler plusieurs use cases**). Pour
**chaque** feature (walking skeleton d'abord), joindre les 3 faces **pour chacun de ses `ucs`** :
- **face fonctionnelle** : les briefs cadrage dont `artifacts.briefs[].id ∈ ucs` (chemins `.path`) ;
- **face design** : le **design system synchronisé** (réf. `design.design_system_ref`) + les
  **guidelines** (`design-guidelines.md` : états, patterns d'erreur, socle a11y), appliqués aux
  parcours de la feature (issus du cadrage). Le design est un **contrat global** (pas un artefact par
  feature) : la face design = « les écrans de la feature dérivent du design system et suivent les guidelines » ;
- **face technique** : composants/stack/ADR que la feature touche (architecte `components.md`).
Une face n'est **complète** que si **tous** les `ucs` de la feature sont couverts. Écrire
`assembleur-out/briefs/<id>-feature.brief.md` (gabarit `templates/feature-brief-3faces.md`).
MAJ `assembly.feature_faces[]` (`{feature: <id>, ucs, functional, technical, design, coherent}`).

**Régénération idempotente (boucle de re-découpage).** Si l'équipe a re-découpé (retour
architecte → registre modifié : fusion / scission / réordonnancement), **reconcilier** avant
d'écrire : supprimer les `specs/<id>-feature/` et `briefs/<id>-feature.brief.md` dont l'`id`
**n'est plus** dans le registre courant, puis (re)générer ceux du registre. **Aucun artefact
périmé** d'un ancien découpage ne subsiste.

### Étape 3 — Rapport de cohérence (porte humaine : garant de cohérence)
Vérifier que **chaque feature part avec ses 3 faces complètes et non contradictoires**.
Contrôles :
1. **3 faces présentes** par feature du registre (fonctionnelle, technique, design).
2. **Couverture inverse** : aucun brief cadrage **orphelin** — tout `uc` couvert en amont a bien une
   feature dans `architecture.feature_sequence`. (Les parcours viennent du cadrage ; le design est un
   contrat global via le handoff.)
3. **Non-contradiction** : le design system + guidelines couvrent les composants/états requis par les
   parcours ; pas de parcours sans FR ni de FR sans parcours ; glossaire sans terme en conflit.
4. **Aucun trou bloquant** : pas de `[À VALIDER]` bloquant dans une face.
Écrire `assembleur-out/coherence-report.md` (gabarit `templates/coherence-report.md`) :
statut par feature + contradictions. **Restituer en chat** ; l'humain valide. Ne **jamais**
passer `assembly.coherence_validated` à vrai de soi-même. (Le garde-fou
`scripts/check_assembly.py` couvre les contrôles 1 et 2 ; 3 et 4 sont arbitrés par l'humain.)

### Étape 4 — Constitution finale convergée
Générer `<target_repo>/.specify/memory/constitution.md` — **remplace le gabarit posé par
`specify init`** (le repo a été initialisé avant la convergence, cf. `assembleur-init` ; bon ordre,
pas de clobber) (gabarit
`templates/converged-constitution.md`, **format SpecKit** : métadonnées, principes P1..Pn,
gouvernance) en **convergeant les principes non négociables** des 3 contrats :
fonctionnel (identité, hors-périmètre, langage), technique (stack, règles ADR, cibles
qualité, conventions, walking-skeleton-first), design (**§6 — principes non négociables, à graver**) :
- **tout écran dérive du design system synchronisé** (`/design-sync`) ; **aucune valeur de style en
  dur** → on utilise les **tokens et composants** ;
- **chaque écran couvre ses états** : chargement, vide, erreur, succès ;
- **les erreurs suivent le contrat** : le format d'erreur de l'API se projette en affichage selon les
  patterns définis (handoff design).
MAJ `assembly.constitution_generated = true`.

### Étape 5 — CLAUDE.md projet + MEMORY.md
- `<target_repo>/CLAUDE.md` (gabarit `templates/project-claude-md.md`) : section gérée entre
  `<!-- SPECKIT START -->` et `<!-- SPECKIT END -->` + guidance factory (vue d'ensemble,
  règles des 3 contrats, où vit quoi, comment lancer SpecKit, pointeurs glossaire/guidelines/
  MEMORY) + **§6 design** : instruction d'exécuter **`/design-sync` au démarrage** et de ne
  construire qu'à partir des **tokens/composants synchronisés**, la **checklist des états** à couvrir
  par écran, les **patterns d'erreur** et le **socle d'accessibilité** à respecter. MAJ
  `assembly.claude_md_generated = true`.
- `<target_repo>/MEMORY.md` (gabarit `templates/memory-index.md`) : index des 3 contrats +
  décisions (ADR + DDR) + glossaire + faces par feature. MAJ `assembly.memory_index_generated = true`.

### Étape 6 — Seeds spec.md par feature
Pour chaque feature, écrire `<target_repo>/specs/NNN-feature/spec.md` (gabarit
`templates/spec-seed.md`, **mappé sur le `spec.md` SpecKit**) : User Scenarios (P1/P2/P3,
Given/When/Then ← parcours + brief), Functional Requirements (FR-xxx), Success Criteria
(SC-xxx mesurables ← scénarios qualité + a11y), Key Entities (← glossaire), Assumptions
(trous → `NEEDS CLARIFICATION`) + annexes face technique / face design.

### Étape 7 — Guidelines
Écrire `assembleur-out/guidelines/` (gabarit `templates/review-guidelines.md`) : guidelines
de **review** par face (fonctionnelle / technique / design) + guidelines dev. MAJ
`assembly.guidelines_generated = true`.

### Étape 8 — Plan d'attaque
Écrire `assembleur-out/attack-plan.md` (gabarit `templates/attack-plan.md`) : `specify init
--ai claude` → constitution déjà fournie → `/speckit.specify` par feature **dans l'ordre des
dépendances** (walking skeleton d'abord, parallélisables signalées) → `/speckit.plan` →
`/speckit.tasks` ; + étape CI + étape Linear (gated). MAJ `assembly.attack_plan` + `phase = "converge"`.

## Porte de sortie
- Glossaire consolidé ; briefs 3-faces ; rapport de cohérence restitué ; constitution
  finale, `CLAUDE.md`, `MEMORY.md`, seeds `spec.md`, guidelines, plan d'attaque produits.
  `assembly.phase = "converge"`.
- **Traçabilité** : chaque énoncé porte sa source `(src: cadrage | architecte | designer)`.
  **Rien d'inventé** ; tout trou reste `[À VALIDER]` / `NEEDS CLARIFICATION`.

## Règles invariantes
- **Proposer, ne pas décider.** La cohérence est validée par l'humain (garant de cohérence).
- **Effets de bord gated.** Ce skill **génère** des fichiers ; il ne lance pas `specify init`
  (précondition lancée par l'équipe **avant** la convergence) ni Linear (c'est `assembleur-amorce`,
  après la porte équipe).
- **Pas de fuite de champ** en sortie utilisateur (voir `references/ux-conventions.md`).
- **Skill indépendant.** Lit/écrit le manifeste partagé.

Étape suivante : `/assembleur:assembleur-amorce` — amorcer l'environnement (CI) et initialiser Linear après validation de l'équipe.
