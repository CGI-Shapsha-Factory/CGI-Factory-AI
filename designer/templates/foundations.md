# Fondations visuelles

<!-- Public visé : designers + Claude Code. Les VALEURS exécutables vivent dans
     design-system/tokens.json (format DTCG) ; ce document explique et justifie les choix,
     avec les ratios de contraste. La source de vérité des valeurs = les tokens. -->
<!-- Remplir chaque [placeholder]. Marqueurs [À VALIDER]/[À CHIFFRER]. (src: …). -->

> Toutes les valeurs ci-dessous correspondent à un token DTCG de `design-system/tokens.json`.
> Extraites de la maquette validée (src: maquette) sauf indication contraire.

## Couleur
- **Tiers** : primitive (palette brute) → semantic (rôles) → component (optionnel).
- **Rôles sémantiques** : surface, sur-surface (texte/icône), bordure, marque (brand),
  retour (succès / avertissement / erreur / info).
- **Contraste (WCAG 2.2 AA)** : texte normal ≥ 4,5:1 ; grand texte & éléments d'UI ≥ 3:1.

| Token sémantique | Primitive | Usage | Paire de contraste | Ratio |
|------------------|-----------|-------|--------------------|-------|
| color.text.default | [...] | texte courant | sur color.surface.default | [≥ 4,5:1] [À CHIFFRER] |
| color.brand.default | [...] | actions primaires | sur [...] | [À CHIFFRER] |

## Typographie
- **Familles** : [police texte] / [police titres] — [licence ? À VALIDER].
- **Échelle** (rôles) :

| Rôle | Taille | Interligne | Graisse | Token |
|------|--------|-----------|---------|-------|
| display | [...] | [...] | [...] | typography.display |
| heading | [...] | [...] | [...] | typography.heading |
| body | [...] | [...] | [...] | typography.body |
| caption | [...] | [...] | [...] | typography.caption |

## Espacement & grille
- **Base** : [4 / 8 px] — échelle [4, 8, 12, 16, 24, 32, 48, …] (tokens dimension.space.*).
- **Grille / conteneur** : [colonnes, gouttières, largeur max].

## Élévation (ombres) & rayons
| Niveau | Ombre | Usage | Token |
|--------|-------|-------|-------|
| 0 / 1 / 2 | [...] | [cartes, menus, modales] | elevation.* |
| Rayons | [...] | [boutons, cartes] | radius.* |

## Mouvement
- **Durées** : [rapide / standard / lent] (duration.*). **Easings** : [...] (easing.*).
- **Respecter `prefers-reduced-motion`** : [alternative sans animation].

## Iconographie
- **Set** : [nom / source / licence — À VALIDER]. **Grille** : [24 px]. **Style** : [trait / plein].

## Points de rupture (responsive)
| Nom | Largeur min | Cible |
|-----|-------------|-------|
| mobile / tablet / desktop | [...] | [...] |

<!-- Toute valeur sans trace dans la maquette reste [À VALIDER]. -->
