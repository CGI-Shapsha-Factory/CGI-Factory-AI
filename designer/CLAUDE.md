# CLAUDE.md — plugin `designer`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`designer` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`designer` = **phase 3** de la Factory (contrat de design). Distille la **maquette
validée** (démonstrateur convergé du cadrage) en un **contrat de design opposable** :
un **design system exécutable** — tokens DTCG, fondations, composants & états, parcours,
accessibilité WCAG 2.2 AA — **cohérent avec la stack retenue par l'architecte**. Principe
cardinal : **il fige le système, pas les écrans.** Ce sont des **skills Markdown** ; pas
de build/test.

## Langue & invocation
- **Tout en français** (skills, templates, artefacts, interaction). Seuls les
  identifiants/valeurs machine et noms d'outils/formats (`tokens.json`, DTCG,
  Style Dictionary, WCAG, ARIA) restent tels quels.
- **Skills uniquement, pas de `commands/`** (un command homonyme d'un skill boucle).
  Invocation : `/designer:<skill>` + auto par le modèle.

## Les 3 skills (découpage justifié)
- `designer-init` — setup (zéro décision IA) : gabarits + `design-system/` (seed tokens
  DTCG) + bloc manifeste.
- `designer` — construction interactive du contrat (porte humaine : **arbitrage du
  designer**, gravé en DDR).
- `designer-coherence` — porte humaine : **validation de couverture** (parcours + états).
Mappe les deux portes humaines de la définition + un setup déterministe isolé.

## Workspace & manifeste
Écrit dans le **workspace partagé** `factory-docs/work/` (à côté de cadrage et
architecte). Le manifeste `factory-docs/manifest.json` reçoit un bloc **`design`**
(source_maquette, principles, tokens, foundations, stack_alignment, components,
component_states, states_patterns, journeys, journeys_coverage, accessibility, ddrs,
coverage_validated). `design-system/` est créé à la **racine du projet** (vrais fichiers
de tokens DTCG + config de livraison). Écriture = read-modify-write + revalidation JSON.

## Intégration (entrées)
Lit du **cadrage** : `product-brief.md`, `glossaire.md`, `spec-index.md` (use cases =
parcours candidats), et la **maquette validée** (`manifest.demonstrateur`,
`client_validated: true` + `external_ref`). Lit de l'**architecte** : `tech-stack.md`
(framework front-end → format de livraison des tokens), `components.md`, `standards.md`
+ `conventions/`. La table `references/question-map.md` indique où chaque réponse se
trouve déjà → on ne pose que les trous (identité visuelle / marque si absente).

## Ordre de remplissage (dépendances)
principes → fondations & tokens (DTCG) → livraison des tokens (selon stack) →
composants & états → états & patterns → parcours → accessibilité → DDR (arbitrage) →
validation de couverture.

## Conventions partagées
`references/interactive-loop.md` (boucle 3-options), `references/ux-conventions.md`
(pas de fuite de champ, refus en clair, une ligne « Étape suivante »). Références design :
`references/design-tokens-guide.md` (format DTCG, tiers), `references/states-catalog.md`
(états UI + clavier WAI-ARIA APG). Garde-fou déterministe : `scripts/check_design.py`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
python -c "import json; json.load(open('references/design-system/tokens.seed.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python scripts/check_design.py <projet>/factory-docs/manifest.json
```

## Invariants
Proposer/pas décider (DDR arbitrés par l'humain, couverture validée par l'humain) ;
**figer le système, pas les écrans** ; marquer/pas inventer (`[À VALIDER]`) ; traçabilité
`(src: maquette | cadrage | architecte | atelier)` ; tokens = vrais fichiers DTCG ;
accessibilité WCAG 2.2 AA ; refus et restitutions en langage naturel.
