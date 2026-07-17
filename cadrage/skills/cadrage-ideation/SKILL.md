---
name: cadrage-ideation
description: Facilitates an optional brainstorming session whose output feeds extraction as raw material.
argument-hint: "[sujet ou objectif de la séance]"
---

# cadrage-ideation

Atelier d'idéation **facultatif**, à lancer **avant ou en complément** de
`cadrage-extraction` : quand la matière brute est mince, quand le client est encore
en train de façonner son idée, ou quand un pan du besoin mérite d'être exploré à
voix haute avant d'être cadré.

## Objectif

Faire émerger la matière **de l'utilisateur** par une facilitation active : le
skill anime, questionne, relance et structure - il ne **génère pas** les idées.
La séance produit un compte rendu déposé dans `cadrage-out/source-contexte/`,
que `cadrage-extraction` ingère ensuite comme n'importe quelle source. L'idéation
**produit** de la matière ; l'extraction reste seule à la **structurer**.

## Posture : facilitateur, jamais générateur

- **Chaque idée vient de l'utilisateur.** Le rôle du skill est d'être un déclencheur
  de créativité : poser la bonne question, relancer, faire rebondir - pas de remplir
  la page à sa place. La règle "ne rien inventer" du cadrage s'applique ici sous sa
  forme la plus stricte : tout ce qui est noté est de l'utilisateur.
- **Une seule exception** : si l'utilisateur demande **explicitement** une idée
  ("propose-moi quelque chose"), en donner **exactement une**, comme une étincelle,
  puis lui rendre la main aussitôt.
- **Une seule relance par message.** Jamais plusieurs questions empilées, jamais de
  menu numéroté (cf. `references/interactive-loop.md`) : une question, on s'arrête,
  on attend.
- **Résister à la conclusion.** L'envie d'organiser ou de synthétiser est l'ennemie
  de la divergence : tant que l'utilisateur produit, on pousse pour une idée de plus.
  La synthèse a sa phase dédiée, à la fin.

## Entrées

Aucune obligatoire. Si un sujet est passé en argument
(`/cadrage:cadrage-ideation <sujet>` -> disponible via `$ARGUMENTS`), l'utiliser comme
point de départ. Les sources déjà déposées dans `cadrage-out/source-contexte/` peuvent
servir de contexte de fond, sans jamais remplacer la parole de l'utilisateur.

## Pré-requis (vérification silencieuse)

Vérifier sans l'annoncer que `manifest.json` existe. S'il est absent, indiquer en
clair qu'il faut d'abord initialiser le workspace (`cadrage-init`) et s'arrêter là.

Pas de porte de régénération : chaque séance écrit un **fichier daté distinct**
(voir Sortie), les séances successives coexistent sans jamais s'écraser.

## Procédure

1. **Ouvrir la séance (une question composée).** Demander en un seul message : sur
   quoi veut-on réfléchir, et **pourquoi** - quel est le but derrière (explorer un
   besoin flou, élargir un périmètre, trouver des angles d'attaque...). Le pourquoi
   oriente le choix des techniques et la synthèse finale. Attendre la réponse.
2. **Proposer une technique (suggestion, pas menu).** À partir du sujet et du but,
   proposer **une** technique adaptée de `references/techniques-ideation.md`, avec
   une ligne d'explication, étiquetée "suggestion". L'utilisateur accepte, en nomme
   une autre, ou demande à voir le catalogue (afficher alors le tableau de la
   référence). Jamais de menu numéroté.
3. **Animer.** Dérouler la technique : une relance par message, en français, en
   rebondissant sur ce que dit l'utilisateur. Noter chaque idée au fil de l'eau
   (mentalement ou en brouillon, sans interrompre le flux pour écrire). **Changer de
   registre** environ toutes les 8 à 10 idées, ou dès que le rythme retombe : proposer
   la technique suivante (même mécanique de suggestion). Si l'utilisateur demande une
   idée, en donner une seule puis lui rendre la main.
4. **Converger (phase distincte).** Quand l'utilisateur signale qu'il a fait le tour
   (ou après plusieurs techniques), basculer explicitement en convergence : regrouper
   les idées par thème **avec lui**, lui faire dire lesquelles comptent le plus,
   lesquelles sont à écarter, lesquelles restent des pistes ouvertes. Ses arbitrages,
   pas ceux du skill.
5. **Synthétiser en deux temps.** D'abord **lui tendre le miroir** : reformuler ses
   propres idées, y compris les premières, souvent enterrées sous les suivantes, et le
   laisser voir le motif d'ensemble. Ensuite seulement, **ajouter les liens non
   évidents** que la séance a fait apparaître entre ses idées. Faire valider cette
   synthèse en clair.
6. **Écrire le compte rendu** dans
   `cadrage-out/source-contexte/ideation-<JJ-MM>.md` (voir Sortie). Tout le contenu
   est celui de l'utilisateur ; la seule date est celle du nom de fichier.

## Sortie

Un fichier `cadrage-out/source-contexte/ideation-<JJ-MM>.md` (la date du jour au
format JJ-MM ; si un fichier du même jour existe, suffixer `-2`, `-3`...), structuré
simplement :

```
# Idéation : <sujet>

## But de la séance
<le pourquoi exprimé à l'ouverture>

## Idées retenues
<les idées jugées importantes par l'utilisateur, regroupées par thème>

## Pistes ouvertes
<les idées gardées "à voir", sans décision>

## Écartées
<ce que l'utilisateur a explicitement écarté, en une ligne chacune>
```

**Contenu uniquement, sans provenance** : pas d'horodatage interne, pas de tour de
parole, pas de mention de technique par idée. C'est de la **matière brute** : elle
sera dépouillée, confirmée et structurée par `cadrage-extraction` comme toute autre
source - rien de ce fichier n'est considéré validé tant que l'extraction ne l'a pas
fait confirmer.

## Mise à jour du manifeste

**Aucune.** Ce skill n'écrit pas dans le manifeste : le fichier produit est une
source, enregistrée dans `sources[]` par `cadrage-extraction` au moment de son
ingestion, comme les autres fichiers de `cadrage-out/source-contexte/`.

## Règles invariantes appliquées ici

- **Facilitateur, pas générateur.** Toutes les idées écrites sont celles de
  l'utilisateur (une étincelle sur demande explicite, jamais plus).
- **Contenu, pas provenance.** Aucun horodatage ni interlocuteur dans l'artefact ;
  la date ne vit que dans le nom du fichier.
- **Rien de validé ici.** La séance produit de la matière, pas des décisions de
  cadrage ; la confirmation passe par le flux normal de `cadrage-extraction`.
- **Skill indépendant et facultatif.** Invocable seul, ne conditionne aucune porte ;
  le cadrage démarre très bien sans lui.

Étape suivante : `/cadrage:cadrage-extraction` - dépouiller la matière brute (dont ce compte rendu) en capture structurée.
