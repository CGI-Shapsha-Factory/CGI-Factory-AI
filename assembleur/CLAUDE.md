# CLAUDE.md — plugin `assembleur`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`assembleur` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`assembleur` = **phase 4** de la Factory (convergence). Il **coud les 3 contrats**
(fonctionnel = cadrage, technique = architecte, design = designer) **par feature**,
**vérifie leur cohérence** (porte humaine : *garant de cohérence* — chaque feature part
avec ses 3 faces complètes et non contradictoires), puis **amorce un projet SpecKit
consommable directement** : constitution finale convergée, `CLAUDE.md`, briefs 3-faces,
glossaire consolidé, `MEMORY.md`, seeds `spec.md`, guidelines, plan d'attaque, CI, init
Linear. Ce sont des **skills Markdown** ; pas de build/test.

## Langue & invocation
- **Tout en français** (skills, templates, artefacts, interaction). Seuls les
  identifiants/valeurs machine et noms d'outils/formats (`spec.md`, `constitution.md`,
  SpecKit, Linear, `.specify/`) restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/assembleur:<skill>` + auto par
  le modèle.

## Les 4 skills (découpage justifié)
- `assembleur-init` — setup (zéro décision IA) : porte d'entrée = **les 3 contrats validés** ;
  capture le repo SpecKit cible ; gabarits + bloc manifeste.
- `assembleur` — convergence + génération (porte humaine : **garant de cohérence**).
- `assembleur-amorce` — amorçage SpecKit/CI + **porte humaine : validation équipe** du
  découpage/briefs/walking skeleton ; génère le **hook Linear aval** (Todo → En cours sur la 1re
  édition de code) + documente le **filet natif** Linear ; **délègue ensuite l'init Linear**.
- `init-linear` — **initialise les features dans Linear** (effet de bord live, **après** la
  validation équipe) : **clé API Linear dans `.env`** (étapes pour la créer), dédup d'un projet
  existant (informer + lien + stop), défauts **Todo/non-assigné**, via l'API GraphQL.
Mappe les deux portes humaines (cohérence, validation équipe) + un setup déterministe + l'effet Linear isolé.

## Workspace & manifeste
Lit les sorties des 3 plugins amont : `cadrage-out/` (product-brief, glossaire, spec-index,
`features-fonctionnels-brief/*.brief.md`), `architecte-out/` (tech-stack, components, standards,
drivers-quality, design-impact, `decisions/`), `designer-out/` (design-guidelines, coverage-report).
Le manifeste et les gabarits vivent dans `.factory/` (`.factory/manifest.json`, `.factory/templates/`).
Écrit :
- dans le **repo SpecKit cible** (`target_repo`) : `.specify/memory/constitution.md`,
  `CLAUDE.md`, `specs/NNN-feature/spec.md`, `GLOSSARY.md`, `MEMORY.md`,
  `.github/workflows/factory-checks.yml` ;
- dans `assembleur-out/` (ses propres sorties de travail) : `briefs/NNN-feature.brief.md` (3-faces),
  `coherence-report.md`, `guidelines/`, `attack-plan.md`, `linear-features.json`.
**L'assembleur dérive lui-même la constitution convergée** des fichiers bruts du cadrage (pas de
pré-constitution) : il reste le point de convergence/handoff produisant la `converged-constitution`.
Le manifeste reçoit un bloc **`assembly`**. Écriture = read-modify-write + revalidation JSON.

## Convergence (mapping 3 faces → SpecKit)
Voir `references/speckit-mapping.md`. **Clé de jointure des 3 faces = le use case (`uc`)** (registre
canonique `architecture.feature_sequence` = objets `{id, ucs, name, mvp}`, `ucs` étant une
**liste** — une feature peut bundler plusieurs use cases en cas de fusion). Faces **fonctionnelle** (brief
cadrage) et **technique** (architecte) jointes **par use case** ; la **face design est globale** (réf. du
design system Claude Design synchronisé via `/design-sync` + `design-guidelines.md`, appliquée à tous les
écrans). Résumé : *fonctionnel* (brief cadrage + parcours du cadrage) → User Scenarios + FR ; *technique*
(scénarios qualité architecte) + *design* (socle a11y des guidelines) → Success Criteria ; glossaire → Key
Entities ; faces technique/design en annexe → Technical Context du futur `plan.md`. La constitution
converge les **principes non négociables** des 3 contrats, **dont les règles design-sync (§6)** : tout
écran dérive du design system synchronisé (aucune valeur de style en dur), états couverts, contrat
d'erreur — gravées aussi dans le `claude.md` et la CI.

## Ordre de remplissage (dépendances)
glossaire consolidé → couture 3-faces par feature → rapport de cohérence (porte) →
constitution + CLAUDE.md + MEMORY.md + seeds spec.md → guidelines → plan d'attaque →
(porte équipe) CI + init Linear.

## Conventions partagées
`references/interactive-loop.md`, `references/ux-conventions.md`. Référence clé :
`references/speckit-mapping.md` ; `references/linear-guide.md` (init Linear via **clé API
personnelle dans `.env`** + API GraphQL, **après la porte** ; couvre aussi la transition aval
**Todo → En cours** via `issueUpdate`). Gabarits aval : `templates/linear-start-hook.py` +
`templates/claude-settings-hook.json` (hook `PostToolUse` généré dans le repo cible par
`assembleur-amorce`). Garde-fou déterministe : `scripts/check_assembly.py`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python scripts/check_assembly.py <projet>/.factory/manifest.json
```

## Invariants
Proposer/pas décider (cohérence validée par l'humain, découpage validé par l'équipe) ;
**effets de bord gated** (l'assembleur génère ; l'équipe lance la CI ; Linear créé live
**seulement après la porte équipe**) ; **`specify init` est une précondition** (lancé par l'équipe
**avant** la convergence — `assembleur-init` l'exige) pour que la constitution convergée **remplace**
le gabarit de SpecKit sans être réécrasée ; constitution = vrai fichier au format SpecKit ; marquer/pas inventer (`[À VALIDER]`/`NEEDS CLARIFICATION`) ; traçabilité
`(src: cadrage | architecte | designer)` ; refus et restitutions en langage naturel.
