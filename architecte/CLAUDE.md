# CLAUDE.md — plugin `architecte`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`architecte` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`architecte` = **phase 2** de la Factory (contrat technique). Transforme le besoin
fonctionnel (sortie de `cadrage`) en cadre technique : drivers & attributs de
qualité, composants, stack, **ADR transverses**, walking skeleton, normes/linters,
diagrammes, validation de cohérence. **Ne décide pas à la place de l'architecte** :
il discipline et grave. Ce sont des **skills Markdown** ; pas de build/test.

## Langue & invocation
- **Tout en français** (skills, templates, artefacts, interaction). Seuls les
  identifiants/valeurs machine et les noms d'outils (`ruff.toml`, `biome.json`) restent tels quels.
- **Skills uniquement, pas de `commands/`** (un command homonyme d'un skill boucle).
  Invocation : `/architecte:<skill>` (utilisateur) + auto par le modèle.

## Les 3 skills (découpage justifié)
- `architecte-init` — setup (zéro décision IA) : gabarits + `conventions/` + bloc manifeste.
- `architecte` — construction interactive du contrat (porte humaine : **arbitrage des ADR**).
- `architecte-coherence` — porte humaine : **validation de cohérence**.
Mappe les deux portes humaines de la définition + un setup déterministe isolé.

## Workspace & manifeste
Écrit dans le **workspace partagé** `factory-docs/work/` (à côté de cadrage). Le
manifeste `factory-docs/manifest.json` reçoit un bloc **`architecture`** (drivers,
quality_attributes, components, stack, conventions_installed, adrs, walking_skeleton,
feature_sequence, risks, coherence_validated). `conventions/` est créé à la **racine
du projet** (vrais fichiers de config). Écriture = read-modify-write + revalidation JSON.

## Intégration cadrage (entrées)
Lit `factory-docs/work/{project-frame, product-brief, glossaire, spec-index,
*.brief, pre-constitution}.md`. La table `references/question-map.md` indique où
chaque réponse d'architecture se trouve déjà → on ne re-pose que les trous (profil
d'équipe). Convergence : `architecte` **fige le registre canonique**
`architecture.feature_sequence` — la liste numérotée/séquencée des features (le 2ᵉ
découpage), en objets `{id, ucs, name, mvp}` (`ucs` = **liste** de use cases, une feature
pouvant en bundler plusieurs ; `id` `001…` = ordre de fabrication) — à partir des use
cases du `spec-index.md`.

## Ordre de remplissage (dépendances)
drivers/qualité → composants → stack → conventions → ADR → walking skeleton+numérotation
→ diagrammes → risques → validation de cohérence.

## Conventions partagées
`references/interactive-loop.md` (boucle 3-options), `references/ux-conventions.md`
(pas de fuite de champ, refus en clair, une ligne « Étape suivante » par skill).
Garde-fou déterministe : `scripts/check_architecture.py`.

## Vérifications
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md   # doit ne rien retourner
python scripts/check_architecture.py <projet>/factory-docs/manifest.json
```

## Invariants
Proposer/pas décider (ADR arbitrés par l'humain, cohérence validée par l'humain) ;
marquer/pas inventer (`[À VALIDER]`) ; traçabilité `(src:)` ; conventions = vrais
fichiers ; refus et restitutions en langage naturel.
