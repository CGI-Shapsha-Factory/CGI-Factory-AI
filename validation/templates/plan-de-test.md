# Plan de test fonctionnel : [intitulé de la feature] ([numéro de registre])

<!-- Généré par `plan-de-validation` dans `validation-out/<feature>/plan-de-test.md`.
     TOUT EST EN TABLEAUX, et le plan doit rester court : un lecteur humain le scanne d'un
     coup d'oeil. UNE LIGNE = UN SCENARIO DE TEST, jamais deux : un critère qui porte
     plusieurs scénarios (sc.1, sc.2...) donne autant de lignes, chacune avec son propre
     identifiant TC-, ses préconditions, ses étapes et son résultat attendu. On ne regroupe
     jamais deux scénarios dans une cellule, on n'écrit jamais "voir le cas précédent".
     Le critère d'acceptation n'est JAMAIS recopié mot pour mot : la colonne "Source" porte
     la référence compacte (ex. "US1 sc.1 / FR-001"), la colonne "Ce qui est vérifié" porte
     une PHRASE en français. Jamais l'inverse : une référence nue ne dit rien au testeur.
     Un critère non testable est marqué à clarifier avec sa raison, JAMAIS interprété, et
     vit uniquement dans la table "Critères à clarifier" (pas de ligne vide ailleurs).
     Le plan est AUTO-PORTANT : un exécuteur qui n'a que ce fichier (Cowork, une autre
     session) doit pouvoir tout jouer. Ne rien inventer : les données de test viennent du
     testeur (boucle interactive), une donnée absente s'omet.
     FORME DES TABLES (séparateur `|---|` entre chaque ligne de données, étapes en <br>,
     cellule vide = "-") : section 4bis de `ux-conventions.md`. -->

## Feature

(Une ou deux lignes : l'intitulé de la feature suivi de son numéro de registre entre
parenthèses, ex. "la recherche en langage naturel (001)", et ce qu'elle apporte. Ticket
Linear de la feature : identifiant + lien si connus.)

## Environnement de recette

- **Adresse** : (l'URL de l'application déployée à tester)
- **Point d'entrée** : (la page ou l'écran de départ des tests, si différent de l'adresse)

## Pré-requis et données de test

(Tout ce qu'il faut avant de jouer le premier cas : comptes de test avec leur rôle, jeu de
données à l'état initial attendu, préparations manuelles éventuelles. Uniquement des données
de test fournies par le testeur - jamais de données réelles, jamais de valeur inventée.)

## Vue d'ensemble

<!-- Une ligne par cas, TOUS les cas (testables et à clarifier), dans l'ordre de jeu.
     "Ce qui est vérifié" est une phrase française qui se lit sans rouvrir la spécification. -->

| Cas | Ce qui est vérifié | Statut |
|---|---|---|
| TC-[numéro]-001 | (la phrase : ce que le cas prouve, ex. "une note saisie apparait dans la liste et le compteur augmente") | testable |
|---|---|---|
| TC-[numéro]-002 | (...) | à clarifier |

## Déroulé des cas

<!-- Une sous-table par thème fonctionnel (une user story, ou un groupe de cas qui se jouent
     à la suite). Numérotation TC-<numéro>-001, -002... dans l'ordre des user stories, où
     <numéro> est le numéro de registre à 3 chiffres de la feature (ex. TC-001-003), jamais
     le nom complet du dossier specs/. Les étapes d'une cellule sont numérotées et séparées
     par <br> : une étape par ligne visible, jamais un pavé de texte. Les cas à clarifier
     n'apparaissent pas ici. -->

### [intitulé du thème, ex. "Créer et lister des notes"]

| Cas | Préconditions | Étapes | Résultat attendu | Source |
|---|---|---|---|---|
| TC-[numéro]-001 | (l'état de départ : compte connecté, données présentes...) | 1. (action concrète : ouvrir, cliquer, saisir)<br>2. (...) | (ce qui doit être observable à l'écran, factuel et vérifiable - jamais un jugement de valeur) | (référence compacte, ex. "US1 sc.1 / FR-001") |
|---|---|---|---|---|
| TC-[numéro]-002 | (...) | 1. (...)<br>2. (...) | (...) | (référence compacte) |

## Critères à clarifier

<!-- Les critères qui ne peuvent pas devenir un cas jouable, avec leur raison (ambigu, non
     observable dans le navigateur, donnée manquante). Ils sortiront NON TESTABLE à
     l'exécution. Si aucun, écrire sous le titre : "Aucun - tous les critères sont
     testables." et supprimer la table. -->

| Cas | Ce qui est demandé | Pourquoi ce n'est pas testable | Source |
|---|---|---|---|
| TC-[numéro]-0NN | (le critère reformulé en une phrase) | (la raison, factuelle) | (référence compacte) |
