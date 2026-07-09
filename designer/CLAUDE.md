# CLAUDE.md — plugin `designer`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`designer` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`designer` = **phase 3** de la Factory (contrat de design), repensé comme un **atelier de conception
dirigé**. Son cœur est une **checklist de couverture** (3 blocs : fondation / expérience /
technique-qui-se-voit) **pré-remplie par les handoffs** Cadrage (C) et Architecte (A), **co-construite**
avec l'humain (H), qui garantit que **rien d'important n'est oublié avant Claude Design**. **Il ne génère
PAS le design system** : celui-ci naît dans **Claude Design** (nativement) et son **export est committé**
dans `designer-out/maquette-de-claude-design/`. Le plugin produit le **prompt Claude Design**, le **rapport de
couverture** et le **handoff design**. Ce sont des **skills Markdown** ; pas de build/test.

## Décision structurante (spec)
Le design system **n'est pas** un fichier produit par un skill. Le plugin n'écrit **plus** de tokens DTCG
ni de dossier `design-system/`. Il **mène l'atelier** puis **prépare le prompt** ; Claude Design crée le
système, son **export est committé** dans `designer-out/maquette-de-claude-design/`, l'humain le valide, puis
il passe à la fabrication. Pas de front imposé CGI : **feuille blanche stylistique** possible (la marque est
une entrée optionnelle).

## Langue & invocation
- **Tout en français** ; seuls les identifiants/valeurs machine et noms d'outils/formats (Claude Design,
  WCAG, ARIA) restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/designer:<skill>` + auto par le modèle.

## Les 3 skills (découpage justifié)
- `designer-init` — setup (zéro décision) : installe les 4 gabarits + sème la **checklist** dans le
  manifeste. **Jamais bloquant** : amorce le socle **toujours**, puis **signale** (sans refuser) si la
  maquette validée / l'architecture validée / les *Décisions à impact design* manquent.
- `designer-atelier` — **l'atelier** : ingère les handoffs, pré-remplit la checklist, déroule les 3 blocs
  (chaque item : `deduced`/`decided`/`sans_objet`/`open` ; affiché **validé** / **à traiter** / **sans
  objet**), **porte humaine : arbitrage des choix d'expérience**, **résout en session tout point resté à
  traiter**, puis produit le **prompt Claude Design** + le **rapport de couverture** quand la couverture est
  jugée suffisante.
- `designer-coherence` — **après Claude Design** : **porte humaine : validation du système généré** ;
  vérifie la couverture (aucun item `open`) ; produit le **handoff design** (réf. du système synchronisé +
  guidelines : états, patterns d'erreur, socle a11y). → assembleur.

## Workspace & manifeste
Lit les handoffs cadrage (`cadrage-out/`) et architecte (`architecte-out/`). Écrit tout dans
`designer-out/` : rapport de couverture, guidelines, `designer-out/prompts/` (prompt Claude Design, **fichier
plat**) et `designer-out/maquette-de-claude-design/` (export du design system committé par l'humain) ;
dossiers créés par `designer-init`. Les **gabarits** vivent dans `.factory/designer/` (git-ignoré) ; le **manifeste** est **committé** dans `manifest.json`.
**Ne crée plus** `design-system/`. Le manifeste reçoit un bloc **`design`** orienté **couverture** :
`{phase, inputs{cadrage_ok, design_impact_ok}, checklist{foundation[], experience[], technical[]} (items
{id,label,origin,status,note}), coverage_sufficient(H), prompt_path, coverage_report_path,
design_system_ref (chemin de l'export committé), design_validated(H), guidelines_path}`. Écriture = read-modify-write + revalidation JSON.

## Intégration (entrées) — lecture parallèle exhaustive
`designer-atelier` lit les handoffs **en parallèle** (fan-out de sous-agents `designer-reader`,
retours structurés complets + passe de complétude) pour pré-remplir la checklist sans rien manquer :
- **Cadrage** : `product-brief.md` (vision/ton), `glossaire.md` (**entités/données affichées**),
  `spec-index.md` (**parcours/use cases**, lu jamais modifié), **maquette validée** (`demonstrateur`,
  `client_validated`) = **direction, pas cible**.
- **Architecte** : **`impact-design.md`** (section *Décisions à impact design* : stack front + style,
  contrats transverses visibles, conventions d'API qui décident les états d'UI, NFR qui se voient). C'est
  le contrat propre qui alimente le **versant technique** de la checklist.

## Sorties (3)
1. **Prompt Claude Design** (`designer-out/prompts/<NNN>-<JJ-MM>-claude-design.md`, **fichier plat**, **corps seul prêt à coller — plein texte, aucun Markdown**) — fait naître le design system. **Direction visuelle délibérée et CONCRÈTE (anti-slop)** : valeurs **nommées** écrites dans le prompt — palette en **hex + rôle**, **polices nommées**, espacement/rayons — déduites du domaine (ou marque client), **jamais** le violet/indigo par défaut ni polices par défaut, **jamais** les clichés d'IA (bloc « À éviter absolument » + phrase de verrou « tout choix non spécifié = un défaut générique »). *« Silence = Claude defaults »* : on ne laisse aucun choix esthétique au défaut.
2. **Rapport de couverture** (`designer-out/coverage-report.md`) — la trace de la rigueur.
3. **Handoff design** (`designer-out/design-guidelines.md`) — réf. du système synchronisé +
   guidelines, consommé par l'Assembleur (qui grave la règle « tout écran dérive de l'export committé » en constitution/claude.md).

## Portes humaines (2, jamais automatisées)
1. **Arbitrage des choix d'expérience** (pendant l'atelier) — `coverage_sufficient`.
2. **Validation du système généré** (après Claude Design, sur l'export committé) — `design_validated`.

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
python scripts/check_design.py <projet>/manifest.json
```

## Invariants
Proposer/pas décider (arbitrage expérience + validation système = humain) ; **marquer/pas inventer**
(`sans objet` plutôt que forcer) ; **ne pas générer le design system** (Claude Design + export committé) ;
commencer petit (anti-usine-à-gaz) ; traçabilité `(src: cadrage | architecte | maquette | atelier)` ;
accessibilité = item de checklist + gravée en fabrication par l'assembleur ; refus en langage naturel.
