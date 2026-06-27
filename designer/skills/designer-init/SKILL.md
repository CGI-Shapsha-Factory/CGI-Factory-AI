---
name: designer-init
description: Amorce la phase design : crée le dossier design-system (seed tokens DTCG), installe les gabarits et étend le manifeste.
---

# designer-init

Skill d'amorçage de la phase **design** : **tout premier skill** à lancer après que
l'architecte a figé et validé le contrat technique. Il prépare le terrain (zéro décision
de design) ; les autres skills (`designer`, `designer-coherence`) supposent qu'il a
tourné.

## Objectif
Rendre un projet **prêt pour la phase design** : installer les gabarits, créer le dossier
`design-system/` (avec un seed de tokens DTCG), et étendre le manifeste partagé avec un
bloc `design`.

## Porte d'entrée
**Le cadrage ET l'architecture doivent être prêts.** Lire `factory-docs/manifest.json` :
- si la maquette n'a pas convergé (le démonstrateur n'est pas validé par le client) ou si
  l'architecture n'est pas validée (la validation de cohérence n'est pas faite),
  **refuser** en clair :
  > « La phase design ne peut pas démarrer : il faut une maquette validée par le client
  > (fin du cadrage) **et** un contrat technique validé par l'architecte. Termine d'abord
  > ces deux phases. »
- Vérifier la présence des artefacts attendus dans `factory-docs/work/` : côté cadrage
  `product-brief.md`, `glossaire.md`, `spec-index.md` ; côté architecte `tech-stack.md`,
  `components.md`, `standards.md`.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant.

## Procédure
1. **Installer les gabarits de design** dans `factory-docs/templates/` : copier depuis le
   plugin `templates/` : `design-principles.md`, `foundations.md`, `components.md`,
   `states-and-patterns.md`, `journeys.md`, `accessibility.md`, `ddr.md`.
2. **Créer le dossier `design-system/`** à la **racine du projet** et y déposer le seed
   universel de tokens DTCG (copie de `references/design-system/tokens.seed.json` →
   `design-system/tokens.json`). **Le format de livraison spécifique à la stack**
   (variables CSS, thème React/TS, preset Tailwind, config Style Dictionary) **n'est PAS
   choisi ici** : le front-end n'est connu qu'après lecture du `tech-stack.md` — c'est le
   skill `designer` qui le déposera (voir son étape de livraison des tokens).
3. **Créer `factory-docs/work/design-decisions/`** (dossier des DDR, vide).
4. **Étendre le manifeste** `factory-docs/manifest.json` : ajouter le bloc `design`
   ci-dessous s'il est absent (read-modify-write + revalidation JSON) :

```json
"design": {
  "phase": "init",
  "source_maquette": null,
  "principles": [],
  "tokens": { "format": "dtcg", "file": null, "tiers": [], "validated": false },
  "foundations": { "color": false, "typography": false, "spacing": false, "elevation": false, "motion": false, "iconography": false, "breakpoints": false },
  "stack_alignment": { "frontend": null, "token_delivery": null },
  "components": [],
  "required_states": ["default", "hover", "focus", "active", "disabled", "loading", "empty", "error"],
  "component_states": {},
  "states_patterns": [],
  "journeys": [],
  "journeys_coverage": [],
  "accessibility": { "standard": "WCAG 2.2", "target": "AA", "validated": false },
  "ddrs": [],
  "coverage_validated": false
}
```

## Porte de sortie
- `design-system/` existe à la racine avec `tokens.json` (seed DTCG).
- Les 7 gabarits de design sont dans `factory-docs/templates/`.
- `factory-docs/work/design-decisions/` existe.
- Le manifeste contient le bloc `design` (`phase: "init"`), et reparse sans erreur.
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision de design.** Ce skill prépare ; il ne choisit ni couleurs, ni
  typographie, ni composants.
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/designer:designer` — construire le contrat de design (principes, tokens, composants & états, parcours, accessibilité).
