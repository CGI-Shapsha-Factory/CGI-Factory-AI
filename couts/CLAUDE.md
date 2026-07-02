# CLAUDE.md — plugin `couts`

This file provides guidance to Claude Code (claude.ai/code) when working **on the `couts` plugin**
(this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`couts` = **mesure transversale des coûts** de fabrication de la Factory (pas une phase). Deux chiffres
jamais mélangés : le **coût réel** (abonnements Max fixes + usages clé API + Cowork, saisis depuis la
Console) et le **coût de simulation** (les tokens des sessions valorisés au tarif API — le chiffre
commercialement défendable). Skills Markdown + scripts Python ; pas de build/test.

## Langue & invocation
- **Tout en français** ; identifiants machine et noms d'outils/formats restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/couts:<skill>` + auto par le modèle.

## Les 3 skills
- `couts-init` — pose le compteur **à la racine** (à lancer tôt, après `cadrage-init`) : copie
  `turn_cost.py` en `.claude/hooks/`, **fusionne** le hook `SessionEnd` dans `.claude/settings.json`
  (sans écraser les hooks de test de l'architecte), installe la table de prix datée + la config dans
  `.factory/couts/`, crée `.factory/couts/` + **`.gitignore`** (données individuelles, jamais poussées).
- `couts-rapport` — restitue les **2 vues** (réel vs simulation ventilée par phase / feature / **tier**).
- `couts-total` — produit un **bilan unique partageable** (total tokens, coût estimé, sessions) pour le
  chef d'équipe ; écrit `.factory/couts/bilan-couts.md`.

## Le compteur (`references/turn_cost.py`) — hook `SessionEnd` (écriture en fin de session)
Best-effort (ne bloque jamais, exit 0). **Un seul comportement**, déclenché par `SessionEnd` : lit
`transcript_path` (stdin), valide le chemin, lit le **transcript complet** → **dédup streaming
`(message.id, requestId)` en gardant la DERNIÈRE valeur** (le streaming réécrit le même message ; garder la
1ʳᵉ sous-compte, bug ccusage #888) → **un enregistrement par message assistant** (= une requête/réponse
API) avec 5 catégories (`input`, `output`, `cache_read`, `cache_write_5m`, `cache_write_1h`) → tarif
**par tier** (**1h = 2× input**, non porté par LiteLLM) → attribution **phase (namespace skill) XOR feature
(branche `NNN-` → `feature_sequence`)**, sinon `autre` → **RÉÉCRIT** (overwrite) le fichier de la session
`.factory/couts/<aaaa-mm>/<session-id>.jsonl`. Chaque enregistrement porte sa clé
**`key:"<message.id>:<requestId>"`** (dédup globale au rapport).

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
est **git-ignoré** (données individuelles, jamais poussées au repo). Table de prix + config dans
`.factory/couts/`. **Partage au chef d'équipe** via `couts-total` (un seul fichier, remis à la main) ou
rollup org via OTel.

**Reprise de session** : (1) **même id** → réécriture idempotente du fichier depuis le transcript complet
(pas de doublon) ; (2) **nouvel id qui rejoue** l'historique → chaque enregistrement porte sa `key`
`(message.id, requestId)` → `cost_report.py` **déduplique GLOBALEMENT** (chaque requête comptée une fois).

## Table de prix (`references/price-table.json`, datée)
Structurée par **tier** : `{ tiers:{haiku,sonnet,opus,fable}, overrides:{<model-id>}, cache_write_1h_multiplier }`.
Résolveur `model-id → tier` dans `turn_cost.py` (sous-chaîne + `overrides` pour les versions au prix
différent, ex. Opus 4.1 = 3×). Externe et **datée** (jamais en dur).

## Coût réel vs simulation
Simulation = local (journal, estimation). Réel = `cost-config.json` (abonnements Max + montants API/Cowork
saisis Console). Post-v0 : auto-pull Admin Cost API (`/v1/organizations/cost_report`, clé `sk-ant-admin`).
**Ne jamais** présenter la simulation comme du réel.

## Manifeste
Bloc `costs` : `{ installed, hook:"SessionEnd", price_table_date, gitignored:true }`.

## Cowork
Le futur `cowork.md` (généré par l'assembleur) réserve « un pointeur vers la source des coûts » → pointera
sur `.factory/couts/` + `/couts:couts-rapport`. v0 = ligne globale manuelle.

## Scripts
`references/turn_cost.py` (compteur, hook `SessionEnd`), `references/cost_report.py` (2 restitutions +
ventilation tier, dédup globale par `key`), `references/cost_total.py` (bilan unique partageable),
`references/install_cost_hook.py` (fusion hook SessionEnd),
`references/{price-table.json, cost-config.json}`, `references/OTEL.md` (rollup org).
Garde-fou : `scripts/check_costs.py`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python -m py_compile references/turn_cost.py references/cost_report.py references/cost_total.py references/install_cost_hook.py scripts/check_costs.py
python scripts/check_costs.py <projet>/.factory/manifest.json
```

## Invariants
**Fin de session** (hook `SessionEnd`, réécriture idempotente du fichier de session ; **zéro latence par
tour**) ; **granularité par message** conservée (relue du transcript) ; deux chiffres jamais mélangés
(réel = plateforme + abonnements ; local = estimation) ; **dédup `(message.id, requestId)` last-wins**
(streaming) **puis dédup globale par `key`** au rapport (reprise/fork comptés une fois) ; **5 catégories**
dont **cache 1h à 2×** ; **table de prix par tier, externe et datée** ; attribution **phase XOR feature**
(lue du contexte) ; **un fichier par session** ; installation **fusionnante** (ne jamais écraser un hook
existant) ; restitution en prose.
