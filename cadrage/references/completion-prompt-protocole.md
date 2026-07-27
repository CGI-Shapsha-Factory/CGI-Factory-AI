# Passe de complétion du prompt : protocole partagé

Convention du skill `cadrage-demonstrateur-brief`. À la fin du skill, une relecture d'expert en
prompt engineering du **prompt Claude Design fraîchement produit** et de sa **base amont** cherche
tout ce qui manque ou reste flou pour obtenir la **meilleure maquette possible**, puis chaque point
se complète **avec l'utilisateur**, une question à la fois, correction appliquée **en place** dans le
prompt. Rien n'est inventé : l'expert diagnostique, l'utilisateur décide, le skill écrit. La
priorité est la **qualité et la complétude du prompt**, pas la vitesse : la passe peut prendre du
temps.

Cette passe **remplace la passe d'attaque générique** (`references/attaque-protocole.md`) pour ce
skill : elle en absorbe la relecture de cohérence amont (dimension "cohérence amont" ci-dessous) et y
ajoute la complétion du brief de design. On ne déroule pas les deux.

## Quand la passe tourne (et où)

Après la production du prompt et sa sauvegarde sous `cadrage-out/prompts/`, **avant la mise à jour du
manifeste** - ainsi les compteurs reflètent l'état complété. La passe est une étape du skill, pas un
skill séparé : elle se déroule dans la même session, sans commande dédiée.

## Ce qu'on cherche : la checklist du brief de design

Neuf dimensions, balayées systématiquement - pour chacune, ce qui manque, reste flou, ou rendrait la
maquette plus forte :
1. **identité visuelle & direction artistique** : palette dérivée du domaine (jamais le violet/indigo
   par défaut), duo de polices, ambiance/mood, références ou inspirations, couleurs de marque et
   actifs existants du client, clair/sombre, densité ;
2. **écrans & périmètre de la maquette** : 3 à 6 écrans, un écran héros, tous les parcours clés du
   `spec-index.md` couverts, ce qui est explicitement hors de la maquette ;
3. **fonctionnalités & comportements attendus** par écran : interactions clés, CTA principal,
   navigation entre écrans ;
4. **expérience utilisateur** : positionnement / émotion visée, première impression, contexte du
   persona (mobile ou desktop, expert ou novice), ton de la microcopie ;
5. **états & contenu réaliste** : états utiles par écran (chargé, vide, erreur, chargement), données
   plausibles du `glossaire.md`, volume de données montré ;
6. **contraintes techniques** : cibles responsive, accessibilité, composants imposés, hors
   périmètre ;
7. **cas limites & scénarios manquants** : premier lancement vs utilisateur connu, chemins d'erreur
   ou vides ;
8. **auto-portance** : le prompt donne tout à Claude Design sans aucun contexte projet, aucune
   référence pendante à un fichier ou au manifeste ;
9. **cohérence avec l'amont** (absorbée de la passe d'attaque) : décalage entre le prompt et
   `product-brief.md` / `glossaire.md` / `spec-index.md` - contradiction, information manquante,
   ambiguïté, incohérence inter-artefacts, dépendance citée mais introuvable.

Pas d'échelle de gravité qui plafonne le traitement : on vise la meilleure maquette possible, donc on
traite **tout point significatif**. On ordonne cependant du plus structurant (identité, écrans,
comportements, cohérence amont) au plus fin (microcopie, détails d'état) pour que les questions à fort
enjeu viennent d'abord.

## Fan-out : diagnostiquer en parallèle

- **Par défaut : un seul agent** (`agentType: "prompt-engineer-cadrage"`), qui reçoit tout le
  périmètre (le prompt sauvegardé + la base amont en entier).
- **Contenu réellement volumineux : 2 à 4 lots**, dispatchés **en un seul message** (appels
  parallèles), plafonnés à 4. Chaque lot reçoit la base amont partagée en entier (les dimensions se
  croisent).
- Chaque agent reçoit **exactement trois choses** : la liste des fichiers de son lot, le fait que le
  brief démonstrateur vient de tourner (et son mode, initial ou adaptatif), et le schéma de sortie de
  `agents/prompt-engineer-cadrage.md`.
- **Isolation stricte (le mécanisme qui fait marcher la passe).** Ne **jamais** transmettre à l'agent
  le fil de la session, le raisonnement du skill ni une justification : un regard neuf sur pièces
  détecte ce que la session ne voit plus.

## Fan-in : consolider avant toute interaction

1. **Fusionner** tous les constats en un rapport unique de session, **avant la moindre question**.
2. **Dédoublonner** : clé `artefact + localisation + dimension` ; un même manque présent sur plusieurs
   écrans = **un seul constat** (une seule question ; la correction s'applique partout).
3. **Ordonner** du plus structurant au plus fin.
4. Le rapport vit **en session seulement** : jamais écrit dans un fichier, jamais affiché en liste à
   l'utilisateur.

## Vérification : anti faux positifs (avant toute question)

Pour chaque constat consolidé, l'orchestrateur **revérifie sur pièces** avant de déranger
l'utilisateur :
1. la `citation` **existe mot pour mot** dans le prompt ou l'amont, à l'endroit indiqué ;
2. le point n'est pas **déjà couvert** ailleurs dans le prompt (un état déjà décrit dans une autre
   section, une contrainte déjà posée) ;
3. le constat ne **rouvre pas un point que l'utilisateur a explicitement tranché** dans cette session
   (cf. `ux-conventions.md` : ne jamais ré-insister sur un point tranché).

Un constat qui échoue est **écarté sans bruit** - jamais montré. Tous les constats survivants sont
traités, **sans plafond** ; l'utilisateur peut clore la boucle à tout moment ("ça me suffit").

## La boucle de complétion : un point, une question - deux modes

Pour chaque constat retenu, du plus structurant au plus fin, poser **une seule question par
message**, attendre la réponse, appliquer la correction **en place** dans le prompt, puis passer au
suivant. Le mode de la question dépend du constat (`mode question` renvoyé par l'agent) :

- **Décision de design** (un choix à figer où deux lectures crédibles existent : jeu d'états d'un
  écran, clair ou sombre, densité, écran héros, cible responsive) -> **`AskUserQuestion`, exactement
  deux options** (la recommandée d'abord avec son coût, puis l'alternative crédible avec le sien),
  conformément à `references/interactive-loop.md` ; l'outil ajoute lui-même la saisie libre. Un choix
  de direction visuelle engageant est un **fork de conception** : chaque option nomme ce qu'elle
  ouvre ou ferme.
- **Exploratoire** (un cadrage ouvert où la réponse se formule librement : "que doit ressentir un
  primo-visiteur sur l'écran d'accueil ?", "qu'est-ce qui distingue ce produit d'un tableur ?") ->
  **question en prose dans le fil**, une par message, réponse libre - même esprit que la passe
  d'attaque.

Dans les deux modes : ancrer la question dans **les mots du projet** (jamais une question gabarit
posable sur n'importe quel projet) ; **relance unique par défaut** sur une réponse vague ; **sondage
approfondi en opt-in** sur un point structurant à fort enjeu resté mince (laddering court, plafond de
trois crans) ; "on garde tel quel" est une réponse légitime (aucune modification, on passe au
suivant).

Appliquer la correction **en place** dans le fichier prompt, qui reste **corps seul, prêt à coller**
(aucun titre, aucune métadonnée ; cf. `references/ux-conventions.md`). Un point que l'utilisateur ne
tranche pas est **omis**, jamais persisté en marqueur.

## Mode initial vs adaptatif

- **Initial** : passe **complète**, les neuf dimensions.
- **Adaptatif** (prompt DELTA) : passe **légère et ciblée** - on ne vérifie que la **clarté et la
  complétude des changements demandés** (le delta se suffit-il à lui-même, référence-t-il bien la
  maquette existante, borne-t-il les changements). On ne **rouvre jamais** le design déjà validé
  (palette, mise en page, composants, écrans non touchés).

## Fin de passe

La passe se termine quand chaque constat retenu est **complété ou explicitement gardé tel quel**.
**Une seule passe** : on ne relance pas de diagnostic sur le prompt corrigé dans la même session.
Alors seulement : la mise à jour silencieuse du manifeste du skill (entrées `prompts[]` et
`demonstrateur.iterations[]`, inchangées), puis sa ligne "Étape suivante :". Aucun drapeau de
manifeste nouveau, aucune trace de la passe dans un artefact.

## Rappels UX (contraignants)

`references/ux-conventions.md` s'applique en entier :
- **Aucune mécanique exposée.** Pas de nom d'agent, de lot, de dimension ou de champ à l'écran, et
  les mots "passe de complétion" ne sont jamais dits à l'utilisateur : chaque question apparaît comme
  une clarification naturelle avant de figer le prompt (au plus une phrase d'ancrage du type "avant de
  figer le prompt, un point sur l'écran d'accueil", puis la question).
- **Typographie humaine** : tiret simple " - ", flèches "->", guillemets droits, trois points ASCII
  "...", Oui/Non.
- **Tout en français.**
- **Facilitateur, jamais générateur** : chaque précision vient d'une réponse de l'utilisateur ;
  l'expert diagnostique, il ne décide pas la palette ni les états à sa place.
