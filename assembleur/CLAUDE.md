# CLAUDE.md — plugin `assembleur`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`assembleur` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`assembleur` = **phase 4** de la Factory (convergence). Il **lit les 3 contrats**
(fonctionnel = cadrage, technique = architecte, design = designer), les **converge**, et
**produit un paquet de handoff** que l'équipe donne à SpecKit. **Il n'écrit jamais dans un
repo cible** : tout sort dans **`assembleur-out/`**. Pas de constitution dans `.specify/`,
pas de `specs/NNN/spec.md`, pas de GLOSSARY.md, **pas de Linear ni de CI**. Ce sont des
**skills Markdown** ; pas de build/test.

## Langue & invocation
- **Tout en français** (skills, templates, artefacts, interaction). Seuls les
  identifiants/valeurs machine et noms d'outils/formats (`spec.md`, `constitution.md`,
  SpecKit, `/design-sync`) restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/assembleur:<skill>` + auto par le modèle.

## Les 2 skills
- `assembleur-init` — setup (zéro décision) : pré-requis = **les 3 contrats validés** ; installe
  les gabarits ; crée `assembleur-out/` ; étend le manifeste (bloc `assembly` allégé). **Aucun
  repo cible à capturer.**
- `assembleur-convergence` — **lit les 3 contrats en parallèle** (5 sous-agents `contract-reader`,
  map-reduce), converge, **produit le paquet** dans `assembleur-out/`, **résout les marqueurs en
  session**, et fait la cohérence (porte humaine : *garant de cohérence*).

## Le paquet `assembleur-out/`
```
assembleur-out/
├── pre-constitution.md        # principes non négociables, format constitution.md (→ /speckit.constitution)
├── features/NNN-…spec-seed.md  # une graine par feature, format spec.md (→ /speckit.specify)
├── feature-map.md             # séquence + couplage/dépendances + walking skeleton
├── technical-context.md       # Technical Context (→ /speckit.plan)
├── CLAUDE.md                  # CLAUDE.md projet (< 200 lignes, @imports memory/)
├── memory/{MEMORY,domain,architecture,design,features}.md
├── coherence-report.md
└── attack-plan.md
```
Le manifeste et les gabarits vivent dans `.factory/`. Écriture = read-modify-write + revalidation JSON.

## Lecture parallèle (map-reduce)
`assembleur-convergence` est l'orchestrateur ; il dispatche **5 lecteurs** (`agents/contract-reader.md`)
en parallèle (fonctionnel, domaine, technique, décisions, design), chacun avec un schéma de sortie,
puis synthétise. Cadrage : 3–5 sous-agents, objectif/format/limites clairs (Explore ne lit que des
extraits → on utilise un agent dédié à lecture complète).

## Convergence (mapping 3 faces → SpecKit)
Voir `references/speckit-mapping.md`. **Clé de jointure = le use case** (registre canonique
`architecture.feature_sequence` = objets `{id, ucs, name}`). Fonctionnel + technique joints **par use
case** ; design **global** (système synchronisé via `/design-sync` + guidelines). La pré-constitution
converge les **principes non négociables** des 3 contrats (dont la règle design-sync : tout écran
dérive du design system synchronisé, aucune valeur de style en dur, états couverts, contrat d'erreur).

## Conventions partagées
`references/interactive-loop.md`, `references/ux-conventions.md`, `references/speckit-mapping.md`.
Garde-fou déterministe : `scripts/check_assembly.py` (présence du paquet + aucun marqueur résiduel +
couverture des features). Agent : `agents/contract-reader.md`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python scripts/check_assembly.py <projet>/.factory/manifest.json
```

## Invariants
**Paquet seul** (n'écrit que dans `assembleur-out/`, jamais un fichier que SpecKit génère) ;
proposer/pas décider (cohérence validée par l'humain) ; **rien laissé indéfini** (tout marqueur
résolu en session, en place) ; **contenu seul** (aucune `(src:)`, horodatage, nom de personne) ;
restitutions en prose, manifeste mis à jour en silence.
