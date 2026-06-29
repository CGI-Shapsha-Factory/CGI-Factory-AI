---
name: architecte-init
description: Amorce la phase architecture : crée le dossier conventions, installe les gabarits et étend le manifeste.
---

# architecte-init

Skill d'amorçage de la phase **architecture** : **tout premier skill** à lancer
après le cadrage. Il prépare le terrain technique sans prendre aucune décision
d'architecture (zéro choix IA). Les autres skills (`architecte`,
`architecte-coherence`) supposent qu'il a tourné.

## Objectif
Rendre un projet **prêt pour la phase technique** : installer les gabarits
d'architecture, créer le dossier `conventions/`, et étendre le manifeste partagé
avec un bloc `architecture`.

## Porte d'entrée
**Le cadrage doit être prêt.** Lire `.factory/manifest.json` :
- s'il est absent, ou si la phase amont n'est pas prête (le verdict « cadrage
  complet » n'est pas atteint, ou les artefacts clés manquent), **refuser** avec un
  message en clair :
  > « La phase technique ne peut pas démarrer : le cadrage n'est pas encore prêt.
  > Termine d'abord la phase de cadrage (jusqu'au handoff). »
- Vérifier la présence des artefacts cadrage attendus : `cadrage-out/project-frame.md`,
  `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`,
  et les briefs sous `cadrage-out/features-fonctionnels-brief/*.brief.md`.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant.

## Procédure
1. **Installer les gabarits d'architecture** dans `.factory/templates/` (à côté
   des gabarits de cadrage) : copier depuis le plugin `templates/` :
   `drivers-quality.md`, `components.md`, `tech-stack.md`, `standards.md`,
   `diagrams.md`, `adr.md`, `risks.md`, `design-impact.md`.
2. **Créer le dossier `conventions/`** à la **racine du projet** et y déposer le
   socle universel `.editorconfig` (copie de
   `references/conventions/.editorconfig`). **Les fichiers de conventions par
   langage ne sont PAS installés ici** : le langage n'est connu qu'après le workflow
   stack — c'est le skill `architecte` qui les déposera (voir son étape conventions).
3. **Créer `architecte-out/decisions/`** (dossier des ADR, vide).
4. **Étendre le manifeste** `.factory/manifest.json` : ajouter le bloc
   `architecture` ci-dessous s'il est absent (read-modify-write + revalidation JSON) :

```json
"architecture": {
  "phase": "init",
  "team_profile": null,
  "drivers": [],
  "quality_attributes": [],
  "components": [],
  "stack": {},
  "conventions_installed": [],
  "adrs": [],
  "walking_skeleton": null,
  "feature_sequence": [],
  "risks": [],
  "design_impact": false,
  "coherence_validated": false
}
```

## Porte de sortie
- `conventions/` existe à la racine avec `.editorconfig`.
- Les 8 gabarits d'architecture (dont `design-impact.md`) sont dans `.factory/templates/`.
- `architecte-out/decisions/` existe.
- Le manifeste contient le bloc `architecture` (`phase: "init"`), et reparse sans erreur.
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision IA.** Ce skill prépare ; il ne classe pas de drivers, ne choisit
  pas de composants ni de stack.
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/architecte:architecte` — construire le contrat technique (drivers, composants, stack, ADR, walking skeleton, diagrammes).
