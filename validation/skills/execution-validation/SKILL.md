---
name: execution-validation
description: Exécute le plan de test fonctionnel dans le navigateur contre l'environnement de recette : extension Chrome en priorité, MCP Playwright en repli, ou mission différée pour Claude Cowork ; résultats et preuves au format commun.
---

# execution-validation

Bras "exécution" de la validation fonctionnelle : joue le plan de test d'une feature dans le
navigateur, contre l'environnement de recette, et écrit des **résultats au format commun**
(un bloc par cas : verdict, déroulé effectif, preuves) dont le bilan est agnostique.
**L'IA exécute et rapporte ; elle ne juge pas la livraison.**

## Objectif
Produire `validation-out/<feature>/resultats/execution-<JJ-MM>.md` (+ les captures dans
`resultats/preuves/`) en jouant chaque cas de test du plan, avec l'outil choisi par le
testeur, sans jamais interpréter un critère ambigu.

## Pré-requis (vérification silencieuse)
- Le bloc de la validation existe dans `manifest.json` ; sinon refuser, puis poser une question
  `AskUserQuestion` : "amorcer le terrain maintenant" (`/validation:validation-init`, en
  premier avec la mention "(recommandé)") ou "vérifier d'abord le dossier de travail" (le skill
  s'ancre sur le dossier courant, un projet ouvert au mauvais endroit donne le même symptôme).
- Le plan existe : `validation-out/<feature>/plan-de-test.md`. **Plusieurs plans présents** :
  demander lequel jouer **avec `AskUserQuestion`**, une option par feature ayant un plan, en
  premier celle qui n'a pas encore de résultats. **Aucun plan pour la feature visée** : refuser
  en nommant le fichier manquant, puis poser la question des issues (cf. la règle "jamais de
  cul-de-sac" de `references/interactive-loop.md`) - "écrire le plan de <feature>"
  (`/validation:plan-de-validation`), ou "jouer plutôt le plan de <autre feature>" quand une
  autre en a un.
- L'adresse de l'environnement de recette est connue (manifeste ou section Environnement du
  plan) ; sinon la demander (une question) et la retenir dans le manifeste, en silence.

## Procédure

### Étape 1 : choisir l'outil (à chaque lancement)
Demander au testeur quelle voie utiliser **avec `AskUserQuestion`** (trois options, cf.
`references/interactive-loop.md` et `references/execution-navigateur.md`), chacune décrite en
une ligne (ce qu'elle exige, ce qu'elle donne) :
- **l'extension Chrome (Claude in Chrome)** - la recommandée par défaut, à mettre en premier
  avec la mention "(recommandé)" : vrai navigateur, session réelle ;
- **Playwright** (le MCP, en session) : repli, aucune installation dans Chrome ;
- **une mission pour Claude Cowork** (exécution différée, hors session).
Si un outil habituel est retenu au manifeste, c'est **lui** qui passe en premier avec la
mention "(recommandé)". Enregistrer le choix comme outil habituel, en silence. **On redemande à
chaque lancement** : le choix n'est jamais automatique.

### Étape 2a : exécuter avec l'extension Chrome (voie prioritaire)
- **Détection** : tenter une action de lecture navigateur. Si l'extension ne répond pas,
  afficher la marche à suivre (installer "Claude in Chrome", relancer la session avec
  `claude --chrome`, autoriser le domaine de recette) et **proposer le repli Playwright** -
  jamais d'exécution à moitié.
- Jouer le plan **cas par cas, dans l'ordre**, contre l'adresse de recette : préconditions,
  étapes, vérification du résultat attendu. Capture d'écran au point de vérification de chaque
  cas, enregistrée dans `resultats/preuves/TC-<feature>-NNN-<n>.png`.
- Sur un écran de connexion ou un captcha : rendre la main au testeur (comptes de test du plan
  uniquement), puis reprendre.

### Étape 2b : exécuter avec Playwright (repli)
Mêmes cas, mêmes règles, via les outils du MCP Playwright (`browser_navigate`,
`browser_snapshot` pour se repérer par rôles et libellés, `browser_click` / `browser_type` /
`browser_fill_form`, `browser_wait_for`, `browser_take_screenshot`,
`browser_console_messages` / `browser_network_requests` sur KO) - détail dans
`references/execution-navigateur.md`. Si le MCP manque aussi : ne rien exécuter, proposer la
mission Cowork ou l'installation d'un des deux outils.

### Étape 2c : générer la mission Cowork (voie différée)
La mission est un fichier destiné à **un autre outil** : la confirmer par une question
`AskUserQuestion` avant de l'écrire ("générer la mission" en premier avec la mention
"(recommandé)" / "revenir au choix de l'outil"), en disant en une ligne ce qu'elle contiendra
et ce que le testeur devra faire ensuite. Puis générer
`validation-out/<feature>/mission-cowork.md` depuis le gabarit
`.factory/validation/mission-cowork.md` (adresse de recette, renvoi au plan, règles
d'exécution, format de résultats imposé - le document est auto-portant : Cowork n'a pas cette
session). Si une mission existe déjà pour la feature, appliquer la porte de régénération
(repartir de zéro ou archiver sous `_archives/`). Afficher la marche à suivre (ouvrir Cowork
sur le dossier du projet, extension Chrome autorisée sur le domaine, donner la mission), puis
**s'arrêter là** : l'exécution se fait hors session, le bilan se lancera quand les résultats
seront apparus.

### Étape 3 : écrire les résultats (voies en session)
Un fichier `validation-out/<feature>/resultats/execution-<JJ-MM>.md` (si le nom du jour existe
déjà, suffixer `-2`, `-3`... - **on n'écrase jamais une exécution**). En tête : l'adresse
testée et l'outil. Puis un bloc par cas, dans l'ordre du plan :
- **Verdict** : OK / KO / NON TESTABLE (avec la raison) ;
- **Déroulé effectif** : les étapes réellement jouées, numérotées, en langage naturel ;
- **Preuves** : les captures référencées (chemin relatif) ;
- sur KO : **Constaté vs attendu** (factuel) + ce que la console / le réseau montrent
  d'anormal.
En fin de fichier, une ligne de synthèse (cas OK / KO / NON TESTABLE), restituée aussi au
testeur en prose.

## Règles de fiabilité (non négociables)
Cf. `references/regles-validation.md` :
- un cas au statut A CLARIFIER dans le plan sort **NON TESTABLE** (jamais deviné) ; de même
  toute étape ou résultat attendu ambigu rencontré en cours d'exécution ;
- **relance unique avec tri** avant de conclure KO (lenteur -> attendre et rejouer une fois ;
  élément introuvable -> re-repérer par libellé une fois ; vrai écart -> KO avec preuves) ;
- **budget d'étapes borné** : un cas qui dépasse le double de ses étapes prévues sort
  NON TESTABLE avec la raison ;
- **aucune action destructive** (suppression, paiement, envoi externe) sans confirmation
  explicite du testeur : l'exécution **s'arrête** et pose une question `AskUserQuestion`
  ("exécuter l'action, c'est bien une donnée de test" / "sauter ce cas, il sortira NON
  TESTABLE"), en décrivant l'action et son effet ; données de test du plan uniquement, jamais
  de données réelles.

## Vérification avant de conclure
Confirmer que le fichier de résultats existe, qu'il contient un bloc par cas du plan (aucun
cas oublié), et que chaque KO a sa preuve. Restituer la synthèse en prose (pas de tableau de
booléens) : ce qui passe, ce qui échoue, ce qui n'a pas pu être testé.

## Règles invariantes
- **Constater, pas juger** : les verdicts de cas sont des faits ; le verdict de la livraison
  appartient au testeur (porte de recette, au bilan).
- **Un contrat de sortie unique** quel que soit l'outil : le bilan ne doit pas savoir qui a
  exécuté.
- Manifeste silencieux, typographie humaine (cf. `references/ux-conventions.md`).
- **Toujours afficher la phrase "Étape suivante"** avec ses branches en fin d'exécution, y
  compris sur la voie Cowork où le skill s'arrête avant d'exécuter (cf. la section 5 de
  `references/ux-conventions.md`).
- **Jamais de cul-de-sac, questions à choix pour l'énumérable.** Choix de l'outil, choix du
  plan à jouer, confirmation de la mission Cowork et de toute action destructive se demandent
  avec `AskUserQuestion` ; l'adresse de recette reste en prose ; **un refus se termine par une
  question** (cf. `references/interactive-loop.md`).

Étape suivante : `/validation:bilan-validation` - assembler le rapport de recette tracé et trier les écarts avec le testeur. Sur la voie Cowork, attendre d'abord que le fichier de résultats soit apparu, puis lancer ce même bilan. Ou relancer `/validation:execution-validation` pour une nouvelle exécution (changement d'outil, cas restés à rejouer, ou vérification après correction) : chaque exécution produit son propre fichier, aucune n'écrase la précédente.
