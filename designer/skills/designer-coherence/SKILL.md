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
Le skill `designer` a produit le prompt + le rapport de couverture (`design.phase = "atelier"`,
`design.coverage_sufficient = true`). Sinon, orienter en clair vers `/designer:designer`.
*(Entre les deux : l'humain a lancé **Claude Design** avec le prompt et obtenu un design system.)*

## Entrées
`factory-docs/work/coverage-report.md` ; le bloc `design` du manifeste (checklist) ; le `spec-index.md`
(parcours) et `design-impact.md` (architecte) ; la **référence du design system produit dans Claude
Design** (à fournir par l'humain).

## Procédure
1. **Vérifier la couverture** : la checklist (`design.checklist`) ne contient **aucun item `open`** (tout
   `deduced`/`decided`/`sans_objet`). Les parcours du `spec-index.md` sont tous couverts (E1). Sinon,
   renvoyer vers `/designer:designer` pour statuer les items restants. Lancer le garde-fou déterministe
   `scripts/check_design.py`.
2. **Porte humaine : validation du système généré** (porte 2, jamais automatisée). Le designer **valide**
   le design system produit par Claude Design (cohérent avec la couverture, la direction stylistique et la
   stack). Capter sa référence dans `design.design_system_ref`. Le skill ne passe **jamais**
   `design.design_validated` à vrai de lui-même ; il le propose, l'humain confirme.
3. **Produire le handoff design** → `factory-docs/work/design-guidelines.md` (gabarit
   `templates/design-guidelines.md`) : **référence du design system validé + synchronisable** (`/design-sync`),
   **règles d'états** (par écran), **patterns d'erreur** (validation à la sortie du champ, format API →
   messages par champ), **socle d'accessibilité** (niveau visé), et la règle **aucune valeur de style en
   dur**. MAJ `design.guidelines_path`.

## Sortie
- **Rapport de couverture** à jour (statut par item) + tableau de synthèse en chat (couvert / à corriger /
  manquant).
- **Handoff design** (`design-guidelines.md`) prêt pour l'assembleur ; `design.design_system_ref` posée.
- **Porte humaine** : `design.design_validated = true` **par l'humain uniquement** ; `design.phase = "valide"`
  une fois acté. Verdict honnête : pas de vert tant qu'un item reste `open`.

## Handoff (vers l'assembleur)
Le contrat de design prêt à transmettre = la **référence du design system validé/synchronisé** (Claude
Design, pont `/design-sync`) + les **guidelines** (règles d'états, patterns d'erreur, socle a11y). C'est ce
que l'Assembleur grave dans la constitution / le `claude.md` / la CI (voir §6 de la spec : forcer
`/design-sync`, interdire les valeurs de style en dur, contrôler les états et patterns d'erreur).

## Règles invariantes
- **L'humain valide.** Le système généré n'est jamais auto-validé par l'IA.
- **Refléter l'état réel.** Aucun item maquillé ; un `open` reste un trou.
- **Le design system vit dans Claude Design** ; le plugin ne le régénère pas.
- **Pas de fuite de champ** en sortie utilisateur (voir `references/ux-conventions.md`).

Étape suivante : `/assembleur:assembleur-init` — démarrer la convergence des 3 contrats (fonctionnel, technique, design) puis l'amorçage du repo SpecKit. Ou corriger d'abord les items signalés via `/designer:designer`.
