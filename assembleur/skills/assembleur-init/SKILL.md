---
name: assembleur-init
description: Amorce la phase de convergence : vérifie les 3 contrats, capture le repo SpecKit cible, installe les gabarits et étend le manifeste.
---

# assembleur-init

Skill d'amorçage de la phase **convergence** : **tout premier skill** à lancer après que
les trois contrats (cadrage, architecte, designer) ont été validés. Il prépare le terrain
(zéro décision de convergence) ; les autres skills (`assembleur`, `assembleur-amorce`)
supposent qu'il a tourné.

## Objectif
Rendre un projet **prêt pour la convergence** : confirmer que les 3 contrats sont validés,
capturer le **repo SpecKit cible**, installer les gabarits, et étendre le manifeste partagé
avec un bloc `assembly`.

## Porte d'entrée
**Les 3 contrats doivent être validés.** Lire `.factory/manifest.json` :
- si la phase amont n'est pas prête (`definition_of_ready.cadrage_complete` faux), **ou** si
  l'architecture n'est pas validée (`architecture.coherence_validated` faux), **ou** si le
  design n'est pas validé (`design.design_validated` faux — le système Claude Design a été validé) →
  **refuser** en clair :
  > « La convergence ne peut pas démarrer : il faut les trois contrats validés — le cadrage
  > (prêt pour SpecKit), l'architecture (cohérence validée) et le design (système validé). Termine
  > d'abord la phase qui manque. »
- Vérifier la présence des artefacts attendus : cadrage
  (`cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`,
  `cadrage-out/features-fonctionnels-brief/*.brief.md`), architecte
  (`architecte-out/tech-stack.md`, `architecte-out/components.md`, `architecte-out/decisions/`,
  `architecte-out/design-impact.md`), designer
  (`designer-out/design-guidelines.md` = handoff design : réf. du design system synchronisé + guidelines).

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant.

## Procédure
1. **Capturer le repo SpecKit cible** : demander le chemin du repo cible (boucle 3-options).
   L'écrire dans `assembly.target_repo`. C'est là qu'iront la constitution convergée, `CLAUDE.md`,
   `specs/`. **Précondition — le repo doit déjà être initialisé** (`specify init --ai claude` lancé
   par l'équipe) : il contient `.specify/` (scripts, templates, gabarit de constitution) et les
   commandes `/speckit.*`. **Si `.specify/` est absent, refuser en clair** :
   > « Avant la convergence, initialise le repo cible : lance `specify init --ai claude` dedans, puis
   > relance `/assembleur:assembleur-init`. »
   Ainsi l'assembleur **écrit après** `specify init` (le bon ordre) : sa constitution convergée
   **remplace** le gabarit de SpecKit, sans risque d'être écrasée par un init ultérieur.
2. **Installer les gabarits de convergence** dans `.factory/templates/` : copier depuis
   le plugin `templates/` : `converged-constitution.md`, `project-claude-md.md`,
   `feature-brief-3faces.md`, `spec-seed.md`, `glossary-consolidated.md`,
   `coherence-report.md`, `review-guidelines.md`, `attack-plan.md`, `memory-index.md`.
3. **Créer `assembleur-out/briefs/` et `assembleur-out/guidelines/`** (vides).
4. **Étendre le manifeste** `.factory/manifest.json` : ajouter le bloc `assembly`
   ci-dessous s'il est absent (read-modify-write + revalidation JSON) :

```json
"assembly": {
  "phase": "init",
  "target_repo": null,
  "constitution_generated": false,
  "claude_md_generated": false,
  "glossary_consolidated": false,
  "feature_faces": [],
  "coherence_report": null,
  "guidelines_generated": false,
  "memory_index_generated": false,
  "attack_plan": null,
  "ci_generated": false,
  "coherence_validated": false,
  "team_validated": false,
  "linear_initialized": false,
  "linear_issues": [],
  "linear_project": null
}
```

## Porte de sortie
- `assembly.target_repo` renseigné **et** repo déjà initialisé par SpecKit (`.specify/` présent).
- Les 9 gabarits de convergence sont dans `.factory/templates/`.
- `assembleur-out/briefs/` et `assembleur-out/guidelines/` existent.
- Le manifeste contient le bloc `assembly` (`phase: "init"`), et reparse sans erreur.
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision de convergence.** Ce skill prépare ; il ne coud rien, ne génère aucune
  constitution.
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/assembleur:assembleur` — coudre les 3 contrats par feature et générer le pack SpecKit.
