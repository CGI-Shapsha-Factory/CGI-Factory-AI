---
name: maintenance-init
description: Amorce la phase de maintenance : installe les gabarits d'anomalie et d'évolution, étend le manifeste et vérifie le raccordement Linear (équipe, labels, statut de requalification).
---

# maintenance-init

Skill d'amorçage de la phase **maintenance** : **tout premier skill** à lancer quand une feature
livrée entre en recette (après la fabrication SpecKit, donc après l'assembleur et la première
alimentation de Linear). Il prépare le terrain (zéro décision) ; les 4 skills métier
(`creation-anomalie`, `correction-anomalie`, `creation-evolution`, `realisation-evolution`)
supposent qu'il a tourné.

## Objectif
Rendre un projet **prêt pour la maintenance** : installer les gabarits de ticket, étendre le
manifeste partagé avec un bloc `maintenance` (configuration statique seulement), et vérifier le
raccordement Linear (équipe, labels de maintenance, statut de requalification).

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** - celui où la session est lancée (le cwd) -
**jamais** un dossier parent, **jamais** un `.factory/` / `*-out/` situé plus haut. Tous les
chemins de ce skill (`manifest.json`, `.factory/maintenance/`, `.gitignore`, `specs/`) se résolvent
**sous ce dossier**. **Ne jamais remonter l'arborescence** pour trouver le manifeste ou les
dossiers amont : un `manifest.json` situé dans un dossier **parent** n'appartient **pas** à ce
projet - le traiter comme **absent** (ne jamais le lire ; on crée/étend le manifeste **du
cwd**). En cas de doute sur un chemin relatif, l'écrire en **absolu à partir du cwd**.

## `.factory/` d'abord : clone frais, `.factory/` git-ignoré (impératif)
`.factory/` est **entièrement git-ignoré** : il ne voyage **jamais** avec le repo. La maintenance
peut être menée par **une autre personne**, sur une **autre machine**, à partir d'un **clone
frais** où **aucun `.factory/` n'existe encore**. Ce skill ne présuppose donc **jamais** un
`.factory/` déjà présent : **avant toute autre chose**, il (re)pose dans `.factory/maintenance/`
les deux gabarits (`gabarit-anomalie.md`, `gabarit-evolution.md`) et le bloc `maintenance` du
manifeste `manifest.json` (créé s'il manque).

## Setup inconditionnel + état de l'amont (jamais bloquant)
**Ce skill ne bloque jamais.** L'installation des gabarits et l'amorçage du bloc `maintenance`
sont déterministes : ils s'installent **toujours**, dans le dossier courant. **Ne jamais
refuser** au motif que Linear, l'assembleur ou SpecKit manquent - on installe, puis on
**signale en clair** ce qui manque pour que la maintenance soit opérante.

**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant. Si
`manifest.json` n'existe pas encore, le **créer à la racine du projet** (le cwd) comme objet
JSON valide `{ "maintenance": { ... } }` (les autres phases le complètent par fusion, sans écraser
le bloc `maintenance`).

## Procédure
1. **Installer les gabarits** dans `.factory/maintenance/` (copier depuis le plugin `templates/`) :
   `gabarit-anomalie.md`, `gabarit-evolution.md`.
2. **Étendre le manifeste** `manifest.json` : ajouter le bloc `maintenance` ci-dessous s'il est
   absent (read-modify-write + revalidation JSON) :

```json
"maintenance": {
  "phase": "init",
  "team": null,
  "labels": { "anomalie": null, "evolution": null },
  "statut_requalification": { "name": "Requalifiée en évolution", "present": false }
}
```

   *Le bloc ne porte que la configuration statique. Les anomalies, les évolutions et leurs
   statuts vivent **uniquement dans Linear** (activité concurrente, jamais dans le fichier
   committé - cf. `references/linear-maintenance.md`).*
3. **Git-ignore `.factory/` (compléter, jamais réécrire)** : le **`.gitignore` est généré en
   premier par le cadrage** et **committé**. **Ne jamais le réécrire ni l'écraser** : s'assurer
   seulement qu'il **contient** la ligne `.factory/` - l'**ajouter** si elle manque (sans
   dupliquer), en **préservant** le reste. **Le créer uniquement s'il est absent** (clone où le
   cadrage n'a pas tourné ici).
4. **Sonder Linear** (signaler, jamais refuser - cf. `references/linear-maintenance.md`) :
   - **Détection du MCP** : `list_teams`. S'il ne répond pas, signaler que les skills de
     maintenance ne pourront rien créer dans Linear tant que le plugin `linear-prism` n'est pas
     installé et authentifié (afficher les instructions d'installation de
     `references/linear-maintenance.md`), et s'arrêter là pour cette étape (le reste du setup est
     déjà posé).
   - **Équipe** : reprendre celle du bloc `linear` du manifeste (posée par l'assembleur) ; à
     défaut, `list_teams` et confirmation avec l'utilisateur. La retenir dans le bloc `maintenance`.
   - **Labels** : résoudre `Anomalie` et `Evolution` par nom via `list_issue_labels`
     (insensible à la casse) ; créer via `create_issue_label` ceux qui manquent (best-effort).
     Retenir leurs UUID dans le bloc `maintenance`.
   - **Statut de requalification** : chercher "Requalifiée en évolution" dans
     `list_issue_statuses({team})`. S'il existe (famille des statuts annulés), le noter comme
     présent. S'il manque, **afficher la marche à suivre manuelle** (section "Statut
     'Requalifiée en évolution'" de `references/linear-maintenance.md`) et le noter comme absent -
     la maintenance peut démarrer, mais la requalification d'une anomalie attendra ce statut.
5. **Signaler l'état de l'amont** (sans bloquer) : si le bloc `linear` du manifeste est vide
   (aucun ticket Feature : la première alimentation de Linear n'a pas eu lieu) ou si `specs/`
   n'existe pas dans le repo (aucune feature fabriquée), avertir en clair que la maintenance n'a
   pas encore d'objet et nommer ce qui manque (`/assembleur:premier-alimente-linear`, ou la
   fabrication SpecKit de la première feature).

## Porte de sortie (vérification silencieuse)
- Les 2 gabarits sont dans `.factory/maintenance/`.
- `.gitignore` contient la ligne `.factory/`.
- Le manifeste contient le bloc `maintenance` et reparse sans erreur.
- L'équipe, les labels et le statut de requalification ont été sondés (ou l'absence du MCP a
  été signalée avec les instructions d'installation).
- **État de l'amont signalé** : si les tickets Feature ou `specs/` manquent, l'utilisateur a
  été **averti** (pas bloqué).
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes
- **Aucune décision de maintenance.** Ce skill prépare le terrain ; il ne crée ni ne modifie aucun
  ticket d'anomalie ou d'évolution.
- **Jamais bloquant.** Le setup s'amorce toujours ; l'amont manquant **avertit**, ne refuse pas.
- **Mécanique interne silencieuse.** Ne jamais annoncer à l'utilisateur le manifeste (ni un
  `champ: valeur`/`true`/`false`) **ni les gabarits installés dans `.factory/`** (dossier caché
  git-ignoré, sans intérêt pour l'utilisateur) ; confirmer en clair seulement ce qui lui est utile
  (dossier de sortie, invitations, raccordements) + la prochaine étape (cf.
  `references/ux-conventions.md`).
- **Typographie humaine** : aucun glyphe de style IA dans les sorties (cf. la section
  Typographie de `references/ux-conventions.md`).

Étape suivante : `/maintenance:creation-anomalie` ou `/maintenance:creation-evolution` - créer le premier écart constaté en recette, selon sa nature.
