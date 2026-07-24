# Boucle interactive : convention partagée

Convention DRY pour toute collecte d'information manquante (données de test, choix de
l'outil d'exécution, tri d'un écart, verdict de recette). Référencée par les skills
concernés. **Aucune information n'est inventée : on demande, on ne comble pas.**

## Règle d'or
- **Jamais de cul-de-sac.** Chaque fois que le skill **rend la main en attendant quelque chose
  du testeur** - il refuse, un pré-requis manque, il attend un accord, il s'apprête à écrire
  hors du repo - il **termine par une question `AskUserQuestion`** dont les options sont les
  **issues réellement praticables ici et maintenant**, la plus sensée en premier avec la
  mention "(recommandé)". Un refus n'est pas une impasse : c'est un choix entre plusieurs
  façons d'avancer. Les options d'un refus sont **actionnables** - lancer le skill amont sur
  telle feature, poser le terrain manquant, prendre une autre feature, ouvrir ce qui existe
  déjà - **jamais** un simple "OK j'ai compris". Le refus reste un refus (rien n'est écrit),
  mais il se termine par la question, pas par un point final.
  Seules fins **sans** question : la fin normale d'un skill (elle a déjà sa ligne "Étape
  suivante", cf. `ux-conventions.md`) et une erreur technique que seul le testeur peut lever.
- **Une question à la fois.** Poser **une seule** question par message, puis **attendre** la réponse
  de l'utilisateur avant la suivante ; ne jamais enchaîner ni **auto-compléter** plusieurs points d'un
  coup, **même si une source (plan, résultat d'exécution, spécification) semble tout répondre** - une
  réponse issue d'une source **reste une suggestion à confirmer**, pas une validation.
- **Une seule forme de question : l'outil `AskUserQuestion`. Sans exception.** Toute question
  posée au testeur passe par l'outil - **jamais** une question rédigée en prose dans le fil de
  la conversation. Le testeur doit toujours retrouver le même geste : une puce de contexte, des
  choix, et la saisie libre. Cela vaut pour les réponses énumérables **comme** pour les réponses
  libres :
  - **Réponses énumérables** (quelle feature passe en recette, quel outil d'exécution, quel
    fichier de résultats, le sort d'un critère à clarifier, la nature d'un écart, le verdict de
    recette, une porte de régénération) : une option par choix réel.
  - **Réponses libres** (l'adresse de l'environnement de recette, les comptes et les données de
    test, la lecture observable d'un critère clarifié, le texte d'un constat) : **les options
    portent les candidats plausibles**, déduits de ce qu'on a lu dans le dépôt - par exemple, pour
    une adresse de recette, l'URL locale servie par un serveur et l'ouverture directe du fichier.
    Le testeur choisit un candidat ou saisit le sien. Une seule piste crédible ? Une option
    "aucune de ces adresses" suffit à ouvrir la saisie ; **ne jamais renoncer à l'outil faute de
    deuxième option évidente**.
- **L'outil est le moyen, jamais le message.** Ne **jamais** annoncer la mécanique de
  questionnement à l'utilisateur : pas de "via `AskUserQuestion`", pas de "je te pose la
  question avec deux options", pas de "options tirées de la matière", pas de "je vais utiliser
  l'outil...". La question **apparaît directement** ; si un mot d'introduction est utile, il
  porte sur le **contenu** - jamais sur le mécanisme.
- **Forme des options.** La **recommandation en premier** avec la mention "(recommandé)" dans
  son libellé, et une `description` courte qui dit ce que le choix implique concrètement.
  **Ne jamais fabriquer d'option "Saisir ma réponse"** : l'outil offre toujours la saisie libre.
- **Toujours attendre la réponse.** Présenter une recommandation ne
  vaut jamais réponse : rien n'est écrit sans un choix ou une saisie explicite du testeur.
- **Regroupement autorisé pour les points de même nature.** Une même série (le sort de plusieurs
  critères à clarifier, le tri de plusieurs écarts) peut être posée en un seul appel à
  `AskUserQuestion`, une question par point. C'est le seul assouplissement de la règle "une
  question à la fois" ; la relecture avant écriture (ci-dessous) reste obligatoire.
- **Si l'utilisateur ne tranche pas un point** (il préfère le laisser de côté) : **on n'écrit rien**
  pour ce point. Aucun marqueur, aucune liste de points ouverts persistée - le point est simplement
  omis. On peut le lui rappeler oralement en fin de boucle, jamais l'écrire dans un fichier ou un ticket.
- **Décisions groupées -> relecture obligatoire.** Si l'utilisateur tranche **plusieurs points en un
  seul message**, **relire la liste parsée avant d'écrire** : "J'enregistre : 1) ... 2) ... 3) ... - tu
  confirmes ?" et attendre l'accord. Ne jamais enregistrer un lot de décisions sans cette relecture.
- À la fin de la boucle : "**Tout est complété - tu peux passer à l'étape suivante.**"

## Ce qu'on écrit
- Un point n'est enregistré que sur une **réponse explicite** de l'utilisateur (suggestion acceptée ou
  réponse saisie). La réponse recommandée est une **suggestion** : la présenter ne vaut pas réponse.
- **Ne jamais écrire de provenance** : pas d'horodatage superflu, pas d'interlocuteur, pas de
  `(src: ...)`. On écrit le **contenu décidé**, rien d'autre. (La règle "ne rien inventer" reste une
  consigne interne de grounding, pas une mention écrite.)
- **Interdit** : écrire une valeur "démo" / "aléatoire" comme si c'était un fait. La seule façon de
  remplir est une réponse explicite de l'utilisateur ; sinon on omet.
- **Exception factuelle des résultats d'exécution** : un verdict de test (OK / KO / NON TESTABLE) est
  un **constat**, pas une décision - il s'écrit tel quel dans les résultats et le rapport sans passer
  par la boucle. Seuls le **tri d'un écart** et le **verdict de recette** sont des décisions humaines.

## Langue
- **Tout est en français** : les questions, la réponse recommandée, les messages, et ce qui est écrit
  dans les fichiers. (Seules les clés/valeurs machine du manifeste - `environnement_recette`,
  `outil_prefere`, etc. - restent des identifiants.)
