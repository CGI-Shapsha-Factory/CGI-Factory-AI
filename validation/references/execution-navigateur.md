# Exécution navigateur : les trois voies et le contrat de sortie commun

Référence d'usage d'`execution-validation`. Trois voies d'exécution, un seul contrat de
sortie : le bilan (`bilan-validation`) est **agnostique de l'outil**.

## Le choix de l'outil (à chaque lancement)
Le skill demande au testeur quelle voie utiliser (une question, cf. `interactive-loop.md`),
avec **l'extension Chrome en suggestion recommandée** (voie la plus fidèle : vrai navigateur,
session réelle). Le dernier choix est retenu dans le manifeste comme **suggestion** pour la
prochaine fois - jamais comme automatisme : on redemande à chaque lancement.

## Voie 1 (prioritaire) : l'extension Chrome (Claude in Chrome), en session
Claude Code pilote directement l'extension "Claude in Chrome" : navigation, clics, saisie de
formulaires, lecture de la console et des requêtes réseau, captures d'écran sauvegardées sur
disque.
- **Pré-requis** : l'extension installée dans Chrome, et la session lancée avec le navigateur
  connecté (`claude --chrome`, ou le panneau navigateur de l'app desktop). Non disponible
  sous WSL.
- **Détection** : tenter une action de lecture navigateur ; si le navigateur ne répond pas,
  afficher la marche à suivre (installer l'extension depuis chrome.google.com/webstore,
  relancer la session avec `claude --chrome`, autoriser le domaine de recette dans les
  permissions par site de l'extension) et **proposer la voie Playwright en repli** - jamais
  d'exécution à moitié.
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
  `browser_take_screenshot` (preuve, enregistrée dans `resultats/preuves/`),
  `browser_console_messages` / `browser_network_requests` (diagnostic sur KO).
- Si le MCP Playwright n'est pas disponible non plus, ne rien exécuter : proposer la voie 3
  (mission Cowork) ou l'installation d'un des deux outils.

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
   lancer `/validation:bilan-validation`.

## Le contrat de sortie commun (quel que soit l'outil)
Un fichier de résultats par exécution : `validation-out/<feature>/resultats/execution-<JJ-MM>.md`
(si un fichier du même jour existe déjà, suffixer `-2`, `-3`... - on n'écrase jamais une
exécution). Contenu : l'adresse testée, l'outil utilisé, puis **un bloc par cas de test** :
- `## TC-<feature>-NNN - <intitulé>`
- **Verdict** : OK / KO / NON TESTABLE (avec la raison pour NON TESTABLE)
- **Déroulé effectif** : les étapes réellement jouées, numérotées, en langage naturel (c'est
  la matière des scénarios rejouables)
- **Preuves** : les captures d'écran référencées (chemin relatif)
- sur KO : **Constaté vs attendu** (factuel) + ce que la console / le réseau montrent d'anormal

## Règles de fiabilité (les trois voies)
Cf. `regles-validation.md`, section "Fiabilité d'exécution" : relance unique avec tri
(lenteur / élément introuvable / vrai écart) avant de conclure KO ; budget d'étapes borné ;
un critère ambigu se constate NON TESTABLE, jamais interprété ; aucune action destructive
sans confirmation ; données de test du plan uniquement.
