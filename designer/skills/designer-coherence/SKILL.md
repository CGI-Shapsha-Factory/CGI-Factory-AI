---
name: designer-coherence
description: Valide le design system généré par Claude Design, vérifie la couverture, et produit le handoff design (réf. du système synchronisé + guidelines) pour l'assembleur.
---

# designer-coherence

Dernière étape de la phase design : la **porte de validation du système généré** (def : « après Claude
Design, la validation du système généré ; le designer valide avant que `/design-sync` ne l'engage vers la
fabrication »). On vérifie que la **couverture** est tenue et que le design system produit est validé,
puis on prépare le **handoff** pour l'assembleur.

## Porte d'entrée
Le skill `designer-atelier` a produit le prompt + le rapport de couverture (`design.phase = "atelier"`,
`design.coverage_sufficient = true`). Sinon, orienter en clair vers `/designer:designer-atelier`.
*(Entre les deux : l'humain a lancé **Claude Design** avec le prompt et obtenu un design system.)*

## Entrées
`designer-out/coverage-report.md` ; le bloc `design` du manifeste (checklist) ; le `cadrage-out/spec-index.md`
(parcours) et `architecte-out/design-impact.md` (architecte) ; la **référence du design system produit dans Claude
Design** (à fournir par l'humain).
> **Lecture seule.** `cadrage-out/spec-index.md` est un **artefact du cadrage** : on le **lit** pour
> vérifier que tous les parcours sont couverts, on ne le **crée ni ne le modifie jamais**.

## Procédure
1. **Vérifier la couverture** : la checklist (`design.checklist`) ne contient **aucun item `open`** (tout
   `deduced`/`decided`/`sans_objet`). Les parcours du `spec-index.md` sont tous couverts (versant
   expérience). Sinon, renvoyer vers `/designer:designer-atelier` pour statuer les items restants. Lancer le
   garde-fou déterministe `scripts/check_design.py`.
2. **Porte humaine : validation du système généré** (porte 2, jamais automatisée). Le designer **valide**
   le design system produit par Claude Design (cohérent avec la couverture, la direction stylistique et la
   stack). Capter sa référence dans `design.design_system_ref`. Le skill ne passe **jamais**
   `design.design_validated` à vrai de lui-même ; il le propose, l'humain confirme.
3. **Produire le handoff design** → `designer-out/design-guidelines.md` (gabarit
   `.factory/templates/design-guidelines.md`) : **référence du design system validé + synchronisable** (`/design-sync`),
   **règles d'états** (par écran), **patterns d'erreur** (validation à la sortie du champ, format API →
   messages par champ), **socle d'accessibilité** (niveau visé), et la règle **aucune valeur de style en
   dur**. MAJ `design.guidelines_path`.

## Sortie
- **Rapport de couverture** à jour (statut par item, dans l'artefact). En chat, **pas de tableau de
  synthèse** : un **bilan en prose** qui dit, en clair, ce qui est **validé**, ce qui reste éventuellement
  **à traiter ou à corriger**, puis **la prochaine étape** — rien de plus.
- **Handoff design** (`design-guidelines.md`) prêt pour l'assembleur ; `design.design_system_ref` posée.
- **Porte humaine** : `design.design_validated = true` **par l'humain uniquement** ; `design.phase = "valide"`
  une fois acté — **mise à jour du manifeste en silence** (jamais narrée). Verdict honnête : rien n'est
  annoncé validé tant qu'un point reste **à traiter**.

## Handoff (vers l'assembleur)
Le contrat de design prêt à transmettre = la **référence du design system validé/synchronisé** (Claude
Design, pont `/design-sync`) + les **guidelines** (règles d'états, patterns d'erreur, socle a11y). C'est ce
que l'Assembleur grave dans la constitution / le `claude.md` / la CI (voir §6 de la spec : forcer
`/design-sync`, interdire les valeurs de style en dur, contrôler les états et patterns d'erreur).

## Règles invariantes
- **L'humain valide.** Le système généré n'est jamais auto-validé par l'IA.
- **Refléter l'état réel.** Aucun item maquillé ; un point « à traiter » reste un trou.
- **Lecture seule du cadrage** : `spec-index.md` est lu pour vérifier la couverture des parcours, jamais
  créé ni modifié (artefact du cadrage).
- **Le design system vit dans Claude Design** ; le plugin ne le régénère pas.
- **Pas de fuite de champ** en sortie utilisateur ni de tableau de booléens ; **manifeste mis à jour en
  silence** (voir `references/ux-conventions.md`).

Étape suivante : `/assembleur:assembleur-init` — démarrer la convergence des 3 contrats (fonctionnel, technique, design) puis l'amorçage du repo SpecKit. Ou corriger d'abord les items signalés via `/designer:designer-atelier`.
