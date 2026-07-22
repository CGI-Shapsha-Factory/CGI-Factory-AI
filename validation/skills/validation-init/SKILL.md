---
name: validation-init
description: Amorce la phase de validation fonctionnelle : installe les gabarits (plan de test, mission Cowork, rapport de recette, scénario rejouable), étend le manifeste et enregistre l'environnement de recette.
---

# validation-init

Skill d'amorçage de la **validation fonctionnelle** : **tout premier skill** à lancer quand une
feature livrée doit passer en recette fonctionnelle (après la fabrication SpecKit, donc après
l'assembleur et la première alimentation de Linear). Il prépare le terrain ; les 3 skills
métier (`plan-de-validation`, `execution-validation`, `rapport-de-recette`) supposent qu'il a
tourné.

## Objectif
Rendre un projet **prêt pour la validation fonctionnelle** : installer les gabarits, étendre
le manifeste partagé avec un bloc `validation` (configuration statique seulement), enregistrer
l'adresse de l'environnement de recette, et signaler ce qui manque en amont.

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** - celui où la session est lancée (le cwd) -
**jamais** un dossier parent, **jamais** un `.factory/` / `*-out/` situé plus haut. Tous les
chemins de ce skill (`manifest.json`, `.factory/validation/`, `validation-out/`, `.gitignore`,
`specs/`) se résolvent **sous ce dossier**. **Ne jamais remonter l'arborescence** : un
`manifest.json` situé dans un dossier **parent** n'appartient **pas** à ce projet - le traiter
comme **absent** (ne jamais le lire ; on crée/étend le manifeste **du cwd**). En cas de doute
sur un chemin relatif, l'écrire en **absolu à partir du cwd**.

## `.factory/` d'abord : clone frais, `.factory/` git-ignoré (impératif)
`.factory/` est **entièrement git-ignoré** : il ne voyage **jamais** avec le repo. La
validation peut être menée par **une autre personne**, sur une **autre machine**, à partir d'un
**clone frais** où **aucun `.factory/` n'existe encore**. Ce skill ne présuppose donc
**jamais** un `.factory/` déjà présent : **avant toute autre chose**, il (re)pose dans
`.factory/validation/` les quatre gabarits (`plan-de-test.md`, `mission-cowork.md`,
`rapport-de-recette.md`, `scenario-rejouable.md`) et le bloc `validation` du manifeste
`manifest.json` (créé s'il manque).

## Setup inconditionnel + état de l'amont (jamais bloquant)
**Ce skill ne bloque jamais.** L'installation des gabarits et l'amorçage du bloc `validation`
sont déterministes : ils s'installent **toujours**, dans le dossier courant. **Ne jamais
refuser** au motif que Linear, la maintenance ou SpecKit manquent - on installe, puis on **signale
en clair** ce qui manque pour que la validation soit opérante.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant. Si
`manifest.json` n'existe pas encore, le **créer à la racine du projet** (le cwd) comme objet
JSON valide `{ "validation": { ... } }` (les autres phases le complètent par fusion, sans
écraser le bloc `validation`).

## Procédure
1. **Installer les gabarits** dans `.factory/validation/` (copier depuis le plugin
   `templates/`) : `plan-de-test.md`, `mission-cowork.md`, `rapport-de-recette.md`,
   `scenario-rejouable.md`. Créer `validation-out/` s'il n'existe pas.
2. **Étendre le manifeste** `manifest.json` : ajouter le bloc `validation` ci-dessous s'il est
   absent (read-modify-write + revalidation JSON) :

```json
"validation": {
  "phase": "init",
  "environnement_recette": null,
  "outil_prefere": null
}
```

   *Le bloc ne porte que la configuration statique (l'adresse de recette, la préférence
   d'outil). Les verdicts, l'avancement et les écarts vivent dans le rapport committé de
   `validation-out/` et **dans Linear** - jamais dans le manifeste (cf.
   `references/regles-validation.md`).*
3. **Enregistrer l'environnement de recette** : demander au testeur l'adresse de l'application
   déployée à tester **avec `AskUserQuestion`** (cf. `references/interactive-loop.md`) - les
   options portent les adresses plausibles lues dans le projet (variable de déploiement,
   documentation, URL locale servie, ouverture directe du fichier), la plus crédible en premier
   avec la mention "(recommandé)", et la saisie libre reste ouverte. **Jamais de question en
   prose.**
   La retenir dans le bloc `validation`, en silence. S'il préfère la donner plus tard, ne rien
   écrire et signaler que l'exécution la redemandera.
4. **Git-ignore `.factory/` (compléter, jamais réécrire)** : le **`.gitignore` est généré en
   premier par le cadrage** et **committé**. **Ne jamais le réécrire ni l'écraser** : s'assurer
   seulement qu'il **contient** la ligne `.factory/` - l'**ajouter** si elle manque (sans
   dupliquer), en **préservant** le reste. **Le créer uniquement s'il est absent** (clone où le
   cadrage n'a pas tourné ici).
5. **Signaler l'état de l'amont** (sans bloquer) :
   - `specs/` absent du repo (aucune feature fabriquée) -> avertir que la validation n'a pas
     encore d'objet et nommer ce qui manque (la fabrication SpecKit de la première feature).
   - Bloc `linear` du manifeste vide ou MCP `linear-prism` muet -> avertir que le rapport ne
     pourra pas être relié aux tickets Feature ni les écarts tracés dans Linear tant que la
     première alimentation (`/assembleur:premier-alimente-linear`) et le MCP ne sont pas en
     place (installation du MCP : section Linear de `references/regles-validation.md`).
   - Bloc `maintenance` absent du manifeste -> signaler que le traitement des écarts passera par le
     plugin maintenance : lancer `/maintenance:maintenance-init` avant le premier bilan (les anomalies et
     évolutions se créent là-bas, jamais ici).

## Porte de sortie
- Les 4 gabarits sont dans `.factory/validation/` et `validation-out/` existe.
- `.gitignore` contient la ligne `.factory/`.
- Le manifeste contient le bloc `validation` et reparse sans erreur.
- L'adresse de l'environnement de recette est enregistrée (ou son absence a été signalée).
- **État de l'amont signalé** : si `specs/`, Linear ou la maintenance manquent, l'utilisateur a
  été **averti** (pas bloqué).
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision de validation.** Ce skill prépare le terrain ; il ne dérive aucun plan,
  n'exécute aucun test, ne prononce aucun verdict.
- **Jamais bloquant.** Le setup s'amorce toujours ; l'amont manquant **avertit**, ne refuse pas.
- **Manifeste silencieux.** Ne jamais annoncer que le manifeste est créé/mis à jour ni afficher
  un `champ: valeur`/`true`/`false` ; confirmer en clair ce qui est amorcé + la suite (cf.
  `references/ux-conventions.md`).
- **Typographie humaine** : aucun glyphe de style IA dans les sorties (cf. la section
  Typographie de `references/ux-conventions.md`).
- **Toujours afficher la phrase "Étape suivante"** avec ses branches en fin d'exécution, même
  si l'amont manque (cf. la section 5 de `references/ux-conventions.md`).
- **Jamais de cul-de-sac, et toute question passe par `AskUserQuestion`.** Y compris les
  réponses libres comme l'adresse de recette : les options portent les candidats plausibles et
  la saisie libre reste ouverte. **Aucune question rédigée en prose dans le fil**, et on ne rend
  jamais la main sans question quand on attend quelque chose du testeur (cf.
  `references/interactive-loop.md`).

Étape suivante : `/validation:plan-de-validation` - dériver le plan de test de la feature livrée à recetter. Ou `/maintenance:maintenance-init` d'abord si le terrain de maintenance manque (il faut l'avoir posé avant le premier bilan, c'est là que se créent les anomalies et les évolutions). Ou `/assembleur:premier-alimente-linear` si les tickets Linear n'ont jamais été créés et que tu veux que le rapport soit relié à sa feature.
