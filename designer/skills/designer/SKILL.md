---
name: designer
description: Construit le contrat de design (principes, tokens DTCG, composants & états, parcours, accessibilité) en interactif.
---

# designer

Cœur de la phase design. **Distille la maquette validée en un contrat opposable et grave
les décisions de design en design system exécutable.** L'IA propose et structure ;
**l'humain (le designer) tranche** (arbitrage des DDR). **Fige le système, pas les
écrans** : on définit tokens, composants, états et patterns — pas des maquettes d'écran
figées.

## Porte d'entrée
`designer-init` a tourné (le manifeste contient le bloc `design`). Sinon, orienter en
clair vers `/designer:designer-init`.

## Entrées
- **Cadrage** : `product-brief.md` (vision, ton), `glossaire.md` (langage),
  `spec-index.md` (use cases = parcours candidats), et la **maquette validée**
  (`manifest.demonstrateur` : `client_validated: true`, `external_ref`) — **source
  primaire** des couleurs, typographies, espacements, composants observés.
- **Architecte** : `tech-stack.md` (framework front-end → format de livraison des
  tokens), `components.md`, `standards.md` + `conventions/`.
- Conventions : `references/interactive-loop.md`, `references/ux-conventions.md`,
  `references/design-tokens-guide.md`, `references/states-catalog.md`.

## Procédure — ordre imposé (chaque étape consomme la précédente)

### Étape 0 — Vérifier les entrées (ne rien re-demander d'inutile)
Charger `references/question-map.md`. **Auto-remplir** depuis la maquette validée + les
artefacts de cadrage/architecte (avec `(src: …)`). Écrire `design.source_maquette` (réf du
démonstrateur validé). Ne **poser que les trous** (boucle 3-options) — typiquement
l'**identité visuelle / marque** si absente de la maquette (palette de marque, polices,
ton), les **plateformes/tailles cibles** si non couvertes. Toute réponse restée
`[À VALIDER]` bloquante est re-soumise ici ; si elle est « passée », **ne pas démarrer la
génération** : le signaler et s'arrêter.

### Étape 1 — Principes de design
Dériver 3 à 7 **principes de design** de la vision produit (`product-brief.md`) + de la
marque + du ton observé dans la maquette. Restituer en chat, faire valider, puis écrire
`factory-docs/work/design-principles.md` (gabarit `templates/design-principles.md`).
MAJ `design.principles`.

### Étape 2 — Fondations & tokens (DTCG)
**Extraire de la maquette validée** la palette, l'échelle typographique, l'échelle
d'espacement, les rayons, les ombres/élévations, les durées/easings (tracés
`(src: maquette)`). Les structurer en **trois tiers DTCG** (voir
`references/design-tokens-guide.md`) : **primitive** (valeurs brutes) → **semantic**
(rôles : `color.surface/text/border/brand/feedback`, rôles typographiques, rôles
d'espacement) → **component** (optionnel). Écrire les **vrais tokens** dans
`design-system/tokens.json` (**format DTCG** : `$value`/`$type`/`$description`) +
`factory-docs/work/foundations.md` (lisible : système de couleur **avec ratios de
contraste WCAG**, échelle typo, espacement, élévation, mouvement, iconographie, grille &
points de rupture). Valider en chat. MAJ `design.tokens` / `design.foundations`.

### Étape 3 — Livraison des tokens (cohérente avec la stack de l'architecte)
Lire le framework front-end dans `tech-stack.md`. **Proposer le format de livraison**
(2–4 options + recommandation, boucle 3-options) cohérent avec la stack :
- React/TS, Vue, Svelte → **variables CSS** + thème typé via **Style Dictionary** ;
- Tailwind → **preset de tokens** ;
- CSS/HTML simple → **variables CSS** (custom properties).
Matérialiser la config de livraison dans `design-system/` (ex.
`design-system/style-dictionary.config.json` + cible de sortie documentée). **Fallback**
(front-end inconnu/exotique) : **variables CSS universelles**, avertir l'utilisateur,
marquer `[À VALIDER]`. MAJ `design.stack_alignment` (`frontend`, `token_delivery`).

### Étape 4 — Inventaire & contrats de composants (interactif)
Dériver la **liste des composants** depuis la maquette validée + `components.md` de
l'architecte + les use cases. **Afficher la liste en tableau** ; demander si ça convient
ou s'il faut modifier ; **boucler jusqu'à validation**. Pour **chaque** composant, écrire
un contrat (gabarit `templates/design-components.md`) : anatomie, variantes, **états** (default,
hover, focus, active, disabled, loading, empty, error, selected — selon le composant),
props/API, **accessibilité** (rôle ARIA, **interaction clavier** selon WAI-ARIA APG — voir
`references/states-catalog.md`, gestion du focus), comportement responsive. Écrire
`factory-docs/work/design-components.md` (composants UI — distinct du `components.md` de
l'architecte qui liste les services). MAJ `design.components` / `design.component_states`.

### Étape 5 — États & patterns d'interface
Définir les **états canoniques d'écran** (vide/initial, chargement, partiel, erreur,
idéal/succès) et les **patterns** transverses (formulaires & validation, retours/toasts,
navigation, modales, états hors-ligne). Chacun rattaché aux composants concernés. Écrire
`factory-docs/work/states-and-patterns.md` (gabarit `templates/states-and-patterns.md`).
MAJ `design.states_patterns`. *(Couvre la « couverture des états ».)*

### Étape 6 — Parcours (journeys)
Pour **chaque** use case de `spec-index.md`, décrire un **parcours** comme une
**composition de composants et de patterns** (pas un écran figé — *on fige le système, pas
les écrans*) : étapes, états traversés, composants mobilisés. Écrire
`factory-docs/work/journeys.md` (gabarit `templates/journeys.md`). MAJ `design.journeys` /
`design.journeys_coverage` (use case → parcours, **couverture complète** — pas seulement
le MVP).

### Étape 7 — Accessibilité (WCAG 2.2 AA)
Graver le **contrat d'accessibilité** (gabarit `templates/accessibility.md`) : contraste
AA (4,5:1 texte / 3:1 grand texte & éléments d'UI), focus visible non masqué, opérabilité
clavier, **taille de cible 24×24 px min** (critère 2.5.8, nouveau en 2.2), alternatives au
glisser, préférence de mouvement réduit, structure sémantique. Vérifier que les paires de
couleurs sémantiques (texte/fond) respectent les ratios. MAJ `design.accessibility`.

### Étape 8 — DDR (arbitrage humain)
Pour chaque **décision de design structurante** (architecture des tokens, stratégie de
thème sombre, densité, set d'icônes, choix/licence de polices, base d'espacement…),
produire un **DDR** (gabarit `templates/ddr.md`) dans
`factory-docs/work/design-decisions/DDR-NNN-titre.md` : contexte, décision, options,
conséquences, déclencheur de revue. **C'est une porte d'arbitrage humain** : le designer
valide chaque DDR. MAJ `design.ddrs[]`.

## Porte de sortie
- Entrées vérifiées (rien de bloquant en suspens) ; `design-principles.md`,
  `foundations.md`, `design-components.md`, `states-and-patterns.md`, `journeys.md`,
  `accessibility.md`, DDR produits ; **tokens DTCG** dans `design-system/` + config de
  livraison cohérente avec la stack ; couverture des use cases par des parcours.
  `design.phase = "contrat"`.
- **Traçabilité** : chaque énoncé porte sa source `(src: maquette | cadrage | architecte |
  atelier/utilisateur)`. **Rien d'inventé** ; tout trou reste `[À VALIDER]`.

## Règles invariantes
- **Proposer, ne pas décider.** Les DDR sont arbitrés par l'humain ; les listes
  (composants, tokens) se valident en chat.
- **Figer le système, pas les écrans.** Le livrable est le design system (tokens,
  composants, états, patterns), pas des maquettes d'écran.
- **Pas de fuite de champ** ni de jargon machine en sortie utilisateur (voir
  `references/ux-conventions.md`). Refus en langage naturel.
- **Skill indépendant.** Lit/écrit le manifeste partagé.

Étape suivante : `/designer:designer-coherence` — valider la couverture des parcours et des états avant le passage à l'assembleur.
