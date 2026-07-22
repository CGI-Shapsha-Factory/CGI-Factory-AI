# Boucle interactive : convention partagée

Convention DRY pour toute collecte d'information manquante (données de test, choix de
l'outil d'exécution, tri d'un écart, verdict de recette). Référencée par les skills
concernés. **Aucune information n'est inventée : on demande, on ne comble pas.**

## Règle d'or
- **Une question à la fois.** Poser **une seule** question par message, puis **attendre** la réponse
  de l'utilisateur avant la suivante ; ne jamais enchaîner ni **auto-compléter** plusieurs points d'un
  coup, **même si une source (plan, résultat d'exécution, spécification) semble tout répondre** - une
  réponse issue d'une source **reste une suggestion à confirmer**, pas une validation.
- **Deux formes de question, selon la nature de la réponse attendue.** Le testeur ne doit jamais
  se demander ce qu'on attend de lui ni retaper une réponse qu'on connaît déjà :
  - **Réponses énumérables (2 à 4 choix connus) : poser la question avec l'outil
    `AskUserQuestion`.** Une option par choix réel, la **recommandation en premier** avec la
    mention "(recommandé)" dans son libellé, et une `description` courte qui dit ce que le
    choix implique concrètement. **Ne jamais fabriquer d'option "Saisir ma réponse"** :
    l'outil offre toujours la saisie libre. C'est le cas de : quelle feature passe en recette,
    quel outil d'exécution, quel fichier de résultats, le sort d'un critère à clarifier, la
    nature d'un écart, le verdict de recette, une porte de régénération.
  - **Réponses libres : poser la question en prose**, avec **une réponse recommandée** clairement
    étiquetée "suggestion" quand une piste existe. C'est le cas de : l'adresse de l'environnement
    de recette, les comptes et les données de test, la lecture observable d'un critère clarifié,
    le texte d'un constat. Un menu à trois options y serait artificiel.
- **Toujours attendre la réponse**, quelle que soit la forme. Présenter une recommandation ne
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
