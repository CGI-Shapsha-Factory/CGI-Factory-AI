---
name: execution-validation
description: Exécute le plan de test fonctionnel dans le navigateur contre l'environnement de recette : disponibilité des outils sondée avant le choix, extension Chrome en priorité (marche à suivre affichée si absente), MCP Playwright en repli (installé directement si absent), ou mission différée pour Claude Cowork ; résultats et preuves au format commun.
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
  en nommant le fichier manquant, puis poser la question des issues **avec `AskUserQuestion`** (cf. la règle "jamais de
  cul-de-sac" de `references/interactive-loop.md`) - "écrire le plan de <feature>"
  (`/validation:plan-de-validation`), ou "jouer plutôt le plan de <autre feature>" quand une
  autre en a un.
- L'adresse de l'environnement de recette est connue (manifeste ou section Environnement du
  plan) ; sinon la demander **avec `AskUserQuestion`** - les options portent les adresses plausibles
  lues dans le dépôt (URL locale servie, ouverture directe du fichier, URL déployée), la saisie
  libre reste ouverte - et la retenir dans le manifeste, en silence.

## Procédure

### Étape 1 : sonder les outils, puis choisir (à chaque lancement)

**1a. Préflight, en silence, avant toute question** (cf. la table du préflight dans
`references/execution-navigateur.md`). **Un outil ne doit jamais se découvrir indisponible au
milieu d'une exécution** : sonder les deux voies en session **avant** de proposer le choix.
- **extension Chrome** : les outils navigateur du serveur `claude-in-chrome` répondent-ils ?
- **Playwright** : les outils `mcp__playwright__browser_*` sont-ils chargés dans la session ?
  À défaut, `claude mcp list` (chercher `playwright` à l'état `Connected` - lire l'**état
  textuel**, jamais le glyphe : les vieilles consoles Windows n'affichent pas les mêmes).
- **mission Cowork** : aucune sonde, elle est **toujours disponible** (rien à installer
  localement) - c'est la sortie de secours qui garantit qu'il n'y a jamais de cul-de-sac.
Ne rien narrer de ces sondes : elles alimentent les options de la question qui suit.

**1b. Demander l'outil avec `AskUserQuestion`** (trois options, cf.
`references/interactive-loop.md`), chacune décrite en une ligne **portant l'état du préflight**
("disponible" / "à installer") :
- **l'extension Chrome (Claude in Chrome)** : vrai navigateur, session réelle - la voie de
  référence ;
- **Playwright** (le MCP, en session) : repli, aucune installation dans Chrome ;
- **une mission pour Claude Cowork** (exécution différée, hors session).

**La mention "(recommandé)" va à un outil réellement disponible**, jamais à un outil qu'il
faudrait installer : extension Chrome si elle répond, sinon Playwright s'il est chargé, sinon la
mission Cowork. **Un outil habituel retenu au manifeste ne passe en premier que s'il est
disponible** : sa préférence ne prime jamais sur l'état réel de la machine. Enregistrer le choix
comme outil habituel, en silence. **On redemande à chaque lancement** : le choix n'est jamais
automatique.

**1c. Le testeur peut choisir un outil indisponible** (c'est son droit : il veut cet outil-là).
Alors **ne pas basculer d'office sur un autre** : traiter d'abord sa demande - installer
Playwright directement (Étape 2b), ou afficher la marche à suivre de l'extension (Étape 2a) -
et ne proposer le repli **qu'ensuite**, par une question.

### Étape 2a : exécuter avec l'extension Chrome (voie prioritaire)
- **Extension indisponible** : le skill **ne peut pas l'installer lui-même** - `/chrome` et
  `/login` sont des **gestes de l'utilisateur** dans sa session. Afficher la marche à suivre,
  dans cet ordre (détail et cas de panne dans `references/execution-navigateur.md`) :
  **`/chrome`** (panneau d'état : l'intégration marche quand il affiche `Status: Enabled` et
  `Extension: Installed` ; il permet aussi d'installer et de **reconnecter**) ; extension absente
  -> Chrome Web Store ou répondre **"Install extension"** à l'invite "Claude wants to use your
  browser" (installation **guidée, dans la même session**) ; session sans navigateur -> relancer
  avec **`claude --chrome`** ; puis **autoriser le domaine de recette** dans les permissions par
  site. Enfin **proposer le repli avec `AskUserQuestion`** ("passer à Playwright" en premier /
  "réessayer l'extension") - jamais d'exécution à moitié.
- **Impasses à nommer, jamais à contourner** : une session authentifiée par **clé API** ou par
  jeton **`claude setup-token`** garde l'intégration Chrome **désactivée même avec `--chrome`** ;
  sous **WSL** ou via un **fournisseur tiers** (Bedrock, Vertex, Foundry), la voie n'existe pas.
  Le dire tout de suite et orienter vers Playwright ou la mission Cowork, plutôt que d'envoyer le
  testeur réinstaller une extension qui ne pourra pas se connecter.
- **Elle répondait puis s'arrête en cours d'exécution** (service worker en veille, séance
  longue) : `/chrome` puis **"Reconnect extension"**, et reprendre au cas en cours - les cas
  déjà joués gardent leur verdict, on ne rejoue pas le plan depuis le début.
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
`references/execution-navigateur.md`.

**MCP Playwright absent : l'installer directement** (c'est la **seule** voie que le skill peut
poser lui-même). Procédure complète dans `references/execution-navigateur.md` ; en résumé :
1. **Confirmer avec `AskUserQuestion`** ("installer le MCP Playwright maintenant" en premier /
   "générer plutôt la mission Cowork") - une installation modifie une configuration, jamais sans
   accord.
2. **Choisir la portée** (deuxième appel) : **`--scope user`** (recommandé - personnel, tous
   projets, **aucun fichier écrit dans le dépôt**) ou **`--scope project`** (écrit `.mcp.json` à
   la racine, à commiter, partagé par l'équipe).
3. **Vérifier Node.js** : `node -v` doit rendre **18 ou plus**. Sinon, **ne pas installer** :
   le dire en clair et proposer la mission Cowork.
4. **Installer** : `claude mcp add playwright --scope <user|project> -- npx -y @playwright/mcp@latest`
   (le séparateur `--` est obligatoire ; commande identique sous PowerShell et bash).
5. **Vérifier** avec `claude mcp list` (état `Connected`) - la première tentative peut échouer
   pendant le téléchargement par `npx` : **attendre et refaire une fois** avant de conclure.
6. **Redémarrer la session, impérativement** : les outils d'un serveur MCP ne sont chargés qu'au
   **démarrage**, donc **pas** dans la session qui vient de l'installer. Le dire, **s'arrêter
   là**, et indiquer de relancer `/validation:execution-validation` ensuite. **Ne jamais**
   enchaîner sur l'exécution en annonçant que Playwright est prêt.

**Installation refusée ou échouée** (réseau, registre npm bloqué) : relayer le message en clair,
ne pas s'acharner, et poser la question **avec `AskUserQuestion`** - "générer la mission Cowork"
(en premier) ou "réessayer l'installation".

### Étape 2c : générer la mission Cowork (voie différée)
La mission est un fichier destiné à **un autre outil** : la confirmer par une question
`AskUserQuestion` avant de l'écrire ("générer la mission" en premier avec la mention
"(recommandé)" / "revenir au choix de l'outil"), en disant en une ligne ce qu'elle contiendra
et ce que le testeur devra faire ensuite. Puis générer
`validation-out/<feature>/mission-cowork.md` depuis le gabarit
`mission-cowork.md` - celui du **plugin** fait foi, remplacer la copie
`.factory/validation/mission-cowork.md` si elle en diffère (cf.
`references/regles-validation.md`) - (adresse de recette, renvoi au plan, règles
d'exécution, format de résultats imposé - le document est auto-portant : Cowork n'a pas cette
session). Si une mission existe déjà pour la feature, appliquer la porte de régénération
(repartir de zéro ou archiver sous `_archives/`). Afficher la marche à suivre (ouvrir Cowork
sur le dossier du projet, extension Chrome autorisée sur le domaine, donner la mission), puis
**s'arrêter là** : l'exécution se fait hors session, le bilan se lancera quand les résultats
seront apparus.

### Étape 3 : écrire les résultats (voies en session)
Un fichier `validation-out/<feature>/resultats/execution-<JJ-MM>.md` (si le nom du jour existe
déjà, suffixer `-2`, `-3`... - **on n'écrase jamais une exécution**), **depuis le gabarit**
`.factory/validation/execution-resultats.md` - celui du **plugin** fait foi, remplacer la copie
si elle en diffère (cf. `references/regles-validation.md`).

**Tout est en tables**, quatre sections dans cet ordre (forme des tables - séparateurs entre
lignes, étapes en `<br>`, cellule vide = `-` : section 4bis de `references/ux-conventions.md`) :
1. **Contexte d'exécution** - une ligne : adresse testée, outil, plan joué, nombre de cas.
2. **Synthèse** - trois lignes (OK / KO / NON TESTABLE) avec leur compte et les identifiants
   concernés. **Elle est en haut** : le testeur doit savoir en deux secondes ce qui casse, sans
   dérouler le fichier.
3. **Résultats par cas** - `Cas | Intitulé | Verdict | Déroulé effectif | Constaté | Preuve` ;
   **une ligne par cas du plan, dans l'ordre, aucun cas omis** (y compris les NON TESTABLE). Le
   **déroulé effectif** (étapes réellement jouées, numérotées, séparées par `<br>`) est requis
   **même quand le cas passe** : le plan porte les étapes **prévues**, le déroulé porte ce qui
   s'est **vraiment** passé (relances, contournements, ordre effectif). La colonne **Constaté**
   reste **une phrase** factuelle.
4. **Écarts (KO et NON TESTABLE)** - `Cas | Attendu | Constaté | Console et réseau` : le
   diagnostic détaillé vit **ici**, pas dans la table précédente. Pour un NON TESTABLE,
   "Constaté" porte la **raison** de la non-testabilité. **Tous les cas OK** : supprimer la
   table et écrire "Aucun - tous les cas sont OK."

La synthèse est restituée **aussi au testeur en prose** (jamais un tableau de booléens à
l'écran).

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
- **Outil sondé avant d'être proposé, jamais découvert en panne en cours de route.** Le
  préflight tourne avant la question ; la mention "(recommandé)" ne va **qu'à** un outil
  réellement disponible ; un outil habituel devenu indisponible ne passe pas en premier.
- **Installer ce qui s'installe, expliquer ce qui ne s'installe pas.** Le MCP Playwright est
  posé **directement** par le skill (après confirmation et choix de portée), puis la session
  **doit redémarrer** avant de pouvoir l'utiliser - on ne prétend jamais l'inverse. L'extension
  Chrome, elle, dépend de gestes de l'utilisateur (`/chrome`, `/login`, Chrome Web Store) : le
  skill **affiche la marche à suivre** et s'arrête, sans jamais faire semblant de l'installer.
- **Une impasse se nomme.** Clé API ou `claude setup-token`, WSL, fournisseur tiers : l'extension
  Chrome ne se connectera pas, quoi qu'on fasse. Le dire immédiatement et rediriger, plutôt que
  d'envoyer le testeur dans une réinstallation vaine.
- Manifeste silencieux, typographie humaine (cf. `references/ux-conventions.md`).
- **Toujours afficher la phrase "Étape suivante"** avec ses branches en fin d'exécution, y
  compris sur la voie Cowork où le skill s'arrête avant d'exécuter (cf. la section 5 de
  `references/ux-conventions.md`).
- **Jamais de cul-de-sac, et toute question passe par `AskUserQuestion`.** Choix de l'outil,
  choix du plan à jouer, confirmation de la mission Cowork, toute action destructive **et
  l'adresse de recette** - pour celle-ci, les options portent les adresses plausibles déduites
  du dépôt (URL locale servie, ouverture directe du fichier, URL déployée) et la saisie libre
  reste ouverte. **Aucune question rédigée en prose dans le fil.** Un refus se termine par une
  question (cf. `references/interactive-loop.md`).

Étape suivante : `/validation:rapport-de-validation` - assembler le rapport de recette tracé et trier les écarts avec le testeur. Sur la voie Cowork, attendre d'abord que le fichier de résultats soit apparu, puis lancer ce même bilan. Ou relancer `/validation:execution-validation` pour une nouvelle exécution (changement d'outil, cas restés à rejouer, ou vérification après correction) : chaque exécution produit son propre fichier, aucune n'écrase la précédente.
