# Boucle interactive : convention partagée

Convention DRY pour toute collecte d'information manquante (découverte,
arbitrage de couplage, validation de glossaire, résolution de points en
complétude). Référencée par les skills concernés. **Aucune information n'est
inventée : on demande, on ne comble pas.**

## Règle d'or
- **Une question à la fois.** Poser **une seule** question par message, puis **attendre** la réponse
  de l'utilisateur avant la suivante ; ne jamais enchaîner ni **auto-compléter** plusieurs points d'un
  coup, **même si une source (transcript) semble tout répondre** - une réponse issue d'une source
  **reste une suggestion à confirmer**, pas une validation.
- **Toute question passe par l'outil `AskUserQuestion`. Sans exception.** Jamais une question
  rédigée en prose dans le fil de la conversation : l'utilisateur doit toujours retrouver le même
  geste - un intitulé, deux réponses possibles, et la saisie libre. **Variante cadrée (Q14-Q19
  de la passe découverte de `cadrage-extraction`)** : l'outil reste obligatoire, mais **aucune
  option de contenu** - les deux options sont **utilitaires** (retrait "je laisse ce point de
  côté" ; reformulation avec exemple, ou "ça suffit, on avance" pour les sondes Q19) et la
  réponse de fond passe par la **saisie libre**, pour forcer l'utilisateur à formuler lui-même
  (voir le `SKILL.md` d'extraction). Cette variante ne s'étend à **aucun** autre usage (couplage,
  glossaire, complétude, Q1-Q13 gardent les deux options de contenu).
- **Une question par appel.** L'outil sait en porter plusieurs : on ne s'en sert jamais. Un appel
  = une question, puis on s'arrête et on attend. Le groupage est interdit dans la cadrage, y
  compris pour des points de même nature.
- **La puce (`header`) porte le thème en clair** - "Utilisateurs", "Hébergement", "Périmètre",
  "Glossaire" - en quelques caractères. **Jamais un code** (`Q8`, `Q11`, `B1`, `A6`) ni une clé
  de manifeste : c'est une sortie utilisateur comme une autre (cf. la section 3ter de
  `ux-conventions.md`).
- **Exactement deux options par question**, jamais trois ni quatre. L'outil ajoute lui-même la
  saisie libre en troisième ligne : le lecteur voit donc **trois lignes**, dont la dernière lui
  rend la main. Format :
  - **option 1** = la **réponse recommandée** (la suggestion tirée de la matière si elle existe,
    sinon la plus plausible), avec la mention "(recommandé)" dans son libellé et, dans sa
    `description`, **ce qui la soutient** ("ce que dit le transcript : ...") ;
  - **option 2** = l'**alternative crédible** - la lecture concurrente de la matière, ou le cas de
    figure opposé le plus fréquent. Jamais un remplissage : si rien de sérieux ne se présente,
    poser l'alternative "aucune des deux, je précise" et laisser la description dire pourquoi le
    point reste ouvert.
  - **Ne jamais fabriquer d'option "Saisir ma réponse"** : l'outil l'offre déjà, et une troisième
    option la doublonnerait.
- **Quand le point est légitimement esquivable, l'option 2 EST le retrait.** Une question de
  découverte, un point de complétude, un arbitrage que l'utilisateur peut refuser de trancher :
  l'option 2 devient "je laisse ce point de côté", et l'alternative de fond passe dans la saisie
  libre. Sans elle, le retrait n'existe plus à l'écran et l'utilisateur choisit une réponse par
  défaut pour avancer - on enregistrerait alors comme tranché un point qu'il n'a pas voulu
  trancher. **Le retrait doit toujours être visible sans avoir à taper.**
- **Le nombre d'options ne remplace pas l'écoute.** Deux options ne veulent pas dire que la
  réponse est binaire : elles ouvrent la conversation, la saisie libre reste la voie normale
  pour tout ce qui ne rentre pas dans les deux.
- **Forks de conception : exposer le coût dans chaque option.** À un **fork de conception** - un
  choix de cadrage aux conséquences durables (découper ou fusionner une feature, coupler ou
  séparer deux capacités, inclure ou exclure du périmètre) par opposition à une simple
  confirmation - les deux options ne se contentent pas de "recommandée vs alternative" : chacune
  **nomme ce qu'elle coûte ou ferme** dans sa `description` ("ce choix simplifie X mais reporte
  Y"). C'est la version deux-options du "proposer deux ou trois approches avec leurs compromis
  et une recommandation" : l'option 1 porte le cadrage recommandé **avec son coût**, l'option 2
  le meilleur concurrent **avec le sien**, la saisie libre laisse la place à un troisième
  cadrage. Le but n'est pas d'ajouter des questions mais de rendre l'arbitrage **éclairé** là
  où il engage la suite.
- **Relance unique par défaut.** Quand la réponse à un point structurant reste vague
  ("ça doit être rapide", "des utilisateurs classiques"), **coacher, pas quizzer** : reformuler
  concrètement ce que la réponse laisse ouvert et relancer **une seule fois** avec une question
  plus précise ("rapide pour qui, sur quelle action ?"). Si l'utilisateur confirme ou maintient
  sa réponse telle quelle, **l'accepter et l'écrire telle quelle** - jamais de relance
  automatique supplémentaire, jamais de relance sur un point que l'utilisateur a choisi de
  laisser de côté, et **jamais** sur la conformité / le légal (règle Q8). Calibrer l'intensité
  sur l'enjeu du projet : creuser davantage un lancement critique, rester léger sur un outil
  interne modeste.
- **Sondage approfondi sur choix explicite (opt-in).** La relance unique reste la règle ; le
  sondage plus profond est une **exception que l'utilisateur ouvre lui-même**, jamais imposée.
  Conditions cumulatives : le point est **structurant** (utilisateurs cibles, problème résolu,
  signal de succès, contrainte non négociable), l'**enjeu est fort** (pilote ou lancement
  critique - pas un outil interne modeste), et la réponse **reste mince après la relance
  unique**. Alors, proposer **avec `AskUserQuestion`** - deux options : "Creusons ce point
  ensemble (recommandé)" et "Ma réponse tient, on avance". Sur le second choix, **écrire la
  réponse telle quelle** et passer à la suite. Sur le premier, mener un **laddering court** en
  prose (relances ouvertes, une par message) : monter vers la racine ("pourquoi est-ce
  important - qu'est-ce que ça t'apporte vraiment ?") puis descendre vers le concret
  ("concrètement, sur quelle action, pour qui, et à quoi verrais-tu que c'est atteint ?").
  **Plafond de trois crans**, puis on écrit la réponse affinée. À tout moment l'utilisateur
  peut clore ("ça me suffit") : on s'arrête et on écrit l'état atteint. **Jamais** sur Q8 /
  légal, **jamais** sur un point laissé de côté. Pour les seeds qualité (Q2 charge, Q6
  disponibilité, Q7 performance), le laddering cadre l'ordre de grandeur sans jamais le
  présenter comme une cible chiffrée ("rapide, ça veut dire combien, sur quelle opération ?").
- **Si l'utilisateur ne tranche pas un point** (il préfère le laisser de côté) : **on n'écrit rien**
  pour ce point. Aucun marqueur, aucune liste de points ouverts persistée - le point est simplement
  omis de l'artefact. On peut le lui rappeler oralement en fin de boucle, jamais l'écrire dans un fichier.
- **Décisions groupées -> relecture obligatoire.** Si l'utilisateur tranche **plusieurs points en un
  seul message**, **relire la liste parsée avant d'écrire** : "J'enregistre : 1) ... 2) ... 3) ... - tu
  confirmes ?" et attendre l'accord. Ne jamais enregistrer un lot de décisions sans cette relecture.
- À la fin de la boucle : "**Tout est complété - tu peux passer à l'étape suivante.**"

## Ce qu'on écrit
- Un point n'est enregistré que sur une **réponse explicite** de l'utilisateur (suggestion acceptée ou
  réponse saisie). La réponse recommandée est une **suggestion** : la présenter ne vaut pas réponse.
- **Ne jamais écrire de provenance dans l'artefact** : pas d'horodatage, pas d'interlocuteur, pas de
  `(src: ...)`. On écrit le **contenu décidé**, rien d'autre. (La règle "ne rien inventer" reste une
  consigne interne de grounding, pas une mention écrite.)
- **Interdit** : écrire une valeur "démo" / "aléatoire" comme si c'était un fait. La seule façon de
  remplir est une réponse explicite de l'utilisateur ; sinon on omet.

## Langue
- **Tout est en français** : les questions, la réponse recommandée, les messages, et ce qui est écrit
  dans les artefacts/templates. (Seules les clés/valeurs machine du manifeste - `status`, `pending`,
  etc. - restent des identifiants.)
