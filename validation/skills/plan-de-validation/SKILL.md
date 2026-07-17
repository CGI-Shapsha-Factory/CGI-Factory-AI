---
name: plan-de-validation
description: Dérive le plan de test fonctionnel d'une feature livrée depuis les critères d'acceptation de sa spécification : un cas de test par critère, tracé, critère non testable marqué à clarifier.
---

# plan-de-validation

Cœur "traduction" de la validation fonctionnelle : lit la spécification d'une feature livrée
(`specs/<feature>/spec.md`) et en dérive le **plan de test fonctionnel** - un cas de test par
critère d'acceptation, traduit du "Étant donné / quand / alors" en scénario exécutable dans le
navigateur, tracé à son critère source. Les critères non testables sont **marqués à
clarifier**, jamais interprétés.

## Objectif
Produire `validation-out/<feature>/plan-de-test.md` : un plan **auto-portant** (un exécuteur
qui n'a que ce fichier peut tout jouer), **complet** (chaque critère de la spécification a son
cas), **honnête** (aucun critère flou n'est deviné), validé par le testeur avant exécution.

## Pré-requis (vérification silencieuse)
- `manifest.json` existe dans le dossier courant et contient le bloc de la validation ; sinon
  refuser en clair et renvoyer vers `/validation:validation-init`.
- La feature visée a sa spécification : `specs/<feature>/spec.md` existe. Sinon refuser en
  nommant le fichier manquant : la validation n'a pas d'objet tant que la feature n'est pas
  fabriquée via SpecKit.
- Rappel de frontière : la spécification est **lue, jamais écrite** (cf.
  `references/regles-validation.md`).

## Procédure

### Étape 1 : identifier la feature
Lister les features fabriquées (les dossiers de `specs/`), croiser avec le registre des
features et `assembleur-out/feature-map.md` s'ils sont disponibles (intitulés métier), et
demander au testeur laquelle passe en recette (une question, suggestion = la plus récente non
encore validée). La nommer par son intitulé complet suivi de sa référence, ex. "la recherche
en langage naturel (001)". Retrouver au passage son ticket `Feature` Linear (bloc `linear` du
manifeste + `list_issues({team, label Feature})`, jointure par le numéro en tête de titre) -
best-effort : si le MCP est muet, continuer sans lien Linear et le signaler.

### Étape 1bis : porte de régénération (avant tout travail)
Si `validation-out/<feature>/plan-de-test.md` existe déjà, poser **tout de suite** la
décision (avant la lecture et la boucle interactive, pour ne pas faire refaire tout le
travail au testeur avant de découvrir la question) : "repartir de zéro" (supprimer puis
regénérer) ou "garder les deux" (archiver l'existant sous
`validation-out/<feature>/_archives/plan-de-test-v<N>.md`, `N` = index croissant, puis
regénérer au nom canonique) - jamais d'écrasement sans choix explicite.

### Étape 2 : lire la spécification, inventorier les critères
Lire `specs/<feature>/spec.md` en entier et inventorier **tout ce qui est vérifiable** :
- les **scénarios d'acceptation** de chaque user story (Étant donné / quand / alors) ;
- les **exigences fonctionnelles** (`FR-xxx`) observables dans le navigateur ;
- les **critères de succès** (`SC-xxx`) mesurables à l'écran ;
- les **cas limites** (Edge Cases) énoncés.
Aucun critère n'est écarté en silence : ce qui ne devient pas un cas de test doit apparaître
comme "à clarifier" avec sa raison.

### Étape 3 : dériver un cas de test par critère
Pour chaque critère, un cas `TC-<numéro>-NNN` où `<numéro>` est le **numéro de registre à 3
chiffres** de la feature (ex. `TC-001-003` ; jamais le nom complet du dossier `specs/`),
numéroté dans l'ordre des user stories, selon le gabarit
`.factory/validation/plan-de-test.md` :
- **Critère source cité** (la traçabilité du rapport en dépend) ;
- le "Étant donné / quand / alors" traduit en **préconditions + étapes numérotées + résultat
  attendu observable** (des actions concrètes de navigateur : ouvrir, cliquer sur le bouton
  "...", saisir "..." ; un résultat factuel à l'écran, jamais un jugement) ;
- **critère non testable** (ambigu, non observable dans le navigateur, donnée manquante) :
  statut **A CLARIFIER** avec la raison - **ne jamais interpréter** (cf.
  `references/regles-validation.md`).

### Étape 4 : compléter les données de test (boucle interactive)
Le plan doit être auto-portant : demander au testeur, un point à la fois (cf.
`references/interactive-loop.md`), l'adresse de recette si elle manque au manifeste, les
comptes de test et leur rôle, l'état de données attendu, les préparations manuelles. Un point
laissé de côté est omis (le cas concerné passe A CLARIFIER si la donnée lui est
indispensable). **Jamais de valeur inventée.**

### Étape 5 : écrire le plan
Écrire le plan complet dans `validation-out/<feature>/plan-de-test.md` (la porte de
régénération a déjà été passée à l'étape 1bis si un plan existait).

### Étape 6 : relecture humaine + sort des critères à clarifier
Afficher le récapitulatif (un tableau court : critère source -> cas de test -> testable ou à
clarifier) et faire relire le plan par le testeur. Pour **chaque** critère à clarifier,
proposer (un par un) :
- **clarifier maintenant** : le testeur précise la lecture observable du critère ; elle
  s'écrit **dans le cas de test** (la spécification, elle, ne bouge pas) et le cas devient
  testable ;
- **tracer le point dans Linear** : orienter vers un ticket de suivi sur la feature ("Veux-tu
  créer un ticket Linear pour tracer ce point ?") - création seulement sur accord explicite,
  en sous-ticket du ticket Feature, **sans label de recette** (jamais `Anomalie`/`Evolution`,
  ni `Feature`/`Task` - cf. `references/regles-validation.md`, section Linear) ; si le flou
  révèle une spécification fausse ou incomplète, orienter plutôt vers
  `/recette:creation-evolution` (geste du PO) ;
- **laisser tel quel** : le cas reste A CLARIFIER dans le plan et sortira NON TESTABLE à
  l'exécution.
Le plan n'est bon pour exécution qu'après l'accord explicite du testeur.

## Vérification avant de conclure
Lancer le garde-fou déterministe et s'arrêter s'il échoue :
```bash
python <plugin>/scripts/check_validation.py manifest.json <feature>
```
(Il vérifie le terrain et, pour la feature, que le plan existe et que chaque cas cite son
critère source.)

## Règles invariantes
- **Un critère = un cas, cité.** Aucun critère écarté en silence, aucun cas sans source.
- **Jamais interpréter.** Un critère flou est marqué, discuté, ou tracé - jamais deviné.
- **La spécification est en lecture seule.** Toute clarification vit dans le plan ; tout
  changement de critère passe par la recette (évolution, geste PO).
- **Plan validé par l'humain** avant toute exécution.
- Manifeste silencieux, restitutions en prose, typographie humaine (cf.
  `references/ux-conventions.md`).

Étape suivante : `/validation:execution-validation` - jouer le plan dans le navigateur contre l'environnement de recette.
