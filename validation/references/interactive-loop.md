# Boucle interactive : convention partagée

Convention DRY pour toute collecte d'information manquante (données de test, choix de
l'outil d'exécution, tri d'un écart, verdict de recette). Référencée par les skills
concernés. **Aucune information n'est inventée : on demande, on ne comble pas.**

## Règle d'or
- **Une question à la fois.** Poser **une seule** question par message, puis **attendre** la réponse
  de l'utilisateur avant la suivante ; ne jamais enchaîner ni **auto-compléter** plusieurs points d'un
  coup, **même si une source (plan, résultat d'exécution, spécification) semble tout répondre** - une
  réponse issue d'une source **reste une suggestion à confirmer**, pas une validation.
- **Poser la question, proposer une réponse recommandée, attendre.** Pour chaque point : exposer le
  point en clair, puis proposer **une réponse recommandée** - une suggestion plausible, clairement
  étiquetée "suggestion". L'utilisateur **accepte** cette suggestion **ou** donne directement la
  sienne. **Ne pas afficher de menu numéroté d'options** (pas de "1. ... 2. ... 3. Saisir ma réponse") :
  l'utilisateur sait qu'il peut répondre librement.
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
