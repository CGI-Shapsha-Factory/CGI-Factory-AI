# Scénario rejouable : TC-[feature]-[NNN] - [intitulé court]

<!-- Généré par `rapport-de-recette` dans `validation-out/<feature>/scenarios/TC-<feature>-<NNN>.md`
     pour chaque cas passé OK. C'est le capital de NON-RÉGRESSION de la feature : le déroulé
     EFFECTIF (tel que joué, pas tel que prévu), en langage naturel auto-portant, rejouable par
     n'importe quel outil (extension Chrome, Playwright, Cowork). Cibler les éléments par leur
     libellé visible, jamais par un sélecteur technique.
     TOUT EST EN TABLES (forme : section 4bis de `ux-conventions.md` - une ligne de séparation
     entre chaque ligne de données, cellule vide = "-"). Un fichier par cas OK, donc il y en a
     beaucoup : il doit rester court et se lire d'un coup d'oeil. Contenu seul : aucune
     provenance, aucun horodatage. -->

## Identité

| Ce que le scénario prouve | Source | Préconditions et données |
|---|---|---|
| (le critère d'acceptation couvert, reformulé en une phrase française qui se lit sans rouvrir la spécification) | (référence compacte, ex. "US1 sc.1 / FR-003") | (l'état de départ exact et les données de test du passage OK : compte, jeu de données, page de départ) |

## Déroulé (tel que joué)

<!-- Une ligne par étape réellement jouée, dans l'ordre, reprise du déroulé effectif des
     résultats d'exécution. "Résultat observable" ne se remplit que pour les étapes qui
     produisent quelque chose de vérifiable ; sinon un tiret. La DERNIÈRE ligne porte le
     résultat qui fait passer le scénario au vert. -->

| # | Action | Résultat observable |
|---|---|---|
| 1 | (action en langage naturel : ouvrir la page ..., cliquer sur le bouton "...", saisir "..." dans le champ "...") | `-` |
|---|---|---|
| 2 | (...) | (ce qui apparait à l'écran, factuel) |

## Rejouer ce scénario

Ce scénario se rejoue tel quel contre l'environnement de recette, avec n'importe quel outil
d'exécution navigateur. Si une étape ne trouve plus son élément par le libellé indiqué,
c'est soit une évolution volontaire de l'écran (mettre le scénario à jour), soit une
régression (ouvrir une anomalie via `/maintenance:creation-anomalie`).
