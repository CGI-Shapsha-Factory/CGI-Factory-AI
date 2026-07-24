---
name: cadrage-ideation
description: Mandatory post-extraction workshop that studies the extracted material, surfaces gaps, and brainstorms with the user to flesh out the specifications.
argument-hint: "[zone à creuser en priorité]"
---

# cadrage-ideation

Atelier de clarification **obligatoire**, à lancer **juste après `cadrage-extraction`** :
une fois la matière brute extraite (capture, project-frame, passe de découverte),
l'idéation l'**étudie**, repère ce qui manque ou reste flou, puis **brainstorme avec
l'utilisateur** pour faire sortir toutes les spécifications et les détails du projet -
jusqu'à ce que le besoin soit clair. C'est une étape du pipeline, pas un détour
facultatif : elle **garde la vision** (`cadrage-vision` ne démarre pas tant qu'elle
n'a pas eu lieu).

## Objectif

Partir de la matière **déjà extraite** et la rendre complète et nette : combler les
trous, clarifier le flux fonctionnel, expliciter les hypothèses tenues pour acquises,
et faire émerger les détails de spécification encore absents. Le skill **anime** et
**structure** la séance ; les idées et les décisions viennent **de l'utilisateur**.
Les résultats **enrichissent en place** les artefacts extraits (aucun document séparé).

## Posture : facilitateur, jamais générateur

- **Chaque idée vient de l'utilisateur.** Le rôle du skill est de partir des trous de
  la matière extraite, de poser la bonne question, de relancer, de faire rebondir -
  pas de remplir la page à sa place. La règle "ne rien inventer" du cadrage s'applique
  ici sous sa forme la plus stricte : tout ce qui est ajouté est de l'utilisateur.
- **Une seule exception** : si l'utilisateur demande **explicitement** une idée
  ("propose-moi quelque chose"), en donner **exactement une**, comme une étincelle,
  puis lui rendre la main aussitôt.
- **Une seule relance par message.** Jamais plusieurs questions empilées : une relance, on
  s'arrête, on attend.
- **Relances d'animation en prose, décisions avec `AskUserQuestion`.** Les relances qui font
  **produire** ("quoi d'autre sur ce point ?", "et si cette contrainte sautait ?") ne
  collectent aucune décision et restent ouvertes - un menu y tuerait la divergence. Dès qu'une
  réponse est **enregistrée ou oriente la suite** (un trou est comblé, un point tranché, la
  séance se termine), la question passe par `AskUserQuestion`, **deux options** (cf.
  `references/interactive-loop.md`).
- **Ancrée sur les trous, pas sur une page blanche.** On ne relance pas dans le vide : chaque
  question part d'un manque précis repéré dans la matière extraite (une question de découverte
  restée sans réponse, une section mince, un flux ambigu).

## Entrées

- `cadrage-out/capture-brute.md` et `cadrage-out/project-frame.md` (la matière extraite).
- L'état de la passe de découverte (les 19 questions : lesquelles sont répondues, lesquelles
  sont restées en suspens ou laissées de côté).
- Facultatif : une zone à creuser passée en argument
  (`/cadrage:cadrage-ideation <zone>` -> disponible via `$ARGUMENTS`), utilisée comme point
  d'entrée prioritaire.

## Pré-requis (vérification silencieuse)

Vérifier sans l'annoncer que l'extraction a tourné : `artifacts.capture_brute` existe dans
le manifeste (le fichier `cadrage-out/capture-brute.md` est présent). Si l'extraction n'a
pas eu lieu, indiquer en clair qu'il faut d'abord dépouiller la matière
(`/cadrage:cadrage-extraction`) et s'arrêter là.

Pas de porte de régénération : la séance **enrichit en place** des artefacts existants (elle
ne régénère rien à l'aveugle) et applique les règles de fusion additive ci-dessous.

## Procédure

1. **Lire la matière extraite.** Charger `capture-brute.md`, `project-frame.md` et l'état de
   la découverte. Se faire une image du projet tel qu'il ressort de l'extraction.
2. **Cartographier les trous.** Repérer précisément : les questions de découverte restées
   sans réponse ou laissées de côté, les sections minces de la capture, le flux fonctionnel
   ambigu ou incomplet, les hypothèses tenues pour acquises mais jamais explicitées, les
   détails de spécification manquants. En faire une courte liste de points à clarifier.
3. **Présenter la carte des trous** à l'utilisateur, en langage naturel (jamais de nom de
   champ ni d'identifiant technique) : "voilà ce qui me semble encore flou ou absent - par
   quoi veux-tu commencer ?".
4. **Brainstormer chaque trou avec l'utilisateur.** Le prendre point par point : une relance
   par message, en français, en rebondissant sur ce qu'il dit. Faire clarifier le flux, sortir
   les détails, expliciter les hypothèses. Dès qu'une réponse fixe une décision ou une valeur,
   la confirmer **avec `AskUserQuestion`** (deux options : la lecture recommandée et une
   alternative crédible). Si l'utilisateur demande une idée, en donner une seule puis lui
   rendre la main.
5. **Converger, puis synthétiser.** Quand l'utilisateur a fait le tour (ou trou par trou),
   basculer explicitement en convergence : lui **tendre le miroir** (reformuler ce qu'il a
   clarifié), puis **ajouter les liens non évidents** que la séance a fait apparaître. Faire
   valider cette synthèse en clair.
6. **Écrire les enrichissements en place.** Reporter les clarifications dans les artefacts
   extraits (voir Sortie), en **fusion additive** : on complète, on ne réécrit pas à
   l'aveugle. Un acquis contredit par la séance est marqué `[REMIS EN CAUSE]` avec sa raison
   et tranché par l'humain, jamais supprimé ni réécrit en douce.

## Sortie

La séance **met à jour en place** les artefacts déjà produits par l'extraction - aucun
nouveau document, aucune source datée :

- **`cadrage-out/capture-brute.md`** : les détails et clarifications qui manquaient sont
  ajoutés aux sections concernées (contenu, sans provenance ni horodatage).
- **`cadrage-out/project-frame.md`** : les réponses de découverte débloquées pendant la
  séance sont intégrées.
- **Les entrées de découverte** correspondantes passent de "en suspens / laissée de côté" à
  "répondue" dans le manifeste (voir Mise à jour du manifeste).

**Contenu uniquement, sans provenance** : pas d'horodatage interne, pas de tour de parole,
pas de mention de technique par idée. Fusion par identité de section / de point : aucune
duplication ; ce qui existait et reste valable est préservé.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `ideation_complete = true` (l'atelier a eu lieu ; débloque `cadrage-vision`).
- Les entrées `discovery[]` résolues pendant la séance passent à `status: "answered"`
  (avec leur réponse), sans provenance écrite.
- `phase = "ideation"` (si la phase courante est `extraction`).
- `updated_at` à l'horodatage courant.

> **Silencieux - jamais annoncé.** Ne jamais dire à l'utilisateur que le manifeste est mis à
> jour, ni citer un nom de champ ou une valeur `true`/`false`. Confirmer seulement, en clair,
> **ce qui a été clarifié** + la prochaine étape (cf. `references/ux-conventions.md`).

## Règles invariantes appliquées ici

- **Étape obligatoire du pipeline.** En aval de l'extraction, en amont de la vision : elle
  **conditionne** le démarrage de `cadrage-vision`.
- **Facilitateur, pas générateur.** Tout ce qui est ajouté est de l'utilisateur (une
  étincelle sur demande explicite, jamais plus).
- **Enrichissement additif.** On complète les artefacts extraits, on ne les écrase jamais en
  silence ; un acquis contredit est marqué `[REMIS EN CAUSE]` et tranché par l'humain.
- **Contenu, pas provenance.** Aucun horodatage ni interlocuteur dans les artefacts.

Étape suivante : `/cadrage:cadrage-vision` - transformer la capture désormais clarifiée en vision produit.
