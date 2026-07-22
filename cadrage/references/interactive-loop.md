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
  geste - un intitulé, deux réponses possibles, et la saisie libre.
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
- **Relance unique sur réponse mince.** Quand la réponse à un point structurant reste vague
  ("ça doit être rapide", "des utilisateurs classiques"), **coacher, pas quizzer** : reformuler
  concrètement ce que la réponse laisse ouvert et relancer **une seule fois** avec une question
  plus précise ("rapide pour qui, sur quelle action ?"). Si l'utilisateur confirme ou maintient
  sa réponse telle quelle, **l'accepter et l'écrire telle quelle** - jamais de deuxième relance,
  jamais de relance sur un point que l'utilisateur a choisi de laisser de côté, et **jamais**
  sur la conformité / le légal (règle Q8). Calibrer l'intensité sur l'enjeu du projet : creuser
  davantage un lancement critique, rester léger sur un outil interne modeste.
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
