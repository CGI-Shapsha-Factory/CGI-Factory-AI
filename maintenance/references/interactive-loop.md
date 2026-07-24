# Boucle interactive : convention partagée

Convention DRY pour toute collecte d'information manquante (création d'une anomalie,
création d'une évolution, validation d'une cause racine ou d'un plan). Référencée par les
skills concernés. **Aucune information n'est inventée : on demande, on ne comble pas.**

## Règle d'or
- **Une question à la fois.** Poser **une seule** question par message, puis **attendre** la réponse
  de l'utilisateur avant la suivante ; ne jamais enchaîner ni **auto-compléter** plusieurs points d'un
  coup, **même si une source (ticket, spécification) semble tout répondre** - une réponse issue d'une
  source **reste une suggestion à confirmer**, pas une validation.
- **Toute question passe par l'outil `AskUserQuestion`. Sans exception.** Jamais une question
  rédigée en prose dans le fil de la conversation : l'utilisateur doit toujours retrouver le même
  geste - une puce de thème, deux réponses possibles, et la saisie libre.
- **L'outil est le moyen, jamais le message.** Ne **jamais** annoncer la mécanique de
  questionnement à l'utilisateur : pas de "via `AskUserQuestion`", pas de "je te pose la
  question avec deux options", pas de "options tirées de la matière", pas de "je vais utiliser
  l'outil...". La question **apparaît directement** ; si un mot d'introduction est utile, il
  porte sur le **contenu** - jamais sur le mécanisme.
- **Une question par appel.** L'outil sait en porter plusieurs : on ne s'en sert jamais. Un appel
  = un point, puis on s'arrête et on attend.
- **Deux options renseignées, trois lignes à l'écran.** L'outil ajoute lui-même la saisie libre en
  dernière ligne :
  1. **La réponse recommandée** - une suggestion plausible, avec la mention "(recommandé)" dans
     son libellé et, dans sa `description`, **ce qui la soutient** (ce que dit le ticket, la
     spécification, le code). La présenter ne vaut pas réponse : elle le devient quand
     l'utilisateur la choisit.
  2. **L'alternative crédible** - avec deux déclinaisons imposées par ce que le plugin documente :
     - sur une **confirmation avant écriture externe** (créer un ticket, changer un état,
       requalifier), l'option 2 est le **refus** - "ne pas créer", "laisser tel quel". Le refus
       doit rester **cliquable**, jamais relégué à la saisie libre ;
     - sur un point **légitimement esquivable**, l'option 2 est le **retrait** ("je laisse ce
       point de côté") et l'alternative de fond passe dans la saisie libre - sans quoi le retrait
       disparaît de l'écran et l'utilisateur tranche par défaut pour avancer.
     **Exception** : dans les gabarits d'anomalie et d'évolution, la complétude est **exigée** ;
     il n'y a pas de retrait à offrir, les deux options portent deux propositions de fond.
  - **Ne jamais écrire soi-même une option "Saisir ma réponse"** : elle ferait une quatrième
    ligne, en doublon de celle que l'outil ajoute.
- **La puce (`header`) porte le thème en clair** - "Feature", "Ticket", "Cause", "Statut" - en
  quelques caractères. **Jamais un code** (`FR-001`, `TC-001`) ni une clé de manifeste.
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
- **Ne jamais écrire de provenance** : pas d'horodatage, pas d'interlocuteur, pas de
  `(src: ...)`. On écrit le **contenu décidé**, rien d'autre. (La règle "ne rien inventer" reste une
  consigne interne de grounding, pas une mention écrite.)
- **Interdit** : écrire une valeur "démo" / "aléatoire" comme si c'était un fait. La seule façon de
  remplir est une réponse explicite de l'utilisateur ; sinon on omet.

## Langue
- **Tout est en français** : les questions, la réponse recommandée, les messages, et ce qui est écrit
  dans les tickets. (Seules les clés/valeurs machine du manifeste - `status`, `pending`,
  etc. - restent des identifiants.)
