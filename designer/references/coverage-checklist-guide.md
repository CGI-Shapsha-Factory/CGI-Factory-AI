# Référence — la checklist de couverture (le cœur du plugin)

Définition canonique de la checklist déroulée par `/designer:designer`. **Le plugin applique des règles
établies du domaine, il ne les invente pas** : NN/g pour les états d'écran et les règles d'erreur, WCAG
pour l'accessibilité.

## Principe
La checklist tient ensemble **deux natures** qu'on sépare souvent à tort :
- le **versant expérience** (purement fonctionnel) qu'un développeur néglige → tiré de **l'humain** ;
- le **versant technique qui se voit** (erreurs, async, rôles…) qu'un designer oublie → tiré des
  **handoffs** (Architecte, section *Décisions à impact design*).
La force du plugin = **forcer la couverture des deux**.

## Colonne Origine & statuts
- **C** déduit du handoff Cadrage · **A** déduit du handoff Architecte · **H** co-construit avec l'humain.
- Statut : `open` (non couvert, bloquant) → `deduced` (rempli d'un handoff) | `decided` (tranché H) |
  `sans_objet` (sans objet, marqué pas forcé). **Aucun `open`** quand la couverture est suffisante.

## Calibrage (anti-usine-à-gaz)
Commencer petit : tokens essentiels, composants de base, patterns clés. **Étendre seulement** quand un
besoin réel apparaît. Ne pas créer de tokens ni de composants par anticipation. La checklist est un **filet
de couverture sur ce qui compte**, pas une obligation de tout remplir.

## Les 3 blocs (résumé — détail dans `templates/coverage-checklist.md`)
- **Fondation** : F1 tokens essentiels · F2 thématisation · F3 composants de base + états · F4 mouvement.
- **Expérience** (H tranche) : E1 parcours · E2 états d'écran · E3 états vides utiles · E4 hiérarchie/densité
  · E5 feedback/confirmation · E6 microcopie.
- **Technique qui se voit** (découle de l'archi) : T1 erreurs · T2 chargement/async · T3 listes/pagination ·
  T4 identité/rôles · T5 navigation/routage · T6 accessibilité · T7 responsive · T8 i18n · T9 budget perf.

## Ancrages (le plugin applique)
- **États canoniques d'écran** : chargement, vide, erreur, contenu/succès — distinguer 1re utilisation et
  aucun résultat. *(NN/g — Nielsen Norman Group.)*
- **Règles d'erreur** : explicite, humaine, polie, précise, constructive ; **validation à la sortie du
  champ** (pas pendant la frappe) ; message actionnable ; erreurs identifiées en texte (pas par la couleur
  seule) ; focus sur le 1er champ en erreur. *(NN/g + WCAG.)*
- **Accessibilité** : niveau visé fixé par l'architecte (ex. WCAG 2.2 AA) → contraste, focus visible,
  cibles tactiles, navigation clavier. *(WCAG ; détail composant : `states-catalog.md`.)*

## Ce qui n'est PAS dans la checklist
Le design system lui-même (tokens/composants concrets) : **produit par Claude Design**, pas par le plugin.
La checklist garantit la **couverture** ; le prompt traduit cette couverture en consignes pour Claude Design.
