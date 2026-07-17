---
name: realisation-evolution
description: Réalise une évolution sur une feature livrée sans déborder : spécification d'abord, clarification SpecKit, plan validé avant le code, implémentation cadrée au périmètre, preuve de non-régression.
---

# realisation-evolution

Skill du **développeur**, quand il prend en charge une évolution créée par le PO. Son rôle :
réaliser l'évolution sur une feature **déjà livrée**, sans dérive, en mettant à jour **la
spécification d'abord** et le code ensuite, et surtout **sans déborder** sur ce qui marchait
déjà. C'est le skill le plus sensible de la recette : il applique les **4 disciplines
chirurgicales** de `references/regles-recette.md`.

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** (le cwd) - **jamais** un dossier parent. Tous
les chemins (`manifest.json`, `specs/`, `assembleur-out/`, `architecte-out/`) se résolvent
**sous ce dossier**. **Ne jamais remonter l'arborescence.**

## Pré-requis (vérification silencieuse)
- **MCP Linear disponible** (`list_teams` répond - cf. `references/linear-recette.md`). Sinon,
  refuser en clair et afficher les instructions d'installation.
- **L'évolution existe** : identifiant Linear fourni (ou retrouvée par `list_issues`, à
  confirmer), label `Evolution`, ticket Feature parent, et une **proposition de mise à jour de
  la spécification** dans sa description. Une évolution sans proposition circonscrite retourne
  au PO (`/recette:creation-evolution`) - le dire en clair.
- **La spécification de la feature existe** : `specs/<feature>/spec.md`.

## Procédure
1. **Prendre en charge.** Lire tout le ticket (`get_issue`), dont la proposition de changement,
   identifier la feature par le ticket parent, puis passer l'évolution **en cours** (`state`
   de type `started`, idempotent).
2. **Le tri de niveau supérieur : propre à la feature, ou vérité partagée ?** Si l'évolution
   ne touche que la spécification et le code de cette feature, continuer. Si elle touche une
   **vérité partagée** (glossaire, constitution, décision d'architecture, donnée commune,
   règle d'erreur ou de design - cf. `references/regles-recette.md`), **ne pas la traiter
   seul** : commenter le ticket, signaler qu'elle doit remonter au niveau central et impliquer
   l'amont (architecture, cadrage) et l'assemblage, et s'arrêter. Sans ce tri, ce skill
   deviendrait une porte par laquelle on modifierait des contrats partagés feature par feature.
3. **Réouverture volontaire et tracée (première règle d'or).** Rouvrir une feature livrée est
   un geste délibéré, légitime parce que l'évolution est décidée par le PO. Demander la
   **confirmation explicite du développeur**, puis déposer un **commentaire Linear** :
   "Réouverture de la feature <intitulé (numéro)> pour <identifiant de l'évolution>". *(Ce
   commentaire est le point d'accroche de la future protection anti-écrasement côté
   assemblage : la réouverture est visible, jamais un effet de bord silencieux.)*
4. **La spécification d'abord.** Mettre à jour `specs/<feature>/spec.md` selon la proposition
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
   ce qui a changé, la preuve de non-régression). Puis passer l'évolution à **terminé**
   (`state` de type `completed`). Si les phases de `tasks.md` ont changé, rappeler
   `/assembleur:creation-task-linear` (idempotent) pour réaligner les sous-tickets de phase.

## Résultat attendu
Une feature dont la spécification et le code ont évolué de façon cohérente et circonscrite,
avec sa trace à jour, et l'évolution refermée dans Linear. Rien dans le manifeste (l'état vit
dans Linear).

## Règles invariantes
- **La spécification commande, le reste se régénère** : jamais d'édition manuelle du plan ou
  des tâches.
- **Plan validé par l'humain avant tout code** ; **implémentation toujours cadrée**.
- **Jamais de clôture sans preuve de non-régression.**
- **Typographie humaine** dans la spécification, les commentaires et les sorties (cf. la
  section Typographie de `references/ux-conventions.md`).

Étape suivante : `/recette:creation-anomalie` ou `/recette:creation-evolution` - tracer le prochain écart constaté en recette.
