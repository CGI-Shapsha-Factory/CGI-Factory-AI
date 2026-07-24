# Boucle interactive : convention partagée (designer)

Convention pour toute collecte d'information manquante et toute validation (identité de
marque manquante, arbitrage des choix d'expérience, items de checklist à traiter).
**Aucune information n'est inventée : on demande, on ne comble pas.**

## Règle d'or
- **Toute question passe par l'outil `AskUserQuestion`. Sans exception.** Jamais une
  question rédigée en prose dans le fil de la conversation : le designer doit toujours
  retrouver le même geste - une puce de thème, deux réponses possibles, et la saisie libre.
- **L'outil est le moyen, jamais le message.** Ne **jamais** annoncer la mécanique de
  questionnement à l'utilisateur : pas de "via `AskUserQuestion`", pas de "je te pose la
  question avec deux options", pas de "options tirées de la matière", pas de "je vais utiliser
  l'outil...". La question **apparaît directement** ; si un mot d'introduction est utile, il
  porte sur le **contenu** - jamais sur le mécanisme.
- **Une question par appel.** L'outil sait en porter plusieurs : on ne s'en sert jamais.
  Un appel = un point, puis on s'arrête et on attend. Jamais une liste en bloc.
- **Deux options renseignées, trois lignes à l'écran.** L'outil ajoute lui-même la saisie
  libre en dernière ligne :
  1. **La proposition recommandée** - une suggestion pré-remplie, plausible, avec la
     mention "(recommandé)" dans son libellé et, dans sa `description`, **ce qui la
     soutient** (le handoff ou la maquette qui l'appuie). Ce n'est pas encore une décision
     actée : elle le devient quand le designer la choisit.
  2. **"Sans objet"** - le point ne s'applique pas à ce projet. Il est marqué `sans_objet`
     (décision explicite, pas un oubli) et ne bloque plus. **C'est l'option 2 par défaut
     sur tout item de checklist** : c'est un statut du manifeste, il doit rester
     atteignable sans avoir à taper, sinon le designer tranche par défaut pour avancer.
     L'alternative de fond passe alors dans la saisie libre.
  - Sur un point qui **ne peut pas** être sans objet (un arbitrage d'expérience qu'il faut
    trancher), l'option 2 porte l'**alternative crédible** à la place.
  - **Ne jamais écrire soi-même une option "Saisir ma réponse"** : elle ferait une
    quatrième ligne, en doublon de celle que l'outil ajoute.
- **La puce (`header`) porte le thème en clair** - "Tokens", "États", "Microcopie",
  "Accessibilité" - en quelques caractères. **Jamais un code d'item** (`F1`, `E2`, `T8`)
  ni une clé de manifeste.
- **Attendre la réponse** avant de poser la question suivante. **Tout point se résout en
  session** : aucun report, aucun marqueur `[À VALIDER]` écrit, aucun statut laissé
  `open` en fin d'atelier (c'est l'invariant des skills `designer-atelier` et
  `designer-prompt`).
- À la fin : "**Tout est complété - on peut passer à l'étape suivante.**"

## Workflow de validation (composants, checklist)
Pour les listes proposées : **afficher la proposition en tableau dans le chat**, puis poser la
validation **avec `AskUserQuestion`** - deux options, "ça me convient" (recommandé) et "il faut
modifier", la saisie libre recevant le détail des retouches. **Appliquer les modifications**
demandées, puis ne continuer qu'une fois **validé** par l'utilisateur. L'IA propose, le
designer tranche.

## Traçabilité
- Réponse via l'option recommandée ou la saisie libre -> décision **humaine**, origine
  `atelier` dans la checklist ;
  un item déduit des documents amont porte l'origine `cadrage`, `architecte` ou `maquette`.
- **Interdit** : écrire une valeur "démo"/inventée (couleur, taille, police) comme si
  c'était un fait. La maquette validée est la source primaire des valeurs visuelles.

## Langue
Tout en **français** (questions, options, tableaux affichés, artefacts). Seuls les
identifiants/valeurs machine du manifeste et noms de format (WCAG, ARIA) restent
tels quels.
