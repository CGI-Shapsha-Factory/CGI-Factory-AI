---
name: init-linear
description: Initialise les features (registre figé) dans Linear — clé API dans .env, dédup d'un projet existant, défauts Todo/non-assigné, carte issue↔feature pour le hook — après validation de l'équipe.
---

# init-linear

Crée le **projet Linear** et **une issue par feature** du découpage figé, **après** la validation de
l'équipe (porte 5). L'écriture Linear (effet de bord live) n'a lieu qu'une fois la **porte humaine**
franchie. **Source de vérité de l'existant = Linear** (pas le flag local : un collègue a pu déjà
initialiser sur sa machine).

## Porte d'entrée
`assembly.coherence_validated == true` **ET** `assembly.team_validated == true` (l'équipe a arbitré le
découpage via `assembleur-amorce`). Sinon, **refuser en clair** :
> « L'initialisation Linear ne peut pas démarrer : l'équipe doit d'abord valider le découpage. »
et orienter vers `/assembleur:assembleur-amorce`. Le découpage = le **registre canonique**
`architecture.feature_sequence` (objets `{id, ucs, name, mvp}`).

## Étape 1 — Connexion à Linear (clé API personnelle dans `.env`)
Lire la clé API Linear depuis `.env` (variable **`LINEAR_API_KEY`**).
- **Si absente** → **afficher les étapes** pour la créer, puis **s'arrêter** (relancer ensuite) :
  1. Dans Linear : avatar / profil → **Settings**.
  2. Barre latérale → **Security & access**.
  3. Section **Personal API keys** → **New API key**.
  4. Nommer la clé (ex. « factory-init »), donner au moins l'accès **Create issues** (ou *Write*), **Create**.
  5. **Copier** la clé `lin_api_…` (affichée **une seule fois**).
  6. La placer dans le fichier **`.env`** à la racine du projet : `LINEAR_API_KEY=lin_api_…`, et
     **vérifier que `.env` est gitignored** (la clé ne doit **jamais** être commitée ni affichée).
  - Puis relancer `/assembleur:init-linear`.
- **Si présente** → l'utiliser pour appeler l'**API Linear GraphQL** (`https://api.linear.app/graphql`,
  en-tête **`Authorization: <LINEAR_API_KEY>`** — sans « Bearer »). Voir `references/linear-guide.md`
  pour les requêtes/mutations. **Ne jamais afficher la clé**, ne jamais la loguer ni la commiter.

## Étape 2 — Cibler le workspace et l'équipe
- Confirmer le **workspace** Linear (l'utilisateur peut en avoir plusieurs — ne pas écrire dans le mauvais).
- Lister les **équipes** (une issue appartient à une équipe). Une seule → l'utiliser ; plusieurs →
  demander laquelle (boucle 3-options) ; aucune ou pas de droits → signaler et s'arrêter.

## Étape 3 — Chercher un projet existant similaire (Linear = source de vérité)
Un collègue a pu **déjà initialiser** le projet : le flag local ne le voit pas → on **interroge Linear**.
- Nom candidat = `manifest.project`. Lister/chercher les projets du workspace ; comparer par **nom
  normalisé** (casse, espaces, accents) + similarité (sous-chaîne / chevauchement de mots) et repérer un
  projet aux **tâches similaires** (features).
- **Si un projet similaire existe** : **préciser à l'utilisateur** qu'un projet avec des tâches
  similaires existe déjà dans le workspace (nom, auteur, date de création, nombre d'issues), **donner le
  lien direct** vers ce projet, **le conseiller** sur l'option (réutiliser et compléter / créer un nouveau
  projet distinct / vérifier avec le collègue), puis **S'ARRÊTER — ne rien écrire**. L'utilisateur tranche
  et relance.
- **Si aucun projet similaire** → continuer (créer).

## Étape 4 — Créer le projet + les issues (défauts : Todo, non assigné)
- Déterminer l'état **« Todo »** de l'équipe = le workflow state de **type `unstarted`** — **jamais le
  `backlog`**. Pas d'état `unstarted` → demander lequel utiliser (fallback : premier état ni backlog ni
  terminé). **Ne jamais mettre en Backlog par défaut.**
- Créer le **projet** Linear : nom = `manifest.project` ; description = résumé (constitution /
  product-brief) + lien du repo SpecKit.
- Pour **chaque** feature de `architecture.feature_sequence`, dans l'ordre (walking skeleton d'abord) :
  - **titre** = `<id> — <name>` (ex. « 001 — Recherche Q&A sourcée ») ;
  - **description** = résumé du brief 3-faces + lien `specs/<id>-feature/spec.md` ;
  - **état = Todo** (`unstarted`) — **jamais Backlog** ;
  - **assigné = personne** (non assigné) ;
  - **labels** : `feature:<id>` (clé de dédup stable), `walking-skeleton` (si `001`), `MVP` (si `mvp`) ;
  - **dépendances** = relations `blocked-by` selon la séquence.
  - **Dédup** : si une issue portant `feature:<id>` (ou le préfixe `<id> —`) existe déjà dans le projet,
    **ne pas la recréer**.
- **Tracer** dans le manifeste : `assembly.linear_project` (`{id, name, url}`), `assembly.linear_issues[]`
  (`{feature, ucs, linear_id, identifier, url, state, assignee}` — `linear_id` = uuid, **`identifier`** =
  forme courte type `ENG-123`), `assembly.linear_initialized = true`, `assembly.phase = "amorce"`.

## Étape 4bis — Carte issue↔feature pour le hook aval (Todo → En cours)
Écrire `<target_repo>/.claude/linear-map.json` = liste `{feature, id, identifier, url, branch_slug}`
(`id` = uuid, `branch_slug` = slug du nom). Elle permet au **hook `linear-start.py`** (généré par
`assembleur-amorce`) de retrouver l'issue depuis la branche git **sans dépendre** du chemin
`factory-docs/`. Indiquer la **convention de branche** : `<identifier>-<slug>` (ex.
`eng-123-recherche-qa`) — c'est la clé de résolution du hook **et** du filet natif Linear.

## Étape 5 — Restitution
Récapituler en clair : projet créé (lien) + N issues créées (M réutilisées), **toutes en Todo et non
assignées**, avec les liens.

## Idempotence
Si `assembly.linear_initialized == true` (déjà fait sur cette machine) : afficher `assembly.linear_issues`
et s'arrêter (pas de doublon). La recherche de l'étape 3 couvre, elle, le cas d'un collègue.

## Fallback (clé API absente / API indisponible)
**Ne rien inventer.** Produire `factory-docs/work/linear-features.json` (une entrée par feature :
`{ordre, feature, ucs, name, walking_skeleton, mvp, spec_path, depends_on}`) à importer manuellement, et
le signaler.

## Règles invariantes
- **Jamais avant la porte.** Aucune écriture Linear sans `team_validated`.
- **Linear = source de vérité de l'existant** : toujours chercher un projet similaire avant de créer ;
  ne pas se fier au seul flag local.
- **Clé API jamais exposée** : lue depuis `.env` (`LINEAR_API_KEY`), jamais affichée/loguée/commitée.
- **Défauts** : features **non assignées**, en **Todo** (jamais Backlog).
- **Pas d'écriture fantôme / pas à moitié** : sur erreur API, tracer ce qui a été créé et signaler ;
  jamais de fausse confirmation.
- **Pas de fuite de champ** en sortie utilisateur (voir `references/ux-conventions.md`).

Étape suivante : la fabrication commence — `specify init --ai claude` puis les `/speckit.specify` selon le plan d'attaque ; les features sont suivies dans Linear.
