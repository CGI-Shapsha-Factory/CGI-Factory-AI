---
name: assembleur-init
description: Amorce la phase de convergence : vérifie les 3 contrats validés, installe les gabarits, crée assembleur-out/ et étend le manifeste.
---

# assembleur-init

Skill d'amorçage de la phase **convergence** : **tout premier skill** à lancer après
que les trois contrats (cadrage, architecte, designer) ont été validés. Il prépare le
terrain (zéro décision de convergence) ; `assembleur-convergence` suppose qu'il a tourné.

## Objectif
Rendre un projet **prêt pour la convergence** : confirmer que les 3 contrats sont
validés, installer les gabarits, créer le dossier de sortie `assembleur-out/`, et
étendre le manifeste partagé avec un bloc `assembly`. **Il n'y a aucun repo cible à
capturer** : l'assembleur produit un **paquet** dans `assembleur-out/`, il n'écrit
jamais dans un repo SpecKit.

## Pré-requis (vérification silencieuse)
**Les 3 contrats doivent être validés.** Lire `.factory/manifest.json` sans l'annoncer :
- si le cadrage n'est pas terminé, **ou** l'architecture pas validée, **ou** le design
  pas validé → **le dire en clair** :
  > « La convergence ne peut pas démarrer : il faut les trois contrats validés — le
  > cadrage, l'architecture (cohérence validée) et le design (système validé). Termine
  > d'abord la phase qui manque. »
- Vérifier la présence des artefacts attendus : cadrage
  (`cadrage-out/product-brief.md`, `glossaire.md`, `spec-index.md`,
  `features-fonctionnels-brief/*.brief.md`), architecte
  (`architecte-out/tech-stack.md`, `components.md`, `decisions/`, `design-impact.md`),
  designer (`designer-out/design-guidelines.md`).

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant.

## Procédure
1. **Installer les gabarits de convergence** dans `.factory/templates/` : copier depuis
   le plugin `templates/` : `pre-constitution.md`, `spec-seed.md`, `feature-map.md`,
   `technical-context.md`, `project-claude-md.md`, `memory-index.md`, `memory-domain.md`,
   `memory-architecture.md`, `memory-design.md`, `memory-features.md`,
   `coherence-report.md`, `attack-plan.md`, `ci-tests.yml`.
2. **Créer le dossier de sortie** `assembleur-out/` avec ses sous-dossiers `features/`
   et `memory/` (vides).
3. **Étendre le manifeste** `.factory/manifest.json` : ajouter le bloc `assembly`
   ci-dessous s'il est absent (read-modify-write + revalidation JSON) :

```json
"assembly": {
  "phase": "init",
  "feature_seeds": [],
  "coherence_report": null,
  "coherence_validated": false,
  "package_paths": {}
}
```

## Vérification avant de conclure
- Les gabarits de convergence sont dans `.factory/templates/`.
- `assembleur-out/` (avec `features/` et `memory/`) existe.
- Le manifeste contient le bloc `assembly` (`phase: "init"`), et reparse sans erreur.
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision de convergence.** Ce skill prépare ; il ne converge rien.
- **Paquet seul.** Aucun repo cible ; tout ira dans `assembleur-out/`.
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/assembleur:assembleur-convergence` — lire les 3 contrats en parallèle, les converger et produire le paquet de handoff SpecKit.
