---
name: designer
description: Atelier de couverture design — déroule la checklist (fondation, expérience, technique) pré-remplie par les handoffs, puis produit le prompt Claude Design et le rapport de couverture.
---

# designer

Cœur de la phase design : **un atelier de conception dirigé, pas un générateur**. Sa valeur n'est pas de
rédiger, c'est de **garantir que rien d'important n'a été oublié** avant de lancer Claude Design. Il mène
l'humain (designer ou PO) à travers **tout ce qu'un front pertinent exige**, en s'appuyant sur les
handoffs comme matière, et ne produit le **prompt** qu'à la fin, une fois la **couverture jugée
suffisante**. **Le design system naît dans Claude Design** (pas ici) ; le pont vers le code est
`/design-sync`.

## Porte d'entrée
`designer-init` a tourné (le manifeste contient le bloc `design` avec la checklist semée). Sinon, orienter
en clair vers `/designer:designer-init`.

## Entrées (matière de la checklist)
- **Cadrage (C)** : `product-brief.md` (vision, ton), `glossaire.md` (entités/données affichées),
  `spec-index.md` (**parcours / use cases**), **maquette validée** (`demonstrateur`, `client_validated`)
  comme **direction, pas cible** — le designer a autorité pour la faire évoluer.
- **Architecte (A)** : **`design-impact.md`** (section *Décisions à impact design* : stack front + style,
  contrats transverses visibles, conventions d'API qui décident les états d'UI, NFR qui se voient).
- Conventions : `references/coverage-checklist-guide.md`, `references/states-catalog.md`,
  `references/question-map.md`, `references/interactive-loop.md`, `references/ux-conventions.md`.

## Procédure (= déroulé de l'atelier)

### Étape 1 — Ingestion des handoffs & pré-remplissage
Lire les handoffs Cadrage et Architecte. **Pré-remplir la checklist** (`design.checklist`) avec ce qui en
est déductible : items d'origine **C** depuis le cadrage (parcours E1, états d'écran E2, hiérarchie E4…),
items d'origine **A** depuis `design-impact.md` (T1–T9 : erreurs, async, listes, identité/rôles,
navigation, accessibilité visée, responsive, i18n, perf ; F2 thématisation/multitenance). Chaque item
rempli passe à `status: deduced` avec sa `note`/source. Marquer `design.inputs.cadrage_ok` /
`design.inputs.design_impact_ok`.

### Étape 2 — Dérouler la checklist par blocs (fondation → expérience → technique)
Pour **chaque** item encore `open`, via la boucle 3-options (`references/interactive-loop.md`), une chose à
la fois :
- soit **déduit** d'un handoff → `deduced` (origine + source) ;
- soit **à trancher** par l'humain → `decided` (capter sa décision, ne pas inventer) ;
- soit **sans objet** sur ce projet → `sans_objet` (marqué, pas forcé) ;
- sinon il reste `open` (non couvert) — **sans comblement**.
Rappeler, pour les items techniques, la **contrainte issue de l'architecture** à honorer (ex. le format
d'erreur API se projette en messages par champ ; l'accessibilité visée fixe contraste/focus/clavier).

### Étape 3 — Co-construction (porte humaine : arbitrage des choix d'expérience)
L'humain **tranche** les décisions de parcours, densité (E4), états vides (E3), feedback/confirmation
(E5), microcopie (E6). **Le plugin propose et rappelle les contraintes ; il ne décide pas.** C'est la
**porte 1** (jamais automatisée).

### Étape 4 — Marquer ce qui reste non couvert (sans comblement)
Tout item resté `open` est listé tel quel — **rien n'est inventé**. Discipline « marquer, ne pas inventer »
et anti-usine-à-gaz : commencer petit (tokens essentiels, composants de base, patterns clés), ne pas créer
de tokens/composants par anticipation.

### Étape 5 — Générer les sorties (seulement quand la couverture est jugée suffisante)
Quand l'humain juge la **couverture suffisante** (`design.coverage_sufficient = true`, **geste humain**) :
- **Prompt Claude Design** → `factory-prompts/<NNN>-<JJ-MM>-claude-design.md` (fichier plat ; gabarit
  `templates/claude-design-prompt.md`) : fondation à produire, direction stylistique (maquette =
  inspiration, marque si présente sinon direction à poser), **stack cible**, et **consignes de discipline**
  (tous les états par composant, tous les parcours, erreurs + états vides, marquer ce qui manque). Les
  items `sans_objet` sont omis ; les items `open` restants sont listés `[À VALIDER]`, jamais comblés.
- **Rapport de couverture** → `designer-out/coverage-report.md` (gabarit `.factory/templates/coverage-report.md`).
- MAJ `design.prompt_path`, `design.coverage_report_path`, `design.phase = "atelier"`.

## Porte de sortie
- Checklist déroulée : **aucun item `open`** ne subsiste (tout `deduced`/`decided`/`sans_objet`), ou les
  rares restants sont explicitement marqués et assumés par l'humain.
- Prompt Claude Design + rapport de couverture produits ; `coverage_sufficient` posé **par l'humain**.
- **Traçabilité** : chaque énoncé porte sa source `(src: cadrage | architecte | maquette | atelier)`.
  **Rien d'inventé.**

## Règles invariantes
- **Proposer, ne pas décider.** L'arbitrage des choix d'expérience est humain (porte 1).
- **Marquer, ne pas inventer** ; « sans objet » plutôt que forcer.
- **Le plugin ne génère pas le design system** (Claude Design + `/design-sync`).
- **Pas de fuite de champ** ni de jargon en sortie utilisateur (voir `references/ux-conventions.md`).

Étape suivante : lance **Claude Design** avec le prompt produit, puis `/designer:designer-coherence` — valider le système généré et préparer le handoff.
