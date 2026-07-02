# CLAUDE.md — plugin `couts`

This file provides guidance to Claude Code (claude.ai/code) when working **on the `couts` plugin**
(this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`couts` = **mesure transversale des coûts** de fabrication de la Factory (pas une phase), **en temps réel,
par tour**. Deux chiffres jamais mélangés : le **coût réel** (abonnements Max fixes + usages clé API +
Cowork, saisis depuis la Console) et le **coût de simulation** (les tokens des sessions valorisés au tarif
API — le chiffre commercialement défendable). Skills Markdown + scripts Python ; pas de build/test.

## Langue & invocation
- **Tout en français** ; identifiants machine et noms d'outils/formats restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/couts:<skill>` + auto par le modèle.

## Les 2 skills
- `couts-init` — pose le compteur **à la racine** (à lancer tôt, après `cadrage-init`) : copie
  `turn_cost.py` en `.claude/hooks/`, **fusionne** les hooks `Stop` (+ `SessionEnd`) dans
  `.claude/settings.json` (sans écraser les hooks de test de l'architecte), installe la table de prix
  datée + la config dans `.factory/cost/`, crée `.factory/costs/`, gitignore l'état + `merge=union`.
- `couts-rapport` — restitue les **2 vues** (réel vs simulation ventilée par phase / feature / **tier**).

## Le compteur (`references/turn_cost.py`) — hooks `Stop` (temps réel) + `SessionEnd` (backstop)
Best-effort (ne bloque jamais, exit 0). Deux sous-commandes :
- **`turn`** (hook `Stop`, tire à **chaque tour**) : lit `transcript_path` (stdin) ; via un **curseur**
  `.factory/costs/.state/<session-id>.json`, ne lit que **les nouvelles lignes depuis le dernier tour** →
  **dédup `(message.id, requestId)` en gardant la DERNIÈRE valeur** (le streaming réécrit le même message ;
  garder la 1ʳᵉ sous-compte) → 4/5 catégories (`input`, `output`, `cache_read`, `cache_write_5m`,
  `cache_write_1h`) → tarif **par tier** (**1h = 2× input**, non porté par LiteLLM) → attribution **phase
  (namespace skill) XOR feature (branche `NNN-` → `feature_sequence`)**, sinon `autre` → **ajoute une
  ligne-tour** `.factory/costs/<aaaa-mm>/<session-id>.jsonl` **immédiatement**.
- **`reconcile`** (hook `SessionEnd`) : recalcule le total du transcript complet ; si le journal est
  en-dessous (un `Stop` raté), ajoute une ligne `{kind:"reconciliation"}` pour le delta. Ne reconstruit pas
  les frontières de tours (non récupérables) ; ne corrige que le total.

Pourquoi pas à l'envoi du prompt : le compte exact d'entrée (historique + cache) est **calculé côté serveur**
et renvoyé dans l'`usage` de la réponse → on mesure chaque tour **à la réponse** (`Stop`).

## Stockage (multi-développeurs, temps réel)
**Un fichier par session**, **une ligne par tour** (append) → sans conflit git par construction (deux devs
ne touchent jamais le même fichier), dédup par `(session_id, turn)`. Journal committé dans `.factory/costs/`
+ `.gitattributes merge=union` (filet). L'**état/curseur** `.factory/costs/.state/` est **local, gitignoré**
(offset dans un transcript local, non partagé). Table de prix + config dans `.factory/cost/`.

## Table de prix (`references/price-table.json`, datée)
Structurée par **tier** : `{ tiers:{haiku,sonnet,opus,fable}, overrides:{<model-id>}, cache_write_1h_multiplier }`.
Résolveur `model-id → tier` dans `turn_cost.py` (sous-chaîne + `overrides` pour les versions au prix
différent, ex. Opus 4.1 = 3×). Externe et **datée** (jamais en dur).

## Coût réel vs simulation
Simulation = local (journal, estimation). Réel = `cost-config.json` (abonnements Max + montants API/Cowork
saisis Console). Post-v0 : auto-pull Admin Cost API (`/v1/organizations/cost_report`, clé `sk-ant-admin`).
**Ne jamais** présenter la simulation comme du réel.

## Manifeste
Bloc `costs` : `{ installed, hooks:["Stop","SessionEnd"], price_table_date }`.

## Cowork
Le futur `cowork.md` (généré par l'assembleur) réserve « un pointeur vers la source des coûts » → pointera
sur `.factory/costs/` + `/couts:couts-rapport`. v0 = ligne globale manuelle.

## Scripts
`references/turn_cost.py` (compteur, hooks Stop+SessionEnd), `references/cost_report.py` (2 restitutions +
ventilation tier), `references/install_cost_hook.py` (fusion des hooks), `references/{price-table.json,
cost-config.json}`. Garde-fou : `scripts/check_costs.py`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python -m py_compile references/turn_cost.py references/cost_report.py references/install_cost_hook.py scripts/check_costs.py
python scripts/check_costs.py <projet>/.factory/manifest.json
```

## Invariants
**Temps réel par tour** (hook `Stop`, une ligne/tour ; `SessionEnd` = réconciliation) ; deux chiffres jamais
mélangés (réel = plateforme + abonnements ; local = estimation) ; **dédup `(message.id,requestId)` last-wins**
via curseur (pas de double-comptage) ; **4/5 catégories** dont **cache 1h à 2×** ; **table de prix par tier,
externe et datée** ; attribution **phase XOR feature** (lue du contexte) ; **un fichier par session, une
ligne par tour** ; installation **fusionnante** (ne jamais écraser un hook existant) ; restitution en prose.
