# Boucle interactive — convention partagée (architecte)

Convention pour toute collecte d'information manquante et toute validation
(réponses d'architecture manquantes, workflow composants, workflow stack,
arbitrage des ADR, résolution des points de cohérence). **Aucune information n'est
inventée : on demande, on ne comble pas.**

## Règle d'or
- **Une question / un point à la fois.** Jamais une liste en bloc, jamais un tableau.
- Pour **chaque** point, présenter en clair :
  1. **Une réponse recommandée** — la proposition la plus adaptée au **contexte du
     projet**, clairement étiquetée « recommandée ».
  2. **Une (ou des) alternative(s)** plausible(s).
  3. **« Saisir ma réponse »** — l'utilisateur écrit sa propre décision.
- **Attendre la réponse** avant le point suivant. **Écrire la réponse en place** dans
  l'artefact concerné (`architecte-out/…`) — **aucun fichier annexe** pour stocker les
  réponses.
- Désigner chaque chose par son **nom métier** en clair, jamais par un code (`C1`,
  `UC1`, `P1`…).

## Aucun point laissé indéfini (règle globale)
- Après production d'un artefact, **balayer tout marqueur** `[À VALIDER]` /
  `[À CHIFFRER]` / `[À DÉFINIR]` qui y subsiste et **poser la question** correspondante
  (format ci-dessus), un point à la fois, jusqu'à ce qu'**aucun marqueur ne reste**.
- **Ne jamais se contenter d'afficher** « il reste X points » : on **pose les
  questions**. **Ne pas avancer** à l'étape suivante (ni, en fin de phase, vers
  `/designer:designer-init`) tant qu'un point reste ouvert.
- Cette règle vaut pour **tous les skills** : rien d'« à définir » n'est laissé dans
  un fichier sans avoir posé la question à l'utilisateur.

## Workflow de validation (composants, stack)
Pour les propositions (composants, choix de stack) : **restituer en prose claire**
dans le chat (nom métier + rôle en une phrase), demander « est-ce que ça te convient,
ou faut-il modifier ? », **appliquer les modifications** demandées, puis ne continuer
qu'une fois **validé**. L'IA propose, l'humain tranche. **Pas de tableau.**

## Ce qu'on écrit
- Une décision n'est enregistrée que sur une **réponse explicite** de l'utilisateur
  (recommandée acceptée, alternative choisie, ou réponse saisie).
- **Aucune provenance écrite** : pas de `(src: …)`, pas d'horodatage, pas de nom de
  personne. On écrit le **contenu** de la décision.
- **Interdit** : écrire une valeur « démo »/inventée comme si c'était un fait.

## Langue
Tout en **français** (questions, options, artefacts). Seuls les identifiants/valeurs
machine du manifeste restent des identifiants — et **jamais affichés**.
