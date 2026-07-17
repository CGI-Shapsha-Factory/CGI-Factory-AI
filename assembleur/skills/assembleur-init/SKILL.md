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

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** - celui où la session est lancée (le cwd) -
**jamais** un dossier parent, **jamais** un `.factory/` / `factory-docs/` / `*-out/` situé
plus haut. Tous les chemins de ce skill (`manifest.json`, `.factory/assembleur/`,
`assembleur-out/`, et les 3 dossiers amont lus `cadrage-out/` / `architecte-out/` /
`designer-out/`) se résolvent **sous ce dossier**. **Ne jamais remonter l'arborescence** :
un `.factory/` ou un dossier `-out/` situé dans un dossier **parent** n'appartient **pas** à
ce projet - le traiter comme **absent** (ne jamais le lire ; on crée/étend le manifeste **du
cwd**). En cas de doute sur un chemin relatif, l'écrire en **absolu à partir du cwd**.

## `.factory/` d'abord : clone frais, `.factory/` git-ignoré (impératif)
`.factory/` est **entièrement git-ignoré** : il ne voyage **jamais** avec le repo. Cette phase peut être
menée par **une autre personne**, sur une **autre machine**, à partir d'un **clone frais** où **aucun
`.factory/` n'existe encore**. Ce skill ne présuppose donc **jamais** un `.factory/` déjà présent :
**avant toute autre chose**, il (re)pose dans `.factory/` **tout ce dont la convergence a besoin** - les
gabarits de convergence (`.factory/assembleur/`) et le bloc `assembly` du manifeste
`manifest.json` (créé s'il manque). Le **handoff** entre phases passe **uniquement** par les
dossiers `-out/` committés, jamais par `.factory/` (régénérable en relançant ce `-init`).

## Setup inconditionnel + état de l'amont (jamais bloquant)
**Ce skill ne bloque jamais.** L'installation des gabarits de convergence, la création de
`assembleur-out/` (avec `features/` et `memory/`) et l'amorçage du bloc `assembly` sont
**déterministes et sans dépendance à l'amont** : ils s'installent **toujours**, dans le dossier
courant. **Ne jamais refuser** au motif que les dossiers `-out/` amont manquent.

Après le setup, **vérifier l'état des 3 dossiers de sortie amont** - présence et complétude,
**sur le disque**, sans lire aucun flag de validation (validé ou non n'est pas le problème de
l'assembleur) - puis le **signaler** (sans bloquer) :
- **cadrage** : `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md`,
  `cadrage-out/spec-index.md`, et **au moins un** brief sous
  `cadrage-out/features-fonctionnels-brief/*.md`.
- **architecte** : `architecte-out/stack-technique.md`, `architecte-out/composants.md`,
  `architecte-out/impact-design.md`, et le dossier `architecte-out/decisions/`.
- **designer** : `designer-out/design-guidelines.md`.

- **Amont complet** -> rien à signaler ; enchaîner sur `/assembleur:assembleur-convergence`.
- **Amont absent, vide ou incomplet** -> **ne pas refuser**. Confirmer que le terrain de
  convergence est posé, puis **avertir en clair** ce qui manque ou est vide (**par chemin**) et la
  **phase amont** qui doit le produire/compléter (cadrage / architecte / designer), en indiquant
  que **la convergence** (`/assembleur:assembleur-convergence`) a besoin de ces dossiers `-out/`.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant. Si
`manifest.json` n'existe pas encore, **créer d'abord le dossier `cadrage-out/` s'il est
absent** (même sans amont), puis y **créer** le manifeste comme objet JSON valide
`{ "assembly": { ... } }` (les autres phases le complètent par fusion, sans écraser le bloc `assembly`).

## Procédure
1. **Installer les gabarits de convergence** dans `.factory/assembleur/` : copier depuis
   le plugin `templates/` : `pre-constitution.md`, `spec-seed.md`, `feature-map.md`,
   `technical-context.md`, `project-claude-md.md`, `memory-index.md`, `memory-domain.md`,
   `memory-architecture.md`, `memory-design.md`, `memory-features.md`,
   `coherence-report.md`, `attack-plan.md`, `init-cowork.md`.
2. **Git-ignore `.factory/` (compléter, jamais réécrire)** : le **`.gitignore` est généré en premier
   par le cadrage** et **committé** - présent dans un clone frais. **Ne jamais le réécrire ni l'écraser** :
   s'assurer seulement qu'il **contient** la ligne `.factory/` - l'**ajouter** si elle manque (sans
   dupliquer), en **préservant** le reste. **Le créer uniquement s'il est absent** (clone où le cadrage
   n'a pas tourné ici). Tout `.factory/` est local, non versionné.
3. **Créer le dossier de sortie** `assembleur-out/` avec ses sous-dossiers `features/`
   et `memory/` (vides).
4. **Étendre le manifeste** `manifest.json` : ajouter le bloc `assembly`
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
- Les gabarits de convergence sont dans `.factory/assembleur/`.
- `.gitignore` contient la ligne `.factory/`.
- `assembleur-out/` (avec `features/` et `memory/`) existe.
- Le manifeste contient le bloc `assembly` (`phase: "init"`), et reparse sans erreur.
- **État de l'amont signalé** : si un dossier `-out/` amont manque ou est vide, l'utilisateur a
  été **averti** (pas bloqué).
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision de convergence.** Ce skill prépare ; il ne converge rien.
- **Jamais bloquant.** Le terrain de convergence se pose toujours ; un `-out/` amont manquant
  **avertit**, ne refuse pas.
- **Vérification, pas validation.** L'assembleur ne juge pas si l'amont est "validé" : il
  vérifie seulement que les fichiers de sortie sont **là et non vides**, et le **signale**. Aucun
  flag de validation lu ni exigé.
- **Aucun hook à poser.** L'assembleur n'a **pas de hook ni d'enforcement propre** à installer :
  l'enforcement (hooks de test + formatage `PostToolUse`) est posé **en amont par `architecte-init`**
  et déjà committé dans le repo (la protection de branche est gérée côté GitHub) ; l'assembleur n'a
  donc **rien à poser** de ce côté.
- **Paquet seul.** Aucun repo cible ; tout ira dans `assembleur-out/`.
- **Manifeste silencieux.** Ne jamais annoncer que le manifeste est créé/mis à jour ni afficher un
  `champ: valeur`/`true`/`false` ; confirmer en clair ce qui est posé + la suite (cf.
  `references/ux-conventions.md`).
- **Skill indépendant.** La cohérence passe par le manifeste partagé.

Étape suivante : `/assembleur:assembleur-convergence` - lire les 3 contrats en parallèle, les converger et produire le paquet de handoff SpecKit.
