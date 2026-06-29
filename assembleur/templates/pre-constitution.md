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
- **Tout écran dérive du design system synchronisé** (`/design-sync`) ; **aucune valeur de style en
  dur** → on utilise les **tokens et composants**.
- **Chaque écran couvre ses états** : chargement, vide, erreur, succès.
- **Les erreurs suivent le contrat** : le format d'erreur de l'API se projette en affichage selon les
  patterns définis.
- Accessibilité au **niveau visé** (ex. WCAG 2.2 AA).

<!-- Ajouter P4.. selon les contrats. Chaque principe : énoncé APPLICABLE (pas une intention). -->

## Contraintes techniques & réglementaires
[Déploiement, authentification, intégrations, contraintes légales…]

## Hors périmètre global
[Ce que le produit ne fait PAS.]

## Gouvernance
- **Amendement :** [procédure de modification de la constitution].
- **Versioning :** sémantique (MAJEUR.MINEUR.CORRECTIF) ; 1.0.0 à la ratification.
- **Revue de conformité :** chaque `plan.md` passe la *Constitution Check* avant implémentation.
