# Carte de couplage — État partagé et parallélisme

> Carte de couplage produite par `cadrage-decoupage`, aux côtés du découpage
> fonctionnel (`spec-index.md`). C'est une **hypothèse** de couplage, matière
> d'entrée pour la décision de revue de couplage : elle rend les points d'attention
> visibles, elle ne décide pas. Elle est **à confronter à l'architecture**, qui fige le
> couplage réel. **Hypothèse — revue de couplage pas encore faite.**

## État partagé entre features
Les données, entités ou état manipulés par plus d'une feature. Chaque état partagé
est un couplage à surveiller : un changement dans l'un peut casser
l'autre.

| état partagé | features concernées | nature du couplage | attention |
|--------------|--------------------|------------------------|-----------|
| <entité / donnée> | 001, 003 | lecture / écriture concurrente | … |

## Couplages directs
Liens forts entre features au-delà d'une simple dépendance d'ordre : contrat
d'interface, sémantique partagée, invariant commun.

| feature A | feature B | type de couplage | conséquence en cas de désynchronisation |
|-----------|-----------|------------------|----------------------------|
| 002 | 003 | … | … |

## Vue parallélisme
Ce qui peut avancer en même temps, ce qui doit attendre.

- **Peut avancer en parallèle :** <groupes de features sans couplage bloquant>
- **Doit attendre :** <features dépendantes, avec l'amont qui les débloque>
- **Chemin critique :** <la plus longue chaîne de dépendances>

## Walking skeleton
Défini dans le `spec-index.md` (source unique). Ici, seuls les **couplages que
le walking skeleton expose** sont à arbitrer en premier.

<!--
Cette carte est l'hypothèse de couplage, puis le support des décisions de revue
de couplage. Les arbitrages se font EN SESSION avec l'utilisateur et leurs
résultats sont écrits EN PLACE dans cette carte (état partagé / couplages /
parallélisme mis à jour). Aucun journal d'arbitrage séparé, aucun point ouvert
persisté, aucun marqueur `[À VALIDER]`. Pas de provenance écrite.
-->
