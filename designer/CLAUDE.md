# CLAUDE.md — plugin `designer`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`designer` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`designer` = **phase 3** de la Factory (contrat de design), repensé comme un **atelier de conception
dirigé**. Son cœur est une **checklist de couverture** (3 blocs : fondation / expérience /
technique-qui-se-voit) **pré-remplie par les handoffs** Cadrage (C) et Architecte (A), **co-construite**
avec l'humain (H), qui garantit que **rien d'important n'est oublié avant Claude Design**. **Il ne génère
PAS le design system** : celui-ci naît dans **Claude Design** (nativement) et est matérialisé en code par
**`/design-sync`** (outil natif). Le plugin produit le **prompt Claude Design**, le **rapport de
couverture** et le **handoff design**. Ce sont des **skills Markdown** ; pas de build/test.

## Décision structurante (spec)
Le design system **n'est pas** un fichier produit par un skill. Le plugin n'écrit **plus** de tokens DTCG
ni de dossier `design-system/`. Il **mène l'atelier** puis **prépare le prompt** ; Claude Design crée le
système, l'humain le valide, `/design-sync` l'engage vers la fabrication. Pas de front imposé CGI : **feuille
blanche stylistique** possible (la marque est une entrée optionnelle).

## Langue & invocation
- **Tout en français** ; seuls les identifiants/valeurs machine et noms d'outils/formats (`/design-sync`,
  Claude Design, WCAG, ARIA) restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/designer:<skill>` + auto par le modèle.

## Les 3 skills (découpage justifié)
- `designer-init` — setup (zéro décision) : installe les 4 gabarits + sème la **checklist** dans le
  manifeste. Porte : maquette validée **ET** architecture validée **ET** *Décisions à impact design*
  présente.
- `designer-atelier` — **l'atelier** : ingère les handoffs, pré-remplit la checklist, déroule les 3 blocs
  (chaque item : `deduced`/`decided`/`sans_objet`/`open` ; affiché **validé** / **à traiter** / **sans
  objet**), **porte humaine : arbitrage des choix d'expérience**, **résout en session tout point resté à
  traiter**, puis produit le **prompt Claude Design** + le **rapport de couverture** quand la couverture est
  jugée suffisante.
- `designer-coherence` — **après Claude Design** : **porte humaine : validation du système généré** ;
  vérifie la couverture (aucun item `open`) ; produit le **handoff design** (réf. du système synchronisé +
  guidelines : états, patterns d'erreur, socle a11y). → assembleur.

## Workspace & manifeste
Lit les handoffs cadrage (`cadrage-out/`) et architecte (`architecte-out/`). Écrit dans
`designer-out/` (rapport de couverture, guidelines) et `prompts/designer/` (prompt Claude Design, **fichier
plat** ; dossier créé par `designer-init`). Le manifeste et les gabarits vivent dans `.factory/`.
**Ne crée plus** `design-system/`. Le manifeste reçoit un bloc **`design`** orienté **couverture** :
`{phase, inputs{cadrage_ok, design_impact_ok}, checklist{foundation[], experience[], technical[]} (items
{id,label,origin,status,note}), coverage_sufficient(H), prompt_path, coverage_report_path,
design_system_ref, design_system_kind (`claude_design_ref` | `committed_export`), design_validated(H), guidelines_path}`. Écriture = read-modify-write + revalidation JSON.

## Intégration (entrées) — lecture parallèle exhaustive
`designer-atelier` lit les handoffs **en parallèle** (fan-out de sous-agents `designer-reader`,
retours structurés complets + passe de complétude) pour pré-remplir la checklist sans rien manquer :
- **Cadrage** : `product-brief.md` (vision/ton), `glossaire.md` (**entités/données affichées**),
  `spec-index.md` (**parcours/use cases**, lu jamais modifié), **maquette validée** (`demonstrateur`,
  `client_validated`) = **direction, pas cible**.
- **Architecte** : **`design-impact.md`** (section *Décisions à impact design* : stack front + style,
  contrats transverses visibles, conventions d'API qui décident les états d'UI, NFR qui se voient). C'est
  le contrat propre qui alimente le **versant technique** de la checklist.

## Sorties (3)
1. **Prompt Claude Design** (`prompts/designer/<NNN>-<JJ-MM>-claude-design.md`, **fichier plat**, **corps seul prêt à coller**) — fait naître le design system.
2. **Rapport de couverture** (`designer-out/coverage-report.md`) — la trace de la rigueur.
3. **Handoff design** (`designer-out/design-guidelines.md`) — réf. du système synchronisé +
   guidelines, consommé par l'Assembleur (qui grave les règles `/design-sync` en constitution/claude.md/CI).

## Portes humaines (2, jamais automatisées)
1. **Arbitrage des choix d'expérience** (pendant l'atelier) — `coverage_sufficient`.
2. **Validation du système généré** (après Claude Design, avant `/design-sync`) — `design_validated`.

## Conventions partagées
`references/coverage-checklist-guide.md` (définition canonique + ancrages NN/g & WCAG),
`references/states-catalog.md` (états écran/composant + clavier WAI-ARIA APG), `references/question-map.md`
(d'où chaque item se déduit C/A), `references/interactive-loop.md`, `references/ux-conventions.md`.
Agent de lecture : `agents/designer-reader.md` (lecture complète + sortie structurée, dispatché en
parallèle par `designer-atelier`).
Garde-fou déterministe : `scripts/check_design.py` (valide la **couverture** : aucun item `open`, prompt +
rapport + handoff présents — pas des tokens).

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python scripts/check_design.py <projet>/.factory/manifest.json
```

## Invariants
Proposer/pas décider (arbitrage expérience + validation système = humain) ; **marquer/pas inventer**
(`sans objet` plutôt que forcer) ; **ne pas générer le design system** (Claude Design + `/design-sync`) ;
commencer petit (anti-usine-à-gaz) ; traçabilité `(src: cadrage | architecte | maquette | atelier)` ;
accessibilité = item de checklist + gravée en fabrication par l'assembleur ; refus en langage naturel.
