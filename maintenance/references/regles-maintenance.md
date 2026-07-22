# Règles de la maintenance : frontière, règles d'or, discipline chirurgicale

Référence partagée des 4 skills métier (`creation-anomalie`, `correction-anomalie`,
`creation-evolution`, `realisation-evolution`). Chaque skill y renvoie au lieu de dupliquer.

## La frontière de la livraison
**Tant qu'une feature n'est pas livrée, on est en fabrication et rien ne se trace. Une fois
livrée et en recette, tout écart constaté devient un objet suivi dans Linear.**

Avant la livraison, le développeur est seul dans sa feature : il code, casse, répare - tracer
ces corrections serait du bruit. Un défaut trouvé en revue de code avant intégration n'a jamais
atteint le code de référence : le développeur corrige, rien à tracer. Le basculement, c'est la
**livraison** : la feature est intégrée au code de référence, déclarée terminée, et mise à
l'épreuve par quelqu'un d'autre que le développeur (le PO, en recette). À partir de là, tout
écart concerne l'équipe et mérite d'exister comme objet suivi.

Conséquence pratique : si `specs/<feature>/` n'existe pas ou si la feature n'est pas déclarée
terminée, la maintenance n'a pas d'objet - signaler que la frontière n'est pas franchie, ne rien créer.

## Anomalie ou évolution : la distinction fondamentale
- **Anomalie** : le logiciel ne fait pas ce que sa spécification promet. La spécification est
  bonne, le code est en faute. On répare le code ; la spécification ne change pas.
- **Évolution** : le logiciel respecte sa spécification, mais la spécification était incomplète
  ou fausse au regard du vrai besoin. On change d'abord la spécification, puis le code suit.

C'est le **PO qui tranche la nature au moment de la création** (il ouvre soit une anomalie,
soit une évolution). Cas particulier : une anomalie ouverte de bonne foi qui se révèle être une
évolution déguisée (le code respecte la spécification) - `correction-anomalie` la referme en
"Requalifiée en évolution" avec une explication, mais **ne crée pas l'évolution** : c'est au PO
d'ouvrir l'évolution, parce que c'est lui qui porte le périmètre.

## Les quatre règles d'or (non négociables)
1. **On ne réécrit jamais le travail d'autrui.** Une feature livrée ne doit jamais être écrasée
   par un automatisme. Rouvrir une feature livrée est un **geste volontaire et tracé**
   (confirmation explicite du développeur + commentaire Linear), jamais un effet de bord.
2. **On ne touche pas à une vérité partagée dans le coin d'une feature.** Si le changement
   concerne quelque chose que plusieurs features ont en commun, il remonte au niveau central
   au lieu d'être réglé dans la feature. Sinon la même vérité finit recopiée et désynchronisée.
   **Remonter veut dire arbitrer et amender au niveau central, pas abandonner** : la remontée
   se termine toujours par une décision humaine (amender maintenant, ou parquer avec une
   condition de reprise nommée), jamais par un arrêt sans issue.
3. **On ne referme jamais sans avoir mis la trace à jour.** Une correction ou une évolution est
   finie quand la spécification reflète le comportement, que les tâches sont à jour, et que
   Linear suit. Chaque skill refuse la clôture tant que ces trois mises à jour ne sont pas faites.
4. **La spécification commande, le reste se régénère.** La spécification est la seule source de
   vérité. **On ne modifie jamais le plan ni les tâches à la main** : on change la
   spécification, puis on régénère le plan (`/speckit.plan`) et les tâches (`/speckit.tasks`).

## Le tri "propre à la feature ou vérité partagée"
Sont des **vérités partagées** (elles remontent au niveau central, jamais réglées dans une
feature) : un terme du **glossaire**, un principe de la **constitution**
(`.specify/memory/constitution.md`, via `/speckit.constitution`), une **décision
d'architecture** (ADR, composant partagé), une **donnée métier** manipulée par plusieurs
features, une **règle d'erreur ou de design** commune (guidelines). Le repérage se fait par la
feature : son entrée du registre (`architecture.feature_sequence`, champ `ucs`), la carte
`assembleur-out/feature-map.md` (dépendances et couplage) et `architecte-out/composants.md`
(composants touchés). Ces sources se **lisent** avant de trancher : le tri est un jugement,
il ne se fait pas de mémoire.

**Comment se résout une vérité partagée.** Ne pas traiter seul ne veut pas dire s'arrêter là.
Le constat est **exposé en clair** (ce que dit le contrat partagé et où, ce que demande le
changement, pourquoi les deux s'opposent), commenté sur le ticket, puis **tranché par
l'humain** - question posée **avec `AskUserQuestion`**, la voie recommandée en premier (cf.
`interactive-loop.md`). Trois issues possibles, jamais un arrêt nu ; **les deux plus plausibles
au vu du constat deviennent les options**, la troisième restant accessible par la saisie libre :
- **Faux positif** : ce n'en est pas une. Tracer le motif en commentaire, continuer.
- **Arbitrage déjà rendu** : la référence de la décision est fournie et vérifiée, citée en
  commentaire, on continue.
- **Arbitrage à rendre** : soit **amender maintenant** (voie recommandée) - le contrat est
  mis à jour **avant** la spécification, via `/speckit.constitution`, sur confirmation
  explicite ; soit **remonter et parquer** - commentaire d'escalade nommant ce qui doit être
  arbitré, ticket remis en Backlog, et **condition de reprise nommée** (relancer le skill sur
  le même ticket une fois le contrat amendé).

**L'ordre compte** : le contrat partagé s'amende **avant** la spécification. Une
spécification qui porte une exigence encore interdite par la constitution devance une
décision non prise, et sera rejetée à la prochaine Constitution Check.

## La discipline chirurgicale d'une évolution (4 disciplines, dans cet ordre)
Implémenter une évolution, c'est modifier du code qui existe et qui marche. Laissé libre,
l'outil régénère trop large et casse en silence. "Cibler uniquement l'évolution" n'est pas
automatique : c'est le skill qui l'impose.
1. **Borner le changement avant de toucher au code.** L'évolution s'exprime comme un écart
   précis par rapport à la spécification existante (telle exigence change), jamais une
   réécriture. Exigé dès la création (`creation-evolution`).
2. **Passer par le plan avant le code, et le faire valider.** Régénérer d'abord le plan, qui
   annonce ce qui va être touché, et le faire regarder par le développeur. Un plan qui annonce
   dix fichiers pour une petite évolution est un signal d'alerte, visible **avant** que le code
   ne bouge. Le plan est le garde-fou de périmètre.
3. **Lancer l'implémentation dans le cadre de l'évolution, pas en grand.** `/speckit.implement`
   est **cadré explicitement** : le périmètre de l'évolution (les exigences qui changent, les
   fichiers du plan validé) et la consigne de ne toucher que ça. Jamais une implémentation
   ouverte qui repasserait sur toute la feature.
4. **Prouver la non-régression à la sortie.** L'évolution est finie quand le nouveau
   comportement marche **et** que l'ancien n'a pas cassé : tests existants de la feature verts,
   et l'analyse d'impact sur les features couplées confirme que rien d'autre n'est abîmé.

## Ce qui est humain, ce qui est automatisé
**Gestes humains, jamais automatisés** : décider qu'un écart est une anomalie ou une évolution
(le PO, à la création) ; valider la cause racine d'une anomalie (le développeur) ; valider le
plan d'une évolution avant le code (le développeur) ; décider d'ouvrir une évolution après une
requalification (le PO) ; confirmer la réouverture d'une feature livrée (le développeur).

**Automatisés par les skills** : récupérer un objet depuis Linear, changer son statut, déposer
un commentaire, mettre à jour la spécification et régénérer plan et tâches, refuser une clôture
incomplète, signaler les features potentiellement impactées. La requalification d'une anomalie
est automatique parce qu'elle découle d'un constat technique clair (le code est conforme) ; la
création d'une évolution reste un geste du PO.
