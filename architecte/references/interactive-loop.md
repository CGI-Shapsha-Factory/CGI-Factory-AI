# Boucle interactive : convention partagée (architecte)

Convention pour toute collecte d'information manquante et toute validation
(réponses d'architecture manquantes, workflow composants, workflow stack,
arbitrage des ADR, résolution des points de cohérence). **Aucune information n'est
inventée : on demande, on ne comble pas.**

## Règle d'or
- **Toute question passe par l'outil `AskUserQuestion`. Sans exception.** Jamais une
  question rédigée en prose dans le fil de la conversation : l'utilisateur doit toujours
  retrouver le même geste - une puce de thème, deux réponses possibles, et la saisie libre.
- **Une question par appel.** L'outil sait en porter plusieurs : on ne s'en sert jamais.
  Un appel = un point, puis on s'arrête et on attend. Jamais une liste en bloc, jamais un
  tableau de points à trancher.
- **Deux options renseignées, trois lignes à l'écran.** L'outil ajoute lui-même la saisie
  libre en dernière ligne :
  1. **La réponse recommandée** - la proposition la plus adaptée au **contexte du
     projet**, avec la mention "(recommandé)" dans son libellé et, dans sa `description`,
     **ce qui la soutient** (ce que dit le cadrage, la contrainte qui la motive).
  2. **L'alternative crédible** - l'autre proposition défendable. Pour un **point de
     cohérence** qui peut légitimement ne pas s'appliquer, l'option 2 est **"sans objet"**
     (elle se solde par un `[SANS OBJET : raison]`, cf. `coherence-checklist-guide.md`) et
     l'alternative de fond passe dans la saisie libre : sans quoi ce dénouement disparaît
     de l'écran et l'utilisateur tranche par défaut pour avancer.
  - **Ne jamais écrire soi-même une option "Saisir ma réponse"** : elle ferait une
    quatrième ligne, en doublon de celle que l'outil ajoute.
- **Pas de retrait ailleurs.** Une réponse d'architecture, un choix de stack, un arbitrage
  d'ADR **ne se laissent pas de côté** (voir "Aucun point laissé indéfini") : les deux
  options portent alors deux propositions de fond.
- **La puce (`header`) porte le thème en clair** - "Hébergement", "Profil d'équipe",
  "Base de données" - en quelques caractères. **Jamais un code** (`C1`, `UC1`, `P1`) ni
  une clé de manifeste.
- **Attendre la réponse** avant le point suivant. **Écrire la réponse en place** dans
  l'artefact concerné (`architecte-out/...`) - **aucun fichier annexe** pour stocker les
  réponses.
- Désigner chaque chose par son **nom métier** en clair, jamais par un code (`C1`,
  `UC1`, `P1`...).

## Aucun point laissé indéfini (règle globale)
- Après production d'un artefact, **balayer tout marqueur** `[À VALIDER]` /
  `[À CHIFFRER]` / `[À DÉFINIR]` qui y subsiste et **poser la question** correspondante
  (format ci-dessus), un point à la fois, jusqu'à ce qu'**aucun marqueur ne reste**.
- **Ne jamais se contenter d'afficher** "il reste X points" : on **pose les
  questions**. **Ne pas avancer** à l'étape suivante (ni, en fin de phase, vers
  `/designer:designer-init`) tant qu'un point reste ouvert.
- Cette règle vaut pour **tous les skills** : rien d'"à définir" n'est laissé dans
  un fichier sans avoir posé la question à l'utilisateur.

## Workflow de validation (composants, stack)
Pour les propositions (composants, choix de stack) : **restituer en prose claire**
dans le chat (nom métier + rôle en une phrase), puis poser la validation **avec
`AskUserQuestion`** - deux options, "ça me convient" (recommandé) et "il faut modifier",
la saisie libre recevant le détail des retouches. **Appliquer les modifications**
demandées, puis ne continuer qu'une fois **validé**. L'IA propose, l'humain tranche.
**Pas de tableau.**

## Ce qu'on écrit
- Une décision n'est enregistrée que sur une **réponse explicite** de l'utilisateur
  (recommandée acceptée, alternative choisie, ou réponse saisie).
- **Aucune provenance écrite** : pas de `(src: ...)`, pas d'horodatage, pas de nom de
  personne. On écrit le **contenu** de la décision.
- **Interdit** : écrire une valeur "démo"/inventée comme si c'était un fait.

## Langue
Tout en **français** (questions, options, artefacts). Seuls les identifiants/valeurs
machine du manifeste restent des identifiants - et **jamais affichés**.
