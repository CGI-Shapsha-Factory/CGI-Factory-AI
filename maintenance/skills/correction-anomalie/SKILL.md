---
name: correction-anomalie
description: Prend en charge une anomalie de maintenance : requalifie en évolution si le code respecte la spécification, sinon analyse l'impact, enquête dans le code, corrige et referme avec la trace à jour.
---

# correction-anomalie

Skill du **développeur**, quand il prend en charge une anomalie créée par le PO. Son rôle :
vérifier qu'elle en est bien une, trouver la **cause racine** avec le développeur, corriger
dans le respect des règles du projet, et **refermer proprement** (spécification, tâches et
Linear à jour - cf. `references/regles-maintenance.md`).

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** (le cwd) - **jamais** un dossier parent. Tous
les chemins (`manifest.json`, `specs/`, `assembleur-out/`, `architecte-out/`,
`.specify/memory/constitution.md`) se résolvent **sous ce dossier**. **Ne jamais remonter
l'arborescence.**

## Pré-requis (vérification silencieuse)
- **MCP Linear disponible** (`list_teams` répond - cf. `references/linear-maintenance.md`). Sinon,
  refuser en clair et afficher les instructions d'installation.
- **L'anomalie existe** : identifiant Linear fourni par le développeur (ou retrouvée par
  `list_issues` sur mots-clés, à confirmer **avec `AskUserQuestion`** : deux candidats, le mieux
  apparié en premier). Elle porte le label `Anomalie` et un ticket
  Feature parent ; sinon signaler l'objet mal rattaché (orphelin) et poser la suite **avec
  `AskUserQuestion`** - "le PO le reprend via `/maintenance:creation-anomalie`" (recommandé) et
  "je désigne un autre ticket".
- **La spécification de la feature existe** : `specs/<feature>/spec.md`. Un fichier réellement
  manquant est nommé en clair.

## Procédure
1. **Prendre en charge.** Lire tout le contenu du ticket (`get_issue`), identifier la feature
   par le ticket parent, puis passer l'anomalie **en cours** : résoudre le statut de travail
   de l'équipe **par son nom** via `list_issue_statuses` (ex. "In Progress" - jamais le type
   brut `started`, qui peut désigner aussi un statut de revue, cf.
   `references/linear-maintenance.md`), idempotent (ne rien écrire si c'est déjà l'état courant)
   et **vérifier l'état retourné** après l'écriture.
2. **Le tri le plus important : vraie anomalie ou évolution déguisée ?** Comparer le
   comportement constaté à `specs/<feature>/spec.md`.
   - **Le logiciel ne respecte pas sa spécification** -> vraie anomalie, continuer.
   - **Le logiciel respecte sa spécification** (c'est elle qui était insuffisante) -> ce n'est
     pas un défaut. **Refermer automatiquement** : passer le ticket au statut **"Requalifiée en
     évolution"** et déposer un commentaire qui explique pourquoi (le code est conforme à la
     spécification ; voici le cas d'usage que la spécification ne couvrait pas), puis
     **s'arrêter là**. Le skill **ne crée pas l'évolution** : c'est au PO de l'ouvrir
     (`/maintenance:creation-evolution`), parce que c'est lui qui porte le périmètre. **Vérifier
     d'abord** que le statut "Requalifiée en évolution" existe (`list_issue_statuses`), puis
     **vérifier l'état retourné** par l'écriture : un état inconnu est **ignoré en silence**
     par le MCP (aucune erreur), ne jamais annoncer une requalification non confirmée. Si le
     statut de requalification n'existe pas encore dans l'équipe, **ne pas requalifier** : le
     ticket reste en cours, afficher la marche à suivre manuelle (cf.
     `references/linear-maintenance.md`) et s'arrêter.
3. **Analyser l'impact.** À partir de la feature (son entrée du registre et ses use cases),
   croiser `assembleur-out/feature-map.md` (dépendances, couplage) et
   `architecte-out/composants.md` : **nommer les features potentiellement touchées** par la
   correction, pour éviter une régression. Appliquer le tri de la règle d'or : si la
   correction touche une **vérité partagée** (terme du glossaire, principe de constitution,
   décision d'architecture, donnée commune, règle d'erreur ou de design - cf.
   `references/regles-maintenance.md`), **alerter** qu'elle doit remonter au niveau central plutôt
   que d'être faite dans la feature, commenter le ticket, et laisser l'équipe décider avant de
   continuer.
4. **Mener l'enquête technique avec le développeur.** Trouver la cause d'une anomalie, c'est
   comprendre pourquoi le code dévie de sa spécification : une **enquête dans le code** (lire
   le code existant, proposer des hypothèses, les vérifier), **pas une clarification de
   besoin** (le besoin est clair, ne pas utiliser `/speckit.clarify` ici). Itérer jusqu'à ce
   que la **cause racine soit validée par le développeur** (porte humaine : le skill aide à
   chercher, le développeur valide).
5. **Corriger le code** pour qu'il respecte la spécification, dans le respect des règles déjà
   gravées dans le projet (`.specify/memory/constitution.md`, `.claude/CLAUDE.md`). La
   spécification, elle, **ne change pas** (elle était juste). Ne pas créer de nouvelles
   règles : rappeler et faire respecter celles qui existent. Si le plan ou les tâches sont
   devenus faux, les **régénérer** depuis la spécification inchangée (`/speckit.plan`,
   `/speckit.tasks`) - jamais d'édition manuelle (la spécification commande, le reste se
   régénère). *(Si la régénération crée une **phase** dans `tasks.md`, son titre doit **nommer
   ce ticket d'anomalie** : `## Phase N: Anomalie <identifiant> - <intitulé>`. Corriger le
   titre si `/speckit.tasks` ne l'a pas produit ainsi. Sans ce marqueur, l'outillage aval
   proposera de créer un sous-ticket `Task` pour cette phase : un doublon de ce ticket. **Ne
   pas appeler** `/assembleur:creation-tasks-linear` - ce ticket est l'objet suivi de la
   correction. Cf. `assembleur/references/linear-guide.md`, 4e clé de jointure.)*
6. **Refermer proprement (garde-fou clé).** Refuser la clôture tant que ces trois choses ne
   sont pas faites :
   - la **spécification** de la feature reflète bien le comportement (inchangée ici, mais
     vérifiée) ;
   - les **tâches** portent la trace de la correction (régénérées si besoin, cohérentes avec
     le code corrigé) et les **tests de la feature passent** ;
   - **Linear suit** : un commentaire sur le ticket avec la cause racine et le correctif.
   Une fois tout à jour, passer l'anomalie à **terminé** (le statut de type `completed` de
   l'équipe, résolu par son nom, ex. "Done", état retourné vérifié).

## Résultat attendu
Soit une anomalie corrigée et refermée avec sa trace à jour, soit une anomalie refermée en
"Requalifiée en évolution" avec son explication. Dans les deux cas, rien n'est écrit dans le
manifeste (l'état vit dans Linear).

## Règles invariantes
- **La requalification est automatique** (elle découle d'un constat technique clair) ; la
  **création de l'évolution reste un geste du PO**.
- **Cause racine validée par l'humain** avant toute correction.
- **Jamais de clôture incomplète** : les trois traces (spécification vérifiée, tâches et
  tests, Linear) sont non négociables.
- **Typographie humaine** dans les commentaires et sorties (cf. la section Typographie de
  `references/ux-conventions.md`).

Étape suivante : `/maintenance:creation-evolution` si l'anomalie a été requalifiée (geste du PO), sinon reprendre la recette de la feature.
