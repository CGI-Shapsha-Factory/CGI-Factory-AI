# Boucle interactive — convention partagée

Convention DRY pour toute collecte d'information manquante (découverte,
arbitrage de couplage, validation de glossaire, résolution de trous en
complétude). Référencée par les skills concernés. **Aucune information n'est
inventée : on demande, on ne comble pas.**

## Règle d'or
- **Une question à la fois.** Jamais une liste de trous en bloc.
- Pour **chaque** question, présenter **trois options** :
  1. **Réponse recommandée** — une suggestion pré-remplie, plausible, clairement
     étiquetée « suggestion » (le client ne l'a pas encore dite).
  2. **« Passer pour l'instant »** — diffère la question (le client n'a pas encore
     répondu). La valeur reste `[À VALIDER]` et **demeure un trou bloquant**.
  3. **« Saisir ma réponse »** — l'utilisateur écrit sa propre réponse.
- **Attendre la réponse** avant de poser la question suivante. Boucler jusqu'à ce
  que chaque question soit **répondue** (option 1 ou 3) ou **passée** (option 2).
- **Décisions groupées → relecture obligatoire.** Si l'utilisateur tranche **plusieurs points
  en un seul message**, **relire la liste parsée avant d'écrire** : « J'enregistre : 1) … 2) …
  3) … — tu confirmes ? » et attendre l'accord. Ne jamais enregistrer un lot de décisions sans
  cette relecture.
- À la fin de la boucle : « **Tout est complété — tu peux passer à l'étape
  suivante.** » (ou indiquer combien de points ont été passés et restent bloquants).

## Traçabilité
- **La réponse recommandée (option 1) est une SUGGESTION : la présenter ne vaut pas
  réponse.** Une question/un point ne passe `answered`/arbitré que sur un **choix
  explicite** de l'utilisateur (option 1 ou 3). Sans choix, il reste ouvert — **jamais
  auto-validé**.
- Réponse via option 1 ou 3 → décision **humaine**, tracée `(src: atelier/utilisateur)`.
- Option 2 (passer) → `[À VALIDER]`, `status: deferred` dans le manifeste, reste
  un **trou bloquant** (ne débloque jamais une gate).
- **Interdit** : écrire une valeur « démo » / « aléatoire » comme si c'était un
  fait. La seule façon de remplir est un choix explicite de l'utilisateur.

## Langue
- **Tout est en français** : les questions, options, messages, et ce qui est écrit
  dans les artefacts/templates. (Seules les clés/valeurs machine du manifeste —
  `status`, `pending`, etc. — restent des identifiants.)
