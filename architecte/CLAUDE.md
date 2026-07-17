# CLAUDE.md : plugin `architecte`

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

## Les 6 skills (découpage justifié)
- `architecte-init` - setup (zéro décision IA) : **d'abord (re)pose ce dont la phase a besoin** - gabarits dans `.factory/architecte/` (git-ignoré, absent d'un clone frais) + bloc `architecture` dans le **manifeste committé** `manifest.json` (créé s'il manque) ; puis `conventions/` **+ pose des hooks de l'architecte** (enforcement des tests + formatage `PostToolUse`, déterministe ; **pas de protection de branche locale** - gérée côté GitHub). **Jamais bloquant** : installe le socle **toujours** (même sans cadrage), puis **avertit** (sans refuser) si `cadrage-out/` manque. **`.gitignore` : jamais réécrit** - la première version est générée par le cadrage ; `architecte-init` **ajoute** seulement la ligne `.factory/` (et `architecte-livrables` les lignes `.env`), en le créant **uniquement s'il est absent**.
- `architecte-fondations` - lit **tout le cadrage** en parallèle (fan-out `architecte-reader`), puis pose les **fondations** : drivers & attributs de qualité (deux tableaux clairs), puis composants (Frontend/UI compris). Portes humaines : validation des drivers/qualité et des composants.
- `architecte-stack` - **stack technique** (2-4 options + compromis par domaine, **sans biais fournisseur**, versions **exactes épinglées**), activation des **conventions/linters** (vrais fichiers + install best-effort), **ADR** (consignés après décision) et **walking skeleton + séquence de features** (couverture 1:1, proposée - figée par l'assembleur). Portes humaines : **choix de stack** et **arbitrage des ADR**.
- `architecte-livrables` - livrables **dérivés** des décisions déjà prises : diagrammes D2 (+ images SVG/PNG), registre de risques, **`impact-design.md`** (handoff designer), fichiers d'environnement (`.env`+`.env.example`), vérification de l'enforcement ; puis **balayage final** de tout `architecte-out/` (rien laissé d'indéfini) avant la porte de cohérence.
- `architecte-coherence` - **porte de cohérence stricte et adversariale, ancrée méthodes**.
  Relit tout `architecte-out/` + le cadrage aval **en parallèle** (fan-out `architecte-reader`),
  puis challenge le contrat en **3 lentilles** (Cohérence / Consistance / Complétude) grillées
  sur ATAM, scénarios qualité 6-parties, revue ADR, traçabilité bidirectionnelle, walking
  skeleton sans stub, risque-driven, arc42, AWS WAR (`references/coherence-checklist-guide.md`).
  **Chaque point trouvé devient une décision** (question "que veux-tu faire ?" + 3 choix +
  application en place - jamais un constat "bloquant" nu), résolu **un par un** avant le
  passage au designer. Puis **porte humaine : validation de cohérence**.
- `gen-tests` - **outil de maintenance hors chaîne** (`/architecte:gen-tests [chemin]`) : génère les tests manquants (pytest/jest/vitest/go) pour les sources qui n'en ont pas, **puis les exécute et itère jusqu'à ce que la suite passe au vert** (contrat de sortie = suite verte, pas seulement des fichiers écrits).
**Flux de construction** : `architecte-init` -> `architecte-fondations` -> `architecte-stack` -> `architecte-livrables` -> `architecte-coherence`. Mappe les portes humaines de la définition (drivers/qualité + composants, choix de stack, **arbitrage des ADR**, validation de cohérence) + un setup déterministe isolé.
*(Aucun skill de construction ne porte le nom `architecte` - pour ne pas porter le même nom que le plugin ; un command homonyme d'un skill boucle.)*

## Workspace & manifeste
Écrit ses propres sorties dans `architecte-out/` (à côté de `cadrage-out/`). Le
manifeste `manifest.json` reçoit un bloc **`architecture`** (drivers,
quality_attributes, components, stack, conventions_installed, adrs, walking_skeleton,
feature_sequence, risks, **design_impact**, **env_files**, **test_enforcement**, coherence_validated). `conventions/` est créé à la **racine
du projet** (vrais fichiers de config). Écriture = read-modify-write + revalidation JSON.
**Handoff designer** : le skill `architecte-livrables` produit `impact-design.md` (section "Décisions à
impact design") - la tranche de l'archi qui se voit à l'écran, consommée par `/designer:designer-ingestion` ;
`check_architecture.py` exige `architecture.design_impact = true`. Les diagrammes sont écrits en
**syntaxe D2** (moteur ELK : routage orthogonal, sans chevauchement) et rendus en **SVG** (source de
vérité, vectoriel) **+ PNG** (best-effort) dans `architecte-out/diagrammes/` (via
`scripts/render_diagrams.py`, binaire **D2**) ; le rendu est **robuste et auto-installé** (SVG sans
navigateur ; PNG via navigateur système, CA d'entreprise respectée sans désactiver TLS ; repli D2 ->
Kroki local), pré-provisionné par `architecte-init` (`scripts/provision_render.py` installe le binaire
D2 épinglé dans `.factory/d2/`, sans admin), sans prompt.

## Intégration cadrage (entrées) : lecture parallèle exhaustive
Lit `cadrage-out/{project-frame, product-brief, glossaire, spec-index, coupling-map}.md` et les
briefs sous `cadrage-out/features-fonctionnels-brief/*.md`. **`architecte-fondations` lit le
cadrage en parallèle** (fan-out de sous-agents `architecte-reader`, partitionnés par préoccupation,
retours structurés complets + passe de complétude) - pour maximiser l'exactitude et le temps mural,
sans rien manquer. La table `references/question-map.md` indique ensuite où chaque réponse se trouve
déjà -> on ne re-pose que les trous (profil d'équipe). Convergence : `architecte` **propose la séquence**
`architecture.feature_sequence` - la liste numérotée/séquencée des features (le 2ᵉ
découpage), en objets `{id, ucs, name}` (`ucs` = **liste** de use cases, une feature
pouvant en bundler plusieurs ; `id` `001...` = ordre de fabrication) - à partir des use
cases du `spec-index.md`. **Aucune notion de MVP** : on ne décide pas ce qui est MVP ou
non ; l'ordre est purement technique (dépendances). **Proposition, pas verdict** : cette séquence est
un **point de départ** ; l'**arbitrage final** du découpage (split/merge) et le **gel** appartiennent à
l'**assembleur** (`assembleur-convergence` réécrit `architecture.feature_sequence`, figée à l'init Linear).

## Ordre de remplissage (dépendances)
drivers/qualité -> composants -> stack -> conventions -> ADR -> walking skeleton+numérotation
-> diagrammes -> risques -> **fichiers d'environnement (automatique : `.env`+`.env.example` générés dès que la stack a des dépendances)** -> validation de cohérence. *(L'enforcement - hooks de test + formatage - est posé plus tôt, dès `architecte-init`, pas dans la construction du contrat.)* Répartition par skill : **fondations** (drivers/qualité -> composants), **stack** (stack -> conventions -> ADR -> walking skeleton+numérotation), **livrables** (diagrammes -> risques -> impact-design -> fichiers d'environnement -> vérification enforcement).
**Drivers ≠ attributs de qualité** : les drivers sont les **objectifs métier + contraintes +
risques** (le pourquoi / les limites) ; les attributs de qualité sont les **-ilités mesurées qui en
découlent** (cible + scénario QAW). Jamais de doublon entre les deux (cf. `templates/facteurs-et-qualite.md`).

## Conventions partagées
`references/interactive-loop.md` (boucle 3-options), `references/ux-conventions.md`
(pas de fuite de champ, refus en clair, une ligne "Étape suivante" par skill),
`references/coherence-checklist-guide.md` (grille canonique de la porte de cohérence, ancrée
ATAM / scénarios qualité 6-parties / revue ADR / traçabilité / walking skeleton / risque-driven
/ arc42 / AWS WAR - lue par `architecte-coherence`).
Agent de lecture : `agents/architecte-reader.md` (lecture complète + sortie structurée,
dispatché en parallèle par `architecte-fondations` et `architecte-coherence`).
Scripts : `scripts/check_architecture.py` (garde-fou : présence, **versions exactes** de
`stack-technique.md`, **front-matter `version`/`date`** de chaque doc, **stratégie de test** de
`standards-ingenierie.md`, **existence réelle des fichiers d'env à la racine** (`env_files.files` + `.env` gitignoré) / flag `test_enforcement`, marqueurs résiduels) ;
`scripts/render_diagrams.py` (rendu D2 robuste -> SVG+PNG, auto-install, replis Kroki, sans prompt) ;
`scripts/provision_render.py` (pré-installe le rendu à l'init) ; `scripts/bump_doc_version.py`
(incrément du compteur de version des documents) ; `scripts/install_formatter.py` (**installe l'outil
de formatage retenu à l'Étape 4** - `ruff` via pip, `@biomejs/biome` ou `eslint`+`prettier` via npm local ;
idempotent, sans admin, non bloquant).
Catalogues copiés à la racine du projet : `references/conventions/` (linters par langage, Étape 4),
`references/env-templates/` (fichiers d'env par stack, Étape 10), `references/enforcement/`
(hook Claude Code `PostToolUse` `tests_guard.py` + `lefthook.yml` - "tests écrits avec le code" -
**+ hook `PostToolUse` `format_guard.py`** : formatage à l'édition (Python : lit `.editorconfig` ->
`ruff format --config` ; comble le fait que Claude Code/ruff ne lisent pas `.editorconfig` ; posé par
`install_format_hook.py`, non bloquant) -
**tout posé par `architecte-init`**, plus par le contrat**). *(Le hook `Stop` bloquant a été retiré : seul `PostToolUse` reste côté session.)* **Pas de protection de branche locale** : les hooks git `.githooks/` ont été **retirés** ; la règle "aucun push direct sur `main`" est gérée par un **ruleset serveur GitHub**.

## Vérifications
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md   # doit ne rien retourner
python scripts/check_architecture.py <projet>/manifest.json
```

## Invariants
Proposer/pas décider (**jamais la stack à la place de l'utilisateur** : options + compromis +
arbitrage humain, **sans biais fournisseur** ; l'expérience avec une techno ne vaut pas décision ;
ADR consignés **après** décision ; cohérence validée par l'humain) ; **composant frontend** porté
par l'architecte dès qu'il y a des écrans (le designer garde le design system visuel) ; **versions
exactes épinglées** pour chaque techno (jamais "latest") ; **documents versionnés** (front-matter
`version`/`date` ; ADR immuables en version 1) ; **rien laissé indéfini** - tout marqueur se résout
en session, en place, avant d'avancer ; **contenu seul** dans les artefacts (aucune `(src:)`, aucun
horodatage **dans le corps**, aucun nom de personne ; le front-matter version/date est une
métadonnée, pas de la provenance) ; **aucune notion de MVP** ; conventions = vrais fichiers ;
restitutions en **prose** (pas de tableau - **sauf drivers, attributs de qualité et composants, restitués en tableaux clairs**, cf. ux-conventions §4), **noms en clair** (jamais `C1`/`UC1`/`P1`),
**manifeste mis à jour en silence** (jamais narré) ; **typographie humaine** : aucun glyphe de style IA dans les artefacts/prompts (pas de tiret cadratin, de points de suspension unicode, de flèches unicode, de guillemets à chevrons, ni de coche/croix ; équivalents clavier, cf. la section Typographie de `references/ux-conventions.md`).
