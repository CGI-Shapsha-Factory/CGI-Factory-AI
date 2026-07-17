# couts : mesure du coût de simulation

Plugin Claude qui mesure **ce que coûterait la fabrication au tarif API** - le **coût de simulation**
(une estimation, jamais un montant facturé). Simple et autonome : tout s'installe et se mesure dans le
**dossier courant**.

## Principe
Un hook **`SessionEnd`** lit, **à la fin de chaque session**, le transcript complet et en produit **un
enregistrement par message** (= une requête/réponse API) : les **5 catégories** (entrée, sortie, lecture
cache, écriture cache **5min + 1h**), **dédupliquées** (le streaming réécrit le même message -> on garde
la dernière valeur), valorisées via une **table de prix datée par tier** (Haiku/Sonnet/Opus/Fable). Il
écrit **un fichier par session** dans `.factory/couts/`, réécrit à chaque fin de session. Ce dossier est
**git-ignoré** (données individuelles, jamais poussées au repo).

Le compteur est **ancré sur son propre emplacement** : il n'écrit que dans le `.factory/couts/` du
dossier où il a été posé, et **ne mesure que les sessions lancées dans ce dossier**.

**Pourquoi la fin de session, pas un hook par tour** : les hooks Claude Code sont **bloquants** - un
hook à chaque tour rallonge chaque interaction (+13-16 s rapportés). `SessionEnd` tire **une fois, à la
fin** -> **zéro latence pendant le dev**, sans rien perdre de la granularité (un enregistrement par
message, relu du transcript). Pour un rollup **organisation** sans hook par machine : OpenTelemetry
(voir `references/OTEL.md`).

## Les 2 skills
| # | Skill | Rôle | Quand |
|---|-------|------|-------|
| 0 | `couts-init` | Pose le compteur **dans le dossier courant** (hook `SessionEnd` + table de prix), sans question ni écrasement des hooks existants | **tôt**, avant de travailler |
| 1 | `couts-rapport` | Restitue un **tableau par session** (tokens input/output + coût en euros) ; écrit un rapport **versionné** (jamais d'écrasement) | à tout moment |

## Le rapport (par session)
`couts-rapport` produit un tableau, une ligne par session :

| Session (début -> fin) | Tokens input | Tokens output | Coût (€) |
|---|---|---|---|

- **Session** : dates début/fin au format `JJ-MM`.
- **Tokens input** : tokens d'entrée bruts (hors cache).
- **Tokens output** : tokens de sortie.
- **Coût (€)** : coût complet de simulation (input + output + cache lu + cache écrit, tarif par tier),
  converti en euros via un **taux de change figé dans le script** (`cost_report.py`).
- Une **ligne Total** agrège les trois colonnes.

**Versionnage** : chaque exécution écrit un **nouveau fichier**, jamais un écrasement -
`rapport-couts.md` au 1ᵉʳ run, puis `rapport-couts-2.md`, `rapport-couts-3.md`, ... Le script renvoie le
chemin du fichier écrit.

## Les points gravés dans le code
1. **Dédup** par `(message.id, requestId)` en gardant la **dernière** valeur (sinon total gonflé) - au
   sein d'une session (streaming) **et globalement au rapport** (reprise/fork comptés une seule fois).
2. **Table de prix externe et datée** (`.factory/couts/price-table.json`), jamais en dur ; chaque coût
   porte sa date.
3. **Estimation, pas facturé** : le journal local est une **simulation** au tarif API.
4. **Dossier courant** : installation et mesure confinées au dossier où la session est lancée.

## Structure
```
couts/
├── .claude-plugin/plugin.json
├── skills/{couts-init, couts-rapport}/SKILL.md
├── references/   # turn_cost.py (hook SessionEnd) · cost_report.py · install_cost_hook.py · price-table.json · OTEL.md
├── scripts/check_costs.py
└── README.md
```

## Portée
**Simulation seule** - aucun coût réel, aucune saisie manuelle, aucun fichier de config. Mesure **à la
fin de session** (un enregistrement par message). Rollup org via OpenTelemetry (`references/OTEL.md`).
