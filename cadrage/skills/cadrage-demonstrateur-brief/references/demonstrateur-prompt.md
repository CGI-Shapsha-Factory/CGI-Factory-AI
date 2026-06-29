# Gabarit — Prompt Claude Design du démonstrateur

> Gabarit statique lu par `cadrage-demonstrateur-brief`. **Cet en-tête reste dans le
> plugin** ; le fichier sauvegardé sous `factory-prompts/…/prompt.md` ne contient
> **que le corps du prompt** (le bloc de code ci-dessous, rempli), sans titre ni
> métadonnée — cf. `references/ux-conventions.md`.
>
> Le modèle qui génère le prompt **remplace tous les `<…>`** par le contenu réel tiré
> du `product-brief.md`, du `spec-index.md` et du `glossaire.md`. Le prompt doit être
> **auto-portant** : Claude Design n'a aucun contexte projet, tout doit être dans le
> prompt. **Aucune `(src:)` dans le prompt sauvegardé.**

## Variante INITIAL

```
Crée une maquette web interactive, propre et professionnelle, pour <produit en 1 phrase>.
Objectif : valider la direction produit avec le client — elle doit paraître crédible et
finie, comme un vrai produit, pas un wireframe.

Contexte produit
- Problème résolu : <le problème, 1–2 phrases>.
- Utilisateurs : <profils / rôles principaux>.
- Valeur : <ce que l'utilisateur gagne>.

Écrans à produire (un par parcours clé), navigables entre eux :
1. <Écran 1 — nom + ce qu'on y fait>
2. <Écran 2 — nom + ce qu'on y fait>
3. <Écran 3 — nom + ce qu'on y fait>
(reprendre les parcours clés du découpage ; 3 à 6 écrans, pas plus)

Pour chaque écran
- Une vraie mise en page : navigation persistante, en-tête, contenu structuré, hiérarchie
  visuelle claire (titres, sections, espacements généreux et réguliers).
- Du contenu réaliste et plausible du domaine (noms, libellés, données crédibles) —
  jamais de « lorem ipsum » ni de texte bouché.
- Sur les écrans clés, montrer les états utiles : contenu chargé, état vide (avec message
  + action), et un cas d'erreur ou de chargement si pertinent.

Style
- Direction de marque : violet #5336AB en primaire, esthétique conseil premium, sobre et
  aérée, beaucoup de blanc, typographie sans-serif lisible, coins arrondis discrets,
  ombres légères. Aucun emoji.
- Cohérent d'un écran à l'autre : mêmes composants, mêmes espacements, même palette.
- Responsive : lisible et utilisable sur desktop et mobile.

Rendu attendu : une maquette soignée et convaincante qui donne à voir le produit fini et
sa valeur, suffisante pour décider de la direction. Tu peux poser des hypothèses
raisonnables pour combler un manque, mais reste fidèle à l'objectif décrit.
```

## Variante ADAPTATIF (delta)

```
À partir de la maquette existante <référence de la maquette vX>, applique uniquement les
changements suivants, en préservant tout le reste (écrans, style, navigation déjà validés).

Changements demandés
- <changement 1 — écran concerné + ce qui change>
- <changement 2 — …>
- <changement 3 — …>

Contraintes
- Ne régénère pas à blanc : conserve la mise en page, la palette violet #5336AB et les
  composants existants.
- Garde la cohérence visuelle et le niveau de finition professionnel.
- Reste borné aux changements ci-dessus ; ne touche pas à ce qui a été validé.
```
