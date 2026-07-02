# CLAUDE.md — plugin `couts`

This file provides guidance to Claude Code (claude.ai/code) when working **on the `couts` plugin**
(this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`couts` = **mesure transversale des coûts** de fabrication de la Factory (pas une phase). Il produit
**deux chiffres jamais mélangés** : le **coût réel** (abonnements Max fixes + usages clé API + Cowork,
saisis depuis la Console) et le **coût de simulation** (les tokens des sessions valorisés au tarif API —
le chiffre commercialement défendable). Ce sont des **skills Markdown + scripts Python** ; pas de build/test.

## Langue & invocation
- **Tout en français** ; seuls les identifiants machine et noms d'outils/formats restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/couts:<skill>` + auto par le modèle.

## Les 2 skills
- `couts-init` — pose le compteur **à la racine du projet** (à lancer tôt, après `cadrage-init`) :
  copie `session_cost.py` en `.claude/hooks/`, **fusionne** un hook `SessionEnd` dans
  `.claude/settings.json` (sans écraser les hooks de test de l'architecte), installe la table de prix
  datée + la config dans `.factory/cost/`, crée `.factory/costs/`, ajoute la règle `.gitattributes`.
- `couts-rapport` — restitue les **2 vues** (réel vs simulation ventilée) depuis le journal + la config.

## Le compteur (`references/session_cost.py`, hook SessionEnd)
Best-effort (SessionEnd ne peut pas bloquer). À chaque fin de session : lit `transcript_path` (stdin) →
garde les lignes `assistant` avec `message.usage` → **déduplique par `(message.id, requestId)` en gardant
la DERNIÈRE valeur** (piège : Claude Code réécrit le même message pendant le streaming ; garder la 1ʳᵉ
sous-compte) → somme les **4 catégories** (`input`, `output`, `cache_read`, `cache_write` avec split TTL
`ephemeral_5m`/`ephemeral_1h`) → valorise via `price-table.json` (**1h = 2× input**, non porté par
LiteLLM) → **attribue** (namespace de skill `/cadrage|architecte|designer|assembleur:` → phase ; sinon
branche `NNN-` → feature via `manifest.architecture.feature_sequence` ; sinon `autre` — **jamais les
deux**) → écrit **un fichier par session** `.factory/costs/<aaaa-mm>/<session-id>.jsonl`.

## Stockage (multi-développeurs)
**Un fichier par session** = sans conflit git par construction (deux devs ne touchent jamais le même
fichier), dédup triviale par `session_id`, agrégation par glob. `.gitattributes merge=union` en filet.
Le journal vit dans **`.factory/costs/`** (committé, partagé). La table de prix et la config vivent dans
`.factory/cost/`.

## Coût réel vs simulation
- **Simulation** = local, calculé depuis le journal (estimation). C'est ce que produit le compteur.
- **Réel** = `cost-config.json` (abonnements Max fixes + montants API/Cowork saisis depuis la Console).
  Post-v0 : auto-pull via l'Admin Cost API Anthropic (`/v1/organizations/cost_report`, clé `sk-ant-admin`).
- **Ne jamais** présenter la simulation comme du réel.

## Manifeste
Bloc `costs` : `{ installed, hook:"SessionEnd", price_table_date }`. Écriture read-modify-write.

## Cowork
Le futur `cowork.md` (généré par l'assembleur) réserve « un pointeur vers la source des coûts » → il
pointera sur `.factory/costs/` + `/couts:couts-rapport`. Pour le v0, Cowork est une **ligne globale**
lue plateforme (saisie manuelle en config), sans attribution fine.

## Scripts
`references/session_cost.py` (compteur/hook), `references/cost_report.py` (les 2 restitutions),
`references/install_cost_hook.py` (fusion du hook SessionEnd), `references/{price-table.json,cost-config.json}`
(gabarits copiés dans `.factory/cost/`). Garde-fou : `scripts/check_costs.py`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python -m py_compile references/session_cost.py references/cost_report.py references/install_cost_hook.py scripts/check_costs.py
python scripts/check_costs.py <projet>/.factory/manifest.json
```

## Invariants
Deux chiffres jamais mélangés (réel = plateforme + abonnements ; local = estimation) ; **dédup
`(message.id,requestId)` last-wins** ; **4 catégories** avec cache 1h à 2× ; **table de prix externe et
datée** (jamais en dur) ; attribution **phase XOR feature** (lue du contexte, jamais demandée) ; **un
fichier par session** ; installation **fusionnante** (ne jamais écraser un hook existant) ; restitution
en prose (pas de nom de variable).
