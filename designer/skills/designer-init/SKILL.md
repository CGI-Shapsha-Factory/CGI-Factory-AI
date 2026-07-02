---
name: designer-init
description: Amorce l'atelier design : installe les gabarits (checklist de couverture, rapport, prompt, guidelines) et étend le manifeste. Ne génère pas de design system.
---

# designer-init

Skill d'amorçage de la phase **design** : **tout premier skill** à lancer après que l'architecte a figé et
validé le contrat technique **et** produit sa section *Décisions à impact design*. Il prépare l'**atelier de
couverture** (zéro décision de design) ; les autres skills (`designer`, `designer-coherence`) supposent
qu'il a tourné. **Le plugin ne génère pas le design system** (il naît dans Claude Design, via `/design-sync`).

## Objectif
Rendre un projet **prêt pour l'atelier design** : installer les gabarits et étendre le manifeste partagé
avec un bloc `design` orienté **couverture** (checklist pré-remplie par les handoffs).

## Porte d'entrée
**Cadrage prêt + maquette validée + architecture validée + Décisions à impact design présentes.** Lire
`.factory/manifest.json` ; **refuser en clair** si :
- la maquette n'a pas convergé (`demonstrateur.client_validated != true`), ou
- l'architecture n'est pas validée (`architecture.coherence_validated != true`), ou
- la section *Décisions à impact design* manque (`architecture.design_impact != true` / pas de
  `design-impact.md`).
  > « L'atelier design ne peut pas démarrer : il faut une maquette validée par le client, un contrat
  > technique validé, et la section *Décisions à impact design* de l'architecte. Termine d'abord ces phases. »
- Vérifier les artefacts : côté cadrage `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`,
  `cadrage-out/spec-index.md` (parcours + entités affichées) ; côté architecte `architecte-out/design-impact.md`.

**Refus précis (fichier réellement manquant).** Nommer en clair **ce qui bloque** : soit un **flag
manifeste à `false`** + le **skill amont** à relancer (maquette → `/cadrage:cadrage-retour-demonstrateur` ;
cohérence archi → `/architecte:architecte-coherence`), **puis committer `.factory/manifest.json`** ; soit un
**fichier `cadrage-out/…` / `architecte-out/…` absent, par chemin**. Rappel : `.factory/manifest.json` + les
dossiers `-out/` amont doivent avoir été **committés** — s'ils manquent du clone, c'est un fichier réellement absent.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant.

## Procédure
1. **Installer les gabarits** dans `.factory/templates/` (copier depuis le plugin `templates/`) :
   `coverage-checklist.md`, `coverage-report.md`, `claude-design-prompt.md`, `design-guidelines.md`.
   **Créer le dossier des prompts** `prompts/designer/` à la racine du projet (il recevra le prompt Claude
   Design en fichier plat). *(Le plugin ne crée plus de dossier `design-system/` ni de seed de tokens : le
   design system naît dans Claude Design.)*
2. **Étendre le manifeste** `.factory/manifest.json` : ajouter le bloc `design` ci-dessous s'il est
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
*Statut de chaque item : `open` → `deduced` (rempli depuis un handoff) | `decided` (tranché par l'humain) |
`sans_objet` (sans objet, marqué pas forcé). Les portes `coverage_sufficient` et `design_validated` sont
des **gestes humains** (jamais auto).*

## Porte de sortie
- Les 4 gabarits sont dans `.factory/templates/`.
- Le dossier `prompts/designer/` existe à la racine du projet (prêt à recevoir le prompt Claude Design).
- Le manifeste contient le bloc `design` (`phase: "init"`, checklist semée), et reparse sans erreur.
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision de design** ni génération de design system. Ce skill prépare l'atelier.
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/designer:designer-atelier` — dérouler la checklist de couverture (fondation, expérience, technique) et produire le prompt Claude Design.
