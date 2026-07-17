# Découpage fonctionnel : use cases / capacités

> ⚠️ **PROPOSITION FONCTIONNELLE - revue de couplage pas encore faite**
> Découpage **par valeur**, à partir de la seule vision produit (le savoir du PO),
> **sans stack ni architecture**. Les **IDs et l'ordre sont provisoires** et la
> carte de couplage n'est qu'une **hypothèse**. La **liste numérotée et séquencée des features,
> ainsi que le walking skeleton, se figent en sortie d'architecture** (convergence :
> l'architecture confronte ce découpage aux contrats et au squelette
> technique). Porte humaine à deux niveaux côté assembleur (entrées + sortie
> finale). Ici, `cadrage-decoupage` propose, il ne décide jamais.

Méthode : trois passes (surface, parcours, risque). Chaque use case est une
**tranche verticale de valeur** (jamais une couche technique). Calibrage visant
5 à 10 use cases. Ordre **par importance/valeur**, non par séquence technique.

## Use cases (proposition fonctionnelle)

| id  | nom | frontière IN | frontière OUT | activités utilisateur couvertes | couplage suspecté (hypothèse) |
|-----|------|-------------|--------------|----------------------------------|----------------------------------|
| UC1 | <use case> | ... | ... | ... | - |
| UC2 | <use case> | ... | ... | ... | UC1 ? |
| UC3 | <use case> | ... | ... | ... | UC1 ? |

> Une ligne par use case. `couplage suspecté` est une **hypothèse** à confronter
> à l'architecture, pas un ordre de construction. Les IDs (`UC...`) sont provisoires :
> la numérotation finale `feature 00X` est fixée par l'architecture. **Aucune
> notion de MVP**, **aucune provenance écrite** (pas de `(src:)`). Les frontières
> non tranchées par la matière se tranchent **en session** lors de la revue de
> couplage, pas marquées `[À VALIDER]`.

## Walking skeleton (candidat)
Use case **candidat** pour la première tranche bout-en-bout. Ce n'est qu'une
hypothèse : le walking skeleton **définitif** est désigné à l'architecture (il
dérisque la stack, c'est donc une affaire technique).

## Couverture du périmètre IN
Cartographie de **chaque capacité du périmètre IN** (product-brief §4) vers le ou les use cases
qui la couvrent. Une capacité **non couverte** est un trou **bloquant**.

| capacité IN (product-brief §4) | couverte par |
|----------------------------------|------------|
| <capacité> | UC1, UC3 |
| <capacité> | <à trancher en session> |

<!--
VÉRIFICATION (cadrage-decoupage) : chaque use case est une tranche verticale
de valeur, avec une frontière et un couplage suspecté (hypothèse) ; la coupling-map est
produite ; la couverture du périmètre IN est complète (toute capacité non couverte
se tranche EN SESSION) ; aucune notion de MVP ; aucune provenance écrite ; aucun
`[À VALIDER]` persisté. arbitrated passe à vrai après la revue de couplage en session.
La numérotation/séquençage final et le walking skeleton relèvent de l'architecture.
-->
