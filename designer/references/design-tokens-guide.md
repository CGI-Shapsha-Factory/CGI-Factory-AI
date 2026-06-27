# Guide — tokens de design (format DTCG)

Référence lue par le skill `designer` (étapes fondations & livraison). Les tokens sont
écrits dans `design-system/tokens.json` au **format DTCG** (Design Tokens Community Group —
première version *stable* 2025.10, format vendor-neutral consommé par Style Dictionary,
Figma, Tokens Studio…).

## Format DTCG (l'essentiel)
- Fichier JSON ; extension `.tokens.json` ou `.json` ; un token = un objet avec :
  - `$value` — la valeur,
  - `$type` — le type (`color`, `dimension`, `fontFamily`, `fontWeight`, `duration`,
    `cubicBezier`, `shadow`, `number`, …),
  - `$description` — optionnel, lisible.
- Les **groupes** peuvent porter `$type` (hérité par les tokens enfants).
- **Alias** : une valeur peut référencer un autre token via `"{chemin.du.token}"`.

```json
{
  "primitive": {
    "color": { "$type": "color", "blue-600": { "$value": "#2563eb" } }
  },
  "semantic": {
    "color": { "$type": "color", "brand": { "default": { "$value": "{primitive.color.blue-600}" } } }
  }
}
```

## Trois tiers (recommandé)
1. **primitive** — valeurs brutes (palette, échelle typo, échelle d'espacement). Sans sens
   métier.
2. **semantic** — rôles (`color.surface`, `color.text`, `color.border`, `color.brand`,
   `color.feedback.*`, rôles typographiques, rôles d'espacement). **Les composants ne
   référencent que ce tier.**
3. **component** — tokens spécifiques à un composant (optionnel ; alias vers le semantic).

## Thèmes / modes
- Thème sombre = un **jeu d'alias** alternatif sur le tier semantic (les primitives ne
  changent pas). Gérer via fichiers séparés ou `$extensions` selon l'outil retenu.

## Livraison (« exécutable »)
- **Style Dictionary** transforme `tokens.json` (DTCG) en sorties plateforme : variables
  CSS, thème JS/TS, iOS/Android. Config d'exemple :
  `references/design-system/style-dictionary.config.example.json`.
- Le format de livraison concret est choisi selon le front-end de l'architecte (variables
  CSS par défaut ; preset Tailwind ; thème typé). **Fallback** : variables CSS universelles.

> Règle : **aucune valeur de couleur/taille codée en dur** dans les composants — tout passe
> par un token sémantique. Les valeurs proviennent de la maquette validée `(src: maquette)`.
