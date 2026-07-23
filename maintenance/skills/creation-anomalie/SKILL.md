---
name: creation-anomalie
description: Accompagne le PO pour créer dans Linear une anomalie de maintenance complète (comportement attendu et constaté, critère en échec, reproduction), rattachée au ticket Feature de sa feature.
---

# creation-anomalie

Skill du **PO en recette**, quand il constate que le logiciel **ne respecte pas sa
spécification** (le code est en faute, la spécification est bonne - cf.
`references/regles-maintenance.md`). Son rôle : garantir qu'une anomalie **naît complète et bien
rattachée**. Le vrai risque, ce sont les anomalies trouées où il manque l'information qui
permettrait au développeur de travailler : ce skill l'empêche.

C'est aussi la **porte de création unique** : qu'une anomalie soit constatée à la main par le
PO ou détectée par un outil d'analyse automatique (la validation fonctionnelle du plugin
`validation` via `/validation:rapport-de-validation`, une extension de navigateur, un agent de recette),
elle passe par ce skill. Un appel outillé fournit un contenu déjà structuré : le skill le
reprend, ne repose que les questions des champs manquants, et la **validation finale reste
humaine** avant toute création.

## Ancrage du répertoire (impératif)
**La racine du projet est le dossier courant** (le cwd) - **jamais** un dossier parent. Tous
les chemins (`manifest.json`, `.factory/maintenance/`, `specs/`) se résolvent **sous ce dossier**.
**Ne jamais remonter l'arborescence** : un `manifest.json` situé dans un dossier parent
n'appartient pas à ce projet - le traiter comme absent.

## Pré-requis (vérification silencieuse)
- **MCP Linear disponible** (`list_teams` répond - cf. `references/linear-maintenance.md`). Sinon,
  **ne rien créer** : refuser en clair et afficher les instructions d'installation.
- **Terrain de maintenance posé** : le bloc `maintenance` du manifeste et le gabarit
  `.factory/maintenance/gabarit-anomalie.md` existent. Sinon, poser la suite **avec
  `AskUserQuestion`** ("lancer maintenant" en recommandé / "vérifier d'abord le dossier de
  travail") pour lancer d'abord
  `/maintenance:maintenance-init` (une phrase, pas de refus technique).
- **Frontière de la livraison franchie** : la feature visée est livrée (elle a un ticket
  Feature dans Linear et un dossier `specs/<feature>/`). Un écart sur une feature encore en
  fabrication ne se trace pas (cf. `references/regles-maintenance.md`) - le dire en clair et ne
  rien créer.

## Procédure
1. **Identifier la feature concernée.** Demander **avec `AskUserQuestion`** laquelle - deux
   options tirées du registre (bloc `linear` du manifeste : intitulé en langage naturel suivi du
   numéro entre parenthèses), la plus probable au vu du constat en premier, la saisie libre pour
   toute autre feature. Résoudre le **ticket Feature parent** (par son identifiant Linear
   consigné dans le manifeste, cf. `references/linear-maintenance.md`). **Règle dure anti-orphelin** : sans ticket Feature
   rattachable, ne rien créer - expliquer en clair et renvoyer vers
   `/assembleur:premier-alimente-linear`.
2. **Compléter le gabarit, section par section** (`.factory/maintenance/gabarit-anomalie.md`),
   en boucle interactive (`references/interactive-loop.md` : un appel `AskUserQuestion` par
   section, deux options - la suggestion recommandée et l'alternative crédible ; la complétude
   étant **exigée** ici, aucune option de retrait) :
   - le **comportement attendu** (ce que la spécification promet - lire
     `specs/<feature>/spec.md` pour proposer une suggestion ancrée sur l'exigence réelle) ;
   - le **comportement constaté** (factuel, sans interprétation de cause) ;
   - le **critère de recette en échec** (le cas d'usage ou critère d'acceptation qui échoue) ;
   - les **étapes de reproduction** (numérotées, reproductibles par n'importe qui).
   Si un contenu structuré a été fourni (appel outillé), pré-remplir et **faire confirmer avec
   `AskUserQuestion`** chaque section pré-remplie ("le contenu me convient" / "il faut le
   reprendre") au lieu de la re-demander.
   **Signal de nature** : si le comportement attendu déclaré ne correspond à **aucune**
   exigence ni critère de la spécification de la feature (le logiciel fait bien ce que la
   spécification promet), le dire au PO en clair : cet écart ressemble à une **évolution**
   (`/maintenance:creation-evolution`), pas à une anomalie. Le PO tranche **avec
   `AskUserQuestion`** - "basculer en évolution" et "maintenir l'anomalie" ; s'il maintient
   l'anomalie, continuer sans revenir dessus.
3. **Porte de complétude.** Tant qu'une section du gabarit est vide, **le skill le signale en
   nommant la section en clair et ne crée rien**. Une anomalie incomplète n'existe pas dans
   Linear.
4. **Relecture et validation humaine.** Restituer le ticket complet (titre proposé + corps),
   puis demander l'accord **avec `AskUserQuestion`** - "créer le ticket" (recommandé) et "ne pas
   créer" ; le refus reste cliquable. Ne créer que sur l'accord explicite du PO.
5. **Créer le ticket** (cf. `references/linear-maintenance.md`) : `save_issue` avec l'équipe, un
   **titre métier court**, le **ticket Feature en parent**, le **label `Anomalie`**, l'état
   **Backlog**, et le gabarit rempli en description (Markdown réel). Vérifier dans la réponse
   que le parent et le label sont bien posés, puis restituer l'**identifiant Linear** et
   l'**url** au PO.

## Résultat attendu
Une anomalie créée dans Linear, complète, rattachée à sa feature, prête à être prise par un
développeur. Aucune écriture dans le repo, aucune écriture dans le manifeste (l'état vit dans
Linear).

## Règles invariantes
- **Le PO a déjà tranché la nature** (anomalie) en invoquant ce skill : ne pas rejouer le
  débat anomalie/évolution ici (c'est `correction-anomalie` qui détectera une évolution
  déguisée, preuve en main).
- **Ne rien inventer** : chaque section vient d'une réponse explicite du PO (ou d'un contenu
  outillé confirmé par lui). Jamais de valeur démo, jamais de placeholder.
- **Typographie humaine** dans le titre, la description et les sorties (cf. la section
  Typographie de `references/ux-conventions.md`).

Étape suivante : `/maintenance:correction-anomalie` - quand un développeur prend l'anomalie en charge.
