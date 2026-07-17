# Boucle interactive : convention partagée (designer)

Convention pour toute collecte d'information manquante et toute validation (identité de
marque manquante, arbitrage des choix d'expérience, items de checklist à traiter).
**Aucune information n'est inventée : on demande, on ne comble pas.**

## Règle d'or
- **Une question / un point à la fois.** Jamais une liste en bloc.
- Pour **chaque** point, présenter **trois options** :
  1. **Réponse / proposition recommandée** - une suggestion pré-remplie, plausible,
     clairement étiquetée "suggestion" (ce n'est pas encore une décision actée).
  2. **"Sans objet"** - le point ne s'applique pas à ce projet. Il est marqué `sans_objet`
     (décision explicite, pas un oubli) et ne bloque plus.
  3. **"Saisir ma réponse"** - l'utilisateur écrit sa propre réponse / décision.
- **Attendre la réponse** avant de poser la question suivante. **Tout point se résout en
  session** : aucun report, aucun marqueur `[À VALIDER]` écrit, aucun statut laissé
  `open` en fin d'atelier (c'est l'invariant des skills `designer-atelier` et
  `designer-prompt`).
- À la fin : "**Tout est complété - on peut passer à l'étape suivante.**"

## Workflow de validation (composants, checklist)
Pour les listes proposées : **afficher la proposition en tableau dans le chat**, demander
"est-ce que ça te convient, ou faut-il modifier ?", **appliquer les modifications**
demandées, puis ne continuer qu'une fois **validé** par l'utilisateur. L'IA propose, le
designer tranche.

## Traçabilité
- Réponse via option 1 ou 3 -> décision **humaine**, origine `atelier` dans la checklist ;
  un item déduit des documents amont porte l'origine `cadrage`, `architecte` ou `maquette`.
- **Interdit** : écrire une valeur "démo"/inventée (couleur, taille, police) comme si
  c'était un fait. La maquette validée est la source primaire des valeurs visuelles.

## Langue
Tout en **français** (questions, options, tableaux affichés, artefacts). Seuls les
identifiants/valeurs machine du manifeste et noms de format (WCAG, ARIA) restent
tels quels.
