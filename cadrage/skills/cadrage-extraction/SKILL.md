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
contraintes) — **pas** sur qui a dit quoi ni à quel moment. Le skill n'est pas un
formulaire de saisie : la matière existe déjà, on la transforme et on la range.

**Jamais d'horodatage, jamais de tour de parole, jamais de `(src: …)` dans
l'artefact.** On extrait le fond, on ne trace pas la forme. La règle « ne rien
inventer » reste un garde-fou interne (on ne s'appuie que sur la matière), sans
écrire la provenance.

## Entrées

Une ou plusieurs sources déclarées par l'utilisateur. L'entrée est **souple** :
accepter **un seul chemin de fichier**, **plusieurs chemins**, **ou un dossier**
(dans ce cas, ingérer tous les fichiers de format supporté qu'il contient).

Les chemins peuvent être **passés en argument** à l'invocation
(`/cadrage:cadrage-extraction <chemins>` → disponibles via `$ARGUMENTS`) **ou** déclarés
dans le chat. Si `$ARGUMENTS` est non vide, l'utiliser comme sources.

**Emplacement central par défaut** : `cadrage-out/source-contexte/` (créé par `cadrage-init`).
Si aucune source n'est passée en argument ni déclarée dans le chat, **regarder d'abord dans
`cadrage-out/source-contexte/`** et ingérer les fichiers de format supporté qui s'y trouvent.
Ce dossier est **facultatif** : s'il est vide (ou absent), continuer normalement en demandant
les sources — il n'est **jamais** obligatoire ni une porte de validation.

- **Pages Notion** (hubs réunion, transcripts) — via les outils Notion
  disponibles (`notion-fetch`, `notion-search`).
- **Fichiers fournis** — formats supportés : `.txt`, `.md`, transcripts, `.pdf`,
  `.docx`.
  - `.pdf` : lu via l'outil Read.
  - `.docx` : convertir avec `python-docx` ; si le fichier reste illisible,
    demander à l'utilisateur un export texte.

## Workspace et manifeste

Les documents du cadrage vivent dans `cadrage-out/` à la racine du projet client, et le
manifeste `.factory/manifest.json` est le contrat machine entre les skills.
**Les deux sont créés par `cadrage-init`** (skill d'amorçage) — `cadrage-extraction`
ne bootstrappe plus rien. Toute écriture du manifeste est un **read-modify-write**
suivi d'une **revalidation JSON** (le fichier doit reparser sans erreur).

## Pré-requis (vérification silencieuse)

Vérifier sans l'annoncer : **le manifeste existe ET au moins une source est
déclarée.** Ne jamais afficher de statut de « porte » ; si un pré-requis manque,
poser une question en clair.

1. Si `.factory/manifest.json` est absent : indiquer en clair qu'il faut
   d'abord initialiser le workspace (`cadrage-init`) et s'arrêter là.
2. Recueille les sources que l'utilisateur déclare (id de page Notion, chemin de
   fichier, plusieurs chemins, ou un dossier). Si l'entrée est un dossier, lister
   et ingérer tous les fichiers de format supporté qu'il contient. **À défaut de source
   déclarée, regarder dans `cadrage-out/source-contexte/`** et ingérer les fichiers
   supportés qui s'y trouvent. Enregistre chaque source dans `sources[]` avec `type`,
   `ref`, `ingested_at`.
3. Si aucune source n'est déclarée **et** que `cadrage-out/source-contexte/` est vide ou
   absent : demander en clair au moins une source. N'invente pas de matière. (Le dossier
   `source-contexte/` reste facultatif — son absence ne bloque jamais à elle seule.)

## Identité du projet

Avant le dépouillement, **demander à l'utilisateur, en français** (attendre la réponse) :
- « Quel est le **nom du projet** ? » (le nom usuel, lisible).

Écrire la réponse dans `project` du manifeste (laissé `null` par `cadrage-init`).
**Ne jamais le déduire** du nom du dossier. Si l'utilisateur ne répond pas, suivre la
boucle interactive (`references/interactive-loop.md`).

**Ne pas demander le nom du client.** Cette information n'est pas collectée par la
factory — ne pas la poser, ne pas l'écrire dans le manifeste.

## Procédure

1. **Charger** le contenu de chaque source (Notion, ou fichier `.txt`/`.md`/
   transcript/`.pdf`/`.docx` selon les règles de la section Entrées). Écrire la
   capture dans `cadrage-out/capture-brute.md`.
2. **Dépouiller** la matière et la classer dans les **sept sections fixes**
   (voir ci-dessous). Travailler section par section, sur l'ensemble des
   sources. Extraire le **contenu**, reformulé clair et lisible.
3. **Rester fidèle à la matière.** Ne s'appuyer que sur ce que disent les
   sources ; ne jamais ajouter de sens absent. **Ne pas écrire de provenance**
   (ni horodatage, ni interlocuteur, ni `(src: …)`).
4. **Ne pas combler un blanc.** Si une section n'a pas de matière, la laisser
   présente avec une courte mention « non abordé ». Un élément incertain n'est
   **pas écrit comme un fait** ; en cas de doute réel, on l'omet plutôt que de
   l'inventer. Aucune extrapolation.

### Structure de `capture-brute.md`

Sept sections fixes, toutes présentes même vides — **contenu uniquement, sans
trace de source** :

```
# Capture brute — <projet>
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

## Passe découverte (13 questions de cadrage) — **interactive, une question à la fois**

En plus de la capture, exécuter la **passe découverte** sur les 13 questions de
`references/discovery-questions.md` (Q1–Q13). Elle remplit
`cadrage-out/project-frame.md` (gabarit `.factory/cadrage/project-frame.md`)
et le bloc `discovery` du manifeste.

> ⚠️ **Workflow OBLIGATOIRE, jamais en lot.** On **déroule les 13 questions une par une**, même
> quand le transcript semble déjà répondre : le transcript fournit une **suggestion à confirmer**,
> pas une réponse validée. **Interdit** : remplir les 13 d'un coup depuis les sources et annoncer un
> bilan sans avoir rien demandé à l'utilisateur.

1. **Préparer les suggestions (sans rien écrire, sans rien valider).** Pour chaque Qn, chercher dans
   le transcript/docs une **réponse candidate** et la garder comme **suggestion à confirmer**.
   **Aucune question n'est `answered` à ce stade.**
2. **Dérouler la boucle interactive — Q1 → Q13, UNE À LA FOIS** (voir `references/interactive-loop.md`).
   Pour **chaque** question, en français, afficher le compteur **« Qn/13 »**, l'intitulé, puis une
   **réponse recommandée** (la suggestion tirée de la matière si elle existe, sinon une suggestion
   plausible, étiquetée « suggestion »). **Pas de menu numéroté** : l'utilisateur accepte la suggestion
   ou donne la sienne. Puis **POSE UNE SEULE QUESTION, ARRÊTE-TOI, et ATTENDS la réponse** avant de
   passer à la suivante. **Jamais** plusieurs questions dans un même message ; **jamais**
   d'auto-complétion ; **jamais** `answered` sans réponse explicite. Ne jamais remplir de valeur démo.
   - Réponse explicite (suggestion acceptée ou saisie) → statut `answered`. **Aucune `(src:)` écrite.**
   - L'utilisateur laisse de côté → le champ est **omis** (statut `deferred`, rien d'écrit dans
     l'artefact, pas de marqueur).
   - **Q8 (contraintes légales / conformité / RGPD) est OPTIONNELLE.** La proposer **une seule fois**,
     sans insister. Si l'utilisateur la décline / la laisse à l'équipe (« on gère nous-mêmes ») →
     statut **`na`** (traité hors cadrage), **pas `deferred`** : elle ne doit **jamais** bloquer la
     complétude ni revenir. **Ne jamais pousser la conformité** (cf. `references/discovery-questions.md`,
     note Q8, et `references/ux-conventions.md` §2bis).
   - Décisions groupées (l'utilisateur tranche plusieurs questions d'un coup) → **relire la liste parsée et
     faire confirmer** avant d'écrire (cf. interactive-loop) ; sinon, une question à la fois.
   À la fin de la boucle, annoncer que **tout est complété** (ou rappeler oralement les points laissés
   de côté). Vaut en particulier pour les *seeds qualité* Q2/Q6/Q7.
3. **Écrire** les réponses dans `project-frame.md` (chaque champ = le contenu décidé, **sans `(src:)`** ;
   un champ non tranché est **omis**). Le project-frame vit sous
   `cadrage-out/project-frame.md`. Les réponses Q1 (qui utilise), Q3 (rôles)
   et Q9 (type de projet) seront aussi reprises côté vision par `cadrage-vision`.

Les questions Q2 (charge), Q6 (disponibilité), Q7 (performance) sont des **seeds
de qualité** : on les capte bruts ici, le plugin **architecte** les transformera
en drivers / scénarios de qualité. Une réponse **directionnelle / non chiffrée** à Q2/Q6/Q7
(ex. « fiabilité avant la vitesse ») se note telle quelle comme orientation ; ne **jamais** la
présenter comme une cible chiffrée.

## Auto-contrôle (avant écriture)

Pour **chaque ligne** de la capture, poser la question : *est-ce bien soutenu par la
matière source ?* Si non, la ligne disparaît (on ne l'invente pas). C'est le
garde-fou anti-hallucination — interne, sans écrire de provenance.

## Vérification avant écriture

Avant d'écrire le manifeste, vérifier :
- Les **sept sections sont présentes** (vides autorisées, avec une courte mention « non abordé »).
- **Aucune invention** (auto-contrôle passé), **aucune `(src:)` ni horodatage** dans l'artefact.
- **Chaque question de découverte tranchée est écrite** ; les questions laissées de côté sont
  simplement absentes. Vérifiable par
  `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_discovery.py" <racine>/.factory/manifest.json`.

Si une de ces conditions échoue, corriger avant d'écrire.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.capture_brute.status = "draft"`.
- `phase = "extraction"`.
- `sources[]` complété par les sources dépouillées (si pas déjà fait au pré-requis).
- `artifacts.project_frame.status`.
- `discovery[]` : mettre à jour chaque entrée Qn (`status`, `answer`). **Pas de champ
  `source`.** Une question tranchée → `answered` ; laissée de côté → `deferred` ; **Q8 légal/conformité
  laissée à l'équipe → `na`** (terminal, non bloquant).
- `discovery_complete` : `true` si aucune question n'est `pending`/`deferred` (un `na` — dont un Q8
  légal laissé à l'équipe — **n'empêche pas** la complétude).
- `updated_at` à l'horodatage courant.

## Règles invariantes appliquées ici

- **Ne pas inventer.** On ne s'appuie que sur la matière ; un point non soutenu est
  omis, jamais comblé ni présenté comme un fait.
- **Contenu, pas provenance.** Aucun horodatage, aucun interlocuteur, aucune `(src:)`
  dans l'artefact.
- **Skill indépendant.** Invocable seul ; la cohérence passe par le manifeste,
  pas par un orchestrateur.

Étape suivante : `/cadrage:cadrage-vision` — transformer la capture en vision produit.
