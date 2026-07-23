# Exécution navigateur : les trois voies et le contrat de sortie commun

Référence d'usage d'`execution-validation`. Trois voies d'exécution, un seul contrat de
sortie : le bilan (`rapport-de-validation`) est **agnostique de l'outil**.

## Préflight : sonder les outils AVANT de proposer le choix
**Un outil ne se découvre jamais indisponible au milieu d'une exécution.** Avant de poser la
question, sonder les deux voies en session (extension Chrome, MCP Playwright) et **reporter
l'état dans les options** ("disponible" / "à installer"), pour que le testeur choisisse en
connaissance de cause. Sondes **silencieuses** (aucune narration) :

| Voie | Sonde | Disponible si |
|---|---|---|
| Extension Chrome | les outils navigateur du serveur `claude-in-chrome` sont-ils présents dans la session ? | ils répondent (session lancée avec `claude --chrome`, ou Chrome activé par défaut) |
| Playwright | les outils `mcp__playwright__browser_*` sont-ils présents ? sinon `claude mcp list` | `playwright` est listé avec l'état `Connected` **et** ses outils sont chargés dans la session |
| Mission Cowork | aucune sonde | **toujours disponible** : rien à installer localement, c'est la sortie de secours |

`claude mcp list` peut afficher l'état sous forme de glyphe (coche / croix) ou, sur les
consoles Windows anciennes, `√` / `×` : lire l'**état textuel** (`Connected`,
`Failed to connect`, `Needs authentication`), jamais le glyphe.

**Ordre de recommandation.** L'outil marqué "(recommandé)" est **celui qui est déjà
disponible** (extension Chrome d'abord si les deux le sont, sinon Playwright), et non un outil
à installer. Si **aucune** des deux voies en session n'est disponible, la recommandée devient
**la mission Cowork**, et l'installation est proposée comme alternative.

## Le choix de l'outil (à chaque lancement)
Le skill demande au testeur quelle voie utiliser **avec `AskUserQuestion`** (cf. `interactive-loop.md`),
options **annotées de l'état du préflight**. À disponibilité égale, **l'extension Chrome** reste
la voie de référence (la plus fidèle : vrai navigateur, session réelle). Le dernier choix est
retenu dans le manifeste comme **suggestion** pour la prochaine fois - jamais comme automatisme :
on redemande à chaque lancement, et **un outil habituel devenu indisponible ne passe pas en
premier**.

## Voie 1 (prioritaire) : l'extension Chrome (Claude in Chrome), en session
Claude Code pilote directement l'extension "Claude in Chrome" : navigation, clics, saisie de
formulaires, lecture de la console et des requêtes réseau, captures d'écran sauvegardées sur
disque.
- **Pré-requis** (tous nécessaires) : un navigateur Chromium (Chrome, Edge, Brave, Arc, Vivaldi,
  Opera) ; l'extension "Claude in Chrome" en **version 1.0.36 ou plus** ; la session lancée avec
  le navigateur connecté (`claude --chrome`, ou Chrome activé par défaut) ; un **abonnement
  Anthropic direct** (Pro, Max, Team ou Enterprise) ; et une **connexion via `/login`**.
  **Non disponible sous WSL**, ni via un fournisseur tiers (Bedrock, Vertex, Foundry).
- **Deux impasses qu'il faut nommer au testeur, pas contourner** :
  - **Authentification par clé API ou par jeton `claude setup-token`** : l'intégration Chrome
    reste **désactivée même avec `--chrome`** (l'extension ne peut pas s'authentifier ainsi).
    Aucun réglage n'y change quoi que ce soit : il faut se connecter avec `/login`, ou prendre
    une autre voie.
  - **WSL / fournisseur tiers** : la voie est structurellement indisponible ; passer à
    Playwright ou à la mission Cowork sans faire perdre de temps au testeur.
- **Détection** : vérifier au préflight que les outils navigateur répondent (cf. la table
  ci-dessus). L'installation ne peut **pas** être faite par le skill : `/chrome` et `/login` sont
  des **gestes de l'utilisateur** dans sa session. Le skill **affiche la marche à suivre** et
  **s'arrête** sur cette voie - jamais d'exécution à moitié :
  1. **`/chrome`** dans la session : c'est le panneau d'état. L'intégration fonctionne quand il
     affiche `Status: Enabled` **et** `Extension: Installed`. Le panneau permet aussi de
     **réinstaller**, de **reconnecter l'extension**, de gérer les permissions par site et de
     choisir le navigateur quand plusieurs sont connectés.
  2. **Extension absente** : l'installer depuis le Chrome Web Store, ou répondre **"Install
     extension"** à l'invite "Claude wants to use your browser" quand elle apparaît - cette voie
     est **guidée et se termine dans la même session** (Claude Code attend l'installation, se
     connecte, puis active les outils navigateur).
  3. **Session sans navigateur** : relancer avec `claude --chrome` (ou `/chrome` puis
     "Enabled by default" pour ne plus avoir à passer le drapeau).
  4. **Autoriser le domaine de recette** dans les permissions par site de l'extension.
  Puis **proposer le repli avec `AskUserQuestion`** : "passer à Playwright" / "réessayer
  l'extension" (et la mission Cowork si Playwright manque aussi).
- **Extension présente mais qui ne répond plus** (le cas le plus courant en séance longue : le
  service worker de l'extension se met en veille) : `/chrome` puis **"Reconnect extension"**.
  Autres pistes, dans l'ordre : vérifier l'extension dans `chrome://extensions`, vérifier que
  Chrome tourne, `claude --version` (Claude Code à jour), puis redémarrer Chrome **et** Claude
  Code. À la toute première activation, Chrome doit être **redémarré** pour lire le fichier de
  messagerie native que Claude Code vient d'écrire.
- **Session partagée** : le navigateur porte les logins de l'utilisateur. Se connecter à
  l'environnement de recette avec les **comptes de test du plan** uniquement ; sur un login ou
  un captcha, rendre la main au testeur (il se connecte, puis l'exécution reprend).
- **Preuves** : captures d'écran enregistrées dans `validation-out/<feature>/resultats/preuves/`
  (nommées par cas : `TC-<feature>-NNN-<n>.png`).

## Voie 2 (repli) : le MCP Playwright, en session
Mêmes cas, mêmes règles, via les outils `mcp__playwright__browser_*` :
- `browser_navigate` (ouvrir une page), `browser_snapshot` (état de la page par l'arbre
  d'accessibilité - c'est le **repère d'action** : cibler les éléments par rôle et libellé,
  jamais par pixel), `browser_click` / `browser_type` / `browser_fill_form` /
  `browser_select_option` (agir), `browser_wait_for` (attendre un texte ou un délai),
  `browser_take_screenshot` (preuve, destination finale `resultats/preuves/`),
  `browser_console_messages` / `browser_network_requests` (diagnostic sur KO).
- **Captures** : le MCP Playwright n'écrit que sous sa propre racine autorisée (un chemin hors
  de la session est refusé, et un nom relatif atterrit dans son dossier de sortie, pas dans
  `preuves/`). Capturer avec un nom relatif `TC-<feature>-NNN-<n>.png`, puis **déplacer** les
  fichiers dans `validation-out/<feature>/resultats/preuves/` avant d'écrire les résultats -
  aucune preuve référencée ne doit rester dans le dossier de l'outil.
### Playwright absent : l'installer directement (seule voie installable par le skill)
Contrairement à l'extension Chrome, le MCP Playwright **s'installe en une commande**, sans
droits administrateur. Le skill le fait **lui-même**, après confirmation.

1. **Confirmer avec `AskUserQuestion`** : "installer le MCP Playwright maintenant" (recommandé)
   / "générer plutôt la mission Cowork". L'installation modifie une configuration de la machine
   ou du dépôt : elle ne se fait **jamais** sans accord.
2. **Choisir la portée avec `AskUserQuestion`** (deuxième appel, un point à la fois) :
   - **`--scope user`** (recommandé) : personnel, valable pour **tous** les projets, écrit dans
     `~/.claude.json`. **Aucun fichier écrit dans le dépôt** - c'est la portée qui respecte la
     frontière "la validation n'écrit que dans `validation-out/`".
   - **`--scope project`** : écrit `.mcp.json` **à la racine du dépôt**, à **commiter** ; toute
     l'équipe qui clone dispose de Playwright pour la recette. Le dire en clair : c'est un
     fichier versionné de plus, et chaque coéquipier devra **approuver** le serveur au premier
     démarrage.
3. **Vérifier Node.js** : `node -v` doit rendre **18 ou plus** (Playwright MCP tourne via `npx`).
   En dessous, ou si `node` est introuvable : **ne pas installer**, le dire en clair (installer
   Node.js 18+ depuis nodejs.org) et proposer la mission Cowork.
4. **Installer**, depuis le shell (la commande est identique sous PowerShell, bash et cmd) :
   `claude mcp add playwright --scope <user|project> -- npx -y @playwright/mcp@latest`
   Le séparateur `--` est **obligatoire** : sans lui, tout ce qui suit n'est pas pris comme la
   commande de lancement du serveur.
5. **Vérifier** : `claude mcp list` doit lister `playwright` avec l'état **`Connected`**. La
   **première** vérification peut rendre `Failed to connect` pendant que `npx` télécharge le
   paquet : **attendre puis refaire** une fois avant de conclure à un échec. Si le démarrage
   dépasse le délai, le signaler avec le remède : `MCP_TIMEOUT=60000 claude` (PowerShell :
   `$env:MCP_TIMEOUT = "60000"; claude`).
6. **Redémarrer la session, impérativement.** Les outils d'un serveur MCP ne sont chargés qu'au
   **démarrage** d'une session : ils ne sont **pas** utilisables dans celle qui vient de faire
   l'installation. Le dire clairement, **s'arrêter là**, et indiquer de relancer
   `/validation:execution-validation` après redémarrage. **Ne jamais** annoncer "Playwright est
   prêt, on exécute" dans la foulée. En portée `project`, ajouter qu'il faudra **approuver** le
   serveur au redémarrage et **commiter `.mcp.json`**.

**Si l'installation échoue** (réseau, `npx` indisponible, entreprise qui bloque le registre npm) :
relayer le message d'erreur en clair, **ne pas s'acharner**, et proposer **avec
`AskUserQuestion`** la voie 3 (mission Cowork) ou une nouvelle tentative.

Si le testeur **refuse** l'installation, ou si les deux voies en session sont hors d'atteinte :
ne rien exécuter et proposer **avec `AskUserQuestion`** la voie 3 (mission Cowork, toujours
disponible) ou l'installation d'un des deux outils.

## Voie 3 (différée) : la mission Cowork (exécution hors session)
Quand le testeur préfère faire exécuter par **Claude Cowork** (qui pilote la même extension
Chrome depuis son propre environnement), le skill ne pilote rien : il génère
`validation-out/<feature>/mission-cowork.md` depuis le gabarit - un document de mission
**auto-portant** (Cowork n'a pas l'historique de cette session) : l'adresse de recette, le
renvoi au plan de test, les règles d'exécution, et le **format de résultats imposé**.
Marche à suivre affichée au testeur :
1. Ouvrir Cowork et lui donner accès au **dossier du projet** (il y lira la mission et le plan).
2. Vérifier que l'extension "Claude in Chrome" est installée et autorisée sur le domaine de recette.
3. Donner la consigne : "Exécute la mission de recette décrite dans
   `validation-out/<feature>/mission-cowork.md`."
4. Une fois l'exécution finie (le fichier de résultats est apparu), revenir dans Claude Code et
   lancer `/validation:rapport-de-validation`.

## Le contrat de sortie commun (quel que soit l'outil)
Un fichier de résultats par exécution : `validation-out/<feature>/resultats/execution-<JJ-MM>.md`
(si un fichier du même jour existe déjà, suffixer `-2`, `-3`... - on n'écrase jamais une
exécution). **Gabarit de référence : `execution-resultats.md`.** C'est ce contrat qui permet au
rapport de recette de lire les résultats **sans savoir qui a exécuté** : les trois voies
produisent le **même fichier**.

**Tout est en tables** (forme : section 4bis de `ux-conventions.md` - une ligne de séparation
entre chaque ligne de données, étapes en `<br>`, cellule vide = `-`), quatre sections :

| Section | Colonnes | Ce qu'elle porte |
|---|---|---|
| Contexte d'exécution | Adresse testée, Outil, Plan joué, Cas joués | une seule ligne |
|---|---|---|
| Synthèse | Verdict, Nombre, Cas concernés | trois lignes (OK / KO / NON TESTABLE), **en haut du fichier** |
|---|---|---|
| Résultats par cas | Cas, Intitulé, Verdict, Déroulé effectif, Constaté, Preuve | **une ligne par cas du plan, dans l'ordre, aucun omis** |
|---|---|---|
| Écarts (KO et NON TESTABLE) | Cas, Attendu, Constaté, Console et réseau | le diagnostic détaillé ; supprimée si tous les cas sont OK |

Deux règles qui portent l'aval :
- le **déroulé effectif** (étapes réellement jouées, numérotées, séparées par `<br>`) est requis
  **pour tous les cas, y compris OK** : le plan porte les étapes **prévues**, le déroulé porte ce
  qui s'est **vraiment** passé (relances, contournements, ordre effectif). Le fichier de résultats
  étant committé et jamais écrasé, c'est **lui** qui garde cette trace ;
- la colonne **Constaté** de la table principale reste **une phrase** ; l'attendu contredit, la
  console et le réseau vont dans la table **Écarts** - c'est ce qui garde la vue par cas
  scannable.

## Règles de fiabilité (les trois voies)
Cf. `regles-validation.md`, section "Fiabilité d'exécution" : relance unique avec tri
(lenteur / élément introuvable / vrai écart) avant de conclure KO ; budget d'étapes borné ;
un critère ambigu se constate NON TESTABLE, jamais interprété ; aucune action destructive
sans confirmation ; données de test du plan uniquement.
