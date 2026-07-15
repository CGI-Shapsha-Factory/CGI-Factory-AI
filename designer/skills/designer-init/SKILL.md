---
name: designer-init
description: Amorce l'atelier design : installe les gabarits (checklist de couverture, rapport, prompt, guidelines) et étend le manifeste. Ne génère pas de design system.
---

# designer-init

Skill d'amorçage de la phase **design** : **tout premier skill** à lancer après que l'architecte a figé et
validé le contrat technique **et** produit sa section *Décisions à impact design*. Il prépare l'**atelier de
couverture** (zéro décision de design) ; les autres skills (`designer-ingestion`, `designer-atelier`, `designer-prompt`, `designer-coherence`) supposent
qu'il a tourné. **Le plugin ne génère pas le design system** : il naît dans Claude Design, et son export
est **committé dans `designer-out/maquette-de-claude-design/`**.

## Objectif
Rendre un projet **prêt pour l'atelier design** : installer les gabarits et étendre le manifeste partagé
avec un bloc `design` orienté **couverture** (checklist pré-remplie par les handoffs).

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** — celui où la session est lancée (le cwd) — **jamais** un
dossier parent, **jamais** un `.factory/` / `factory-docs/` / `*-out/` situé plus haut. Tous les chemins de
ce skill (`manifest.json`, `.factory/designer/`, `designer-out/`, `designer-out/prompts/`,
`designer-out/maquette-de-claude-design/`) se
résolvent **sous ce dossier**. **Ne jamais remonter l'arborescence** pour trouver le manifeste ou les
dossiers `-out/` amont : un `manifest.json` (ou un `cadrage-out/` / `architecte-out/`) situé dans
un dossier **parent** n'appartient **pas** à ce projet — le traiter comme **absent** (ne jamais le lire ;
on crée/étend le manifeste **du cwd**). En cas de doute sur un chemin relatif, l'écrire en **absolu à partir du cwd**.

## `.factory/` d'abord — clone frais, `.factory/` git-ignoré (impératif)
`.factory/` est **entièrement git-ignoré** : il ne voyage **jamais** avec le repo. Cette phase peut être
menée par **une autre personne**, sur une **autre machine**, à partir d'un **clone frais** où **aucun
`.factory/` n'existe encore**. Ce skill ne présuppose donc **jamais** un `.factory/` déjà présent :
**avant toute autre chose**, il (re)pose dans `.factory/` **tout ce dont l'atelier a besoin** — les
gabarits de couverture (`.factory/designer/`) et le bloc `design` du manifeste `manifest.json`
(créé s'il manque). Le **handoff** entre phases passe **uniquement** par les dossiers `-out/` committés,
jamais par `.factory/` (régénérable en relançant ce `-init`).

## Setup inconditionnel + état de l'amont (jamais bloquant)
**Ce skill ne bloque jamais.** L'installation des gabarits, la création de `designer-out/` (avec ses
sous-dossiers `prompts/` et `maquette-de-claude-design/`) et
l'amorçage du bloc `design` (checklist semée) sont **déterministes et sans dépendance à l'amont** : ils
s'installent **toujours**, dans le dossier courant. **Ne jamais refuser** au motif que la maquette,
l'architecture ou les *Décisions à impact design* manquent.

Après le setup, **vérifier l'état de l'amont** dans le cwd et le **signaler** (sans bloquer) :
- maquette convergée (`demonstrateur.client_validated`), architecture validée
  (`architecture.coherence_validated`), section *Décisions à impact design*
  (`architecture.design_impact` / `architecte-out/impact-design.md`) ;
- artefacts : `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`,
  `architecte-out/impact-design.md`.

- **Amont prêt** → rien à signaler ; enchaîner sur `/designer:designer-ingestion`.
- **Amont absent ou incomplet** → **ne pas refuser**. Confirmer que l'atelier est amorcé, puis
  **avertir en clair** ce qui manque (flag `false` + skill amont à relancer — maquette →
  `/cadrage:cadrage-retour-demonstrateur`, cohérence archi → `/architecte:architecte-coherence` — ou
  fichier `…-out/…` absent, par chemin) et indiquer que **l'ingestion** (`/designer:designer-ingestion`) a
  besoin de ces handoffs pour pré-remplir la checklist.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant. Si `manifest.json`
n'existe pas encore, **créer d'abord le dossier `cadrage-out/` s'il est absent** (même sans cadrage), puis y
**créer** le manifeste comme objet JSON valide `{ "design": { … } }` (les autres phases le
complètent par fusion, sans écraser le bloc `design`).

## Procédure
1. **Installer les gabarits** dans `.factory/designer/` (copier depuis le plugin `templates/`) :
   `coverage-checklist.md`, `coverage-report.md`, `claude-design-prompt.md`, `design-guidelines.md`.
   **Créer le dossier de sortie `designer-out/`** à la racine du projet, avec ses deux sous-dossiers :
   - `designer-out/prompts/` — recevra le prompt Claude Design (fichier plat) ;
   - `designer-out/maquette-de-claude-design/` — créé **vide** ; l'humain y déposera l'export du design
     system produit par Claude Design.

   Après création, **afficher à l'utilisateur, en gras**, cette invitation : **« Déposez l'export du
   design system généré par Claude Design directement dans `designer-out/maquette-de-claude-design/`.
   Format attendu : le dossier de fichiers DÉZIPPÉ (fichiers et assets tels quels), pas une archive ZIP.
   Si vous n'avez qu'un `.zip`, dézippez-le dans ce dossier. »** *(Raison : l'export reste directement
   consultable et lisible dans le repo ; un `.zip` est un blob binaire que git ne sait pas comparer et
   que `designer-coherence` / l'assembleur devraient extraire.)*

   *(Le plugin ne crée plus de dossier `design-system/` ni de seed de tokens : le design system naît dans
   Claude Design et son export est committé dans `designer-out/maquette-de-claude-design/`.)*
2. **Étendre le manifeste** `manifest.json` : ajouter le bloc `design` ci-dessous s'il est
   absent (read-modify-write + revalidation JSON), en **semant la checklist** avec les items canoniques
   de `coverage-checklist.md` au statut `open` :

```json
"design": {
  "phase": "init",
  "inputs": { "cadrage_ok": false, "design_impact_ok": false },
  "checklist": {
    "foundation":  [ {"id":"F1","label":"Tokens essentiels","origin":"H","status":"open","note":""}, {"id":"F2","label":"Thématisation","origin":"A+H","status":"open","note":""}, {"id":"F3","label":"Composants de base + états","origin":"H","status":"open","note":""}, {"id":"F4","label":"Mouvement","origin":"H","status":"open","note":""} ],
    "experience":  [ {"id":"E1","label":"Parcours et variantes","origin":"C","status":"open","note":""}, {"id":"E2","label":"États de chaque écran","origin":"C+H","status":"open","note":""}, {"id":"E3","label":"États vides utiles","origin":"H","status":"open","note":""}, {"id":"E4","label":"Hiérarchie et densité","origin":"C+H","status":"open","note":""}, {"id":"E5","label":"Feedback et confirmation","origin":"H+A","status":"open","note":""}, {"id":"E6","label":"Microcopie","origin":"H","status":"open","note":""} ],
    "technical":   [ {"id":"T1","label":"Affichage des erreurs","origin":"A","status":"open","note":""}, {"id":"T2","label":"Chargement et asynchrone","origin":"A","status":"open","note":""}, {"id":"T3","label":"Listes, tableaux, pagination","origin":"A","status":"open","note":""}, {"id":"T4","label":"Identité, rôles, autorisations","origin":"A","status":"open","note":""}, {"id":"T5","label":"Navigation et routage","origin":"A","status":"open","note":""}, {"id":"T6","label":"Accessibilité, socle","origin":"A","status":"open","note":""}, {"id":"T7","label":"Responsive","origin":"A","status":"open","note":""}, {"id":"T8","label":"Internationalisation","origin":"A","status":"open","note":""}, {"id":"T9","label":"Budget de performance","origin":"A","status":"open","note":""} ]
  },
  "coverage_sufficient": false,
  "prompt_path": null,
  "coverage_report_path": null,
  "design_system_ref": null,
  "design_validated": false,
  "guidelines_path": null
}
```
*`design_system_ref` = chemin de l'export committé (`designer-out/maquette-de-claude-design/`), renseigné
par `designer-coherence`. Source unique désormais : plus de distinction `claude_design_ref` /
`committed_export`.*

*Statut de chaque item : `open` → `deduced` (rempli depuis un handoff) | `decided` (tranché par l'humain) |
`sans_objet` (sans objet, marqué pas forcé). Les portes `coverage_sufficient` et `design_validated` sont
des **gestes humains** (jamais auto).*
3. **Git-ignore `.factory/` (compléter, jamais réécrire)** : le **`.gitignore` est généré en premier par
   le cadrage** et **committé** — présent dans un clone frais. **Ne jamais le réécrire ni l'écraser** :
   s'assurer seulement qu'il **contient** la ligne `.factory/` — l'**ajouter** si elle manque (sans
   dupliquer), en **préservant** le reste. **Le créer uniquement s'il est absent** (clone où le cadrage
   n'a pas tourné ici). Tout `.factory/` est local, non versionné.

## Porte de sortie
- Les 4 gabarits sont dans `.factory/designer/`.
- `.gitignore` contient la ligne `.factory/`.
- Le dossier `designer-out/` existe à la racine, avec `designer-out/prompts/` (prêt à recevoir le prompt
  Claude Design) et `designer-out/maquette-de-claude-design/` (vide, prêt à recevoir l'export du design
  system) ; la phrase de dépôt de la maquette a été affichée à l'utilisateur.
- Le manifeste contient le bloc `design` (`phase: "init"`, checklist semée), et reparse sans erreur.
- **État de l'amont signalé** : si maquette/architecture/*Décisions à impact design* manquent,
  l'utilisateur a été **averti** (pas bloqué).
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision de design** ni génération de design system. Ce skill prépare l'atelier.
- **Jamais bloquant.** Le setup s'amorce toujours ; l'amont manquant **avertit**, ne refuse pas.
- **Manifeste silencieux.** Ne jamais annoncer que le manifeste est créé/mis à jour ni afficher un
  `champ: valeur`/`true`/`false` ; confirmer en clair ce qui est amorcé + la suite (cf.
  `references/ux-conventions.md`).
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/designer:designer-ingestion` — ingérer les handoffs cadrage + architecte et pré-remplir la checklist de couverture.
