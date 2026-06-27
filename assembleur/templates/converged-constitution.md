# Constitution — <PROJECT_NAME>

<!-- Format SpecKit : destiné à `.specify/memory/constitution.md`. Généré par l'assembleur en
     convergeant les 3 contrats (fonctionnel, technique, design). Remplir chaque [placeholder].
     Tout trou reste [À VALIDER]. Conserver la convention (src: …). -->

**Version :** 1.0.0
**Ratifiée le :** AAAA-MM-JJ
**Dernier amendement :** AAAA-MM-JJ

## Mission produit
[Identité produit : problème résolu + objectif métier.] (src: cadrage/product-brief §1-2)

## Principes (non négociables)

### P1 — [nom] (fonctionnel)
[Règle applicable dérivée du périmètre / hors-périmètre / langage ubiquitaire.] (src: cadrage)

### P2 — [nom] (technique)
[Règle dérivée de la stack / d'un ADR / d'une cible de qualité.] (src: architecte/ADR-00X)

### P3 — Accessibilité & design (design)
Conformité **WCAG 2.2 niveau AA** ; discipline des tokens (aucune valeur brute) ; « on fige le
système, pas les écrans ». (src: designer/accessibility, foundations)

<!-- Ajouter P4.. selon les contrats. Chaque principe : énoncé APPLICABLE (pas une intention)
     + source. Un principe sans source reste [À VALIDER]. -->

## Contraintes techniques & réglementaires
[Déploiement, authentification, intégrations, RGPD…] (src: cadrage/project-frame + architecte)

## Hors périmètre global
[Ce que le produit ne fait PAS.] (src: cadrage/product-brief §5)

## Gouvernance
- **Amendement :** [procédure de modification de la constitution].
- **Versioning :** sémantique (MAJEUR.MINEUR.CORRECTIF) ; 1.0.0 à la ratification.
- **Revue de conformité :** chaque `plan.md` passe la *Constitution Check* avant implémentation.
