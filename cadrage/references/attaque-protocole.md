# Passe d'attaque : protocole partagé

Convention partagée par les **skills de production** du cadrage. À la fin de chaque skill
couvert, une relecture adversariale des **sorties fraîches** et de leur **base amont** cherche
toutes les faiblesses du travail qui vient d'être produit, puis chaque faiblesse se résout
**avec l'utilisateur**, une question ouverte à la fois, correction appliquée **en place**.
Rien n'est inventé : l'attaquant constate, l'utilisateur décide, le skill écrit.

## Quand la passe tourne (et où)

Après la production des artefacts et l'auto-vérification du skill, **avant la mise à jour du
manifeste** - ainsi les compteurs et drapeaux reflètent l'état corrigé. La passe est une étape
du skill, pas un skill séparé : elle se déroule dans la même session, sans commande dédiée.

Périmètre par skill (chemins depuis la racine du projet) :

| Skill | Sorties fraîches attaquées | Base amont |
|---|---|---|
| `cadrage-ideation` | `cadrage-out/capture-brute.md` + `cadrage-out/project-frame.md` (enrichis en place) + l'état des questions de découverte (manifeste) | cohérence interne du couple enrichi (pas d'amont distinct) |
| `cadrage-vision` | `cadrage-out/product-brief.md` | `cadrage-out/capture-brute.md`, `cadrage-out/project-frame.md` |
| `cadrage-glossaire` | `cadrage-out/glossaire.md` | `cadrage-out/capture-brute.md`, `cadrage-out/product-brief.md` |
| `cadrage-decoupage` | `cadrage-out/spec-index.md`, `cadrage-out/coupling-map.md` | `cadrage-out/product-brief.md`, `cadrage-out/glossaire.md` |
| `cadrage-briefs` | les briefs produits dans `cadrage-out/features-fonctionnels-brief/` | `cadrage-out/spec-index.md`, `cadrage-out/coupling-map.md`, `cadrage-out/glossaire.md`, `cadrage-out/product-brief.md` |

**Exclusions (voulues, ne pas étendre)** :
- `cadrage-init` : rien à attaquer (amorçage du workspace).
- `cadrage-extraction` : la matière brute n'est pas un contrat ; l'idéation la challenge juste
  après.
- `cadrage-retour-client` : intake à résolution totale en session, immédiatement suivi du point
  d'état.
- `cadrage-completude` : porte terminale qui porte déjà sa propre grille adversariale
  (4 lentilles + relecture fan-out `cadrage-reader`) - ne pas dupliquer.
- `cadrage-demonstrateur-brief` : couvert par sa **passe de complétion du prompt** dédiée
  (`references/completion-prompt-protocole.md`), qui absorbe la cohérence amont et y ajoute la
  complétion du brief de design - ne pas dérouler l'attaque générique en plus.

Un fichier amont absent est **ignoré sans constat** : le séquencement relève des pré-requis des
skills, pas de la passe.

## Ce qu'on cherche

Cinq types de faiblesse, balayés systématiquement :
- **contradiction** : deux passages inconciliables, dans un même artefact ou entre artefacts de
  la même sortie ;
- **information manquante** : section mince ou vide, détail nécessaire à l'étape suivante
  absent ;
- **ambiguïté** : formulation à double lecture, terme vague qui laisse deux interprétations ;
- **incohérence inter-artefacts** : décalage entre une sortie fraîche et sa base amont (terme,
  frontière, critère, périmètre) ;
- **dépendance manquante** : élément cité mais introuvable (use case référencé absent du
  spec-index, terme employé absent du glossaire, capacité IN sans trace).

Échelle de gravité :
- **bloquant** : empêche l'étape suivante de produire juste (la faiblesse se propagerait) ;
- **majeur** : risque de contresens en aval (deux lectures possibles, l'aval peut choisir la
  mauvaise) ;
- **mineur** : imprécision rattrapable plus tard sans dégât.

## Fan-out : attaquer en parallèle

- **Par défaut : un seul agent** (`agentType: "attacker-cadrage"`), qui reçoit tout le
  périmètre.
- **Contenu réellement volumineux : 2 à 4 lots**, dispatchés **en un seul message** (appels
  parallèles), plafonnés à la concurrence - au-delà de 4, on n'ajoute pas de couverture, on
  sature. Chaque lot = une tranche des sorties fraîches **+ la base amont partagée en entier**
  (les croisements inter-artefacts l'exigent).
- **Briefs nombreux : un agent par brief** (ou par petit lot de briefs), chacun avec la base
  amont - la seule exception qui justifie un fan-out plus large, les briefs étant des documents
  indépendants.
- Chaque agent reçoit **exactement trois choses** : la liste des fichiers de son lot, le nom du
  skill qui vient de tourner, et le schéma de sortie de `agents/attacker-cadrage.md`.
- **Isolation stricte (le mécanisme qui fait marcher la passe).** Ne **jamais** transmettre à
  l'agent le fil de la session, le raisonnement du skill, un résumé de ce qui a été décidé ni
  aucune justification : un regard neuf sur pièces détecte ce que la session ne voit plus. Les
  constats que la session contesterait sont filtrés à la vérification, pas évités en orientant
  l'attaquant.

## Fan-in : consolider avant toute interaction

1. **Fusionner** tous les constats en un rapport unique de session, **avant la moindre
   question à l'utilisateur**.
2. **Dédoublonner** : clé `artefact + localisation + type` ; une même faiblesse racine présente
   dans plusieurs fichiers = **un seul constat** (une seule question ; la correction
   s'appliquera partout où la faiblesse apparaît).
3. **Ordonner** : bloquant -> majeur -> mineur.
4. Le rapport vit **en session seulement** : jamais écrit dans un fichier, jamais affiché en
   liste à l'utilisateur.

## Vérification : anti faux positifs (avant toute question)

Pour chaque constat consolidé, l'orchestrateur **revérifie sur pièces** avant de déranger
l'utilisateur :
1. la `citation` du constat **existe mot pour mot** dans l'artefact, à l'endroit indiqué
   (relecture ciblée) ;
2. la faiblesse n'est pas **déjà résolue** ailleurs dans le même artefact (l'attaquant a pu
   lire une section sans voir la réponse dans une autre) ;
3. le constat ne **rouvre pas un point que l'utilisateur a explicitement tranché** dans cette
   session (cf. `ux-conventions.md` : ne jamais ré-insister sur un point tranché).

Un constat qui échoue à l'une de ces vérifications est **écarté sans bruit** - jamais montré.
Tous les constats survivants sont traités, **sans plafond**.

## La boucle de résolution : un constat, une question ouverte

Pour chaque constat retenu, dans l'ordre de gravité :

1. **Une seule question ouverte, en prose, dans le fil.** Le message = au plus une phrase
   d'ancrage factuel, puis la question. Ancrée dans **les mots du projet** (elle cite l'élément
   concret d'où elle part) ; **un seul point par message** ; jamais de liste numérotée de
   constats ; jamais de question gabarit posable sur n'importe quel projet (mêmes règles
   d'ancrage que `cadrage-ideation`).
2. **Attendre la réponse.** Réponse vague sur un point structurant : **une seule relance**
   (règle de relance unique de `references/interactive-loop.md`), puis on écrit tel quel.
   "On garde tel quel" est une réponse légitime : aucune modification, on passe au suivant.
3. **Appliquer la correction en place** dans le ou les artefacts concernés, selon les règles de
   fusion du skill (réjeu incrémental / fusion additive : fusion par identité de section, de
   terme ou de use case, préservation du valide, aucune provenance, artefacts propres et
   définitifs en sortie de session). Effets de bord à respecter : une correction qui change
   matériellement le découpage déclenche le **reset d'arbitrage** de `cadrage-decoupage` ; un
   brief corrigé repasse par sa "Vérification avant écriture" et son statut est réévalué.
4. **Constat suivant**, jusqu'à épuisement.

**Exception assumée à la boucle interactive.** Contrairement aux décisions de
`references/interactive-loop.md` (outil de question fermée, deux options), les questions de
cette passe sont **ouvertes, à réponse libre** : une faiblesse appelle une clarification
formulée par l'utilisateur, pas un choix binaire. Tout le reste de l'esprit de la boucle
s'applique tel quel : une question par message, on attend la réponse, on n'annonce jamais la
mécanique.

## Fin de passe

La passe se termine quand chaque constat retenu est **corrigé ou explicitement gardé tel
quel**. **Une seule passe** : on ne relance pas d'attaque sur les artefacts corrigés dans la
même session (une relecture répétée dans la même session n'apporte rien ; `cadrage-completude`
reste le filet terminal). Alors seulement : la mise à jour silencieuse du manifeste du skill,
puis sa ligne "Étape suivante :". Aucun drapeau de manifeste nouveau, aucune trace de la passe
dans un artefact.

## Rappels UX (contraignants)

`references/ux-conventions.md` s'applique en entier :
- **Aucune mécanique exposée.** Pas de nom d'agent, de lot, de type ou de gravité à l'écran,
  et les mots "passe d'attaque" ne sont jamais dits à l'utilisateur : chaque question apparaît
  comme une clarification naturelle de fin de travail (au plus une phrase d'ancrage du type
  "en relisant ce qu'on vient de produire, un point me semble se contredire", puis la
  question).
- **Typographie humaine** : tiret simple " - ", flèches "->", guillemets droits, trois points
  ASCII "...", Oui/Non.
- **Tout en français.**
- **Facilitateur, jamais générateur** : chaque correction de fond vient d'une réponse de
  l'utilisateur.
