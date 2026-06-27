---
name: architecte-coherence
description: Valide la cohérence du contrat technique et prépare le passage à l'assembleur.
---

# architecte-coherence

Dernière étape de la phase technique : la **porte de validation de cohérence** (def :
« la porte humaine est l'arbitrage des ADR, puis la validation de cohérence »).
Vérifie que le contrat technique tient ensemble, sans contradiction ni trou, avant
de passer le relais à l'assembleur.

## Porte d'entrée
Le skill `architecte` a produit le contrat (`architecture.phase = "contrat"`).
Sinon, orienter en clair vers `/architecte:architecte`.

## Entrées
Les artefacts d'architecture dans `factory-docs/work/` : `drivers-quality.md`,
`components.md`, `tech-stack.md`, `standards.md`, `decisions/ADR-*.md`,
`diagrams.md`, `risks.md`, `design-impact.md` ; le dossier `conventions/` ; les
briefs `*.brief.md` ; le manifeste.

## Contrôles de cohérence
1. **Composants ↔ stack** : chaque composant de `components.md` a une ligne dans la
   matrice de `tech-stack.md` (et inversement). Aucun composant orphelin.
2. **Drivers ↔ ADR** : chaque driver prioritaire est adressé par au moins un ADR ou
   une décision tracée.
3. **Use cases ↔ features numérotées** : chaque use case du `spec-index.md` est
   couvert par une feature de la séquence numérotée (`architecture.feature_sequence`).
4. **Diagrammes ↔ réel** : les diagrammes référencent les vrais composants/stores
   (pas de placeholder résiduel).
5. **Conventions ↔ stack** : chaque langage retenu a son fichier de conventions dans
   `conventions/` (ou un fallback `.editorconfig` + avertissement assumé).
6. **Aucun trou bloquant** : pas de `[À VALIDER]` bloquant ouvert ; toutes les
   réponses structurantes sont présentes.
7. **Walking skeleton** désigné et cohérent avec les dépendances.
8. **Décisions à impact design** (handoff designer) : `design-impact.md` est produit et couvre la
   tranche qui se voit — stack front + approche de style, contrats transverses visibles, conventions
   d'API qui décident des états d'UI, NFR qui touchent l'UX. Sans cette section, le designer ne peut pas
   pré-remplir son versant technique.

Garde-fou déterministe : lancer `scripts/check_architecture.py` sur le manifeste —
il échoue si une réponse bloquante manque, si un langage retenu n'a pas son fichier
de conventions, ou si la section `Décisions à impact design` n'est pas produite.

## Sortie
- Un **rapport de cohérence** `factory-docs/work/coherence-report.md` : statut par
  contrôle (atteint / non atteint) avec la raison, et la liste de ce qui manque
  (actionnable, relié à l'étape/skill qui le résout).
- Affichage en chat d'un **tableau de synthèse** (cohérent / à corriger / manquant).
- **Porte humaine** : l'architecte **valide** la cohérence (geste humain). Le skill
  ne passe **jamais** `architecture.coherence_validated` à vrai de lui-même ; il le
  propose, l'humain confirme. Verdict honnête : pas de vert tant qu'un contrôle échoue.

## Mise à jour du manifeste
- `architecture.phase = "valide"` une fois la validation humaine actée.
- `architecture.coherence_validated` passé à vrai **par l'humain** uniquement.

## Handoff (vers l'assembleur)
Une fois validé, le contrat technique prêt à transmettre comprend : les ADR et
contrats transverses, les normes (`standards.md` + `conventions/`), les diagrammes,
le walking skeleton et la **séquence de features numérotée** (convergence des deux
découpages), le registre de risques, et les **Décisions à impact design**
(`design-impact.md`, consommées par le designer). (L'assembleur coud ensuite ces
contrats par feature, une fois le contrat de design figé.)

## Règles invariantes
- **L'humain valide.** La cohérence n'est jamais auto-validée par l'IA.
- **Refléter l'état réel.** Aucun contrôle maquillé ; un échec reste un échec.
- **Pas de fuite de champ** en sortie utilisateur (voir `references/ux-conventions.md`).

Étape suivante : `/designer:designer-init` — démarrer le contrat de design (la phase design exige le cadrage ET l'architecture validés). Ou corriger d'abord les points signalés via `/architecte:architecte`.
