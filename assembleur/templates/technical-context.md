# Contexte technique : projet

<!-- Livrable de `assembleur-out/`. Mappe la section "Technical Context" du plan.md SpecKit,
     au niveau projet (les graines de feature en reprennent ce qui les concerne). Source :
     architecte (stack-technique, components, standards, facteurs-et-qualite). Contenu seul. -->

- **Langage / version** : [ex. Python 3.12]
- **Dépendances principales** : [frameworks, libs structurantes]
- **Stockage** : [base de données / fichiers / N/A]
- **Tests** : [framework par langage] - **écrits en même temps que le code** ; unitaires par règle
  métier (cas passant/échec/limite) ; intégration API/front/batch avec dépendances **mockées** ;
  garde-fous hooks + pre-commit
- **Plateforme cible** : [OS / runtime / cloud]
- **Type de projet** : [web / CLI / service / lib...]
- **Objectifs de performance** : [cibles chiffrées, ex. p95 < X ms à N utilisateurs]
- **Contraintes** : [latence, mémoire, hors-ligne, souveraineté...]
- **Échelle / périmètre** : [volumes utilisateurs / données estimés]

## Modèle de données
[Entités principales + relations/cardinalités (<- ERD architecte). Détail dans
`architecte-out/diagrammes.md` - qui porte aussi les diagrammes de contexte (systèmes externes),
de conteneurs, de flux des parcours critiques et de déploiement.]

## Déploiement / hébergement
[Cible d'hébergement, topologie de déploiement, responsable d'exploitation, budget infra,
disponibilité visée (<- `diagrammes.md` + `project-frame.md`). Réconcilier avec les cibles qualité
architecte - ne pas dupliquer, surfacer ce qui n'est pas déjà couvert.]

## Conventions
[Où vivent les règles de style/format/nommage (`conventions/`). Les standards non-formatage
(erreurs, logging, sécurité, tests, API, données, git) vivent dans
`architecte-out/standards-ingenierie.md` - les rappeler ici en bref, le fichier fait foi.]

## Cibles de qualité (drivers)
[Les scénarios de qualité testables - chacun avec une mesure observable et chiffrée.]
