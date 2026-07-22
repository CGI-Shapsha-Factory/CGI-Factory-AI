# Boucle interactive : convention partagée (assembleur)

Convention pour toute collecte d'information manquante et toute validation (résolution de
contradictions entre faces, validation de cohérence). **Aucune information n'est inventée : on
demande, on ne comble pas.**

## Règle d'or
- **Toute question passe par l'outil `AskUserQuestion`. Sans exception.** Jamais une question
  rédigée en prose dans le fil de la conversation : l'utilisateur doit toujours retrouver le même
  geste - une puce de thème, deux réponses possibles, et la saisie libre.
- **Une question par appel.** L'outil sait en porter plusieurs : on ne s'en sert jamais. Un appel
  = un point, puis on s'arrête et on attend. Jamais une liste en bloc, jamais un tableau de points
  à trancher.
- **Deux options renseignées, trois lignes à l'écran.** L'outil ajoute lui-même la saisie libre en
  dernière ligne :
  1. **La réponse recommandée** (adaptée au projet), avec la mention "(recommandé)" dans son
     libellé et, dans sa `description`, **ce qui la soutient**.
  2. **L'alternative crédible**. Sur une **confirmation avant écriture externe** (créer un ticket,
     changer un état, écrire `init-cowork.md`), l'option 2 est le **refus** - "ne pas créer",
     "laisser le statut tel quel". Le refus doit rester **cliquable**, jamais relégué à la saisie
     libre : c'est le garde-fou d'une action difficile à défaire.
  - **Ne jamais écrire soi-même une option "Saisir ma réponse"** : elle ferait une quatrième
    ligne, en doublon de celle que l'outil ajoute.
- **Pas de retrait.** "Aucun point laissé indéfini" (ci-dessous) vaut ici : un point de
  convergence ne se laisse pas de côté, les deux options portent deux propositions de fond.
- **La puce (`header`) porte le thème en clair** - "Registre", "Cohérence", "Ticket", "Statut" -
  en quelques caractères. **Jamais un code** (`UC1`, `FR-001`) ni une clé de manifeste.
- Désigner chaque chose par son **nom en clair**, jamais par un code.
- **Attendre la réponse** avant le point suivant, et **écrire la réponse en place** dans le fichier
  concerné du paquet (`assembleur-out/...`) - **aucun fichier annexe**.

## Aucun point laissé indéfini
- Après la synthèse du paquet, **balayer tout marqueur** `[À VALIDER]` / `[À CHIFFRER]` /
  `NEEDS CLARIFICATION` et **poser la question** correspondante, un point à la fois, jusqu'à ce
  qu'**aucun marqueur ne reste**. **Ne jamais se contenter d'afficher** "il reste X points".
- **Ne pas conclure** la convergence tant qu'un point reste ouvert.

## Validation de cohérence
Restituer le rapport de cohérence **en prose** (pas de tableau), puis demander la validation
**avec `AskUserQuestion`** - deux options, "la cohérence me convient" (recommandé) et "il faut
corriger", la saisie libre recevant le détail des corrections. Appliquer
les corrections, et ne marquer la cohérence validée qu'**après** le geste humain. L'IA propose,
l'humain tranche.

## Ce qu'on écrit
- Une décision n'est enregistrée que sur une **réponse explicite** de l'utilisateur.
- **Aucune provenance écrite** : pas de `(src:)`, pas d'horodatage, pas de nom de personne.
- **Interdit** : inventer une décision ou une feature.

## Langue
Tout en **français** (questions, options, restitutions, artefacts). Seuls les identifiants/valeurs
machine et noms de format (SpecKit, `spec.md`) restent tels quels.
