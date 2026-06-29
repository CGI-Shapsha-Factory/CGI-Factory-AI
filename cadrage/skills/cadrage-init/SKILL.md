---
name: cadrage-init
description: Amorce le workspace du projet, installe les gabarits et crée le manifeste.
---

# cadrage-init

Skill d'amorçage du plugin `cadrage` : **tout premier skill** à lancer sur un
projet. Il pose le squelette de travail d'un projet client : l'arborescence, les
gabarits installés et le manifeste. Tous les autres skills supposent qu'il a déjà tourné.

## Objectif

Rendre un projet client **prêt à être cadré** : un workspace `factory-docs/`
auto-portant (gabarits inclus), un dossier `factory-prompts/` pour les prompts
générés, et un manifeste initialisé.

## Pré-requis (vérification silencieuse)

**Aucun.** Invocable sur un projet vierge. **Idempotent** : si un fichier existe
déjà, ne pas l'écraser ; n'installer que le manquant.

## Procédure

> **Ce skill ne demande PAS le nom du projet.** Cette question est posée par
> `cadrage-extraction`, en tête de sa passe (avec les questions de découverte) —
> c'est plus cohérent. Ici, `project` reste `null` dans le manifeste, à renseigner
> par `cadrage-extraction`. **Le nom du client n'est jamais demandé ni stocké.**

1. **Créer l'arborescence** à la racine du projet client (workspace **à plat** :
   tous les artefacts vivent dans `work/`, sans sous-dossiers de phase) :
   ```
   factory-docs/
   ├── manifest.json        (fichier — contrat machine)
   ├── templates/           (copies blanches des gabarits installés)
   └── work/                (tous les artefacts remplis, à plat)
   factory-prompts/         (sibling de factory-docs — prompts générés)
   ```
2. **Installer les gabarits** dans `factory-docs/templates/` : copier les gabarits
   du plugin (`project-frame.md`, `product-brief.md`, `feature-brief.md`,
   `spec-index.md`, `coupling-map.md`, `glossaire.md`, `pre-constitution.md`). Ce
   sont les copies de travail du projet — les skills les lisent depuis là. Copier
   aussi la référence des questions de découverte (`discovery-questions.md`) dans
   `factory-docs/templates/`. Puis **créer `factory-docs/work/` vide** ; les
   artefacts s'y déposeront au fil des skills.
3. **Écrire le manifeste** `factory-docs/manifest.json` (squelette ci-dessous ;
   laisser `project` à `null` — il sera renseigné par `cadrage-extraction` ; pas de
   champ `client` ; dates en ISO 8601, laisser le reste neutre).
4. **Laisser `factory-prompts/` vide** : il se remplit au fil des prompts générés
   (voir `cadrage-demonstrateur-brief` et les autres skills à prompt).

```json
{
  "project": null,
  "created_at": "<ISO 8601 — horodaté à l'exécution>",
  "updated_at": "<ISO 8601 — horodaté à l'exécution>",
  "phase": "init",
  "sources": [],
  "artifacts": {
    "capture_brute": { "path": "factory-docs/work/capture-brute.md", "status": "draft" },
    "project_frame": { "path": "factory-docs/work/project-frame.md", "status": "draft" },
    "product_brief": { "path": "factory-docs/work/product-brief.md", "status": "draft" },
    "glossaire": { "path": "factory-docs/work/glossaire.md", "terms": 0, "validated_terms": 0 },
    "spec_index": { "path": "factory-docs/work/spec-index.md", "features": 0, "arbitrated": false },
    "briefs": [],
    "pre_constitution": { "path": "factory-docs/work/pre-constitution.md", "status": "absent" }
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
    "ready_for_speckit": false
  }
}
```

Le bloc `prompts` trace les prompts générés (démonstrateur et livrables visuels),
sauvegardés sous `factory-prompts/`. Le bloc `demonstrateur` porte la boucle
d'itération ; `validation_points[]` ne sert qu'aux points actifs de cette boucle —
**aucun point de découpage ouvert ou laissé de côté n'y est persisté** (rien
d'irrésolu n'est écrit). Toute écriture du manifeste est un **read-modify-write**
suivi d'une **revalidation JSON**.

**Dates.** `created_at` et `updated_at` sont deux horodatages ISO 8601 réels et
cohérents, posés **au moment de l'exécution**. Ne pas confondre la date de la
réunion ou de l'atelier avec la date du jour : ces deux champs portent l'instant de
création/mise à jour du manifeste, pas la date d'une source.

## Résultat attendu

- `factory-docs/` (avec `templates/` et `work/` à plat) et `factory-prompts/`
  existent ; `work/` est créé et vide.
- `factory-docs/templates/` contient les 7 gabarits installés.
- `factory-docs/manifest.json` reparse sans erreur, `phase = "init"`.
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
