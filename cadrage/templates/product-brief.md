# Product Brief — <Nom du produit>
Statut : draft | validated

> Document de travail (destiné à Notion). Synthèse de niveau produit, le quoi et
> le pourquoi. Aucune technologie. Produit par `cadrage-vision` à partir de
> `work/capture-brute.md`. **Traçabilité : chaque énoncé porte sa source
> `(src: <ref>)`**. Tout élément sans trace reste
> `[À VALIDER]`, jamais comblé.

## 1. Problème
Le problème que le produit résout, dans les mots du métier. Pourquoi il existe.

## 2. Objectif métier
Le résultat attendu du côté de l'organisation. Pourquoi on investit.

## 3. Parties prenantes et rôles
Qui porte le besoin, qui utilise, qui valide, qui est impacté. Le rôle de chacun.

## 4. Périmètre IN
Ce que le produit fait. Les principales capacités couvertes. Une capacité par ligne,
chacune avec sa source `(src: …)` — ces capacités sont confrontées à la couverture
du découpage (`spec-index.md`).

## 5. Hors périmètre OUT
Ce que le produit ne fait PAS, explicitement, pour prévenir la dérive de périmètre.
**Ne doit pas être vide** — c'est une porte de sortie du skill.

## 6. Contraintes
Contraintes captées : techniques, sécurité, réglementaires, intégration,
organisationnelles. Marquer `[À VALIDER]` celles seulement suspectées.

## 7. Critères de succès produit
Résultats traduits en métriques avec une cible chiffrée, côté usage et non code.
Marquer `[À CHIFFRER]` quand la cible n'a pas été captée en atelier.

## 8. Hypothèse produit initiale
L'hypothèse centrale du produit, **explicitement marquée** `[À ÉPROUVER]`.
Jamais présentée comme validée — elle est validée hors du plugin, par le démonstrateur
(Porte 1, direction produit).

## 9. Trous
Liste des éléments `[À VALIDER]` et `[NON COUVERT EN ATELIER]` du brief. Alimente
`cadrage-clarification`. Vide quand la vision est complète.

<!--
PORTE DE SORTIE (cadrage-vision) : toutes les sections présentes, OUT non vide,
critères de succès mesurables ou marqués `[À CHIFFRER]`, hypothèse marquée
`[À ÉPROUVER]`. vision_complete passe à vrai s'il n'y a pas de trou bloquant, si OUT n'est pas vide,
et si les critères de succès sont présents.
-->
