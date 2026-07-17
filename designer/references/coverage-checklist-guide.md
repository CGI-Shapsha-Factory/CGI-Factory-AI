# Référence : la checklist de couverture (le cœur du plugin)

Définition canonique de la checklist déroulée par `/designer:designer-atelier`. **Le plugin applique des règles
établies du domaine, il ne les invente pas** : NN/g pour les états d'écran et les règles d'erreur, WCAG
pour l'accessibilité.

## Principe
La checklist tient ensemble **deux natures** qu'on sépare souvent à tort :
- le **versant expérience** (purement fonctionnel) qu'un développeur néglige -> tiré de **l'humain** ;
- le **versant technique qui se voit** (erreurs, async, rôles...) qu'un designer oublie -> tiré des
  **handoffs** (Architecte, section *Décisions à impact design*).
La force du plugin = **forcer la couverture des deux**.

## Colonne Origine & statuts
- **C** déduit du handoff Cadrage · **A** déduit du handoff Architecte · **H** co-construit avec l'humain.
- **Statut montré à l'utilisateur** : **validé** (couvert) · **à traiter** (non couvert, bloquant) ·
  **sans objet** (ne s'applique pas). **Aucun item "à traiter"** quand la couverture est suffisante.
- *En interne*, le manifeste garde un statut plus fin - `open` -> `deduced` (rempli d'un handoff) |
  `decided` (tranché H) | `sans_objet` - mais l'affichage se réduit aux trois mots ci-dessus, et **chaque
  item se désigne par sa phrase en clair, jamais par un code** (`F1`/`E1`/`T1`... = clés internes).

## Calibrage (anti-usine-à-gaz)
Commencer petit : tokens essentiels, composants de base, patterns clés. **Étendre seulement** quand un
besoin réel apparaît. Ne pas créer de tokens ni de composants par anticipation. La checklist est un **filet
de couverture sur ce qui compte**, pas une obligation de tout remplir.

## Les 3 blocs (résumé : phrases complètes dans `templates/coverage-checklist.md`)
- **Fondation** : la palette/typo/espacements de base · les thèmes d'affichage · les composants de base
  avec tous leurs états · les animations et transitions.
- **Expérience** (H tranche) : chaque parcours clé de bout en bout · les états de chaque écran · les écrans
  sans données (message + action) · la hiérarchie et la densité · les retours et confirmations après action ·
  le ton des textes de l'interface.
- **Technique qui se voit** (découle de l'archi) : l'affichage des erreurs · les temps d'attente et le
  chargement · les listes/tableaux et leur pagination · l'identité et les droits · la navigation et
  l'organisation de l'information · le socle d'accessibilité · l'adaptation aux écrans · la prise en charge
  de plusieurs langues · le budget de performance.

## Ancrages (le plugin applique)
- **États canoniques d'écran** : chargement, vide, erreur, contenu/succès - distinguer 1re utilisation et
  aucun résultat. *(NN/g - Nielsen Norman Group.)*
- **Règles d'erreur** : explicite, humaine, polie, précise, constructive ; **validation à la sortie du
  champ** (pas pendant la frappe) ; message actionnable ; erreurs identifiées en texte (pas par la couleur
  seule) ; focus sur le 1er champ en erreur. *(NN/g + WCAG.)*
- **Accessibilité** : niveau visé fixé par l'architecte (ex. WCAG 2.2 AA) -> contraste, focus visible,
  cibles tactiles, navigation clavier. *(WCAG ; détail composant : `states-catalog.md`.)*

## Ce qui n'est PAS dans la checklist
Le design system lui-même (tokens/composants concrets) : **produit par Claude Design**, pas par le plugin.
La checklist garantit la **couverture** ; le prompt traduit cette couverture en consignes pour Claude Design.
