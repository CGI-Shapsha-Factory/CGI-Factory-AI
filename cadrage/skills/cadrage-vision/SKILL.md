---
name: cadrage-vision
description: Synthétise la capture en un product brief (le quoi et le pourquoi).
---

# cadrage-vision

Deuxième étape de la ligne de production. Élève la capture brute à une vision
produit : le problème, les objectifs, le périmètre, les critères de succès. Le
quoi et le pourquoi, jamais le comment.

## Objectif

Produire un **product brief auto-portant de niveau produit**, lisible par un
comité, qui synthétise la capture sans la trahir et sans rien ajouter qui ne soit
dans la matière.

## Entrée

`factory-docs/work/capture-brute.md` et `factory-docs/work/project-frame.md`
(pour reprendre Q1 qui utilise, Q3 rôles, Q9 type de projet). Le gabarit de sortie
est `factory-docs/templates/product-brief.md` (copie installée par cadrage-init).

## Porte d'entrée

**`artifacts.capture_brute` existe** dans le manifeste (le fichier est présent).
Sinon, **refuse d'agir** et oriente vers `cadrage-extraction`.

## Procédure

1. **Lire** la capture brute, le `project-frame.md` (Q1/Q3/Q9) et le manifeste.
2. **Remplir le product brief** section par section, en n'utilisant **que** la
   matière de la capture. **Chaque énoncé porte sa source `(src: <réf>)`**
   (transcript / doc + repère) ; un énoncé sans trace reste `[À VALIDER]`.
3. **Périmètre OUT (forcé non vide).** Lister les exclusions explicites de la
   capture. S'il n'y en a pas de tracée, **proposer** des exclusions plausibles
   au regard du périmètre IN, chacune **marquée `[À VALIDER]`** comme proposition
   à confirmer. OUT ne doit jamais rester vide, mais aucune exclusion n'est
   présentée comme un fait acquis si elle n'est pas dans la source.
4. **Critères de succès produit.** Traduire les objectifs en métriques d'usage
   (pas de code). Si une cible n'a pas été captée, écrire le critère et le
   marquer `[À CHIFFRER]`.
5. **Hypothèse produit initiale.** Formuler l'hypothèse centrale et la marquer
   **`[À ÉPROUVER]`**. Ne JAMAIS l'écrire comme validée : elle se valide hors
   plugin, par le prototype (Porte 1, direction produit).
6. **Marquer les trous.** Tout élément absent de la capture → `[À VALIDER]` ou
   `[NON COUVERT EN ATELIER]`. Consolider en section Trous.
7. **Classer chaque trou** `bloquant` ou `non bloquant` (voir porte de sortie).

### Sections du product brief

Conformes à `factory-docs/templates/product-brief.md` : Problème, Objectif business,
Parties prenantes et rôles, Périmètre IN, Non-périmètre OUT (non vide),
Contraintes, Critères de succès produit, Hypothèse produit initiale `[À ÉPROUVER]`,
Trous.

## Porte de sortie

Avant d'écrire le manifeste, vérifier :
- **Toutes les sections présentes.**
- **Non-périmètre OUT non vide** (réel ou proposé `[À VALIDER]`).
- **Critères de succès mesurables ou marqués `[À CHIFFRER]`.**
- **Hypothèse produit marquée `[À ÉPROUVER]`**, jamais validée.
- **Chaque énoncé porte sa source `(src:)`** ; sinon `[À VALIDER]`.
- **Trous comptés et classés** bloquant / non bloquant.

### Trou bloquant vs non bloquant

- **Bloquant** : absence qui empêche de tenir la direction produit — pas de
  problème, pas d'objectif business, pas de partie prenante porteuse du besoin,
  périmètre IN vide.
- **Non bloquant** : détail à raffiner sans remettre en cause la direction —
  une cible `[À CHIFFRER]`, une exclusion OUT proposée `[À VALIDER]`, un acteur
  secondaire manquant.

## Réjeu incrémental (idempotence)

Rejoué sur des entrées mises à jour — typiquement une correction issue d'un
retour de démonstrateur (`cadrage-retour-demonstrateur`) — ce skill **met à
jour le product brief en place**, il ne le régénère pas à l'aveugle :
- **Préserve** le contenu déjà validé ou inchangé.
- **Applique** les corrections venues des entrées mises à jour.
- **Retire** les marqueurs résolus (`[À VALIDER]` / `[À CHIFFRER]` levés).
- **Signale les nouveaux** trous apparus.
- **N'écrase jamais en silence un élément contredit** : un acquis remis en cause
  par un retour est marqué `[REMIS EN CAUSE]` avec sa raison, puis tranché par
  l'humain — jamais supprimé ni réécrit en douce (règle « capter et invalider »).

Réconciliation par identité de section / de point : aucune duplication. Recompte
les trous et recalcule `vision_complete` à partir de l'état réconcilié.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.product_brief.status` (`draft` tant qu'il reste un trou bloquant,
  sinon `validated` reste réservé à la validation humaine — garder `draft` par
  défaut), `artifacts.product_brief.gaps = <nombre d'entrées de la section Trous>`.
- `definition_of_ready.vision_complete = true` **si et seulement si** : aucun
  trou bloquant, **ET** OUT non vide, **ET** critères de succès présents. Sinon
  `false`.
- `phase = "vision"` (si la phase courante est `extraction`).
- `validation_points[]` : ajouter les trous structurants, `status = "open"`,
  `raised_by = "vision"`.
- `updated_at` à l'horodatage courant.

## Livrable visuel

Le canvas vision produit (synthèse visuelle d'une page, lisible par un comité) se
génère dans Claude Design à partir du product brief. Le prompt prêt à coller est
dans `references/canvas-vision-prompt.md` (gabarit statique). Le prompt
effectivement utilisé est sauvegardé sous `factory-prompts/<NNN>-<JJ-MM>-canvas-vision/`
et tracé dans `prompts[]` du manifeste. C'est un livrable de communication, pas
une porte — il n'altère pas les autres champs du manifeste.

## Règles invariantes appliquées ici

- **Marquer, ne pas inventer.** OUT proposé est marqué `[À VALIDER]`, jamais
  présenté comme acté. Aucun objectif ou critère fabriqué.
- **Hypothèse à éprouver, jamais validée.** Deux altitudes de validation : la
  direction produit se valide par le prototype, hors plugin.
- **Skill indépendant.** Porte d'entrée vérifiée via le manifeste, pas via un
  orchestrateur.

Étape suivante : `/cadrage:cadrage-glossaire` — fixer le vocabulaire structurant porté par la vision avant le découpage.
