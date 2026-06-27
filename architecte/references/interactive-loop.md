# Boucle interactive — convention partagée (architecte)

Convention pour toute collecte d'information manquante et toute validation
(réponses d'architecture manquantes, workflow composants, workflow stack,
arbitrage des ADR). **Aucune information n'est inventée : on demande, on ne comble
pas.**

## Règle d'or
- **Une question / un point à la fois.** Jamais une liste en bloc.
- Pour **chaque** point, présenter **trois options** :
  1. **Réponse / proposition recommandée** — une suggestion pré-remplie, plausible,
     clairement étiquetée « suggestion » (ce n'est pas encore une décision actée).
  2. **« Passer pour l'instant »** — diffère le point. La valeur reste `[À VALIDER]`
     et **demeure bloquante** (ne débloque aucune porte).
  3. **« Saisir ma réponse »** — l'utilisateur écrit sa propre réponse / décision.
- **Attendre la réponse** avant de poser la question suivante. Boucler jusqu'à ce
  que chaque point soit **répondu** (option 1 ou 3) ou **passé** (option 2).
- À la fin : « **Tout est complété — on peut passer à l'étape suivante.** » (ou
  indiquer combien de points restent passés/bloquants).

## Workflow de validation (composants, stack)
Pour les listes proposées (composants, choix de stack) : **afficher la proposition
en tableau dans le chat**, demander « est-ce que ça te convient, ou faut-il
modifier ? », **appliquer les modifications** demandées, puis ne continuer qu'une
fois **validé** par l'utilisateur. L'IA propose, l'humain tranche.

## Traçabilité
- Réponse via option 1 ou 3 → décision **humaine**, tracée `(src: atelier/utilisateur)`
  ou `(src: <artefact cadrage>)` si elle vient des documents de cadrage.
- Option 2 (passer) → `[À VALIDER]`, statut `deferred`, reste **bloquant**.
- **Interdit** : écrire une valeur « démo »/inventée comme si c'était un fait.

## Langue
Tout en **français** (questions, options, tableaux affichés, artefacts). Seuls les
identifiants/valeurs machine du manifeste restent des identifiants.
