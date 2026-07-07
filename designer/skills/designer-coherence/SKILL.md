---
name: designer-coherence
description: Valide le design system généré par Claude Design, vérifie la couverture, et produit le handoff design (réf. du système synchronisé + guidelines) pour l'assembleur.
---

# designer-coherence

Dernière étape de la phase design : la **porte de validation du système généré** (def : « après Claude
Design, la validation du système généré ; le designer valide l'export committé avant de le transmettre à la
fabrication »). On vérifie que la **couverture** est tenue et que le design system produit est validé,
puis on prépare le **handoff** pour l'assembleur.

## Porte d'entrée
Le skill `designer-atelier` a produit le prompt + le rapport de couverture (`design.phase = "atelier"`,
`design.coverage_sufficient = true`). Sinon, orienter en clair vers `/designer:designer-atelier`.
*(Entre les deux : l'humain a lancé **Claude Design** avec le prompt, obtenu un design system, et **déposé son
export dans `designer-out/maquette-de-claude-design/`**.)*

## Entrées
`designer-out/coverage-report.md` ; le bloc `design` du manifeste (checklist) ; le `cadrage-out/spec-index.md`
(parcours) et `architecte-out/design-impact.md` (architecte) ; la **source du design system validé** =
l'**export committé** dans `designer-out/maquette-de-claude-design/` (dossier ou ZIP avec les tokens, ex.
`tokens.css`), déposé par l'humain. *(Source unique : plus de référence Claude Design externe — l'équipe
travaille à plusieurs et ne partage pas l'accès aux comptes ; tout vit dans le repo committé.)*
> **Lecture seule.** `cadrage-out/spec-index.md` est un **artefact du cadrage** : on le **lit** pour
> vérifier que tous les parcours sont couverts, on ne le **crée ni ne le modifie jamais**.

## Procédure
1. **Vérifier la couverture** : la checklist (`design.checklist`) ne contient **aucun item `open`** (tout
   `deduced`/`decided`/`sans_objet`). Les parcours du `spec-index.md` sont tous couverts (versant
   expérience). Sinon, renvoyer vers `/designer:designer-atelier` pour statuer les items restants. Lancer le
   garde-fou déterministe (**obligatoire**) :
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_design.py" <racine>/.factory/manifest.json`. S'il est
   **introuvable** (chemin plugin non résolu) ou renvoie **exit 1**, **s'arrêter** et **dire en clair**
   ce qui manque — **jamais** de vérification « à la main » silencieuse.
2. **Porte humaine : validation du système généré** (porte 2, jamais automatisée). D'abord **vérifier que
   `designer-out/maquette-de-claude-design/` n'est pas vide** (un dossier d'export ou une archive ZIP y est
   présent) ; s'il est **vide**, le dire en clair (**maquette manquante** — indiquer de déposer l'export de
   Claude Design dans `designer-out/maquette-de-claude-design/`, dossier ou ZIP) et **ne pas sceller**.
   Ensuite, le designer **valide** le design system (cohérent avec la couverture, la direction stylistique et
   la stack). Capter la **source** dans `design.design_system_ref` = chemin
   `designer-out/maquette-de-claude-design/`. Le skill ne passe **jamais** `design.design_validated` à vrai
   de lui-même ; il le propose, l'humain confirme.
3. **Produire le handoff design** → `designer-out/design-guidelines.md` (gabarit
   `.factory/designer/design-guidelines.md`) : **source du design system validé** = l'export committé dans
   `designer-out/maquette-de-claude-design/`, **règles d'états** (par écran), **patterns d'erreur**
   (validation à la sortie du champ, format API → messages par champ), **socle d'accessibilité** (niveau
   visé), et la règle **tout écran dérive de l'export committé, aucune valeur de style en dur**. MAJ
   `design.guidelines_path`.

## Sortie
- **Rapport de couverture** à jour (statut par item, dans l'artefact). En chat, **pas de tableau de
  synthèse** : un **bilan en prose** qui dit, en clair, ce qui est **validé**, ce qui reste éventuellement
  **à traiter ou à corriger**, puis **la prochaine étape** — rien de plus.
- **Handoff design** (`design-guidelines.md`) prêt pour l'assembleur ; `design.design_system_ref` posée.
- **Porte humaine** : `design.design_validated = true` **par l'humain uniquement** ; `design.phase = "valide"`
  une fois acté — **mise à jour du manifeste en silence** (jamais narrée). Verdict honnête : rien n'est
  annoncé validé tant qu'un point reste **à traiter**.

## Handoff (vers l'assembleur)
Le contrat de design prêt à transmettre = la **source du design system validé** — l'**export committé** dans
`designer-out/maquette-de-claude-design/` (repo auto-portable) — + les **guidelines** (règles d'états,
patterns d'erreur, socle a11y). La phase design est **auto-portable** : tout vit dans le repo committé, aucun
accès à un compte externe n'est requis. C'est ce que l'Assembleur grave dans la constitution / le `claude.md`
/ la CI : **tout écran dérive de l'export committé du design system**, interdire les valeurs de style en dur,
contrôler les états et patterns d'erreur.

## Règles invariantes
- **L'humain valide.** Le système généré n'est jamais auto-validé par l'IA.
- **Refléter l'état réel.** Aucun item maquillé ; un point « à traiter » reste un trou.
- **Lecture seule du cadrage** : `spec-index.md` est lu pour vérifier la couverture des parcours, jamais
  créé ni modifié (artefact du cadrage).
- **Le design system vit dans l'export committé** (`designer-out/maquette-de-claude-design/`) ; le plugin ne
  le régénère pas. L'export committé rend la phase auto-portable.
- **Pas de fuite de champ** en sortie utilisateur ni de tableau de booléens ; **manifeste mis à jour en
  silence** (voir `references/ux-conventions.md`).

**Handoff (avant de passer la main).** Committer `.factory/manifest.json` (design **scellé**) **et**
`designer-out/` — **y compris l'export du design system déposé dans
`designer-out/maquette-de-claude-design/`**. La phase suivante lit le **repo committé**, pas ta session.

Étape suivante : `/assembleur:assembleur-init` — démarrer la convergence des 3 contrats (fonctionnel, technique, design) puis l'amorçage du repo SpecKit. Ou corriger d'abord les items signalés via `/designer:designer-atelier`.
