# Plan de test fonctionnel : [intitulé de la feature] ([numéro de registre])

<!-- Généré par `plan-de-validation` dans `validation-out/<feature>/plan-de-test.md`.
     Un cas de test PAR critère d'acceptation de `specs/<feature>/spec.md`. Chaque cas cite son
     critère source (traçabilité du rapport). Un critère non testable est marqué A CLARIFIER
     avec sa raison, JAMAIS interprété. Le plan est AUTO-PORTANT : un exécuteur qui n'a que ce
     fichier (Cowork, une autre session) doit pouvoir tout jouer. Ne rien inventer : les données
     de test viennent du testeur (boucle interactive), une donnée absente s'omet. -->

## Feature

(L'intitulé de la feature suivi de son numéro de registre entre parenthèses, ex. "la recherche
en langage naturel (001)", et une ligne sur ce qu'elle apporte. Ticket Linear de la feature :
identifiant + lien si connus.)

## Environnement de recette

- **Adresse** : (l'URL de l'application déployée à tester)
- **Point d'entrée** : (la page ou l'écran de départ des tests, si différent de l'adresse)

## Pré-requis et données de test

(Tout ce qu'il faut avant de jouer le premier cas : comptes de test avec leur rôle, jeu de
données à l'état initial attendu, préparations manuelles éventuelles. Uniquement des données
de test fournies par le testeur - jamais de données réelles, jamais de valeur inventée.)

## Cas de test

<!-- Répéter le bloc ci-dessous pour chaque critère d'acceptation. Numérotation TC-<numéro>-001,
     -002... dans l'ordre des user stories, où <numéro> est le numéro de registre à 3 chiffres
     de la feature (ex. TC-001-003), jamais le nom complet du dossier specs/. -->

### TC-[numéro]-[NNN] - [intitulé court du cas]

- **Critère source** : (le critère d'acceptation tel qu'écrit dans la spécification : la user
  story ou l'exigence concernée (ex. FR-003, SC-001) + le scénario "Étant donné / quand /
  alors" cité)
- **Statut** : TESTABLE (ou : A CLARIFIER - avec la raison : ambigu, non observable dans le
  navigateur, donnée manquante)
- **Préconditions** : (l'état de départ : compte connecté, données présentes...)
- **Étapes** :
  1. (action concrète dans le navigateur : ouvrir, cliquer, saisir...)
  2. (...)
- **Résultat attendu** : (ce qui doit être observable à l'écran, factuel et vérifiable - jamais
  un jugement de valeur)

## Critères à clarifier

(Reprendre ici la liste des cas au statut A CLARIFIER avec leur raison, pour qu'un lecteur du
plan les voie d'un coup d'oeil. Si aucun : "Aucun - tous les critères sont testables.")
