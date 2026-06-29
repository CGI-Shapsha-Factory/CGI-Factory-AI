# Catalogue des états & interactions clavier

Référence lue par le skill `designer-atelier` (composants & états). Deux familles d'états : **états
de composant** (interactifs) et **états d'écran** (data-driven).

## États de composant (interactifs)
| État | Quand | À définir |
|------|-------|-----------|
| default | repos | rendu nominal |
| hover | survol pointeur | indice visuel |
| focus | focus clavier | **anneau visible, non masqué** (WCAG 2.2, 2.4.11/2.4.13) |
| active / pressed | pression | retour immédiat |
| disabled | indisponible | non focusable ou `aria-disabled`, contraste informatif |
| loading | action en cours | `aria-busy`, indicateur |
| selected / checked | sélection | `aria-selected` / `aria-checked` |
| error | saisie invalide | message lié (`aria-describedby`), `aria-invalid` |
| empty | aucune donnée | état vide explicite |

## États d'écran (UI Stack)
initial/vide · chargement · partiel · **erreur** · idéal/succès — tout écran data-driven
doit traiter ces cinq états.

## Interaction clavier (WAI-ARIA APG — patterns courants)
| Composant | Clavier attendu |
|-----------|-----------------|
| Bouton | Entrée / Espace active |
| Lien | Entrée active |
| Champ texte | saisie ; Tab pour sortir |
| Case à cocher / interrupteur | Espace bascule |
| Boutons radio | flèches naviguent dans le groupe |
| Select / combobox | flèches, Entrée, Échap ; `aria-expanded` |
| Onglets | flèches changent d'onglet ; Tab vers le panneau |
| Menu | flèches, Entrée, Échap |
| Modale (dialog) | **piège de focus**, Échap ferme, focus restitué à l'ouvrant |
| Accordéon | Entrée/Espace plie/déplie ; `aria-expanded` |

> Source des modèles : WAI-ARIA Authoring Practices Guide (APG). Tout composant custom
> reproduit le pattern APG correspondant (rôles, états ARIA, clavier). Les éléments natifs
> HTML (`<button>`, `<a>`, `<input>`) sont préférés quand ils existent.
