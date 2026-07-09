# CLAUDE.md — plugin `couts`

This file provides guidance to Claude Code (claude.ai/code) when working **on the `couts` plugin**
(this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`couts` = **mesure du coût de simulation** de la fabrication (pas une phase). Un seul chiffre : les
tokens des sessions valorisés au **tarif API** (estimation « combien ça coûterait en API », jamais un
montant facturé). **Autonome** et installé dans le **dossier courant**. Skills Markdown + scripts
Python ; pas de build/test. **Pas de coût réel, pas de saisie manuelle, pas de fichier de config.**

## Langue & invocation
- **Tout en français** ; identifiants machine et noms d'outils/formats restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/couts:<skill>` + auto par le modèle.

## Les 2 skills
- `couts-init` — pose le compteur **dans le dossier courant** (à lancer tôt, autonome — pas de
  pré-requis, **aucune question**) : copie `turn_cost.py` en `.claude/hooks/`, **fusionne** le hook
  `SessionEnd` dans `.claude/settings.json` (sans écraser les hooks existants), installe la table de
  prix datée dans `.factory/couts/`, crée `.factory/couts/` + **`.gitignore`** (ligne `.factory/` —
  tout `.factory/` est git-ignoré). Interaction **en français, sans exposer la mécanique**.
- `couts-rapport` — restitue un **tableau par session** (tokens input/output + coût en euros) et écrit
  un rapport **versionné** dans `.factory/couts/` (`rapport-couts.md`, puis `-2`, `-3`… — **jamais
  d'écrasement**).

## Le compteur (`references/turn_cost.py`) — hook `SessionEnd` (écriture en fin de session)
Best-effort (ne bloque jamais, exit 0). **Un seul comportement**, déclenché par `SessionEnd` : lit
`transcript_path` (stdin), valide le chemin, lit le **transcript complet** → **dédup streaming
`(message.id, requestId)` en gardant la DERNIÈRE valeur** (le streaming réécrit le même message ; garder la
1ʳᵉ sous-compte, bug ccusage #888) → **un enregistrement par message assistant** (= une requête/réponse
API) avec 5 catégories (`input`, `output`, `cache_read`, `cache_write_5m`, `cache_write_1h`) → tarif
**par tier** (**1h = 2× input**, non porté par LiteLLM) → **RÉÉCRIT** (overwrite) le fichier de la
session `.factory/couts/<aaaa-mm>/<session-id>.jsonl`. Chaque enregistrement porte sa clé
**`key:"<message.id>:<requestId>"`** (dédup globale au rapport). Le champ `attribution` reste écrit
(exigé par le garde-fou) mais **le rapport ne l'utilise plus** (rapport par session, pas par phase).

**Ancrage (dossier courant).** La racine est **ancrée sur `__file__`** : la copie installée vit à
`<racine>/.claude/hooks/turn_cost.py` → le hook écrit **toujours** dans le `.factory/couts/` de ce
dossier et **ne mesure que les sessions lancées là** (il ne remonte jamais vers un `.factory/` parent).

**Pourquoi à la fin de session, pas par tour** : les hooks sont **bloquants** — un hook par tour rallonge
chaque interaction (+13-16 s rapportés sur des stacks réels). `SessionEnd` tire **une fois, à la fin** →
**zéro latence pendant les tours**, tout en gardant la **granularité par message** (relue du transcript).

## Suivi org (`references/OTEL.md`) — OpenTelemetry, sans hook par machine
Doc (pas de code) : activer `CLAUDE_CODE_ENABLE_TELEMETRY=1` + OTLP (métriques natives
`claude_code.token.usage` / `cost.usage`, par user/modèle) vers un collecteur, via un `settings.json` géré —
pour le rollup au niveau organisation. Alternative au journal-repo. Le journal `.factory/couts/` étant git-ignoré (individuel), OTel est
la voie pour le rollup cross-dev.

## Stockage (individuel, git-ignoré)
**Un fichier par session** `.factory/couts/<aaaa-mm>/<session-id>.jsonl`, **réécrit à chaque `SessionEnd`**
depuis le transcript complet. **Pas d'état/curseur** (on réécrit tout à chaque fois). Tout `.factory/couts/`
est **git-ignoré** (données individuelles, jamais poussées au repo). Table de prix dans
`.factory/couts/`. **Partage au chef d'équipe** : remettre un `rapport-couts.md` (fichier versionné) ou
rollup org via OTel.

**Reprise de session** : (1) **même id** → réécriture idempotente du fichier depuis le transcript complet
(pas de doublon) ; (2) **nouvel id qui rejoue** l'historique → chaque enregistrement porte sa `key`
`(message.id, requestId)` → `cost_report.py` **déduplique GLOBALEMENT** (chaque requête comptée une fois).

## Table de prix (`references/price-table.json`, datée)
Structurée par **tier** : `{ tiers:{haiku,sonnet,opus,fable}, overrides:{<model-id>}, cache_write_1h_multiplier }`.
Résolveur `model-id → tier` dans `turn_cost.py` (sous-chaîne + `overrides` pour les versions au prix
différent, ex. Opus 4.1 = 3×). Externe et **datée** (jamais en dur).

## Rapport (par session, versionné)
`cost_report.py` agrège le journal **par session** : début/fin (`ts` min/max, format `JJ-MM`), tokens
**input** (bruts, hors cache), tokens **output**, et **coût complet** (5 catégories au tarif par tier)
converti en euros via un **taux figé** (`USD_EUR`/`RATE_DATE` en tête du script). Un tableau + une ligne
Total. Aucune ventilation par phase/feature/tier. **Simulation seule.** **Versionnage** (`_next_report_path`) :
chaque run écrit un **nouveau fichier** (`rapport-couts.md`, puis `rapport-couts-2.md`, `-3.md`…) —
**jamais d'écrasement** ; le chemin écrit est renvoyé (stdout + champ `report_path` en `--json`).

## Manifeste (optionnel)
Si un `manifest.json` existe, `couts-init` y ajoute le bloc `costs` :
`{ installed, hook:"SessionEnd", price_table_date, gitignored:true }`. Sinon rien n'est créé (le
garde-fou n'ouvre pas le manifeste).

## Scripts
`references/turn_cost.py` (compteur, hook `SessionEnd`, racine ancrée `__file__`),
`references/cost_report.py` (rapport **par session** versionné + taux figé, dédup globale par `key`,
localise le journal `.factory/couts/` avec journal, pas le git root), `references/install_cost_hook.py`
(fusion hook SessionEnd, cible le dossier courant), `references/price-table.json`,
`references/OTEL.md` (rollup org). Garde-fou : `scripts/check_costs.py`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python -m py_compile references/turn_cost.py references/cost_report.py references/install_cost_hook.py scripts/check_costs.py
python scripts/check_costs.py <projet>/manifest.json
```

## Invariants
**Simulation seule** (estimation au tarif API, jamais un montant facturé ; pas de config, pas de saisie
manuelle) ; **dossier courant** (installation + mesure confinées au dossier de la session, hook ancré sur
`__file__`) ; **fin de session** (hook `SessionEnd`, réécriture idempotente du fichier de session ;
**zéro latence par tour**) ; **granularité par message** conservée (relue du transcript) ; **dédup
`(message.id, requestId)` last-wins** (streaming) **puis dédup globale par `key`** au rapport
(reprise/fork comptés une fois) ; **5 catégories** dont **cache 1h à 2×** ; **table de prix par tier,
externe et datée** ; **rapport par session** (pas de ventilation phase/feature/tier) ; installation
**fusionnante** (ne jamais écraser un hook existant) ; **interaction en français, sans mécanique
exposée** ; **manifeste silencieux** — ne jamais annoncer que le bloc `costs` est écrit, ni afficher un
`champ: valeur`/`true`/`false` (l'utilisateur ne s'intéresse pas à l'état du manifeste).
