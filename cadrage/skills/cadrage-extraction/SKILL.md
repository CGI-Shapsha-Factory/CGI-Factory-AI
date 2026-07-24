---
name: cadrage-extraction
description: Dépouille la matière brute de l'atelier en une capture structurée et traçable.
argument-hint: "[fichier, fichiers ou dossier]"
---

# cadrage-extraction

Première étape de la ligne de production. Dépouille la matière brute et la range
en sections fixes, sans rien inventer. Tout le reste du pipeline part de cette
capture.

## Objectif

Transformer une ou plusieurs sources brutes en une **capture structurée et
lisible**, centrée sur le **contenu** (ce qui doit être fait, les besoins, les
contraintes) - **pas** sur qui a dit quoi ni à quel moment. Le skill n'est pas un
formulaire de saisie : la matière existe déjà, on la transforme et on la range.

**Jamais d'horodatage, jamais de tour de parole, jamais de `(src: ...)` dans
l'artefact.** On extrait le fond, on ne trace pas la forme. La règle "ne rien
inventer" reste un garde-fou interne (on ne s'appuie que sur la matière), sans
écrire la provenance.

## Entrées

Une ou plusieurs sources déclarées par l'utilisateur. L'entrée est **souple** :
accepter **un seul chemin de fichier**, **plusieurs chemins**, **ou un dossier**
(dans ce cas, ingérer tous les fichiers de format supporté qu'il contient).

Les chemins peuvent être **passés en argument** à l'invocation
(`/cadrage:cadrage-extraction <chemins>` -> disponibles via `$ARGUMENTS`) **ou** déclarés
dans le chat. Si `$ARGUMENTS` est non vide, l'utiliser comme sources.

**Emplacement central par défaut** : `cadrage-out/source-contexte/` (créé par `cadrage-init`).
Si aucune source n'est passée en argument ni déclarée dans le chat, **regarder d'abord dans
`cadrage-out/source-contexte/`** et ingérer les fichiers de format supporté qui s'y trouvent.
Ce dossier est **facultatif** : s'il est vide (ou absent), continuer normalement en demandant
les sources - il n'est **jamais** obligatoire ni une porte de validation.

**Matière déposée APRÈS le cadrage initial** (nouveau compte rendu de réunion, exigences
nouvelles, corrections) : ne pas rejouer l'extraction - c'est le rôle de
`cadrage-retour-client` (mode projet), qui détecte les fichiers non encore ingérés, les
confronte à l'existant et met à jour les artefacts en place.

- **Pages Notion** (hubs réunion, transcripts) - via les outils Notion
  disponibles (`notion-fetch`, `notion-search`).
- **Fichiers fournis** - formats supportés : `.txt`, `.md`, transcripts, `.pdf`,
  `.docx`.
  - `.pdf` : lu via l'outil Read.
  - `.docx` : convertir avec `python-docx` ; si le fichier reste illisible,
    demander à l'utilisateur un export texte.

## Workspace et manifeste

Les documents du cadrage vivent dans `cadrage-out/` à la racine du projet client, et le
manifeste `manifest.json` est le contrat machine entre les skills.
**Les deux sont créés par `cadrage-init`** (skill d'amorçage) - `cadrage-extraction`
ne bootstrappe plus rien. Toute écriture du manifeste est un **read-modify-write**
suivi d'une **revalidation JSON** (le fichier doit reparser sans erreur).

## Pré-requis (vérification silencieuse)

Vérifier sans l'annoncer : **le manifeste existe ET au moins une source est
déclarée.** Ne jamais afficher de statut de "porte" ; si un pré-requis manque,
poser une question **avec `AskUserQuestion`** (deux options : l'issue recommandée et
l'alternative crédible).

1. Si `manifest.json` est absent : indiquer en clair qu'il faut
   d'abord initialiser le workspace (`cadrage-init`) et s'arrêter là.
2. Recueille les sources que l'utilisateur déclare (id de page Notion, chemin de
   fichier, plusieurs chemins, ou un dossier). Si l'entrée est un dossier, lister
   et ingérer tous les fichiers de format supporté qu'il contient. **À défaut de source
   déclarée, regarder dans `cadrage-out/source-contexte/`** et ingérer les fichiers
   supportés qui s'y trouvent. Enregistre chaque source dans `sources[]` avec `type`,
   `ref`, `ingested_at`.
3. Si aucune source n'est déclarée **et** que `cadrage-out/source-contexte/` est vide ou
   absent : demander au moins une source **avec `AskUserQuestion`** - deux options tirées de ce
   qu'on voit dans le dossier (un fichier candidat trouvé à la racine, le dépôt d'un export dans
   `cadrage-out/source-contexte/`), la saisie libre pour un chemin quelconque. N'invente pas de
   matière. (Le dossier
   `source-contexte/` reste facultatif - son absence ne bloque jamais à elle seule.)

## Porte de régénération (relance)
Avant toute (re)génération, appliquer `references/regeneration-gate.md`. Si les sorties **de ce
skill** existent déjà, proposer le choix **Repartir de zéro** (supprimer puis générer à neuf,
`version: 1`) ou **Garder les deux (versionner)** (archiver l'existant sous `_archives/`, régénérer
au nom canonique en `version: N+1`) et **attendre** le choix. Premier passage (rien n'existe) :
générer directement, sans porte.

## Identité du projet

Avant le dépouillement, demander **avec `AskUserQuestion`** : "Quel est le **nom du projet** ?"
(le nom usuel, lisible). **Deux options** tirées des sources - le nom qui revient dans le
transcript ou les documents, et la variante concurrente qu'on y lit -, la saisie libre pour tout
autre nom.

Écrire la réponse dans `project` du manifeste (laissé `null` par `cadrage-init`).
**Ne jamais le déduire** du nom du dossier - il ne sert jamais d'option non plus. Si l'utilisateur ne répond pas, suivre la
boucle interactive (`references/interactive-loop.md`).

**Ne pas demander le nom du client.** Cette information n'est pas collectée par la
factory - ne pas la poser, ne pas l'écrire dans le manifeste.

**Aussitôt le nom obtenu, enchaîner directement** sur le dépouillement (silencieux) puis la
passe de découverte : **ne pas s'arrêter** sur un tour de table ou une invitation ouverte
("qu'as-tu à ajouter ?") entre le nom et les questions structurées.

## Procédure

1. **Charger** le contenu de chaque source (Notion, ou fichier `.txt`/`.md`/
   transcript/`.pdf`/`.docx` selon les règles de la section Entrées). Écrire la
   capture dans `cadrage-out/capture-brute.md`.
2. **Dépouiller** la matière et la classer dans les **sept sections fixes**
   (voir ci-dessous). Travailler section par section, sur l'ensemble des
   sources. Extraire le **contenu**, reformulé clair et lisible.
3. **Rester fidèle à la matière.** Ne s'appuyer que sur ce que disent les
   sources ; ne jamais ajouter de sens absent. **Ne pas écrire de provenance**
   (ni horodatage, ni interlocuteur, ni `(src: ...)`).
4. **Ne pas combler un blanc.** Si une section n'a pas de matière, la laisser
   présente avec une courte mention "non abordé". Un élément incertain n'est
   **pas écrit comme un fait** ; en cas de doute réel, on l'omet plutôt que de
   l'inventer. Aucune extrapolation.

### Structure de `capture-brute.md`

Sept sections fixes, toutes présentes même vides - **contenu uniquement, sans
trace de source** :

```
# Capture brute : <projet>
Statut : draft

## 1. Parties prenantes
Les rôles concernés : qui, leur rôle, leur lien au besoin. Une ligne par rôle.

## 2. Jobs (jobs-to-be-done)
Ce que les utilisateurs cherchent à accomplir, dans des cas réels et récents.
Le job, son déclencheur, le contexte.

## 3. Frictions
Les douleurs, blocages, contournements subis aujourd'hui.

## 4. Alternatives réellement utilisées
Ce qui est employé aujourd'hui pour faire le job (outils, tableurs,
processus manuels, concurrents). Du factuel observé, pas du supposé.

## 5. Termes métier candidats
Le vocabulaire du client repéré dans la matière, futurs candidats du
glossaire. Le terme et son sens d'usage. Pas de définition inventée ici.

## 6. Contraintes évoquées
Contraintes citées : techniques, réglementaires, sécurité, organisationnelles,
délais.

## 7. Objectifs évoqués
Les outcomes et buts cités.
```

## Passe découverte (19 questions de cadrage) : **interactive, une question à la fois**

En plus de la capture, exécuter la **passe découverte** sur les 19 questions de
`references/discovery-questions.md` (Q1-Q19). Elle remplit
`cadrage-out/project-frame.md` (gabarit `.factory/cadrage/project-frame.md`)
et le bloc `discovery` du manifeste.

> ⚠️ **Workflow OBLIGATOIRE, jamais en lot.** On **déroule les 19 questions une par une**, même
> quand le transcript semble déjà répondre : le transcript fournit une **suggestion à confirmer**,
> pas une réponse validée. **Interdit** : remplir les 19 d'un coup depuis les sources et annoncer un
> bilan sans avoir rien demandé à l'utilisateur.

1. **Préparer les suggestions (sans rien écrire, sans rien valider).** Pour chaque Qn, chercher dans
   le transcript/docs une **réponse candidate** et la garder comme **suggestion à confirmer**.
   **Aucune question n'est `answered` à ce stade.**
2. **Dérouler la boucle interactive - Q1 -> Q19, UNE À LA FOIS** (voir `references/interactive-loop.md`).
   **POSE UNE SEULE QUESTION, ARRÊTE-TOI, et ATTENDS la réponse** avant de passer à la suivante.
   **Jamais** plusieurs questions dans un même appel ni dans un même message ; **jamais**
   d'auto-complétion ; **jamais** `answered` sans réponse explicite. Ne jamais remplir de valeur démo.
   Deux formes selon la question :
   - **Q1 à Q13 : format deux options via `AskUserQuestion`.** L'intitulé précédé du compteur
     **"Qn/19"**, et **exactement deux options** - la **réponse recommandée** (la suggestion tirée
     de la matière si elle existe, sinon la plus plausible ; sa `description` dit ce qui la soutient)
     puis l'**alternative crédible** (la lecture concurrente, ou le cas opposé le plus fréquent).
     **Une question de découverte est toujours esquivable : l'option 2 est donc "je laisse ce point
     de côté"**, l'alternative de fond passant dans la saisie libre - sans quoi le retrait n'existe
     plus à l'écran. La saisie libre est ajoutée par l'outil : ne jamais la fabriquer en troisième
     option. La **puce** porte le thème en clair ("Utilisateurs", "Hébergement"), **jamais** le code
     de la question. **Aucune question en prose dans le fil** pour cette tranche.
   - **Q14 à Q18 (questions produit) : en PROSE dans le fil, JAMAIS via `AskUserQuestion`.**
     L'outil impose au moins deux options affichées ; ici on n'en veut **aucune** - la question
     est donc posée **directement dans la conversation** et l'utilisateur **tape sa réponse**.
     Garder le compteur **"Qn/19"** et le thème en tête de ligne (ex. "Q15/19 - Pourquoi
     maintenant : ..."), **une seule question par message**, on attend la réponse avant la
     suivante. **Aucune suggestion de contenu** : ne **jamais** proposer de réponse recommandée
     ni d'alternative tirée du transcript. Dire sobrement dans la question qu'il peut répondre
     avec ses mots ou taper "je passe" pour laisser le point de côté (-> `deferred`).
     **Reformuler avec un exemple** uniquement s'il le demande ou si sa réponse montre qu'il n'a
     pas compris la question (**une seule fois**), sans jamais suggérer la réponse.
     **On ne pré-remplit aucune de ces réponses depuis les sources** - le but est de **forcer
     l'utilisateur à les formuler lui-même** (le brainstorm approfondi vit ensuite dans
     `cadrage-ideation`). Le contenu du transcript reste capté dans la capture (sections
     Problème / Contraintes / Objectifs), mais la **réponse de découverte** vient du texte tapé.
     **Enchaînement direct après Q13 : aucune phrase de transition** ("on passe aux questions
     produit...") - même rythme, question suivante directement. La **relance unique** sur
     réponse vague s'applique comme ailleurs (coacher, pas quizzer).
   - **Q19 (incertitudes / hypothèses) : NE PAS poser la question brute. Déduire puis sonder,
     façon brainstorming.** Mécanisme inspiré de `superpowers:brainstorming` (faire émerger
     l'inconnu, une question à la fois) :
     1. **Déduire** (silencieusement, sans afficher de mécanique) les incertitudes et hypothèses
        tacites sur lesquelles le projet repose, à partir de **toute** la matière (capture,
        réponses Q1-Q18). Viser surtout les **angles morts non formulés**. Le
        **nombre suit le nombre d'angles morts réels** : peu si le contexte est clair et complet,
        beaucoup s'il est flou/incomplet (indices : questions restées `deferred`, sections minces,
        contradictions, cibles absentes, dépendances externes non tranchées).
     2. **Sonder une par une, en PROSE dans le fil** (jamais via `AskUserQuestion` - même règle
        que Q14-Q18 : zéro option affichée, l'utilisateur tape sa réponse) : transformer chaque
        hypothèse en une **question de vérification ancrée** ("Le projet suppose X - est-ce
        voulu / vrai ? qu'est-ce qui se passe si ce n'est pas le cas ?"). Au **début du
        sondage** (une seule fois, pas à chaque sonde), rappeler sobrement qu'il peut taper
        "je passe" (-> sonde suivante ; l'hypothèse non sondée est transmise oralement à
        l'atelier `cadrage-ideation`, jamais persistée comme marqueur) ou "ça suffit, on
        avance" (-> fin du sondage, passage à la convergence). **Une seule question par
        message**, on attend la réponse avant la suivante. **Relance unique** sur réponse
        vague ; **jamais** sur le légal (Q8). L'arrêt étant possible à tout moment par un
        simple "ça suffit", **aucun contrôle d'arrêt séparé** n'est nécessaire.
     3. **Converger** : synthétiser les incertitudes/hypothèses confirmées en une **liste**, écrite
        dans le champ Risques & hypothèses de `project-frame.md`. Q19 -> `answered` dès qu'une
        synthèse existe ; si l'utilisateur esquive d'emblée ("je laisse de côté") -> `deferred`.
   - Réponse explicite (suggestion acceptée ou saisie) -> statut `answered`. **Aucune `(src:)` écrite.**
   - L'utilisateur laisse de côté (option "je laisse ce point de côté" sur Q1-Q13, ou "je
     passe" tapé sur Q14-Q19) -> le champ est **omis** (statut `deferred`, rien d'écrit dans
     l'artefact, pas de marqueur).
   - **Q8 (contraintes légales / conformité / RGPD) est OPTIONNELLE.** La proposer **une seule fois**,
     sans insister. C'est la **seule question dont la forme des options est imposée** : option 1 =
     la contrainte pressentie dans la matière, **option 2 = "on gère ça nous-mêmes"**. Sans cette
     seconde option, décliner n'est plus visible et la question devient l'interrogatoire que la
     règle proscrit. Si l'utilisateur la décline / la laisse à l'équipe ->
     statut **`na`** (traité hors cadrage), **pas `deferred`** : elle ne doit **jamais** bloquer la
     complétude ni revenir. **Ne jamais pousser la conformité** (cf. `references/discovery-questions.md`,
     note Q8, et `references/ux-conventions.md` §2bis).
   - Décisions groupées (l'utilisateur tranche plusieurs questions d'un coup) -> **relire la liste parsée et
     faire confirmer** avant d'écrire (cf. interactive-loop) ; sinon, une question à la fois.
   À la fin de la boucle, annoncer **en clair** que tout est complété - "**toutes les questions de
   cadrage sont répondues**" - (ou rappeler oralement les points laissés de côté). **Jamais** de nom
   de champ ("discovery_complete = true") ni de code de question (`Q8`, `Q11`...), et **aucun caveat
   d'architecture** sur un point déjà tranché (cf. `references/ux-conventions.md` §2ter, §3ter). Vaut
   en particulier pour les *seeds qualité* de charge/disponibilité/performance.
3. **Écrire** les réponses dans `project-frame.md` (chaque champ = le contenu décidé, **sans `(src:)`** ;
   un champ non tranché est **omis**). Le project-frame vit sous
   `cadrage-out/project-frame.md`. Les réponses Q1 (qui utilise), Q3 (rôles),
   Q9 (type de projet), Q14 (problème), Q15 (pourquoi maintenant) et Q17 (signaux
   de succès) seront aussi reprises côté vision par `cadrage-vision` (suggestions
   pré-remplies du product-brief, à confirmer, jamais reposées à froid).

Les questions Q2 (charge), Q6 (disponibilité), Q7 (performance) sont des **seeds
de qualité** : on les capte bruts ici, le plugin **architecte** les transformera
en drivers / scénarios de qualité. Une réponse **directionnelle / non chiffrée** à Q2/Q6/Q7
(ex. "fiabilité avant la vitesse") se note telle quelle comme orientation ; ne **jamais** la
présenter comme une cible chiffrée.

## Auto-contrôle (avant écriture)

Pour **chaque ligne** de la capture, poser la question : *est-ce bien soutenu par la
matière source ?* Si non, la ligne disparaît (on ne l'invente pas). C'est le
garde-fou anti-hallucination - interne, sans écrire de provenance.

## Vérification avant écriture

Avant d'écrire le manifeste, vérifier :
- Les **sept sections sont présentes** (vides autorisées, avec une courte mention "non abordé").
- **Aucune invention** (auto-contrôle passé), **aucune `(src:)` ni horodatage** dans l'artefact.
- **Chaque question de découverte tranchée est écrite** ; les questions laissées de côté sont
  simplement absentes. Vérifiable par
  `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_discovery.py" <racine>/manifest.json`.

Si une de ces conditions échoue, corriger avant d'écrire.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.capture_brute.status = "draft"`.
- `phase = "extraction"`.
- `sources[]` complété par les sources dépouillées (si pas déjà fait au pré-requis).
- `artifacts.project_frame.status`.
- `discovery[]` : mettre à jour chaque entrée Qn (`status`, `answer`). **Pas de champ
  `source`.** Une question tranchée -> `answered` ; laissée de côté -> `deferred` ; **Q8 légal/conformité
  laissée à l'équipe -> `na`** (terminal, non bloquant).
- `discovery_complete` : `true` si aucune question n'est `pending`/`deferred` (un `na` - dont un Q8
  légal laissé à l'équipe - **n'empêche pas** la complétude).
- `updated_at` à l'horodatage courant.

> **Silencieux - jamais annoncé.** Ne **jamais** dire à l'utilisateur que le manifeste est mis à jour,
> ni citer un nom de champ ou une valeur `true`/`false` (interdit : "Manifeste à jour : phase:
> extraction, discovery_complete: true", toute liste `champ: valeur`). Confirmer seulement, en clair,
> **ce qui a été produit** + la prochaine étape (cf. `references/ux-conventions.md`).

## Règles invariantes appliquées ici

- **Ne pas inventer.** On ne s'appuie que sur la matière ; un point non soutenu est
  omis, jamais comblé ni présenté comme un fait.
- **Contenu, pas provenance.** Aucun horodatage, aucun interlocuteur, aucune `(src:)`
  dans l'artefact.
- **Skill indépendant.** Invocable seul ; la cohérence passe par le manifeste,
  pas par un orchestrateur.

Étape suivante : `/cadrage:cadrage-ideation` - étudier la matière extraite, combler les trous et brainstormer les détails avec l'utilisateur avant de passer à la vision.
