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

## Tour de table à chaud (avant les questions structurées)

Juste après le nom du projet, **avant** le dépouillement et la passe découverte, ouvrir un
court tour de table libre. Ces temps sont **facultatifs et jamais insistés** : "rien à
ajouter" fait passer directement à la suite.

**Atelier d'idéation si la matière est mince (une seule proposition, facultative).** Si peu ou
pas de sources ont été fournies, ou si le sujet est manifestement encore en train de se former,
proposer **avec `AskUserQuestion`** - deux options : "Cadrons d'abord les zones floues à voix
haute (court atelier)" et "La matière est solide, on structure directement". Sur le premier
choix, orienter vers `/cadrage:cadrage-ideation` (son compte rendu revient comme source, repris
au chargement) puis reprendre l'extraction ; sur le second, continuer le tour de table. **Ne pas
la proposer** si des sources riches sont déjà là - ce serait une friction inutile.

1. **Invitation ouverte (un seul message).** Inviter l'utilisateur à vider son sac : tout ce
   qui lui semble important et qui n'est pas dans les sources - contexte, intuitions,
   contraintes, points non négociables, idées encore floues. Attendre la réponse, puis poser
   **une seule relance** : "quoi d'autre ?" (elle fait souvent remonter ce qu'on a failli
   oublier). Ne pas entrer dans le détail à ce stade : les questions granulaires viennent
   après, elles interrompraient le déballage. Ce qui est dit ici est de la **matière brute
   comme une autre** : ça alimente les sections de la capture et sert de suggestion dans la
   passe découverte, avec confirmation par le flux normal - rien n'est validé d'office.
2. **Lecture de l'enjeu (une question).** Demander **avec `AskUserQuestion`** quel est l'enjeu
   du projet, parmi outil interne, pilote / expérimentation, ou lancement public / critique :
   **deux options** - les deux lectures les plus plausibles au vu de la matière -, la troisième
   reste accessible par la saisie libre. Cette lecture est
   une **calibration interne uniquement, jamais persistée telle quelle** : elle règle
   l'intensité de la relance sur réponse mince (cf. `references/interactive-loop.md`) et la
   richesse des suggestions proposées. Un enjeu fort justifie de creuser davantage ; un outil
   interne modeste ne mérite pas un interrogatoire. (Le recouvrement avec la question sur le
   type de projet est normal : c'est elle qui porte la réponse persistée.)
3. **Projection d'échec et hypothèse-clé (deux relances ouvertes, prose).** Toujours dans le
   registre du tour de table (prose, **pas** `AskUserQuestion` : on fait produire, on ne collecte
   pas de décision), poser deux questions courtes l'une après l'autre, en attendant la réponse à
   chaque fois :
   - Pré-mortem : "Projetons-nous : on est [horizon réaliste] après la mise en service et le
     projet est jugé décevant. Qu'est-ce qui a le plus probablement mal tourné ?"
   - Hypothèse-clé : "Quelle est l'hypothèse que tu tiens pour acquise aujourd'hui et qui, si
     elle se révélait fausse, remettrait tout le projet en cause ?"
   **Facultatif et jamais insisté** ("rien ne me vient" fait passer) ; **calibré sur l'enjeu**
   (appuyé pour un lancement critique, à peine effleuré pour un outil interne modeste). Ce qui
   remonte est de la **matière brute** : ça alimente les sections Frictions, Contraintes et
   Objectifs de la capture, et sert de **suggestion** à la question sur les incertitudes et
   hypothèses (Q19) - jamais validé d'office, confirmé par le flux normal. Ne pas creuser ici :
   le sondage détaillé, s'il est justifié, viendra pendant la passe découverte (relance unique,
   puis sondage approfondi opt-in ; cf. `references/interactive-loop.md`).

## Procédure

1. **Charger** le contenu de chaque source (Notion, ou fichier `.txt`/`.md`/
   transcript/`.pdf`/`.docx` selon les règles de la section Entrées). Écrire la
   capture dans `cadrage-out/capture-brute.md`. **Cas particulier des comptes rendus
   d'idéation** (`cadrage-out/source-contexte/ideation-<JJ-MM>.md`, produits par
   `cadrage-ideation`) : les dépouiller comme toute source pour les sept sections, **et en
   plus** reprendre nommément leurs deux sections finales - les **Hypothèses à vérifier**
   deviennent des **suggestions** de la question sur les incertitudes et hypothèses (Q19), les
   **Questions émergentes** deviennent des **points à creuser** dans la passe découverte. Ces
   éléments restent des suggestions à confirmer par le flux normal, jamais des réponses validées.
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
   Poser **chaque** question **avec `AskUserQuestion`**, en français : l'intitulé de la question
   précédé du compteur **"Qn/19"**, et **exactement deux options** - la **réponse recommandée**
   (la suggestion tirée de la matière si elle existe, sinon la plus plausible ; sa `description`
   dit ce qui la soutient) puis l'**alternative crédible** (la lecture concurrente de la matière,
   ou le cas de figure opposé le plus fréquent). **Une question de découverte est toujours
   esquivable : l'option 2 est donc "je laisse ce point de côté"**, et l'alternative de fond
   passe dans la saisie libre - sans quoi le retrait n'existe plus à l'écran (cf.
   `references/interactive-loop.md`). La saisie libre est ajoutée par l'outil : ne
   jamais la fabriquer en troisième option. La **puce** porte le thème en clair
   ("Utilisateurs", "Hébergement"), **jamais** le code de la question. **Aucune question en prose dans le fil.** Puis **POSE
   UNE SEULE QUESTION, ARRÊTE-TOI, et ATTENDS la réponse** avant de passer à la suivante. **Jamais** plusieurs questions dans un même appel de l'outil ni dans un même message ; **jamais**
   d'auto-complétion ; **jamais** `answered` sans réponse explicite. Ne jamais remplir de valeur démo.
   - Réponse explicite (suggestion acceptée ou saisie) -> statut `answered`. **Aucune `(src:)` écrite.**
   - L'utilisateur laisse de côté (option 2, ou saisie libre équivalente) -> le champ est **omis**
     (statut `deferred`, rien d'écrit dans l'artefact, pas de marqueur).
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

Étape suivante : `/cadrage:cadrage-vision` - transformer la capture en vision produit.
