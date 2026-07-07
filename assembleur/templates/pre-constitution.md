# Constitution — <PROJECT_NAME>

<!-- Pré-constitution : livrable de `assembleur-out/`, au FORMAT du constitution.md SpecKit.
     L'équipe la donne à `/speckit.constitution` (l'assembleur n'écrit PAS dans .specify/).
     Contenu seul : aucune provenance, aucun horodatage, aucun nom de personne. Tout point
     manquant se tranche EN SESSION (on pose la question, on écrit la réponse en place) —
     jamais laissé en marqueur. -->

**Version :** 1.0.0
**Ratifiée le :** AAAA-MM-JJ
**Dernier amendement :** AAAA-MM-JJ

## Mission produit
[Identité produit : problème résolu + objectif métier, en une à deux phrases.]

## Principes (non négociables)

### P1 — [nom] (fonctionnel)
[Règle APPLICABLE dérivée du périmètre / hors-périmètre / langage ubiquitaire.]

### P2 — [nom] (technique)
[Règle dérivée de la stack / d'un ADR / d'une cible de qualité.]

### P3 — Design system opposable (design, non négociable)
- **Tout écran dérive de l'export committé du design system** (dans
  `designer-out/maquette-de-claude-design/`) ; **aucune valeur de style en dur** →
  on utilise les **tokens et composants**.
- **Chaque écran couvre ses états** : chargement, vide, erreur, succès.
- **Les erreurs suivent le contrat** : le format d'erreur de l'API se projette en affichage selon les
  patterns définis.
- Accessibilité au **niveau visé** (ex. WCAG 2.2 AA).

### P4 — Tests écrits avec le code (non négociable)
- **Tout code métier a son test dans le même changement** : dès qu'une fonction est écrite, son test
  l'est aussi (**cas passant / échec / limite**). Aucune source ne part sans test.
- **Intégration des composants** (API, front, batch) avec **dépendances externes mockées** ; le front
  simule les interactions utilisateur et mocke les appels d'API.
- **Appliqué de façon déterministe** : hooks Claude Code (`Stop`/`PostToolUse`) + pre-commit + **un check
  CI diff-coverage requis** (couverture des lignes modifiées) — *required status check* non contournable.

<!-- Ajouter P5.. selon les contrats. Chaque principe : énoncé APPLICABLE (pas une intention). -->

## Contraintes techniques & réglementaires
[Déploiement, authentification, intégrations, contraintes légales…]

## Hors périmètre global
[Ce que le produit ne fait PAS.]

## Gouvernance
- **Amendement :** [procédure de modification de la constitution].
- **Versioning :** sémantique (MAJEUR.MINEUR.CORRECTIF) ; 1.0.0 à la ratification.
- **Revue de conformité :** chaque `plan.md` passe la *Constitution Check* avant implémentation.
