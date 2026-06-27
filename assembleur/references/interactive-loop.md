# Boucle interactive — convention partagée (assembleur)

Convention pour toute collecte d'information manquante et toute validation (repo cible,
résolution de contradictions entre faces, validation de cohérence, validation de l'équipe).
**Aucune information n'est inventée : on demande, on ne comble pas.**

## Règle d'or
- **Une question / un point à la fois.** Jamais une liste en bloc.
- Pour **chaque** point, présenter **trois options** :
  1. **Réponse / proposition recommandée** — pré-remplie, plausible, étiquetée « suggestion ».
  2. **« Passer pour l'instant »** — diffère le point. La valeur reste `[À VALIDER]` et
     **demeure bloquante**.
  3. **« Saisir ma réponse »** — l'utilisateur écrit sa propre réponse / décision.
- **Attendre la réponse** avant le point suivant. Boucler jusqu'à résolution.

## Workflows de validation (cohérence, équipe)
Pour le **rapport de cohérence** et la **validation de l'équipe** : **afficher en chat** le
récapitulatif (features, faces, contradictions ; ou découpage + walking skeleton + briefs),
demander la validation, appliquer les corrections, et ne continuer (constitution finale,
puis Linear) qu'une fois **validé par l'humain**. L'IA propose, l'humain tranche.

## Traçabilité
- Décision via option 1 ou 3 → **humaine**, tracée `(src: atelier/utilisateur)` ou
  `(src: cadrage | architecte | designer)` si elle vient des contrats amont.
- Option 2 (passer) → `[À VALIDER]` / `NEEDS CLARIFICATION`, reste **bloquant**.
- **Interdit** : inventer une décision, une feature, une issue Linear.

## Langue
Tout en **français** (questions, options, restitutions, artefacts). Seuls les
identifiants/valeurs machine et noms de format (SpecKit, Linear, `spec.md`) restent tels quels.
