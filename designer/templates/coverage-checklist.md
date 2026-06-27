# Checklist de couverture — design

> **Le cœur du plugin.** Outil de **couverture** (pas une bureaucratie). Pré-remplie par les handoffs,
> co-construite avec l'humain. Elle sert deux fois : elle **structure l'atelier**, puis elle **structure
> le prompt Claude Design**. Discipline : **marquer, ne pas inventer**. Calibrage : **commencer petit**,
> étendre si besoin ; pas de sur-tokenisation, pas de composant inutile.
>
> **Colonne Origine** : `C` = déduit du handoff **Cadrage** · `A` = déduit du handoff **Architecte**
> (section *Décisions à impact design*) · `H` = à **co-construire avec l'humain**.
> **Statut** de chaque item : `deduced` (rempli depuis un handoff) · `decided` (tranché par l'humain) ·
> `sans_objet` (sans objet sur ce projet — marqué, pas forcé) · `open` (non couvert, **bloquant** tant
> que non statué). Aucun item ne reste `open` quand la couverture est jugée suffisante.

## Bloc 1 — Fondation du design system (le système, pas les écrans)

| id | Élément | Couvre | Origine | Statut | Note / source |
|----|---------|--------|---------|--------|---------------|
| F1 | Tokens essentiels | Couleurs sémantiques (primaire, texte, fond, succès, erreur, alerte), échelle typo (tailles + graisses), échelle d'espacement (4–8 valeurs), rayons, élévation | H (nourri maquette + marque si présente) | | |
| F2 | Thématisation | Clair / sombre si requis ; branding par tenant si la multitenance l'impose | A (multitenance) + H | | |
| F3 | Composants de base + états | Bouton, champ, select, case/radio, bascule, modale, notification, liste/tableau, navigation. Chaque composant : défaut, survol, focus, actif, désactivé, chargement, erreur | H (états techniques nourris par A) | | |
| F4 | Mouvement | Petit jeu standard de durées + courbes d'easing, appliqué partout. Rester minimal | H | | |

## Bloc 2 — Versant Expérience (ce que l'humain tranche)

| id | Élément | Couvre | Origine | Statut | Note / source |
|----|---------|--------|---------|--------|---------------|
| E1 | Parcours et variantes | Chaque parcours clé couvert de bout en bout | C | | |
| E2 | États de chaque écran | Chargement, vide, contenu, succès. Distinguer 1re utilisation et aucun résultat | C déclenche, H tranche | | |
| E3 | États vides utiles | Message clair + une action ; jamais un écran blanc qui ressemble à un bug | H | | |
| E4 | Hiérarchie et densité | Un objectif principal par écran, charge cognitive maîtrisée | C + H | | |
| E5 | Feedback et confirmation | Action asynchrone confirmée ; action destructrice confirmée avec annulation | H (nourri A pour l'async) | | |
| E6 | Microcopie | Langage humain, libellés d'action explicites, ton cohérent | H | | |

## Bloc 3 — Versant Technique qui se voit (découle de l'architecture)

| id | Élément | Couvre | Origine | Statut | Note / source |
|----|---------|--------|---------|--------|---------------|
| T1 | Affichage des erreurs | Validation (inline, à la sortie du champ, message explicite et actionnable), erreur serveur, perte de connexion. Le format d'erreur de l'API se projette en messages par champ | A (format erreur API) + règles UX | | |
| T2 | Chargement et asynchrone | Squelettes, spinners, chargement partiel, attente sur action | A (async) | | |
| T3 | Listes, tableaux, pagination | Liste, tri, pagination, et leurs cas vides | A (conventions API listes) | | |
| T4 | Identité, rôles, autorisations | Variantes par rôle, état non autorisé, écran de connexion, session expirée | A (identité, SSO) | | |
| T5 | Navigation et routage | Architecture de l'information, patterns de navigation | A (routage) | | |
| T6 | Accessibilité, socle | Contraste AA, focus visible, cibles tactiles suffisantes, navigation clavier, erreurs identifiées en texte (pas par la couleur seule), focus porté sur le 1er champ en erreur | A (niveau visé) + règles WCAG | | |
| T7 | Responsive | Breakpoints cibles et comportement mobile | A (cibles responsive) | | |
| T8 | Internationalisation | Si requis : sens de lecture, longueur de texte variable | A (i18n) | | |
| T9 | Budget de performance | Limiter les animations lourdes si contrainte | A (performance) | | |

---
*Fondement (le plugin applique, n'invente pas) : états canoniques d'écran et règles d'erreur (explicite,
humaine, polie, précise, constructive ; validation à la sortie du champ, pas pendant la frappe) suivent
NN/g ; l'accessibilité suit WCAG. Voir `references/coverage-checklist-guide.md`.*
