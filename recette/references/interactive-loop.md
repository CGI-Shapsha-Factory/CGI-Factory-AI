# Boucle interactive — convention partagée (recette)

Convention pour toute collecte d'information manquante et toute validation (complétude d'une anomalie
ou d'une évolution, validation d'une cause racine, validation d'un plan avant le code). **Aucune
information n'est inventée : on demande, on ne comble pas.**

## Règle d'or
- **Une question / un point à la fois.** Jamais une liste en bloc, jamais un tableau.
- Pour **chaque** point, présenter en clair : **une réponse recommandée** (adaptée au projet) +
  **une (ou des) alternative(s)** + **« saisir ma réponse »**. Désigner chaque chose par son **nom
  en clair**, jamais par un code.
- **Attendre la réponse** avant le point suivant, et **écrire la réponse en place** là où elle doit
  vivre (le ticket Linear, la spécification `specs/<id>-*/spec.md`) — **aucun fichier annexe**.

## Aucun point laissé indéfini
- Pour une création (anomalie/évolution) : **balayer tout champ obligatoire manquant** et **poser la
  question** correspondante, un point à la fois, jusqu'à ce que l'objet soit **complet**. **Ne jamais
  se contenter d'afficher** « il manque X » sans poser la question.
- **Ne pas conclure** (créer le ticket, refermer l'objet) tant qu'un point obligatoire reste ouvert.

## Validation d'un geste qui engage
Une **cause racine** d'anomalie, un **plan** d'évolution avant le code, une **requalification** :
restituer **en prose** (pas de tableau), demander la validation, appliquer les corrections, et ne
marquer l'étape franchie qu'**après** le geste humain. **L'IA propose, l'humain tranche.**

## Écritures externes (Linear)
Créer un ticket, changer un état, cocher une case, déposer un commentaire = **effets visibles vers
l'extérieur**. Toujours **confirmer avant d'écrire** ; ne jamais se fier à une simple déduction.
Seule exception assumée : une **requalification automatique** découle d'un constat technique clair
(le code est conforme à la spec) — le skill ferme et trace, mais **ne décide pas** du périmètre à la
place du PO.

## Langue
Tout en **français** (questions, options, restitutions). Seuls les identifiants/valeurs machine et
noms de format (SpecKit, `spec.md`, `/speckit.*`, `feature:<id>`) restent tels quels.
