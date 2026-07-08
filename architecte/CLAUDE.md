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
- `architecte-init` — setup (zéro décision IA) : **d'abord (re)pose ce dont la phase a besoin** — gabarits dans `.factory/architecte/` (git-ignoré, absent d'un clone frais) + bloc `architecture` dans le **manifeste committé** `cadrage-out/manifest.json` (créé s'il manque) ; puis `conventions/` **+ pose de tous les hooks de l'architecte** (enforcement des tests `PostToolUse` + protection de branche `.githooks/`/`SessionStart`, déterministe). **Jamais bloquant** : installe le socle **toujours** (même sans cadrage), puis **avertit** (sans refuser) si `cadrage-out/` manque. **`.gitignore` : jamais réécrit** — la première version est générée par le cadrage ; `architecte-init` **ajoute** seulement la ligne `.factory/` (et `architecte-contrat` les lignes `.env`), en le créant **uniquement s'il est absent**.
- `architecte-contrat` — construction interactive du contrat (porte humaine : **arbitrage des ADR**).
- `architecte-coherence` — porte humaine : **validation de cohérence** (stricte, adversariale).
Mappe les deux portes humaines de la définition + un setup déterministe isolé.
*(Le skill principal s'appelle `architecte-contrat`, pas `architecte` — pour ne pas
porter le même nom que le plugin.)*

## Workspace & manifeste
Écrit ses propres sorties dans `architecte-out/` (à côté de `cadrage-out/`). Le
manifeste `cadrage-out/manifest.json` reçoit un bloc **`architecture`** (drivers,
quality_attributes, components, stack, conventions_installed, adrs, walking_skeleton,
feature_sequence, risks, **design_impact**, **env_files**, **test_enforcement**, **branch_protection**, coherence_validated). `conventions/` est créé à la **racine
du projet** (vrais fichiers de config). Écriture = read-modify-write + revalidation JSON.
**Handoff designer** : le skill `architecte-contrat` produit `design-impact.md` (section « Décisions à
impact design ») — la tranche de l'archi qui se voit à l'écran, consommée par `/designer:designer-atelier` ;
`check_architecture.py` exige `architecture.design_impact = true`. Les diagrammes sont aussi rendus en
**images PNG** dans `architecte-out/diagrammes/` (via `scripts/render_diagrams.py`, mermaid-cli) ; le
rendu est **robuste et auto-installé** (navigateur système, CA d'entreprise respectée sans désactiver
TLS, replis mermaid-cli → npx → Kroki local), pré-provisionné par `architecte-init`
(`scripts/provision_render.py`), sans prompt.

## Intégration cadrage (entrées) — lecture parallèle exhaustive
Lit `cadrage-out/{project-frame, product-brief, glossaire, spec-index, coupling-map}.md` et les
briefs sous `cadrage-out/features-fonctionnels-brief/*.md`. **`architecte-contrat` lit le
cadrage en parallèle** (fan-out de sous-agents `architecte-reader`, partitionnés par préoccupation,
retours structurés complets + passe de complétude) — pour maximiser l'exactitude et le temps mural,
sans rien manquer. La table `references/question-map.md` indique ensuite où chaque réponse se trouve
déjà → on ne re-pose que les trous (profil d'équipe). Convergence : `architecte` **fige le registre canonique**
`architecture.feature_sequence` — la liste numérotée/séquencée des features (le 2ᵉ
découpage), en objets `{id, ucs, name}` (`ucs` = **liste** de use cases, une feature
pouvant en bundler plusieurs ; `id` `001…` = ordre de fabrication) — à partir des use
cases du `spec-index.md`. **Aucune notion de MVP** : on ne décide pas ce qui est MVP ou
non ; l'ordre est purement technique (dépendances).

## Ordre de remplissage (dépendances)
drivers/qualité → composants → stack → conventions → ADR → walking skeleton+numérotation
→ diagrammes → risques → **fichiers d'environnement (automatique : `.env`+`.env.example` générés dès que la stack a des dépendances)** → validation de cohérence. *(L'enforcement — hooks de test + protection de branche — est posé plus tôt, dès `architecte-init`, pas dans le contrat.)*
**Drivers ≠ attributs de qualité** : les drivers sont les **objectifs métier + contraintes +
risques** (le pourquoi / les limites) ; les attributs de qualité sont les **-ilités mesurées qui en
découlent** (cible + scénario QAW). Jamais de doublon entre les deux (cf. `templates/drivers-quality.md`).

## Conventions partagées
`references/interactive-loop.md` (boucle 3-options), `references/ux-conventions.md`
(pas de fuite de champ, refus en clair, une ligne « Étape suivante » par skill).
Agent de lecture : `agents/architecte-reader.md` (lecture complète + sortie structurée,
dispatché en parallèle par `architecte-contrat`).
Scripts : `scripts/check_architecture.py` (garde-fou : présence, **versions exactes** de
`tech-stack.md`, **front-matter `version`/`date`** de chaque doc, **stratégie de test** de
`standards.md`, **existence réelle des fichiers d'env à la racine** (`env_files.files` + `.env` gitignoré) / flag `test_enforcement`, marqueurs résiduels) ;
`scripts/render_diagrams.py` (rendu Mermaid robuste, auto-install, replis, sans prompt) ;
`scripts/provision_render.py` (pré-installe le rendu à l'init) ; `scripts/bump_doc_version.py`
(incrément du compteur de version des documents).
Catalogues copiés à la racine du projet : `references/conventions/` (linters par langage, Étape 4),
`references/env-templates/` (fichiers d'env par stack, Étape 10), `references/enforcement/`
(hook Claude Code `PostToolUse` `tests_guard.py` + `lefthook.yml` — « tests écrits avec le code » —
**+ hook `PostToolUse` `format_guard.py`** : formatage à l'édition (Python : lit `.editorconfig` →
`ruff format --config` ; comble le fait que Claude Code/ruff ne lisent pas `.editorconfig` ; posé par
`install_format_hook.py`, non bloquant) — **et
`.githooks/` + `install_branch_protection.py` : protection de branche locale (refus push/commit
sur `main`/`master` — hooks `pre-push`/`pre-commit`, **posés à la racine du dépôt git**, via
`core.hooksPath` **réactivé automatiquement par un hook `SessionStart`** ; **pas** de blocage du
merge en local — best practice, cf. enforcement/README) —
**tout posé par `architecte-init`**, plus par le contrat**). *(Le hook `Stop` bloquant a été retiré : seul `PostToolUse` reste côté session.)*

## Vérifications
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md   # doit ne rien retourner
python scripts/check_architecture.py <projet>/cadrage-out/manifest.json
```

## Invariants
Proposer/pas décider (**jamais la stack à la place de l'utilisateur** : options + compromis +
arbitrage humain, **sans biais fournisseur** ; l'expérience avec une techno ne vaut pas décision ;
ADR consignés **après** décision ; cohérence validée par l'humain) ; **composant frontend** porté
par l'architecte dès qu'il y a des écrans (le designer garde le design system visuel) ; **versions
exactes épinglées** pour chaque techno (jamais « latest ») ; **documents versionnés** (front-matter
`version`/`date` ; ADR immuables en version 1) ; **rien laissé indéfini** — tout marqueur se résout
en session, en place, avant d'avancer ; **contenu seul** dans les artefacts (aucune `(src:)`, aucun
horodatage **dans le corps**, aucun nom de personne ; le front-matter version/date est une
métadonnée, pas de la provenance) ; **aucune notion de MVP** ; conventions = vrais fichiers ;
restitutions en **prose** (pas de tableau), **noms en clair** (jamais `C1`/`UC1`/`P1`),
**manifeste mis à jour en silence** (jamais narré).
