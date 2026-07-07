---
name: designer-atelier
description: Atelier de couverture design — déroule la checklist (fondation, expérience, technique) pré-remplie par les handoffs, puis produit le prompt Claude Design et le rapport de couverture.
---

# designer-atelier

Cœur de la phase design : **un atelier de conception dirigé, pas un générateur**. Sa valeur n'est pas de
rédiger, c'est de **garantir que rien d'important n'a été oublié** avant de lancer Claude Design. Il mène
l'humain (designer ou PO) à travers **tout ce qu'un front pertinent exige**, en s'appuyant sur les
handoffs comme matière, et ne produit le **prompt** qu'à la fin, une fois **tout point traité** et la
**couverture jugée suffisante**. **Le design system naît dans Claude Design** (pas ici) ; son export est
ensuite **committé dans `designer-out/maquette-de-claude-design/`**.

## Porte d'entrée
`designer-init` a tourné (le manifeste contient le bloc `design` avec la checklist semée). Sinon, orienter
en clair vers `/designer:designer-init`.

## Entrées (matière de la checklist)
- **Cadrage (C)** : `product-brief.md` (vision, ton), `glossaire.md` (entités/données affichées),
  `spec-index.md` (**parcours / use cases**), **maquette validée** (`demonstrateur`, `client_validated`)
  comme **direction, pas cible** — le designer a autorité pour la faire évoluer.
  > **Lecture seule.** `cadrage-out/spec-index.md` est un **artefact du cadrage** : l'atelier le **lit**
  > (parcours, use cases) pour nourrir le versant expérience, mais ne le **crée ni ne le modifie jamais**.
- **Architecte (A)** : **`design-impact.md`** (section *Décisions à impact design* : stack front + style,
  contrats transverses visibles, conventions d'API qui décident les états d'UI, NFR qui se voient).
- Conventions : `references/coverage-checklist-guide.md`, `references/states-catalog.md`,
  `references/question-map.md`, `references/interactive-loop.md`, `references/ux-conventions.md`.

## Affichage des items à l'utilisateur
Chaque item de la checklist se **désigne par une phrase claire** (ex. « la palette de couleurs, l'échelle
typographique et les espacements de base »), **jamais par un code** : `F1`, `E6`, `T3` restent des **clés
internes du manifeste**, jamais montrées à l'utilisateur, jamais de colonne d'identifiants à l'écran. Le
**statut montré** se réduit à trois mots : **validé** (l'item est couvert, qu'il vienne d'un handoff ou
d'une décision humaine), **à traiter** (pas encore couvert), **sans objet** (ne s'applique pas à ce projet).
Les phrases complètes de référence sont dans `templates/coverage-checklist.md`.

## Procédure (= déroulé de l'atelier)

### Étape 1 — Ingestion des handoffs (lecture parallèle) & pré-remplissage
**Toujours (re)lire les handoffs depuis les fichiers committés**, même si tu crois les avoir déjà lus plus
tôt dans cette session — **ne jamais** t'appuyer sur la mémoire du chat (exécution reproductible par
n'importe qui). **Lire tous les handoffs pertinents, en parallèle, pour ne rien manquer.** Dispatcher des sous-agents
lecteurs (`agentType: "designer-reader"`), **un par lot**, chacun avec un **schéma de sortie structuré**,
en **un seul message** (appels parallèles), puis synthétiser. Lots :
1. **Cadrage** — `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`.
   Extraire : ton/vision, entités/données affichées, parcours / use cases, états d'écran impliqués.
2. **Architecte** — `architecte-out/design-impact.md`. Extraire : stack front + style, contrats
   transverses visibles, conventions d'API → états d'UI, NFR qui se voient (a11y, responsive, i18n, perf).

*(Garde simple : entrée minuscule → un seul lecteur ; sinon fan-out.)* **Passe de complétude** : vérifier
qu'aucun élément des handoffs n'a été manqué avant de pré-remplir.

**Pré-remplir la checklist** (`design.checklist`) depuis les retours structurés : items d'origine **C**
(parcours, états d'écran, hiérarchie…), items d'origine **A** depuis `design-impact.md` (erreurs, async,
listes, identité/rôles, navigation, accessibilité visée, responsive, i18n, perf ; thématisation). Chaque
item ainsi rempli passe en interne à `status: deduced` (montré **validé**) avec sa `note`. Marquer
`design.inputs.cadrage_ok` / `design.inputs.design_impact_ok`. Le pré-remplissage suit
`references/question-map.md`.

### Étape 2 — Dérouler la checklist par blocs (fondation → expérience → technique)
Pour **chaque** item encore **à traiter**, via la boucle 3-options (`references/interactive-loop.md`), une
chose à la fois, **désignée par sa phrase claire** :
- soit **déduit** d'un handoff → en interne `deduced` (origine + source), montré **validé** ;
- soit **tranché** par l'humain → en interne `decided` (capter sa décision, ne pas inventer), montré
  **validé** ;
- soit **sans objet** sur ce projet → `sans_objet` (marqué, pas forcé), montré **sans objet** ;
- sinon il reste **à traiter** (non couvert) — **sans comblement**.
Rappeler, pour les items techniques, la **contrainte issue de l'architecture** à honorer (ex. le format
d'erreur API se projette en messages par champ ; l'accessibilité visée fixe contraste/focus/clavier).

### Étape 3 — Co-construction (porte humaine : arbitrage des choix d'expérience)
L'humain **tranche** les décisions de parcours, de densité, d'états vides, de feedback/confirmation et de
microcopie. **Le plugin propose et rappelle les contraintes ; il ne décide pas.** C'est la **porte 1**
(jamais automatisée).

### Étape 4 — Résoudre en session tout point resté « à traiter » (avant toute génération)
**Aucun item ne doit rester « à traiter » à la sortie de l'atelier.** Reprendre chaque point encore non
couvert **un par un**, désigné par sa **phrase claire**, via la boucle 3-options
(`references/interactive-loop.md`) : **réponse recommandée**, **alternative**, ou **réponse propre de
l'humain**. La décision est **écrite en place** dans la checklist (l'item passe à `decided` ou
`sans_objet`). Discipline « marquer, ne pas inventer » et anti-usine-à-gaz : commencer petit (tokens
essentiels, composants de base, patterns clés), ne pas créer de tokens/composants par anticipation. **On ne
passe à l'étape 5 que lorsque plus aucun item n'est « à traiter ».**

### Étape 5 — Générer les sorties (seulement quand plus rien n'est « à traiter »)
Quand tout est traité et que l'humain juge la **couverture suffisante** (`design.coverage_sufficient =
true`, **geste humain**) :
- **Prompt Claude Design** → `designer-out/prompts/<NNN>-<JJ-MM>-claude-design.md` (fichier plat ; gabarit
  `templates/claude-design-prompt.md`) : fondation à produire, direction stylistique (maquette =
  inspiration, marque si présente sinon direction à poser), **stack cible**, et **consignes de discipline**
  (tous les états par composant, tous les parcours, erreurs + états vides, marquer ce qui manque). Les items
  **sans objet** sont omis. **Aucun `[À VALIDER]` n'est émis** : tous les points ayant été résolus en
  session à l'étape 4, le prompt ne contient que des décisions actées.
  > **Le fichier sauvegardé ne contient que le corps du prompt prêt à coller** (le bloc de code rempli du
  > gabarit) : **pas de titre H1, pas de note en blockquote, pas de métadonnée, pas de pied de page**. La
  > métadonnée (sujet, date, version) vit dans l'entrée `prompts[]` du manifeste, **jamais** dans le
  > fichier. Voir `references/ux-conventions.md` §3bis.
- **Rapport de couverture** → `designer-out/coverage-report.md` (gabarit `.factory/templates/coverage-report.md`).
- MAJ `design.prompt_path`, `design.coverage_report_path`, `design.phase = "atelier"` **en silence** (ne pas
  narrer la mise à jour du manifeste ; dire à l'utilisateur **ce qui a été produit** et **la suite**).

## Porte de sortie
- Checklist déroulée : **aucun item « à traiter »** ne subsiste (tout validé ou sans objet).
- Prompt Claude Design + rapport de couverture produits ; `coverage_sufficient` posé **par l'humain**.
- **Traçabilité** : chaque énoncé porte sa source `(src: cadrage | architecte | maquette | atelier)` **dans
  l'artefact** (jamais dans le prompt sauvegardé). **Rien d'inventé.**

## Règles invariantes
- **Proposer, ne pas décider.** L'arbitrage des choix d'expérience est humain (porte 1).
- **Marquer, ne pas inventer** ; « sans objet » plutôt que forcer.
- **Tout point se résout en session** : on ne génère pas le prompt tant qu'un item est « à traiter ».
- **Lecture seule du cadrage** : `spec-index.md` est lu, jamais créé ni écrit (artefact du cadrage).
- **Le plugin ne génère pas le design system** (il naît dans Claude Design ; son export est committé dans
  `designer-out/maquette-de-claude-design/`).
- **Pas de fuite de champ** ni de jargon en sortie utilisateur ; **manifeste mis à jour en silence** (voir
  `references/ux-conventions.md`).

Étape suivante : lance **Claude Design** avec le prompt produit, **dépose l'export dans
`designer-out/maquette-de-claude-design/`** (dossier ou ZIP), puis `/designer:designer-coherence` —
valider le système généré et préparer le handoff.
