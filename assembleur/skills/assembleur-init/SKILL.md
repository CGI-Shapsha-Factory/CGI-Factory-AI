---
name: assembleur-init
description: Amorce la phase de convergence : vérifie que les 3 dossiers de sortie amont (cadrage-out, architecte-out, designer-out) existent, sont complets et non vides, installe les gabarits, crée assembleur-out/ et étend le manifeste.
---

# assembleur-init

Skill d'amorçage de la phase **convergence** : **tout premier skill** à lancer une fois
que les trois phases amont (cadrage, architecte, designer) ont produit leurs dossiers de
sortie. Il prépare le terrain (zéro décision de convergence) ; `assembleur-convergence`
suppose qu'il a tourné.

## Objectif
Rendre un projet **prêt pour la convergence** : **vérifier que les 3 dossiers de sortie
amont** (`cadrage-out/`, `architecte-out/`, `designer-out/`) **existent, contiennent tous
les fichiers attendus et non vides**, installer les gabarits, créer le dossier de sortie
`assembleur-out/`, et étendre le manifeste partagé avec un bloc `assembly`. **Il n'y a
aucun repo cible à capturer** : l'assembleur produit un **paquet** dans `assembleur-out/`,
il n'écrit jamais dans un repo SpecKit.

## Pré-requis (vérification silencieuse)
**Vérifier uniquement la présence et la complétude des 3 dossiers de sortie amont — PAS
leur statut de validation.** Que le cadrage, l'architecture ou le design aient été validés
ou non **n'est pas le problème de l'assembleur** : ne lire **aucun flag de validation** du
manifeste (`cadrage_complete`, `coherence_validated`, design validé…) et ne pas bloquer
dessus. Contrôler seulement, **sur le disque**, que chaque fichier attendu **existe et
n'est pas vide** :
- **cadrage** : `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`,
  `cadrage-out/spec-index.md`, et **au moins un** brief sous
  `cadrage-out/features-fonctionnels-brief/*.brief.md`.
- **architecte** : `architecte-out/tech-stack.md`, `architecte-out/components.md`,
  `architecte-out/design-impact.md`, et le dossier `architecte-out/decisions/`.
- **designer** : `designer-out/design-guidelines.md`.

Un dossier `-out/` **absent ou vide**, ou un fichier attendu **manquant / vide**, est le
**seul** motif de refus.

**Refus précis (fichier réellement manquant ou vide).** Nommer en clair **ce qui manque ou
est vide**, **par chemin**, et indiquer la **phase amont** qui doit le produire/compléter
(cadrage / architecte / designer). Rappel : `.factory/manifest.json` + les 3 dossiers
`-out/` doivent avoir été **committés** par les phases précédentes — s'ils manquent du
clone, c'est un fichier réellement absent, le dire. **Ne jamais bloquer sur un statut de
validation** ; seule l'absence ou la vacuité d'un fichier bloque.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant.

## Procédure
1. **Installer les gabarits de convergence** dans `.factory/templates/` : copier depuis
   le plugin `templates/` : `pre-constitution.md`, `spec-seed.md`, `feature-map.md`,
   `technical-context.md`, `project-claude-md.md`, `memory-index.md`, `memory-domain.md`,
   `memory-architecture.md`, `memory-design.md`, `memory-features.md`,
   `coherence-report.md`, `attack-plan.md`, `ci-tests.yml`, `init-cowork.md`.
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
- **Vérification, pas validation.** L'assembleur ne juge pas si l'amont est « validé » : il
  vérifie seulement que les fichiers de sortie sont **là et non vides**. Aucun flag de
  validation lu ni exigé.
- **Aucun hook à poser.** L'assembleur n'a **pas de hook ni d'enforcement propre** à installer :
  l'enforcement (hook de test `PostToolUse` + protection de branche `SessionStart`/`.githooks/`)
  est posé **en amont par `architecte-init`** et déjà committé dans le repo ; l'assembleur ne
  fait que **livrer le backstop CI** (`ci/tests.yml`) **dans le paquet** (posé par l'équipe).
- **Paquet seul.** Aucun repo cible ; tout ira dans `assembleur-out/`.
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/assembleur:assembleur-convergence` — lire les 3 contrats en parallèle, les converger et produire le paquet de handoff SpecKit.
