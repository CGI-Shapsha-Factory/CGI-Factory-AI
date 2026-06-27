---
name: designer-coherence
description: Valide la couverture du contrat de design (parcours + états) et prépare le passage à l'assembleur.
---

# designer-coherence

Dernière étape de la phase design : la **porte de validation de couverture** (def : « la
porte humaine est l'arbitrage du designer, puis la validation de couverture des parcours
et des états »). Vérifie que le contrat de design tient ensemble, sans trou, avant de
passer le relais à l'assembleur.

## Porte d'entrée
Le skill `designer` a produit le contrat (`design.phase = "contrat"`). Sinon, orienter en
clair vers `/designer:designer`.

## Entrées
Les artefacts de design dans `factory-docs/work/` : `design-principles.md`,
`foundations.md`, `design-components.md`, `states-and-patterns.md`, `journeys.md`,
`accessibility.md`, `design-decisions/DDR-*.md` ; le dossier `design-system/` (tokens DTCG
+ config de livraison) ; le `spec-index.md` du cadrage ; le manifeste.

## Contrôles de cohérence
1. **Tokens ↔ fondations** : chaque fondation (couleur, typo, espacement, élévation,
   mouvement) est matérialisée en tokens DTCG ; **aucune valeur brute codée en dur** dans
   `design-components.md` (tout référence un token).
2. **Composants ↔ maquette** : chaque composant visible dans la maquette validée a un
   contrat dans `design-components.md` ; aucun composant orphelin.
3. **Couverture des états** : chaque composant interactif a ses états requis définis
   (default/hover/focus/active/disabled + loading/empty/error là où c'est pertinent) ; les
   états canoniques d'écran sont couverts.
4. **Couverture des parcours** : **chaque** use case du `spec-index.md` est couvert par un
   parcours de `journeys.md` (couverture **complète** — pas seulement le MVP).
5. **Tokens ↔ stack** : le format de livraison est cohérent avec le front-end de
   l'architecte ; `design-system/` contient les fichiers de tokens exécutables (DTCG) + la
   config de livraison (ou un fallback variables CSS + avertissement assumé).
6. **Accessibilité** : cibles WCAG 2.2 AA présentes et cohérentes (paires de contraste
   définies pour les tokens de couleur sémantiques ; modèle focus/clavier par composant).
7. **Aucun trou bloquant** : pas de `[À VALIDER]` bloquant ouvert.

Garde-fou déterministe : lancer `scripts/check_design.py` sur le manifeste — il échoue si
une entrée structurante manque (maquette, tokens, composants & états, parcours, alignement
stack, accessibilité).

## Sortie
- Un **rapport de couverture** `factory-docs/work/coherence-report.md` : statut par
  contrôle (atteint / non atteint) avec la raison, et la liste de ce qui manque
  (actionnable, relié à l'étape/skill qui le résout).
- Affichage en chat d'un **tableau de synthèse** (couvert / à corriger / manquant).
- **Porte humaine** : le designer **valide** la couverture (geste humain). Le skill ne
  passe **jamais** `design.coverage_validated` à vrai de lui-même ; il le propose, l'humain
  confirme. Verdict honnête : pas de vert tant qu'un contrôle échoue.

## Mise à jour du manifeste
- `design.phase = "valide"` une fois la validation humaine actée.
- `design.coverage_validated` passé à vrai **par l'humain** uniquement.

## Handoff (vers l'assembleur)
Une fois validé, le contrat de design prêt à transmettre comprend : les principes, les
**tokens DTCG exécutables** (`design-system/`) + leur format de livraison, les fondations,
les contrats de composants & leurs états, les patterns, les parcours couvrant les use
cases, le contrat d'accessibilité, et les DDR. (L'assembleur coud ces contrats par
feature.)

## Règles invariantes
- **L'humain valide.** La couverture n'est jamais auto-validée par l'IA.
- **Refléter l'état réel.** Aucun contrôle maquillé ; un échec reste un échec.
- **Pas de fuite de champ** en sortie utilisateur (voir `references/ux-conventions.md`).

Étape suivante : `/assembleur:assembleur-init` — démarrer la convergence des 3 contrats (fonctionnel, technique, design) puis l'amorçage du repo SpecKit. Ou corriger d'abord les points signalés via `/designer:designer`.
