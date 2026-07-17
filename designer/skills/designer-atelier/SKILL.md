---
name: designer-atelier
description: Déroule la checklist de couverture (fondation, expérience, technique), arbitre les choix d'expérience et résout chaque point resté à traiter en session.
---

# designer-atelier

Cœur de la phase design : **un atelier de conception dirigé, pas un générateur**. Sa valeur n'est pas de
rédiger, c'est de **garantir que rien d'important n'a été oublié** avant de lancer Claude Design. Il mène
l'humain (designer ou PO) à travers **tout ce qu'un front pertinent exige**, en s'appuyant sur la checklist
**déjà pré-remplie** par `designer-ingestion`, et s'achève quand **plus aucun point n'est "à traiter"** et
que la **couverture est jugée suffisante**. **Le design system naît dans Claude Design** (pas ici) ; le
prompt est ensuite produit par `designer-prompt`.

## Objectif
Mener l'humain à travers la checklist de couverture jusqu'à ce qu'**aucun item ne reste "à traiter"**
(tout **validé** ou **sans objet**), puis capter la **couverture jugée suffisante** (geste humain).

## Entrées
- La **checklist pré-remplie** (`design.checklist`, issue de `designer-ingestion`).
- La même **matière** que l'ingestion, pour appuyer les déductions pendant le déroulé :
  `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md` (**lecture
  seule**), `architecte-out/impact-design.md`.
- Conventions : `references/interactive-loop.md`, `references/coverage-checklist-guide.md`,
  `references/states-catalog.md`, `references/question-map.md`, `references/ux-conventions.md`.

## Pré-requis (vérification silencieuse)
`designer-ingestion` a tourné : les drapeaux d'entrée `design.inputs` sont posés **et/ou** la checklist est
**pré-remplie** (des items en `deduced`). Un seul de ces signaux suffit - ne pas exiger des items déduits
(un amont maigre peut n'en produire aucun). Sinon, orienter en clair (sans nom de champ) : "les handoffs
ne sont pas encore ingérés - lance d'abord `/designer:designer-ingestion`". *(L'ingestion est mécanique et
idempotente : au moindre doute, un renvoi vers elle est sans effet de bord.)*

## Affichage des items à l'utilisateur
Chaque item de la checklist se **désigne par une phrase claire** (ex. "la palette de couleurs, l'échelle
typographique et les espacements de base"), **jamais par un code** : `F1`, `E6`, `T3` restent des **clés
internes du manifeste**, jamais montrées à l'utilisateur, jamais de colonne d'identifiants à l'écran. Le
**statut montré** se réduit à trois mots : **validé** (l'item est couvert, qu'il vienne d'un handoff ou
d'une décision humaine), **à traiter** (pas encore couvert), **sans objet** (ne s'applique pas à ce projet).
Les phrases complètes de référence sont dans `templates/coverage-checklist.md`.

## Procédure (= déroulé de l'atelier)

### Étape 1 : Dérouler la checklist par blocs (fondation -> expérience -> technique)
Pour **chaque** item encore **à traiter**, via la boucle 3-options (`references/interactive-loop.md`), une
chose à la fois, **désignée par sa phrase claire** :
- soit **déduit** d'un handoff -> en interne `deduced` (origine + source), montré **validé** ;
- soit **tranché** par l'humain -> en interne `decided` (capter sa décision, ne pas inventer), montré
  **validé** ;
- soit **sans objet** sur ce projet -> `sans_objet` (marqué, pas forcé), montré **sans objet** ;
- sinon il reste **à traiter** (non couvert) - **sans comblement**.
Rappeler, pour les items techniques, la **contrainte issue de l'architecture** à honorer (ex. le format
d'erreur API se projette en messages par champ ; l'accessibilité visée fixe contraste/focus/clavier).

### Étape 2 : Co-construction (porte humaine : arbitrage des choix d'expérience)
L'humain **tranche** les décisions de parcours, de densité, d'états vides, de feedback/confirmation et de
microcopie. **Le plugin propose et rappelle les contraintes ; il ne décide pas.** C'est la **porte 1**
(jamais automatisée).

### Étape 3 : Résoudre en session tout point resté "à traiter"
**Aucun item ne doit rester "à traiter" à la sortie de l'atelier.** Reprendre chaque point encore non
couvert **un par un**, désigné par sa **phrase claire**, via la boucle 3-options
(`references/interactive-loop.md`) : **réponse recommandée**, **alternative**, ou **réponse propre de
l'humain**. La décision est **écrite en place** dans la checklist (l'item passe à `decided` ou
`sans_objet`). Discipline "marquer, ne pas inventer" et anti-usine-à-gaz : commencer petit (tokens
essentiels, composants de base, patterns clés), ne pas créer de tokens/composants par anticipation. **On ne
clôt l'atelier que lorsque plus aucun item n'est "à traiter".**

### Clôture de l'atelier (porte humaine : couverture suffisante)
Quand **plus aucun item n'est "à traiter"** et que l'humain juge la **couverture suffisante**
(`design.coverage_sufficient = true`, **geste humain, jamais auto**), l'atelier est clos. La génération du
**prompt Claude Design** et du **rapport de couverture** revient à `designer-prompt` : **aucun fichier n'est
produit ici**.

## Porte de sortie
- Checklist déroulée : **aucun item "à traiter"** ne subsiste (tout validé ou sans objet).
- `coverage_sufficient` posé **par l'humain**.
- **Traçabilité** : chaque énoncé porte sa source `(src: cadrage | architecte | maquette | atelier)` **dans
  l'artefact** (la checklist, reprise ensuite dans le rapport). **Rien d'inventé.**

## Mise à jour du manifeste
Read-modify-write + revalidation JSON, **en silence** (ne pas narrer la mise à jour ; dire à l'utilisateur
**où l'on en est** et **la suite**) :
- `design.checklist.*[].status` -> `decided` / `sans_objet` (+ `note`) au fil des décisions.
- `design.coverage_sufficient = true` - **geste humain uniquement** (jamais auto).
- `design.phase` reste `"init"`.

## Règles invariantes
- **Proposer, ne pas décider.** L'arbitrage des choix d'expérience est humain (porte 1).
- **Marquer, ne pas inventer** ; "sans objet" plutôt que forcer.
- **Tout point se résout en session** : on ne clôt pas l'atelier tant qu'un item est "à traiter".
- **Lecture seule du cadrage** : `spec-index.md` est lu, jamais créé ni écrit (artefact du cadrage).
- **Le plugin ne génère pas le design system** (il naît dans Claude Design ; son export est committé dans
  `designer-out/maquette-de-claude-design/`).
- **Pas de fuite de champ** ni de jargon en sortie utilisateur ; **manifeste mis à jour en silence** (voir
  `references/ux-conventions.md`).

Étape suivante : `/designer:designer-prompt` - générer le prompt Claude Design et le rapport de couverture.
