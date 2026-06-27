---
name: help-factory
description: Montre la carte complète de la Factory — les 4 plugins (cadrage, architecte, designer, assembleur), leurs skills, l'ordre et les portes humaines.
---

# help-factory

Skill d'aide. Quand il est invoqué, **affiche à l'utilisateur le guide ci-dessous en
français, en bullet points** (sans noms de champs techniques). Il n'écrit aucun fichier et
ne modifie aucun manifeste. Pour le détail de la phase amont, voir `/cadrage:help-cadrage`.

## Guide à afficher

**La Factory IA transforme un atelier en projet spec-driven, en 4 phases. Chaque phase est
un plugin qui produit un *contrat* validé par un humain, puis passe le relais. Ordre global :
cadrage → architecte → designer → assembleur → SpecKit.**

- **Phase 1 — `cadrage` (contrat fonctionnel)** — de la matière brute (transcripts, docs) au
  pack fonctionnel : vision, glossaire, découpage en use cases, maquette validée, briefs,
  pré-constitution.
  - Skills, dans l'ordre : `cadrage-init` → `cadrage-extraction` → `cadrage-vision` →
    `cadrage-glossaire` → `cadrage-decoupage` → boucle maquette (`cadrage-demonstrateur-brief`
    → `cadrage-retour-demonstrateur` → `cadrage-clarification`) → revue de couplage →
    `cadrage-briefs` → `cadrage-completude` → `cadrage-handoff`. *Détail : `/cadrage:help-cadrage`.*
  - Tu tranches : l'arbitrage du découpage, et la validation de la maquette par le client.
  - → mène à la phase 2.
- **Phase 2 — `architecte` (contrat technique)** — transforme le besoin fonctionnel en cadre
  technique : drivers & attributs de qualité, composants, stack, décisions (ADR), walking
  skeleton, conventions/linters, diagrammes ; fige la **séquence numérotée des features**.
  - Skills : `architecte-init` → `architecte` → `architecte-coherence`.
  - Tu tranches : l'arbitrage des ADR, puis la validation de cohérence du contrat technique.
  - → mène à la phase 3.
- **Phase 3 — `designer` (contrat de design)** — distille la maquette validée en un design
  system exécutable : tokens DTCG, fondations, composants & états, parcours, accessibilité
  WCAG 2.2 — cohérent avec la stack de l'architecte. *Il fige le système, pas les écrans.*
  - Skills : `designer-init` → `designer` → `designer-coherence`.
  - Tu tranches : l'arbitrage du designer, puis la validation de couverture (parcours + états).
  - → mène à la phase 4.
- **Phase 4 — `assembleur` (convergence → SpecKit)** — coud les 3 contrats par feature, vérifie
  leur cohérence, puis amorce un repo SpecKit prêt à fabriquer : constitution finale convergée,
  briefs 3-faces, glossaire consolidé, seeds de specs, CI — et initialise les features dans Linear.
  - Skills : `assembleur-init` → `assembleur` → `assembleur-amorce` → `init-linear`.
  - Tu tranches : le garant de cohérence (chaque feature part avec ses 3 faces complètes), puis
    la validation du découpage par l'équipe.
  - Handoff final : `specify init --ai claude` puis les `/speckit.specify` selon le plan
    d'attaque ; les features sont suivies dans Linear.

**Repère** : chaque skill se termine par une ligne « Étape suivante » qui te dit quoi lancer
ensuite — tu avances ainsi de proche en proche. Pour savoir où tu en es dans une phase, lance
son skill de bilan/cohérence (`cadrage-completude`, `architecte-coherence`, `designer-coherence`).

## Étape suivante
« Étape suivante : `/cadrage:cadrage-init` pour démarrer depuis le début (phase amont), ou lance directement la phase qui correspond à ton avancement — `/architecte:architecte-init`, `/designer:designer-init` ou `/assembleur:assembleur-init`. Détail de la phase 1 : `/cadrage:help-cadrage`. »
