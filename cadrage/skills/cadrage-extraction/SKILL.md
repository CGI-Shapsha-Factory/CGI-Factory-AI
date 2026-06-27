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

Transformer une ou plusieurs sources brutes en une **capture structurée,
agnostique de la source et entièrement traçable**. Le skill n'est pas un
formulaire de saisie : la matière existe déjà, on la transforme et on la range.

## Entrées

Une ou plusieurs sources déclarées par l'utilisateur. L'entrée est **souple** :
accepter **un seul chemin de fichier**, **plusieurs chemins**, **ou un dossier**
(dans ce cas, ingérer tous les fichiers de format supporté qu'il contient).

Les chemins peuvent être **passés en argument** à l'invocation
(`/cadrage:cadrage-extraction <chemins>` → disponibles via `$ARGUMENTS`) **ou** déclarés
dans le chat. Si `$ARGUMENTS` est non vide, l'utiliser comme sources ; s'il est vide et
qu'aucune source n'est déclarée, **demander les sources** (ne rien inventer).

- **Pages Notion** (hubs réunion, transcripts) — via les outils Notion
  disponibles (`notion-fetch`, `notion-search`).
- **Fichiers fournis** — formats supportés : `.txt`, `.md`, transcripts, `.pdf`,
  `.docx`.
  - `.pdf` : lu via l'outil Read.
  - `.docx` : convertir avec `python-docx` ; si le fichier reste illisible,
    demander à l'utilisateur un export texte.

## Workspace et manifeste

Le workspace projet vit dans `factory-docs/` à la racine du projet client, et le
manifeste `factory-docs/manifest.json` est le contrat machine entre les skills.
**Les deux sont créés par `cadrage-init`** (skill d'amorçage) — `cadrage-extraction`
ne bootstrappe plus rien. Toute écriture du manifeste est un **read-modify-write**
suivi d'une **revalidation JSON** (le fichier doit reparser sans erreur).

## Porte d'entrée

**Le manifeste existe ET au moins une source est déclarée.**

1. Si `factory-docs/manifest.json` est absent : **refuse d'agir** et oriente vers
   `cadrage-init`.
2. Recueille les sources que l'utilisateur déclare (id de page Notion, chemin de
   fichier, plusieurs chemins, ou un dossier). Si l'entrée est un dossier, lister
   et ingérer tous les fichiers de format supporté qu'il contient. Enregistre
   chaque source dans `sources[]` avec `type`, `ref`, `ingested_at`.
3. Si `sources[]` est vide : **refuse d'agir** et demande à l'utilisateur de
   fournir au moins une source. N'invente pas de matière.

## Identité du projet

Avant le dépouillement, **demander à l'utilisateur, en français** (attendre la réponse) :
- « Quel est le **nom du projet** ? » (le nom usuel, lisible).

Écrire la réponse dans `project` du manifeste (laissé `null` par `cadrage-init`).
**Ne jamais le déduire** du nom du dossier. Si l'utilisateur ne répond pas, suivre la
boucle interactive à trois options (`references/interactive-loop.md`).

**Ne pas demander le nom du client.** Cette information n'est pas collectée par la
factory — ne pas la poser, ne pas l'écrire dans le manifeste.

## Procédure

1. **Charger** le contenu de chaque source (Notion, ou fichier `.txt`/`.md`/
   transcript/`.pdf`/`.docx` selon les règles de la section Entrées). Écrire la
   capture dans `factory-docs/work/capture-brute.md`.
2. **Dépouiller** la matière et la classer dans les **sept sections fixes**
   (voir ci-dessous). Travailler section par section, sur l'ensemble des
   sources.
3. **Tracer** chaque élément capté : à côté de chaque item, une référence à la
   source (page / fichier + repère : citation courte, horodatage, ou numéro de
   tour de parole). **Pas de trace possible → ne pas l'écrire comme un fait,
   mais le marquer `[À VALIDER]`** s'il s'agit d'un élément pressenti utile à
   clarifier.
4. **Ne jamais combler un blanc.** Une section sans matière reste présente, avec
   la mention `[NON COUVERT EN ATELIER]`. Un élément incertain ou implicite est
   marqué `[À VALIDER]`. Aucune extrapolation, aucune reformulation qui ajoute du
   sens absent de la source.
5. **Consolider et compter les trous** : rassembler tous les marqueurs
   `[À VALIDER]` / `[NON COUVERT EN ATELIER]` en **entrées de la section Trous**,
   une entrée par point distinct à clarifier (un même trou cité dans plusieurs
   sections ne compte qu'une fois). Le **nombre d'entrées de la section Trous**
   est la valeur `gaps` du manifeste.

### Structure de `capture-brute.md`

Sept sections fixes, toutes présentes même vides :

```
# Capture brute — <projet>
Statut : draft
Sources : <liste des sources dépouillées>

## 1. Parties prenantes
Qui a été mentionné : rôle, mandat, lien au besoin. Une ligne par partie
prenante, avec sa trace source.

## 2. Jobs (jobs-to-be-done)
Ce que les utilisateurs cherchent à accomplir, dans des cas réels et récents.
Le job, son déclencheur, le contexte. Trace source par job.

## 3. Frictions
Les douleurs, blocages, contournements subis aujourd'hui. Trace source.

## 4. Alternatives réellement utilisées
Ce qui est employé aujourd'hui pour faire le job (outils, tableurs,
processus manuels, concurrents). Du factuel observé, pas du supposé. Trace.

## 5. Termes métier candidats
Le vocabulaire du client repéré dans la matière, futurs candidats du
glossaire. Terme + extrait source. Pas de définition inventée ici.

## 6. Contraintes évoquées
Contraintes citées : techniques, réglementaires, sécurité, organisationnelles,
délais. Trace source. Les contraintes pressenties mais non confirmées →
[À VALIDER].

## 7. Objectifs évoqués
Les outcomes et buts cités. Trace source. Objectif sous-entendu mais non
formulé → [À VALIDER].

## Trous
Liste consolidée des [À VALIDER] et [NON COUVERT EN ATELIER], avec pour
chacun la section concernée. Alimente cadrage-clarification.
```

## Passe découverte (13 questions de cadrage) — **interactive, une question à la fois**

En plus de la capture, exécuter la **passe découverte** sur les 13 questions de
`references/discovery-questions.md` (Q1–Q13). Elle remplit
`factory-docs/work/project-frame.md` (gabarit `factory-docs/templates/project-frame.md`)
et le bloc `discovery` du manifeste.

> ⚠️ **Workflow OBLIGATOIRE, jamais en lot.** On **déroule les 13 questions une par une**, même
> quand le transcript semble déjà répondre : le transcript fournit une **suggestion à confirmer**,
> pas une réponse validée. **Interdit** : remplir les 13 d'un coup depuis les sources et annoncer un
> bilan sans avoir rien demandé à l'utilisateur.

1. **Préparer les suggestions (sans rien écrire, sans rien valider).** Pour chaque Qn, chercher dans
   le transcript/docs une **réponse candidate** et la garder comme **suggestion pré-remplie** avec sa
   trace `(src: transcript)`. **Aucune question n'est `answered` à ce stade.**
2. **Dérouler la boucle interactive — Q1 → Q13, UNE À LA FOIS** (voir `references/interactive-loop.md`).
   Pour **chaque** question, en français, afficher le compteur **« Qn/13 »**, l'intitulé, puis **trois
   options** :
   1. **Réponse recommandée** = la suggestion du transcript si elle existe (étiquetée `(src: transcript)`),
      sinon une suggestion plausible étiquetée « suggestion » ;
   2. « **passer pour l'instant** » ;
   3. « **saisir ma réponse** ».
   Puis **POSE UNE SEULE QUESTION, ARRÊTE-TOI, et ATTENDS la réponse de l'utilisateur** avant de passer à
   la suivante. **Jamais** plusieurs questions dans un même message ; **jamais** d'auto-complétion ;
   **jamais** `answered` sans **choix explicite** (option 1 ou 3). Ne jamais remplir de valeur démo/aléatoire.
   - Option 1 ou 3 (**choix explicite**) → statut `answered` ; source = `(src: transcript)` si la suggestion
     transcript est **confirmée**, sinon `atelier/utilisateur`.
   - « Passer » (option 2) → `[À VALIDER]`, statut `deferred` — reste un **trou bloquant**.
   - Décisions groupées (l'utilisateur tranche plusieurs questions d'un coup) → **relire la liste parsée et
     faire confirmer** avant d'écrire (cf. interactive-loop) ; sinon, une question à la fois.
   À la fin de la boucle, annoncer soit que **tout est complété**, soit **combien de points ont été passés**
   et restent bloquants. Vaut en particulier pour les *seeds qualité* Q2/Q6/Q7.
3. **Écrire** les réponses dans `project-frame.md` (chaque champ avec sa `(src:)`,
   non répondu → `[À VALIDER]`). Le project-frame vit sous
   `factory-docs/work/project-frame.md`. Les réponses Q1 (qui utilise), Q3 (rôles)
   et Q9 (type de projet) seront aussi reprises côté vision par `cadrage-vision`.

Les questions Q2 (charge), Q6 (disponibilité), Q7 (performance) sont des **seeds
de qualité** : on les capte bruts ici, le plugin **architecte** les transformera
en drivers / scénarios de qualité. **Important** : une réponse **directionnelle / non
chiffrée** à Q2/Q6/Q7 (ex. « fiabilité avant la vitesse ») se note `answered` **mais sa valeur
reste marquée `[À CHIFFRER]`** (c'est un seed, pas une contrainte définitive) ; ne **jamais** la
présenter comme une cible chiffrée. Réinterpréter une phrase de l'atelier comme réponse définitive
sans `[À CHIFFRER]` est interdit.

## Auto-contrôle (avant écriture)

Pour **chaque ligne** de la capture, poser la question : *ai-je une trace dans la
source ?* Si non, soit la ligne disparaît, soit elle devient un `[À VALIDER]`.
C'est le garde-fou anti-hallucination. Aucune exigence fabriquée.

## Porte de sortie

Avant d'écrire le manifeste, vérifier :
- Les **sept sections sont présentes** (vides autorisées, avec marqueur).
- **Chaque élément factuel est tracé** à une source ; tout le reste est marqué.
- **Aucune invention** (auto-contrôle passé).
- Les **trous sont comptés**.
- **Les 13 questions de découverte ont chacune un statut** (`answered`+source via
  option 1/3, ou `deferred` via « passer »). Toute question `pending`/`deferred`
  est un **trou bloquant**. Vérifiable par `scripts/check_discovery.py`.

Si une de ces conditions échoue, corriger avant d'écrire.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.capture_brute.status = "draft"`, `artifacts.capture_brute.gaps =
  <nombre d'entrées de la section Trous>`.
- `phase = "extraction"`.
- `sources[]` complété par les sources dépouillées (si pas déjà fait à la porte
  d'entrée).
- `validation_points[]` : ajouter les trous structurants comme entrées
  `raised_by = "extraction"`, `status = "open"`.
- `artifacts.project_frame.status` et `.gaps` (nombre d'entrées `[À VALIDER]` du
  project-frame).
- `discovery[]` : mettre à jour chaque entrée Qn (`status`, `answer`, `source`).
- `discovery_complete` : `true` si aucune question n'est `pending`/`deferred`.
- `validation_points[]` : chaque question `pending`/`deferred` → entrée
  `status = "open"`, `raised_by = "discovery"` (trou bloquant).
- `updated_at` à l'horodatage courant.

## Règles invariantes appliquées ici

- **Marquer, ne pas inventer.** C'est le cœur de ce skill. Tout blanc est
  marqué, jamais comblé.
- **Skill indépendant.** Invocable seul ; la cohérence passe par le manifeste,
  pas par un orchestrateur.
- **Porte avant écriture.** Les sept sections et l'auto-contrôle sont vérifiés
  avant tout write du manifeste.

Étape suivante : `/cadrage:cadrage-vision` — transformer la capture en vision produit.
