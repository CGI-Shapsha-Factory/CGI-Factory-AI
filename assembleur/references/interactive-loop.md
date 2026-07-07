# Boucle interactive — convention partagée (assembleur)

Convention pour toute collecte d'information manquante et toute validation (résolution de
contradictions entre faces, validation de cohérence). **Aucune information n'est inventée : on
demande, on ne comble pas.**

## Règle d'or
- **Une question / un point à la fois.** Jamais une liste en bloc, jamais un tableau.
- Pour **chaque** point, présenter en clair : **une réponse recommandée** (adaptée au projet) +
  **une (ou des) alternative(s)** + **« saisir ma réponse »**. Désigner chaque chose par son **nom
  en clair**, jamais par un code.
- **Attendre la réponse** avant le point suivant, et **écrire la réponse en place** dans le fichier
  concerné du paquet (`assembleur-out/…`) — **aucun fichier annexe**.

## Aucun point laissé indéfini
- Après la synthèse du paquet, **balayer tout marqueur** `[À VALIDER]` / `[À CHIFFRER]` /
  `NEEDS CLARIFICATION` et **poser la question** correspondante, un point à la fois, jusqu'à ce
  qu'**aucun marqueur ne reste**. **Ne jamais se contenter d'afficher** « il reste X points ».
- **Ne pas conclure** la convergence tant qu'un point reste ouvert.

## Validation de cohérence
Restituer le rapport de cohérence **en prose** (pas de tableau), demander la validation, appliquer
les corrections, et ne marquer la cohérence validée qu'**après** le geste humain. L'IA propose,
l'humain tranche.

## Ce qu'on écrit
- Une décision n'est enregistrée que sur une **réponse explicite** de l'utilisateur.
- **Aucune provenance écrite** : pas de `(src:)`, pas d'horodatage, pas de nom de personne.
- **Interdit** : inventer une décision ou une feature.

## Langue
Tout en **français** (questions, options, restitutions, artefacts). Seuls les identifiants/valeurs
machine et noms de format (SpecKit, `spec.md`) restent tels quels.
