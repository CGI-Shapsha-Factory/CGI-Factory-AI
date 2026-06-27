# Glossaire — Langage ubiquitaire

> Document de travail (destiné à Notion). Construit et maintenu par
> `cadrage-glossaire`. C'est le garde-fou contre la dérive sémantique : les termes
> dans **les mots du client**, jamais reformulés en jargon technique. Chaque
> terme est sourcé. Aucun terme dupliqué avec deux définitions divergentes.

## Termes

| terme | définition (mots du client) | source | structurant | statut |
|------|-----------------------------|--------|------------|--------|
| <terme> | <définition fidèle au client> | <transcript / page : marqueur> | oui \| non | proposed \| validated |

> `statut` : `proposed` à la captation, `validated` après confirmation par le client /
> l'expert métier.
> `structurant` : un **terme structurant** est mobilisé par la vision produit
> (`product-brief.md`) **ou** sert de nom / frontière d'un use case dans le découpage
> (`spec-index.md`). Règle bloquante : le glossaire compte comme validé **si et seulement
> si chaque terme marqué `structurant = oui` est au statut `validated`** (les termes
> non structurants ne le bloquent pas).

## Ambiguïtés et conflits signalés
Termes employés avec des sens différents selon les interlocuteurs, ou définitions
en tension. À trancher avec le client. Chaque entrée pointe vers les sources en
désaccord.

- **<terme>** — sens A (source) vs sens B (source). `[À VALIDER]`

## Termes candidats non encore définis
Termes métier repérés dans la matière source mais sans définition captée. `[À VALIDER]`,
à clarifier en atelier.

<!--
PORTE DE SORTIE (cadrage-glossaire) : chaque terme a une définition ET une
source ; les ambiguïtés / conflits sont signalés ; aucune définition divergente
dupliquée (contrôle de dérive). Marquer, ne pas inventer : aucune définition
fabriquée hors source.
-->
