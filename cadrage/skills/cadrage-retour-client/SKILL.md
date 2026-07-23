---
name: cadrage-retour-client
description: Ingère tout retour client (nouveaux documents de réunion ou retour sur la maquette), le confronte au cadrage existant et met à jour les artefacts en place.
---

# cadrage-retour-client

L'intake universel du retour client. Après chaque nouvelle réunion, le client
apporte des exigences nouvelles, des clarifications et des changements : ce skill
les confronte à tout ce que le cadrage a déjà produit, distingue ce qui
**complète** de ce qui **remplace** ou **contredit**, fait trancher le PO, et met
à jour les artefacts existants **en place**. Il couvre deux situations,
détectées automatiquement et cumulables dans une même session :

- **Mode projet** : de nouveaux documents ont été déposés dans
  `cadrage-out/source-contexte/` après le cadrage initial (compte rendu de
  réunion, nouvelles exigences, corrections).
- **Mode maquette** : un transcript de retour client sur le démonstrateur est
  disponible (l'ancien périmètre de `cadrage-retour-demonstrateur`, préservé
  intégralement).

## Objectif

Faire **converger** le cadrage à partir de tout retour client, sans rejouer
manuellement les skills amont : détecter, comparer, questionner, mettre à jour.
Aucun nouveau fichier n'est créé dans `cadrage-out/` ; aucun rapport delta
n'est persisté.

## Entrées

- `cadrage-out/source-contexte/` (fichiers `.txt`/`.md`/`.pdf`/`.docx`) et le
  registre `sources[]` du manifeste (fichiers déjà ingérés : `type`, `ref`,
  `ingested_at`).
- L'ensemble des artefacts de `cadrage-out/` : capture-brute, project-frame,
  product-brief, glossaire, spec-index, coupling-map,
  `features-fonctionnels-brief/*`.
- Le manifeste : bloc `discovery` (les 19 questions Q1-Q19 et leurs réponses),
  `validation_points`, `demonstrateur` (`current_version`, `external_ref`).
- En mode maquette : le **transcript de retour**, déclaré comme source de type
  `retour` - distinct d'un transcript d'atelier classique.

## Détection du mode (silencieuse)

1. Lister `cadrage-out/source-contexte/` et comparer chaque fichier aux `ref`
   de `sources[]` : tout fichier **absent du registre** forme le **corpus
   delta** -> mode projet.
2. Une source de type `retour` (transcript de retour maquette) non encore
   traitée -> mode maquette. Un même transcript de réunion peut nourrir les
   deux modes.
3. Ni l'un ni l'autre : indiquer en clair qu'il faut d'abord déposer les
   nouveaux documents dans `cadrage-out/source-contexte/` (ou fournir un
   transcript de retour), sans exposer de mécanique interne.

Limite assumée : un fichier **déjà ingéré puis modifié sous le même nom** n'est
pas détecté. Déposer les comptes rendus en fichiers datés par réunion (par ex.
`reunion-<JJ-MM>.md`).

## Mode projet : analyse différentielle et mise à jour en place

### 1. Ingérer le corpus delta

Charger chaque nouveau fichier, l'enregistrer dans `sources[]` avec
`type = "retour-projet"`, `ref`, `ingested_at`.

### 2. Relire l'existant en parallèle

Comme `cadrage-completude` : dispatcher des agents `cadrage-reader`
(`agents/cadrage-reader.md`) en **fan-out** sur les artefacts de `cadrage-out/`
(capture-brute, project-frame, product-brief, glossaire, spec-index,
coupling-map, un lot pour les briefs), et lire directement le manifeste
(`discovery` avec les réponses aux 19 questions, `validation_points`,
`demonstrateur`). Relire depuis les fichiers committés, jamais la mémoire du
chat. Cette relecture est **automatique** : aucune intervention du PO.

### 3. Classer chaque information par clés de jointure

Confronter chaque information du corpus delta à la connaissance existante en
s'appuyant sur les identités structurelles (les artefacts ne portent aucune
provenance) :

- les réponses `Q1..Q19` du bloc `discovery` (la question d'origine et sa
  réponse enregistrée) ;
- les sections du product-brief (problème, objectif business, périmètre IN/OUT,
  contraintes, critères de succès, hypothèse produit) ;
- les termes du glossaire (identité = nom du terme) ;
- les use cases `UCn` du spec-index et leurs briefs associés ;
- les `validation_points` encore ouverts (un nouveau document peut en résoudre).

Quatre verdicts possibles par élément : **complète** (information nouvelle,
compatible), **remplace** (le client change une réponse acquise), **contredit**
(incompatible avec un acquis), **à clarifier** (ambigu, les deux lectures sont
possibles). La table delta se construit **en session seulement** - jamais
persistée dans un fichier.

### 4. Faire trancher le PO (résolution totale en session)

- Les **compléments** purs s'appliquent sans question.
- Chaque **remplace** / **contredit** / **à clarifier** se pose **une question à
  la fois avec `AskUserQuestion`**, formulée comme la question d'origine
  re-posée : l'acquis actuel et la nouvelle information côte à côte, puis les
  options **garder l'existant** et **adopter la nouvelle version** (la
  recommandée d'abord selon le contexte), la saisie libre servant de
  reformulation. Style fork de conception : chaque option nomme son coût.
- **La session ne se termine pas avec un point ouvert.** Chaque point est
  re-posé jusqu'à réponse finale ; ce skill ne persiste **aucun marqueur
  d'incertitude** (ni `[REMIS EN CAUSE]`, ni rien d'équivalent) et ne laisse
  **aucun `validation_point` ouvert** de son fait. Si le PO doit d'abord
  reconsulter le client, la seule issue est **garder l'existant** (l'artefact
  reste tel quel, propre) ; le sujet est alors listé dans le résumé de fin de
  session comme point à porter à la prochaine réunion - jamais écrit dans un
  artefact.
- Aucune mécanique exposée : pas de nom de champ, de porte ni d'identifiant
  codé (seuls les use cases se nomment "Intitulé complet (UCn)").

### 5. Appliquer en place (réjeu incrémental inline)

Pour chaque décision, appliquer la correction **directement dans l'artefact
concerné**, selon les règles de réjeu incrémental déjà définies par les skills
producteurs (`cadrage-vision`, `cadrage-glossaire`, `cadrage-decoupage`) - elles
restent la source de vérité des règles de fusion. Pour les briefs de feature
(`cadrage-briefs`), fusionner par identité de section du gabarit
`templates/feature-brief.md`, sans en modifier la structure :

- **Préserver** le contenu validé ou inchangé.
- **Fusionner par identité** (section du brief produit, terme du glossaire,
  use case, section de feature-brief) : aucune duplication.
- Toute décision étant finale (étape 4), les artefacts sortent de la session
  **clairs et définitifs**, sans marqueur d'incertitude.

Ce flux est du **réjeu incrémental** : il n'ouvre **pas** la porte de
régénération (`references/regeneration-gate.md`, réservée aux régénérations
intégrales demandées par l'utilisateur). Aucun fichier créé, aucune archive.

### 6. Répercuter dans le manifeste (silencieux)

Read-modify-write puis revalidation JSON :

- `sources[]` : les nouveaux fichiers ingérés (`type = "retour-projet"`).
- `discovery[]` : la réponse des questions impactées est mise à jour avec la
  décision finale.
- `validation_points[]` : points résolus par le nouveau document -> `answered`.
- **Portes recalculées à la baisse uniquement** - jamais d'allumage automatique
  d'une porte humaine :
  - changement matériel du découpage (feature ajoutée, fusionnée, supprimée,
    frontière ou dépendance déplacée) -> `spec_index.arbitrated` et
    `definition_of_ready.decoupage_arbitrated` repassent à `false` (règle
    "reset d'arbitrage" de `cadrage-decoupage`) : la revue de couplage humaine
    doit re-trancher ;
  - brief de feature modifié -> son `status` repasse à `draft` et
    `all_briefs_complete` est recalculé ;
  - les autres booléens de `definition_of_ready` sont recalculés sur l'état
    réconcilié.
- `updated_at`.

### 7. Clore la session

Résumer en chat, en langage naturel : ce qui a changé et dans quel document,
ce qui a été conservé après arbitrage, les éventuels sujets à porter à la
prochaine réunion client (jamais persistés). Si un changement est **visible sur
la maquette** (écran, parcours, contenu affiché), recommander
`cadrage-demonstrateur-brief` en mode adaptatif (prompt delta). Recommander
enfin de rejouer `cadrage-completude` pour un verdict frais.

## Mode maquette : capter ET invalider

Le comportement historique du retour de démonstrateur, inchangé.

1. **Rapprocher.** Pour chaque réponse du client, retrouver le(s) point(s)
   ouvert(s) correspondants dans `validation_points`. Marquer `answered`,
   consigner la réponse dans `answer`. Un point **non couvert** par le retour
   **reste `open`** - jamais comblé.
2. **Détecter les invalidations.** Un élément **déjà capté** (vision, glossaire,
   découpage) que le client **remet en cause** au vu de la maquette : créer / mettre
   à jour un `validation_point` de type `contradiction`, statut `invalidated`,
   pointant l'artefact et l'élément concerné. **Ne pas écraser** l'acquis ni le
   garder en silence. Dans la même session, chaque invalidation peut être
   **tranchée immédiatement** comme un point du mode projet (étapes 4 et 5
   ci-dessus) ; à défaut, elle sera marquée `[REMIS EN CAUSE]` dans son artefact
   au réjeu du skill producteur concerné.
3. **Propager.** Les invalidations tranchées en session s'appliquent en place
   (étape 5 du mode projet). Pour celles laissées au réjeu, identifier les
   artefacts touchés et recommander explicitement les skills idempotents
   concernés (`cadrage-vision`, `cadrage-glossaire`, `cadrage-decoupage`).
4. **Faire émerger les nouveaux points.** Toute nouvelle question ou souhait né du
   retour -> nouveau `validation_point` (`open`), qui sera **résolu en session** au
   point de complétude (`cadrage-completude`).

### Mise à jour du manifeste (mode maquette)

Read-modify-write puis revalidation JSON :
- `sources[]` : ajout du transcript de retour (`type = "retour"`).
- `validation_points[]` : résolutions (`answered`), invalidations (`invalidated`),
  nouveaux points (`open`).
- `demonstrateur.iterations[]` : met à jour l'itération courante avec les compteurs
  `resolved`, `invalidated`, `new_points`, et `feedback_source`.
- **Ne touche pas** `demonstrateur.client_validated` (geste humain) - **et ce geste exige une
  maquette réelle** : `client_validated` ne peut passer à vrai **que si `demonstrateur.external_ref`
  est non nul** (une maquette a été générée et référencée). Une validation **verbale** ("tout est
  ok") **sans maquette référencée** ne converge PAS : **demander d'abord la référence de la
  maquette avec `AskUserQuestion`** (lien Claude Design ; deux options - "je colle le lien" et
  "la maquette n'existe pas encore" - la saisie libre reçoit le lien) avant d'enregistrer la
  validation. Pas de maquette -> pas de convergence. **Aucune validation fantôme.**
- `updated_at`.

> **Silencieux, sans nom de champ (impératif).** La mise à jour du manifeste ne se **narre jamais** à
> l'utilisateur. En **enregistrant la référence de la maquette**, ne cite **jamais**
> `demonstrateur.current_version` / `external_ref` ni le chemin de fichier technique. Pour confirmer,
> dire en clair : "**La maquette (v1) est bien enregistrée.**" - aucun nom de variable, aucun chemin
> (cf. `references/ux-conventions.md` §1).

## Vérification

- Mode projet : seuls les fichiers **réellement nouveaux** ont été ingérés ; la
  classification a couvert tout le corpus delta ; chaque remplacement /
  contradiction / ambiguïté a été tranché en session ; les artefacts mis à jour
  sont propres (aucun marqueur d'incertitude) ; **aucun nouveau fichier** dans
  `cadrage-out/` ; les portes touchées ont été recalculées à la baisse.
- Mode maquette : points adressés `answered` avec leur réponse ; invalidations
  tranchées en session ou `invalidated` au registre (jamais d'écrasement
  silencieux) ; nouveaux points inscrits `open`.

## Règles invariantes appliquées ici

- **Capter ET invalider.** Le skill sait remettre en cause un acquis, pas
  seulement ajouter. Sinon le cadrage accumule des couches contradictoires au
  lieu de converger.
- **Résolution totale en session (mode projet).** Tout point détecté est tranché
  avec le PO avant écriture ; rien d'ouvert, rien de marqué, tout est clair et
  final dans les artefacts.
- **Trancher, c'est l'humain.** Le skill détecte et propose ; le PO décide de
  chaque remplacement et contradiction ; le client valide la maquette.
- **Mettre à jour, jamais créer.** Il modifie les artefacts existants en place
  (réjeu incrémental inline) et n'écrit aucun fichier nouveau dans
  `cadrage-out/`.

Étape suivante : `/cadrage:cadrage-completude` - faire le point d'état sur le pack réconcilié (verdict Definition of Ready).
