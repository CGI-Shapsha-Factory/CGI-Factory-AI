# Résultats d'exécution : [intitulé de la feature] ([numéro de registre]) - [JJ-MM]

<!-- Généré par `execution-validation` dans
     `validation-out/<feature>/resultats/execution-<JJ-MM>.md`. UN FICHIER PAR EXÉCUTION : si le
     nom du jour existe déjà, suffixer `-2`, `-3`... - on n'écrase JAMAIS une exécution passée.
     TOUT EST EN TABLES, et la synthèse est EN HAUT : le testeur doit savoir en deux secondes ce
     qui passe et ce qui casse, sans dérouler le fichier. Forme des tables (séparateurs entre
     lignes, étapes en <br>, cellule vide = "-") : section 4bis de `ux-conventions.md`.
     UNE LIGNE = UN CAS, dans l'ordre du plan, aucun cas omis. L'IA CONSTATE, elle ne juge pas la
     livraison : les verdicts de cas sont des faits, le verdict de recette appartient au testeur
     (il se pose au rapport, pas ici). Contenu seul : aucune provenance, aucun horodatage, aucun
     nom de personne. Ce fichier est le CONTRAT DE SORTIE COMMUN aux trois voies d'exécution
     (extension Chrome, Playwright, mission Cowork) : le rapport de recette le lit sans savoir
     qui a exécuté. -->

## Contexte d'exécution

| Adresse testée | Outil | Plan joué | Cas joués |
|---|---|---|---|
| (l'URL de l'environnement de recette) | (extension Chrome / Playwright / Claude Cowork + extension Chrome) | `validation-out/[feature]/plan-de-test.md` | (nombre) |

## Synthèse

<!-- Trois lignes, toujours les trois même à zéro. La colonne "Cas concernés" liste les
     identifiants (plages autorisées quand ils se suivent, ex. "TC-001-001 a TC-001-008"), ou
     "-" si aucun. C'est la table qu'on lit en premier. -->

| Verdict | Nombre | Cas concernés |
|---|---|---|
| OK | (n) | (les identifiants, ou `-`) |
|---|---|---|
| KO | (n) | (les identifiants, ou `-`) |
|---|---|---|
| NON TESTABLE | (n) | (les identifiants, ou `-`) |

## Résultats par cas

<!-- Une ligne par cas du plan, dans l'ordre, AUCUN cas omis - y compris les NON TESTABLE.
     "Déroulé effectif" = les étapes RÉELLEMENT jouées (pas celles prévues au plan), numérotées
     et séparées par <br> : c'est la matière première des scénarios rejouables que le rapport
     génère à partir des cas OK, elle est donc requise même quand le cas passe.
     "Constaté" est UNE PHRASE factuelle (ce qui a été observé), sans jugement de valeur. Le
     détail d'un échec (attendu vs constaté, console, réseau) ne va PAS ici : il va dans la
     table "Écarts", pour que celle-ci reste scannable. -->

| Cas | Intitulé | Verdict | Déroulé effectif | Constaté | Preuve |
|---|---|---|---|---|---|
| TC-[numéro]-001 | (l'intitulé du cas, repris du plan) | OK | 1. (action réellement jouée)<br>2. (...) | (ce qui a été observé, factuel) | `preuves/TC-[numéro]-001-1.png` |
|---|---|---|---|---|---|
| TC-[numéro]-002 | (...) | KO | 1. (...)<br>2. (...) | (ce qui a été observé) | `preuves/TC-[numéro]-002-1.png` |

## Écarts (KO et NON TESTABLE)

<!-- Uniquement les cas dont le verdict n'est pas OK. C'est ici que vit le diagnostic : l'attendu
     du plan, le constaté factuel qui le contredit, et ce que la console et le réseau montrent
     d'anormal. Pour un NON TESTABLE, "Attendu" porte le critère tel qu'écrit et "Constaté" la
     RAISON de la non-testabilité (ambigu, non observable, donnée manquante) - jamais une
     interprétation du critère.
     Si tous les cas sont OK : SUPPRIMER cette table et écrire à la place
     "Aucun - tous les cas sont OK." -->

| Cas | Attendu | Constaté | Console et réseau |
|---|---|---|---|
| TC-[numéro]-002 | (le résultat attendu, repris du plan) | (ce qui se produit réellement, factuel et détaillé) | (erreurs de console, requêtes en échec ; `-` si rien d'anormal) |
