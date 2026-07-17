# Guide Linear : anomalies et évolutions de recette via le MCP linear-prism

Référence d'usage pour les 4 skills métier de la recette. Le dialogue passe par le **MCP du
plugin `linear-prism`** (serveur hébergé `https://mcp.linear.app/mcp`, authentifié en OAuth via
`/mcp` - **aucune clé API** à gérer). Ce plugin est **externe à la Factory** : les skills le
détectent et, s'il est absent, **ne créent ni ne mettent à jour rien** - ils refusent et
renvoient aux instructions d'installation.

## Détection (avant tout)
Sonder `mcp__plugin_linear-prism_linear__list_teams`.
- **Répond** (liste d'équipes) -> le MCP est prêt, continuer.
- **Échoue / indisponible** -> **ne rien créer ni mettre à jour**. Refuser en clair : "Je ne peux
  pas créer/mettre à jour de tickets Linear : le MCP `linear-prism` n'est pas disponible." Puis
  renvoyer à la section "Installation du plugin linear-prism" ci-dessous, et relancer une fois prêt.

## Installation du plugin linear-prism (si le MCP est absent)
1. **Ajouter la marketplace** : `/plugin marketplace add shinpr/linear-prism`
   (variante "bundle" si l'équipe le distribue ainsi : `/plugin marketplace add shinpr/claude-code-workflows`).
2. **Installer le plugin** : `/plugin install linear-prism@linear-prism`
   (ou `/plugin install linear-prism@claude-code-workflows` pour la variante bundle).
3. **Redémarrer Claude Code** (pour charger le serveur MCP du plugin).
4. **S'authentifier** : lancer **`/mcp`**, choisir le serveur `linear`, terminer le login OAuth.

Revalider ensuite avec la détection ci-dessus (`list_teams` répond).

## Cible (équipe et tickets Feature)
- **Équipe** : celle du bloc `linear` du manifeste (posée par `premier-alimente-linear`, côté
  assembleur). Si le bloc est vide, `list_teams` et confirmation avec l'utilisateur.
- **Tickets Feature** : la carte amont figée vit dans `linear.issues` du manifeste (un ticket
  `Feature` par feature du registre, avec son `identifier` type `FAC-12` et son `url`). C'est là
  que se résout le **ticket parent** d'une anomalie ou d'une évolution. Si le manifeste ne suffit
  pas (clone partiel), retrouver le ticket par `list_issues({query, team})` label `Feature`.

## Rattachement à la feature (règle dure, anti-orphelin)
Une anomalie ou une évolution est **toujours un sous-ticket du ticket `Feature`** de sa
feature : `parentId` = le ticket Feature, désigné par son **`identifier`** (ex. `FAC-12`, tel
que consigné dans le manifeste) ou par son id interne si on l'a - `save_issue` accepte les
deux. C'est ce rattachement (plus le registre `architecture.feature_sequence`) qui permet
l'analyse d'impact : un objet sans feature rattachable est un orphelin -> **refuser de le
créer**. Aucune convention de numérotation dans le titre : l'identifiant natif Linear
(`<TEAM>-<n>`) porte déjà le numéro.

## Labels de recette
Deux labels plats : **`Anomalie`** et **`Evolution`**. `save_issue` prend le paramètre
**`labels`** (une liste de **noms** ou d'ids - passer les noms exacts, ex. `["Anomalie"]`).
`recette-init` vérifie leur existence via `list_issue_labels` (comparaison insensible à la
casse) et crée les manquants via `create_issue_label` (avec le `teamId` UUID de l'équipe,
best-effort : ne pas bloquer un skill métier pour un label absent, l'omettre et le signaler).
Attention : `labels` **remplace tout le jeu de labels** du ticket - à la **mise à jour** d'un
ticket existant, ne jamais passer `labels` sans reprendre les labels déjà présents
(`get_issue` d'abord). Jamais de label de numérotation, jamais `Feature`/`Task` sur un objet
de recette.

## Créer un objet de recette
`save_issue({team, title: "<intitulé métier court>", parentId: "<identifier du ticket
Feature>", labels: ["Anomalie" ou "Evolution"], state: "Backlog", description: "<gabarit
rempli>"})`
- **Description** en Markdown réel (newlines littéraux, pas d'échappement), corps du gabarit
  (`gabarit-anomalie.md` / `gabarit-evolution.md`) entièrement rempli.
- **State = Backlog**, non assigné : le développeur le prendra au point quotidien.
- Récupérer dans la réponse l'**identifier** (champ `id`, ex. `FAC-79`) et l'**url**, et les
  restituer à l'utilisateur. Vérifier aussi dans la réponse que `parentId` et `labels` sont
  bien ceux attendus.

## Statut "Requalifiée en évolution" (pré-requis d'équipe)
Pour que `correction-anomalie` puisse refermer une évolution déguisée, le statut **"Requalifiée
en évolution"** doit exister dans le flux de l'équipe, **dans la famille des statuts annulés**
(type `canceled`) : une anomalie requalifiée est fermée sans correction, ce n'était pas un
défaut. Le MCP **ne sait pas créer de statut** : il se crée **une fois à la main** dans Linear.
Marche à suivre à afficher quand il manque (vérification : `list_issue_statuses({team})`) :
1. Linear -> **Settings** de l'équipe -> **Issue statuses & automations**.
2. Dans le groupe **Canceled**, ajouter un statut nommé **"Requalifiée en évolution"**.
3. Relancer la vérification (le skill `recette-init` la refait à la demande).

Tant que le statut manque, `correction-anomalie` **ne requalifie pas** (le ticket reste en
cours) : afficher la marche à suivre et attendre. Cette vérification **préalable** est
obligatoire : passer à `save_issue` un état inexistant **n'échoue pas** - il est ignoré en
silence (voir ci-dessous).

## Mettre à jour un objet de recette
- **Trouver** : `get_issue({id: "<identifier>"})` (retourne aussi l'état courant et la
  description) ; ou `list_issues({query, team})` par mots-clés du titre.
- **Changer l'état** : `save_issue({id, state})` avec le **nom exact** de l'état, résolu au
  préalable via `list_issue_statuses({team})`. **Ne pas passer le type brut** (`started`,
  `completed`) : une équipe a souvent **plusieurs statuts du même type** (ex. "In Progress"
  **et** "In Review", tous deux `started`) et le MCP prend le premier trouvé - la prise en
  charge vise le statut de travail (ex. "In Progress"), jamais un statut de revue. Résolution :
  prise en charge -> le statut de type `started` qui n'est pas une revue ; clôture -> le statut
  de type `completed` (ex. "Done") ; requalification -> le statut nommé "Requalifiée en
  évolution".
- **Vérifier après chaque écriture (impératif)** : `save_issue` **ignore en silence** un état
  qu'il ne résout pas (aucune erreur, le ticket reste dans son état courant). Après chaque
  changement d'état, lire le champ `status` de la **réponse** et confirmer qu'il est bien
  l'état visé ; sinon, traiter comme un échec (ne jamais annoncer un changement non confirmé).
- **Commenter** : `save_comment({issueId, body})` - la trace de recette vit dans le ticket
  (cause racine et correctif d'une anomalie, explication d'une requalification, réouverture
  d'une feature pour une évolution). Markdown réel, typographie humaine.
- **Idempotence** : lire l'état courant (`get_issue`) **avant** d'écrire ; s'il est déjà celui
  visé, ne rien faire.

## L'état vit dans Linear, jamais dans le manifeste
Le manifeste committé ne porte que la **configuration statique** de la recette (bloc
`recette` : équipe, labels vérifiés, statut de requalification vérifié). Les anomalies, les
évolutions, leurs statuts et leurs commentaires vivent **uniquement dans Linear** : l'activité
de recette est concurrente (plusieurs développeurs, plusieurs branches) et un fichier committé
unique entrerait en conflit de merge. **Linear est la source de vérité** de l'avancement.
