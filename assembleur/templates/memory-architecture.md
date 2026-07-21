# Architecture : stack, composants, décisions

<!-- Fichier mémoire (.claude/memory/architecture.md), lu par Claude au besoin. Digest du
     contrat technique pour la fabrication. Contenu seul. -->

## Stack
[Langages, frameworks, base de données, style d'API - la matrice composant × techno en bref.]

## Composants
[Les composants du système et leur rôle en une phrase chacun, par leur nom en clair. Le contrat
complet de chaque composant (interfaces exposées/consommées, "NON responsable de", contraintes
clés) vit dans `architecte-out/composants.md` - à relire avant de créer ou modifier un composant.]

## Décisions structurantes (ADR)
[Les décisions d'architecture non négociables, une ligne par décision : quoi + pourquoi. Le texte
complet de chaque décision (options considérées, conséquences, déclencheur de revue) vit dans
`architecte-out/decisions/ADR-*.md`.]

## Conventions
[Pointeur vers `conventions/` (style/format/nommage) + standards non-formatage clés. Le détail des
standards (erreurs, logging, sécurité, tests, API, données, git) vit dans
`architecte-out/standards-ingenierie.md` - ce fichier fait foi.]

## Tests
[Stratégie : frameworks par langage ; unitaires par règle métier (passant/échec/limite) ; intégration
avec dépendances mockées ; **tests écrits avec le code** ; garde-fous hooks + pre-commit.]

## Cibles de qualité
[Les attributs de qualité prioritaires avec leur cible chiffrée. Les scénarios de qualité testables
en 6 parties (source du stimulus, stimulus, environnement, artefact, réponse, mesure) vivent dans
`architecte-out/facteurs-et-qualite.md`.]
