---
name: realisation-evolution
description: Réalise une évolution sur une feature livrée sans déborder : spécification d'abord, clarification SpecKit, plan validé avant le code, implémentation cadrée au périmètre, preuve de non-régression.
---

# realisation-evolution

Skill du **développeur**, quand il prend en charge une évolution créée par le PO. Son rôle :
réaliser l'évolution sur une feature **déjà livrée**, sans dérive, en mettant à jour **la
spécification d'abord** et le code ensuite, et surtout **sans déborder** sur ce qui marchait
déjà. C'est le skill le plus sensible de la maintenance : il applique les **4 disciplines
chirurgicales** de `references/regles-maintenance.md`.

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** (le cwd) - **jamais** un dossier parent. Tous
les chemins (`manifest.json`, `specs/`, `assembleur-out/`, `architecte-out/`) se résolvent
**sous ce dossier**. **Ne jamais remonter l'arborescence.**

## Pré-requis (vérification silencieuse)
- **MCP Linear disponible** (`list_teams` répond - cf. `references/linear-maintenance.md`). Sinon,
  refuser en clair et afficher les instructions d'installation.
- **L'évolution existe** : identifiant Linear fourni (ou retrouvée par `list_issues`, à
  confirmer), label `Evolution`, ticket Feature parent, et une **proposition de mise à jour de
  la spécification** dans sa description. Une évolution sans proposition circonscrite retourne
  au PO (`/maintenance:creation-evolution`) - le dire en clair.
- **La spécification de la feature existe** : `specs/<feature>/spec.md`.

## Procédure
1. **Prendre en charge.** Lire tout le ticket (`get_issue`), dont la proposition de changement,
   identifier la feature par le ticket parent, puis passer l'évolution **en cours** : le
   statut de travail de l'équipe résolu **par son nom** via `list_issue_statuses` (ex. "In
   Progress" - jamais le type brut `started`, cf. `references/linear-maintenance.md`), idempotent,
   état retourné vérifié.
2. **Le tri de niveau supérieur : propre à la feature, ou vérité partagée ?** Sans ce tri, ce
   skill deviendrait une porte par laquelle on modifierait des contrats partagés feature par
   feature. **Lire avant de juger** (ne jamais trancher de mémoire) : la constitution
   `.specify/memory/constitution.md`, la carte `assembleur-out/feature-map.md` (dépendances
   et couplage), `architecte-out/composants.md` (composants touchés) et le glossaire du
   cadrage. Si l'évolution ne touche que la spécification et le code de cette feature,
   continuer en 3.

   Si elle touche une **vérité partagée** (glossaire, principe de constitution, décision
   d'architecture, donnée commune, règle d'erreur ou de design - cf.
   `references/regles-maintenance.md`) : **ne rien écrire**, et **exposer le conflit en clair** -
   ce que dit le contrat partagé et où il le dit, ce que demande l'évolution, pourquoi les
   deux sont incompatibles. Puis **poser la décision au développeur** en annonçant la voie
   recommandée, et **attendre sa réponse**. Ce point est une **décision, jamais un arrêt
   nu** : ne pas se contenter de signaler et de s'interrompre. Trois issues :
   - **Faux positif** : le développeur établit que ce n'est pas une vérité partagée (le tri
     est un jugement, il peut se tromper). Déposer un commentaire Linear qui trace le motif,
     puis continuer en 3.
   - **Arbitrage déjà rendu** : le développeur fournit la référence de la décision (ADR
     accepté, amendement de constitution déjà voté). Vérifier qu'elle couvre bien l'écart
     demandé, la citer en commentaire Linear, puis continuer en 3.
   - **Arbitrage à rendre** : deux voies, au choix du développeur.
     - **Amender maintenant** (voie recommandée) : sur **confirmation explicite**, le contrat
       partagé est mis à jour **avant** la spécification, via **`/speckit.constitution`** -
       jamais à la main, jamais d'écriture directe dans `.specify/`. Tracer l'amendement en
       commentaire Linear, puis continuer en 3.
     - **Remonter et parquer** : déposer un commentaire d'escalade qui **nomme** le contrat
       touché et ce qui doit être arbitré, **remettre le ticket en Backlog** (statut résolu
       par son nom, état retourné vérifié - cf. `references/linear-maintenance.md`), et
       s'arrêter. **Dire explicitement comment on reprend** : une fois le contrat amendé au
       niveau central, il suffit de relancer `/maintenance:realisation-evolution` sur ce même
       ticket - le tri repassera et laissera continuer.

   *(Suivre `references/interactive-loop.md` : exposer le point, puis poser la question **avec
   `AskUserQuestion`** - deux options, la voie recommandée d'abord ; la saisie libre reste
   ouverte pour une issue que ni l'une ni l'autre ne couvre.)*
3. **Réouverture volontaire et tracée (première règle d'or).** Rouvrir une feature livrée est
   un geste délibéré, légitime parce que l'évolution est décidée par le PO. Demander la
   **confirmation explicite du développeur avec `AskUserQuestion`** - "rouvrir la feature"
   (recommandé) et "ne pas rouvrir maintenant" -, puis déposer un **commentaire Linear** :
   "Réouverture de la feature <intitulé (numéro)> pour <identifiant de l'évolution>". *(Ce
   commentaire est le point d'accroche de la future protection anti-écrasement côté
   assemblage : la réouverture est visible, jamais un effet de bord silencieux.)*
4. **Le contrat partagé d'abord, puis la spécification.** Si l'étape 2 a conclu à un
   amendement, celui-ci est **déjà fait** : la spécification vient après, alignée sur le
   contrat amendé - **jamais l'inverse**. Une spécification qui porte une exigence que la
   constitution interdit encore est une spécification qui devance une décision non prise :
   la prochaine Constitution Check du plan la rejettera. Signaler aussi, sans l'écrire, la
   **divergence amont** que l'amendement laisse derrière lui : `/speckit.constitution` ne
   touche pas `architecte-out/`, donc l'ADR d'origine reste "Accepté" alors qu'il est
   dépassé - nommer l'ADR concerné et le successeur à produire côté architecte, et le tracer
   en commentaire Linear. Ce skill n'écrit jamais dans `architecte-out/`.

   Mettre à jour `specs/<feature>/spec.md` selon la proposition
   du PO, en n'écrivant **que l'écart prévu** (les exigences nommées, rien d'autre). Puis,
   comme toute intention nouvelle contient des zones floues, lancer **`/speckit.clarify`** pour
   poser au développeur les questions qui les lèvent et graver les réponses dans la
   spécification. *(C'est le bon usage de cette commande : préciser un besoin nouveau - à ne
   pas confondre avec l'enquête code d'une anomalie.)*
5. **Régénérer le plan, le faire valider, puis les tâches (deuxième discipline).** Lancer
   **`/speckit.plan`** depuis la spécification mise à jour, puis **restituer le périmètre
   annoncé** (les fichiers qui vont être touchés) et attendre la **validation du développeur**
   (porte humaine). Si le plan annonce un périmètre large pour un petit écart (beaucoup de
   fichiers, des composants non concernés), **le dire explicitement** : c'est le signal
   d'alerte, visible avant que le code ne bouge. Une fois le plan validé, lancer
   **`/speckit.tasks`**.

   **Marquer la phase créée (impératif).** `/speckit.tasks` ajoute une phase à
   `specs/<feature>/tasks.md`. Son titre doit **nommer ce ticket d'évolution** :
   `## Phase N: Évolution <identifiant> - <intitulé>` (ex. `## Phase 7: Évolution RAG-12 -
   Ingestion des pièces scannées au format PNG`). Si `/speckit.tasks` ne l'a pas produit ainsi,
   **corriger le titre de la phase** - c'est la seule écriture de ce skill dans `tasks.md`, et
   elle porte sur le titre seul. Sans ce marqueur, l'outillage aval (le skill
   `/assembleur:creation-tasks-linear` et le hook `tasks.md`) proposera de créer un sous-ticket
   `Task` pour cette phase : un **doublon** de ce ticket, frère sous la même Feature, avec deux
   états à synchroniser (cf. `assembleur/references/linear-guide.md`, 4e clé de jointure).
6. **Implémentation cadrée (troisième discipline).** Lancer **`/speckit.implement`** en le
   **cadrant explicitement** : donner le périmètre de l'évolution (les exigences qui changent,
   les fichiers concernés du plan validé) et la consigne de **ne toucher que ça**. Jamais une
   implémentation ouverte qui repasserait sur toute la feature.
7. **Prouver la non-régression (quatrième discipline).** Le nouveau comportement marche **et**
   l'ancien n'a pas cassé : les **tests existants de la feature passent**, et l'analyse
   d'impact (via `assembleur-out/feature-map.md` et `architecte-out/composants.md`) confirme
   que les features couplées ne sont pas abîmées (leurs tests passent aussi quand elles
   partagent du code touché).
8. **Refermer proprement.** Refuser la clôture tant que : la **spécification** reflète
   l'évolution (écart + clarifications), le **plan et les tâches** sont régénérés et cohérents,
   les **tests** sont verts (feature + couplées), et **Linear suit** (commentaire de synthèse :
   ce qui a changé, la preuve de non-régression). Puis passer l'évolution à **terminé** (le
   statut de type `completed` de l'équipe, résolu par son nom, ex. "Done", état retourné
   vérifié). **Ne pas appeler `/assembleur:creation-tasks-linear`** : ce ticket d'évolution
   **est** l'objet suivi de ce travail, et la phase de `tasks.md` en est un détail
   d'implémentation. Lui créer un sous-ticket de phase produirait un doublon frère sous la même
   Feature. L'avancement se trace ici, par le statut et les commentaires de ce ticket - comme
   le fait déjà `correction-anomalie`.

## Résultat attendu
Une feature dont la spécification et le code ont évolué de façon cohérente et circonscrite,
avec sa trace à jour, et l'évolution refermée dans Linear. Rien dans le manifeste (l'état vit
dans Linear).

## Règles invariantes
- **Une vérité partagée ne se règle jamais en silence** : elle est **exposée, tranchée par
  l'humain, et tracée** dans Linear - amendée ou parquée, jamais ignorée, et jamais un arrêt
  sans issue nommée.
- **Le contrat partagé s'amende avant la spécification**, et **uniquement** via
  `/speckit.constitution` (jamais à la main, jamais d'écriture directe dans `.specify/`).
- **La spécification commande, le reste se régénère** : jamais d'édition manuelle du plan ou
  des tâches.
- **Plan validé par l'humain avant tout code** ; **implémentation toujours cadrée**.
- **Jamais de clôture sans preuve de non-régression.**
- **Typographie humaine** dans la spécification, les commentaires et les sorties (cf. la
  section Typographie de `references/ux-conventions.md`).

Étape suivante : si l'évolution a été parquée en attente d'arbitrage, **relancer ce même skill** sur le ticket une fois le contrat partagé amendé. Sinon, `/maintenance:creation-anomalie` ou `/maintenance:creation-evolution` - tracer le prochain écart constaté en recette.
