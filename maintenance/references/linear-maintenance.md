# Guide Linear : anomalies et évolutions de maintenance via le MCP linear-prism

Référence d'usage pour les 4 skills métier de la maintenance. Le dialogue passe par le **MCP du
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
- **Tickets Feature** : ils vivent **dans Linear** (aucune carte dans le manifeste). Le **ticket
  parent** d'une anomalie ou d'une évolution se résout par `list_issues({team, label Feature})`
  (jointure par titre : l'id de feature `001...` figure en tête, ex. `001 - ...`) ou
  `list_issues({query, team})`.

## Rattachement à la feature (règle dure, anti-orphelin)
Une anomalie ou une évolution est **toujours un sous-ticket du ticket `Feature`** de sa
feature : `parentId` = le ticket Feature, désigné par son **`identifier`** (ex. `FAC-12`, tel
que retrouvé dans Linear) ou par son id interne si on l'a - `save_issue` accepte les
deux. C'est ce rattachement (plus le registre `architecture.feature_sequence`) qui permet
l'analyse d'impact : un objet sans feature rattachable est un orphelin -> **refuser de le
créer**. Aucune convention de numérotation dans le titre : l'identifiant natif Linear
(`<TEAM>-<n>`) porte déjà le numéro.

## Marquer une phase de `tasks.md` possédée par un ticket de maintenance
Quand une anomalie ou une évolution fait **régénérer** `specs/<feature>/tasks.md`, la phase
créée doit **nommer son ticket propriétaire** dans son titre :

```
## Phase 7: Évolution RAG-12 - Ingestion des pièces scannées au format PNG
## Phase 8: Anomalie RAG-31 - Correction du chevauchement de réservations
```

Sans ce marqueur, `/assembleur:creation-tasks-linear` et le hook `tasks.md` voient une phase
sans sous-ticket et proposent d'en créer un : ce serait un **doublon** du ticket de maintenance,
son **frère** sous la même Feature, avec deux états à synchroniser - et "Linear est la seule
source de vérité" tombe. Marquée, la phase est **énoncée et passée**, jamais proposée. Règle
complète et motif exact : `assembleur/references/linear-guide.md`, 4e clé de jointure.

**Ce marqueur ne contredit pas la règle ci-dessus.** L'interdit de numérotation porte sur le
**titre d'un ticket Linear** (l'identifiant natif y suffit). Le marqueur, lui, vit dans un
**titre de phase markdown** dans `tasks.md` : objet différent, besoin différent (un fichier
committé n'a aucun moyen natif de désigner un ticket). Les deux règles coexistent.

**Corollaire** : un skill de maintenance **n'appelle jamais** `/assembleur:creation-tasks-linear`.
Le ticket d'anomalie ou d'évolution **est** l'objet suivi ; la phase en est un détail
d'implémentation, et son avancement se trace par le statut et les commentaires de ce ticket.

## Labels de maintenance
Deux labels plats : **`Anomalie`** et **`Evolution`**. `save_issue` prend le paramètre
**`labels`** (une liste de **noms** ou d'ids - passer les noms exacts, ex. `["Anomalie"]`).
`maintenance-init` vérifie leur existence via `list_issue_labels` (comparaison insensible à la
casse) et crée les manquants via `create_issue_label` (avec le `teamId` UUID de l'équipe,
best-effort : ne pas bloquer un skill métier pour un label absent, l'omettre et le signaler).
Attention : `labels` **remplace tout le jeu de labels** du ticket - à la **mise à jour** d'un
ticket existant, ne jamais passer `labels` sans reprendre les labels déjà présents
(`get_issue` d'abord). Jamais de label de numérotation, jamais `Feature`/`Task` sur un objet
de maintenance.

## Créer un objet de maintenance
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
3. Relancer la vérification (le skill `maintenance-init` la refait à la demande).

Tant que le statut manque, `correction-anomalie` **ne requalifie pas** (le ticket reste en
cours) : afficher la marche à suivre et attendre. Cette vérification **préalable** est
obligatoire : passer à `save_issue` un état inexistant **n'échoue pas** - il est ignoré en
silence (voir ci-dessous).

## Mettre à jour un objet de maintenance
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
- **Commenter** : `save_comment({issueId, body})` - la trace de maintenance vit dans le ticket
  (cause racine et correctif d'une anomalie, explication d'une requalification, réouverture
  d'une feature pour une évolution). Markdown réel, typographie humaine.
- **Idempotence** : lire l'état courant (`get_issue`) **avant** d'écrire ; s'il est déjà celui
  visé, ne rien faire.

## L'état vit dans Linear, jamais dans le manifeste
Le manifeste committé ne porte que la **configuration statique** de la maintenance (bloc
`maintenance` : équipe, labels vérifiés, statut de requalification vérifié). Les anomalies, les
évolutions, leurs statuts et leurs commentaires vivent **uniquement dans Linear** : l'activité
de maintenance est concurrente (plusieurs développeurs, plusieurs branches) et un fichier committé
unique entrerait en conflit de merge. **Linear est la source de vérité** de l'avancement.
