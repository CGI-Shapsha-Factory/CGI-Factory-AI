# Checklist de couverture : design

> **Le cœur du plugin.** Outil de **couverture** (pas une bureaucratie). Pré-remplie par les handoffs,
> co-construite avec l'humain. Elle sert deux fois : elle **structure l'atelier**, puis elle **structure
> le prompt Claude Design**. Discipline : **marquer, ne pas inventer**. Calibrage : **commencer petit**,
> étendre si besoin ; pas de sur-tokenisation, pas de composant inutile.
>
> **Chaque item se désigne par sa phrase en clair**, jamais par un code : les identifiants (`F1`, `E6`,
> `T3`...) restent des **clés internes du manifeste**, jamais affichées à l'utilisateur.
> **Colonne Origine** : `C` = déduit du handoff **Cadrage** · `A` = déduit du handoff **Architecte**
> (section *Décisions à impact design*) · `H` = à **co-construire avec l'humain**.
> **Statut montré à l'utilisateur** : **validé** (couvert - déduit d'un handoff ou tranché par l'humain) ·
> **à traiter** (pas encore couvert, **bloquant**) · **sans objet** (ne s'applique pas à ce projet -
> marqué, pas forcé). *(En interne, le manifeste garde un statut plus fin - `deduced` / `decided` /
> `sans_objet` / `open` - mais l'affichage se réduit à ces trois mots.)* Aucun item ne reste **à traiter**
> quand la couverture est jugée suffisante.

## Bloc 1 : Fondation du design system (le système, pas les écrans)

| Ce qui est couvert (en clair) | Détail | Origine | Statut | Note / source |
|-------------------------------|--------|---------|--------|---------------|
| La palette de couleurs, l'échelle typographique et les espacements de base | Couleurs sémantiques (primaire, texte, fond, succès, erreur, alerte), échelle typo (tailles + graisses), échelle d'espacement (4-8 valeurs), rayons, élévation | H (nourri maquette + marque si présente) | | |
| Les thèmes d'affichage : mode clair et sombre si besoin, et la déclinaison de marque par client | Clair / sombre si requis ; branding par tenant si la multitenance l'impose | A (multitenance) + H | | |
| Les composants de base avec tous leurs états | Bouton, champ, select, case/radio, bascule, modale, notification, liste/tableau, navigation. Chaque composant : défaut, survol, focus, actif, désactivé, chargement, erreur | H (états techniques nourris par A) | | |
| Les animations et transitions de l'interface | Petit jeu standard de durées + courbes d'easing, appliqué partout. Rester minimal | H | | |

## Bloc 2 : Versant Expérience (ce que l'humain tranche)

| Ce qui est couvert (en clair) | Détail | Origine | Statut | Note / source |
|-------------------------------|--------|---------|--------|---------------|
| Chaque parcours clé de l'utilisateur, du début à la fin | Chaque parcours clé couvert de bout en bout | C | | |
| Les différents états de chaque écran | Chargement, vide, contenu, succès. Distinguer 1re utilisation et aucun résultat | C déclenche, H tranche | | |
| Les écrans sans données, traités avec un message et une action | Message clair + une action ; jamais un écran blanc qui ressemble à un bug | H | | |
| La hiérarchie visuelle et la densité d'information | Un objectif principal par écran, charge cognitive maîtrisée | C + H | | |
| Les retours après une action et les confirmations | Action asynchrone confirmée ; action destructrice confirmée avec annulation | H (nourri A pour l'async) | | |
| Le ton des textes de l'interface : boutons, libellés, messages d'erreur | Langage humain, libellés d'action explicites, ton cohérent | H | | |

## Bloc 3 : Versant Technique qui se voit (découle de l'architecture)

| Ce qui est couvert (en clair) | Détail | Origine | Statut | Note / source |
|-------------------------------|--------|---------|--------|---------------|
| L'affichage des erreurs, champ par champ | Validation (inline, à la sortie du champ, message explicite et actionnable), erreur serveur, perte de connexion. Le format d'erreur de l'API se projette en messages par champ | A (format erreur API) + règles UX | | |
| Les temps d'attente et le chargement | Squelettes, spinners, chargement partiel, attente sur action | A (async) | | |
| Les listes, tableaux et leur pagination | Liste, tri, pagination, et leurs cas vides | A (conventions API listes) | | |
| L'identité, les rôles et les autorisations | Variantes par rôle, état non autorisé, écran de connexion, session expirée | A (identité, SSO) | | |
| La navigation et l'organisation de l'information | Architecture de l'information, patterns de navigation | A (routage) | | |
| Le socle d'accessibilité | Contraste AA, focus visible, cibles tactiles suffisantes, navigation clavier, erreurs identifiées en texte (pas par la couleur seule), focus porté sur le 1er champ en erreur | A (niveau visé) + règles WCAG | | |
| L'adaptation aux différentes tailles d'écran | Breakpoints cibles et comportement mobile | A (cibles responsive) | | |
| La prise en charge de plusieurs langues | Si requis : sens de lecture, longueur de texte variable | A (i18n) | | |
| Le budget de performance | Limiter les animations lourdes si contrainte | A (performance) | | |

---
*Fondement (le plugin applique, n'invente pas) : états canoniques d'écran et règles d'erreur (explicite,
humaine, polie, précise, constructive ; validation à la sortie du champ, pas pendant la frappe) suivent
NN/g ; l'accessibilité suit WCAG. Voir `references/coverage-checklist-guide.md`.*
