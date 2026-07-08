---
name: cadrage-init
description: Amorce le workspace du projet, installe les gabarits et crée le manifeste.
---

# cadrage-init

Skill d'amorçage du plugin `cadrage` : **tout premier skill** à lancer sur un
projet. Il pose le squelette de travail d'un projet client : l'arborescence, les
gabarits installés et le manifeste. Tous les autres skills supposent qu'il a déjà tourné.

## Objectif

Rendre un projet client **prêt à être cadré** : un dossier caché **`.factory/`**
(manifeste + gabarits, la mécanique interne), un dossier de sortie **`cadrage-out/`**
à la racine pour les documents générés, un dossier `cadrage-out/prompts/` pour les
prompts générés, un dossier `cadrage-out/source-contexte/` où l'utilisateur dépose la
matière brute du projet (emplacement central, **facultatif**), un dossier
`cadrage-out/maquette-de-claude-design/` (vide au départ) où l'utilisateur collera la **maquette du
démonstrateur** générée par Claude Design, et un manifeste initialisé.

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** — celui où la session est lancée (le
cwd) — **jamais** un dossier parent, **jamais** un `.factory/` / `factory-docs/` /
`*-out/` situé plus haut. Tout ce que ce skill installe (`.factory/`, `cadrage-out/`,
`cadrage-out/source-contexte/`, `cadrage-out/maquette-de-claude-design/`, `cadrage-out/prompts/`) est créé **sous ce dossier**. **Ne jamais remonter l'arborescence**
pour trouver un workspace existant : un `.factory/` (ou `factory-docs/`) trouvé dans un
dossier **parent** n'appartient **pas** à ce projet — l'ignorer et créer le workspace
dans le cwd. En cas de doute sur un chemin relatif, l'écrire en **absolu à partir du cwd**.

## Pré-requis (vérification silencieuse)

**Aucun.** Invocable sur un projet vierge. **Idempotent** : si un fichier existe
déjà, ne pas l'écraser ; n'installer que le manquant.

## Procédure

> **Ce skill ne demande PAS le nom du projet.** Cette question est posée par
> `cadrage-extraction`, en tête de sa passe (avec les questions de découverte) —
> c'est plus cohérent. Ici, `project` reste `null` dans le manifeste, à renseigner
> par `cadrage-extraction`. **Le nom du client n'est jamais demandé ni stocké.**

1. **Créer l'arborescence** à la racine du projet client. **`prompts/` est un
   sous-dossier de `cadrage-out/`, jamais un dossier à la racine** (chemin exact :
   `cadrage-out/prompts/`) :
   ```
   .factory/                        (caché — la mécanique interne)
   ├── manifest.json                (fichier — contrat machine)
   └── cadrage/                     (gabarits du cadrage — copies blanches installées)
   cadrage-out/                     (documents générés par le cadrage, à la racine)
   ├── source-contexte/             (matière brute du projet — déposée par l'utilisateur, facultatif)
   ├── features-fonctionnels-brief/ (un brief par feature)
   ├── maquette-de-claude-design/   (maquette du démonstrateur collée par l'utilisateur — vide au départ)
   └── prompts/                     (prompts générés — bien SOUS cadrage-out/)
   ```
2. **Installer les gabarits** dans `.factory/cadrage/` : copier les gabarits
   du plugin (`project-frame.md`, `product-brief.md`, `feature-brief.md`,
   `spec-index.md`, `coupling-map.md`, `glossaire.md`). Ce sont les copies de
   travail du projet — les skills les lisent depuis là. Copier aussi la référence
   des questions de découverte (`discovery-questions.md`) dans `.factory/cadrage/`.
   Puis **créer `cadrage-out/` (avec ses sous-dossiers `source-contexte/`,
   `features-fonctionnels-brief/` et `maquette-de-claude-design/`) vide** ; les artefacts s'y
   déposeront au fil des skills, et l'utilisateur collera la maquette du démonstrateur dans
   `maquette-de-claude-design/`.
3. **Écrire le manifeste** `.factory/manifest.json` (squelette ci-dessous ;
   laisser `project` à `null` — il sera renseigné par `cadrage-extraction` ; pas de
   champ `client` ; dates en ISO 8601, laisser le reste neutre).
   **Si le manifeste existe déjà** (par ex. un `-init` de phase aval l'a créé avec un bloc
   `architecture`), **ne pas repartir de zéro ni écraser** : le lire et **fusionner** — ajouter
   uniquement les clés de cadrage **manquantes** (project, dates, phase, sources, artifacts,
   demonstrateur, validation_points, prompts, discovery, discovery_complete,
   definition_of_ready), en **préservant** tout bloc déjà présent (dont `architecture`), puis
   revalider le JSON.
4. **Laisser `cadrage-out/prompts/` vide** : il se remplit au fil des prompts générés
   (voir `cadrage-demonstrateur-brief` et les autres skills à prompt).
5. **Git-ignore `.factory/` (première version du `.gitignore` du projet)** : le cadrage **génère la
   première version** du `.gitignore` du projet — le seul `-init` qui le crée normalement. S'assurer
   qu'il **contient** la ligne `.factory/` : le **créer s'il est absent**, sinon **ajouter** la ligne
   manquante (sans dupliquer si déjà présente), en **préservant** le reste. Les phases aval (architecte,
   designer, assembleur) ne font ensuite que **compléter** ce même fichier — elles ne le réécrivent
   jamais. Tout `.factory/` est local, non versionné.
6. **Inviter à centraliser le contexte** : afficher en clair, **en gras**, l'invitation
   suivante à l'utilisateur —
   > **Déposez tous vos fichiers de contexte du projet dans `cadrage-out/source-contexte/` : transcriptions, comptes rendus, fichiers Markdown, PDF, DOCX ou tout autre format.**
   >
   > C'est l'emplacement central de la matière brute, repris automatiquement par `cadrage-extraction`.

   Cette invitation est **facultative** : si l'utilisateur ne dépose rien, le cadrage
   **démarre quand même** (les sources pourront être fournies autrement). Ce dossier n'est
   **jamais** une porte de validation ni une source obligatoire.

7. **Inviter à coller la maquette du démonstrateur** : afficher en clair, **en gras**, l'invitation
   suivante à l'utilisateur —
   > **Collez la maquette du démonstrateur — l'export généré par Claude Design — directement dans le dossier `cadrage-out/maquette-de-claude-design/`.**
   >
   > **Format attendu : le dossier de fichiers DÉZIPPÉ** (les fichiers HTML/CSS/JS et les assets tels quels) — **pas une archive ZIP**. Si vous n'avez qu'un `.zip`, **dézippez-le dans ce dossier**.
   >
   > *(Raison : la maquette reste ainsi directement consultable et lisible dans le repo ; un `.zip` est un blob binaire que git ne sait pas comparer et que les étapes suivantes devraient extraire.)*
   >
   > C'est l'emplacement de la **maquette de validation du cadrage** (le démonstrateur montré au client).

   Cette invitation est **facultative** elle aussi : le dossier est créé **vide** à l'init et se
   remplira quand la maquette existera (après `cadrage-demonstrateur-brief`). Il n'est **jamais** une
   porte de validation ni une source obligatoire.

```json
{
  "project": null,
  "created_at": "<ISO 8601 — horodaté à l'exécution>",
  "updated_at": "<ISO 8601 — horodaté à l'exécution>",
  "phase": "init",
  "sources": [],
  "artifacts": {
    "capture_brute": { "path": "cadrage-out/capture-brute.md", "status": "draft" },
    "project_frame": { "path": "cadrage-out/project-frame.md", "status": "draft" },
    "product_brief": { "path": "cadrage-out/product-brief.md", "status": "draft" },
    "glossaire": { "path": "cadrage-out/glossaire.md", "terms": 0, "validated_terms": 0 },
    "spec_index": { "path": "cadrage-out/spec-index.md", "features": 0, "arbitrated": false },
    "briefs": []
  },
  "demonstrateur": {
    "current_version": 0,
    "external_ref": null,
    "client_validated": false,
    "iterations": []
  },
  "validation_points": [],
  "prompts": [],
  "discovery": [
    { "id": "Q1",  "question": "Qui utilise l'application ?", "status": "pending", "answer": null },
    { "id": "Q2",  "question": "Combien d'utilisateurs differents ? combien en meme temps ?", "status": "pending", "answer": null },
    { "id": "Q3",  "question": "Quels roles d'utilisateurs ?", "status": "pending", "answer": null },
    { "id": "Q4",  "question": "Quelles donnees sont sauvegardees ? quantite, contenu, sensibilite ?", "status": "pending", "answer": null },
    { "id": "Q5",  "question": "Quels systemes externes a integrer ?", "status": "pending", "answer": null },
    { "id": "Q6",  "question": "Quelle disponibilite du systeme est requise ?", "status": "pending", "answer": null },
    { "id": "Q7",  "question": "Contraintes de performance ?", "status": "pending", "answer": null },
    { "id": "Q8",  "question": "Contraintes legales ?", "status": "pending", "answer": null },
    { "id": "Q9",  "question": "Type de projet ? (ponctuel, long terme, perimetre vise)", "status": "pending", "answer": null },
    { "id": "Q10", "question": "Qui s'occupe de la production ? le client ? nous ?", "status": "pending", "answer": null },
    { "id": "Q11", "question": "Ou est deployee l'appli ? infra existante ou nouvelle ? cloud ?", "status": "pending", "answer": null },
    { "id": "Q12", "question": "Budget pour l'infrastructure ?", "status": "pending", "answer": null },
    { "id": "Q13", "question": "Besoins particuliers d'authentification / autorisation ?", "status": "pending", "answer": null }
  ],
  "discovery_complete": false,
  "definition_of_ready": {
    "vision_complete": false,
    "glossary_validated": false,
    "decoupage_arbitrated": false,
    "all_briefs_complete": false,
    "no_blocking_gaps": false,
    "demonstrateur_converged": false,
    "cadrage_complete": false
  }
}
```

Le bloc `prompts` trace les prompts générés (démonstrateur et livrables visuels),
sauvegardés sous `cadrage-out/prompts/`. Le bloc `demonstrateur` porte la boucle
d'itération ; `validation_points[]` ne sert qu'aux points actifs de cette boucle —
**aucun point de découpage ouvert ou laissé de côté n'y est persisté** (rien
d'irrésolu n'est écrit). Toute écriture du manifeste est un **read-modify-write**
suivi d'une **revalidation JSON**.

**Dates.** `created_at` et `updated_at` sont deux horodatages ISO 8601 réels et
cohérents, posés **au moment de l'exécution**. Ne pas confondre la date de la
réunion ou de l'atelier avec la date du jour : ces deux champs portent l'instant de
création/mise à jour du manifeste, pas la date d'une source.

## Résultat attendu

- `.factory/` (avec `manifest.json` et `cadrage/`), `cadrage-out/` (avec
  `source-contexte/`, `features-fonctionnels-brief/` et `maquette-de-claude-design/`) et
  `cadrage-out/prompts/` existent ; `cadrage-out/` est créé et vide.
- `.factory/cadrage/` contient les 6 gabarits installés.
- L'utilisateur a reçu l'invitation **en gras** à déposer sa matière brute dans
  `cadrage-out/source-contexte/` (facultatif — n'empêche jamais de démarrer).
- L'utilisateur a reçu l'invitation **en gras** à coller la maquette du démonstrateur (générée par
  Claude Design) dans `cadrage-out/maquette-de-claude-design/` (facultatif — dossier créé **vide**).
- `.gitignore` contient la ligne `.factory/`.
- `.factory/manifest.json` reparse sans erreur, `phase = "init"`.
- `project` est à `null` (il sera renseigné par `cadrage-extraction`) ; pas de champ `client`.
- Rien d'existant n'a été écrasé (idempotence).

## Règles invariantes appliquées ici

- **Idempotent.** N'installe que le manquant ; ne détruit jamais un travail en
  cours.
- **Skill indépendant.** La cohérence passe par le manifeste, pas par un
  orchestrateur.
- **Frontière claire.** Les gabarits installés appartiennent au projet ; le plugin
  reste la source canonique mais n'est pas modifié par le projet.

Étape suivante : `/cadrage:cadrage-extraction` — dépouiller la matière brute de l'atelier en capture structurée.
