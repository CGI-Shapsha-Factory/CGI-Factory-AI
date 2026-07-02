# couts — mesure des coûts de la Factory

Plugin Claude qui mesure **ce que coûte la fabrication d'un logiciel par la Factory**. Il produit
**deux chiffres, jamais mélangés** :

- **Coût réel (comptable)** — abonnements Max fixes + usages clé API réels + Cowork (lus sur la Console
  Anthropic). Ce que le projet a réellement coûté.
- **Coût de simulation (estimation)** — les tokens des sessions valorisés au tarif API : « combien la
  fabrication coûterait en API ». Le chiffre **commercialement défendable**, ventilé par phase et par feature.

## Principe
Un hook **`SessionEnd`** lit, **à la fin de chaque session**, le transcript complet et en produit **un
enregistrement par message** (= une requête/réponse API) : les **5 catégories** (entrée, sortie, lecture
cache, écriture cache **5min + 1h**), **dédupliquées** (le streaming réécrit le même message → on garde la
dernière valeur), valorisées via une **table de prix datée par tier**, **attribuées** à la **phase amont**
(plugin qui tourne) **ou** à la **feature** (branche `NNN-`). Il écrit **un fichier par session** dans
`.factory/couts/`, réécrit à chaque fin de session. Ce dossier est **git-ignoré**
(données individuelles, jamais poussées) ; le partage au chef d'équipe se fait via `couts-total`.

**Pourquoi la fin de session, pas un hook par tour** : les hooks Claude Code sont **bloquants** — un hook à
chaque tour rallonge chaque interaction (+13-16 s rapportés). `SessionEnd` tire **une fois, à la fin** →
**zéro latence pendant le dev**, sans rien perdre de la granularité (un enregistrement par message, relu du
transcript). Pour un rollup **organisation** sans hook par machine : OpenTelemetry (voir `references/OTEL.md`).

## Les 3 skills
| # | Skill | Rôle | Quand |
|---|-------|------|-------|
| 0 | `couts-init` | Pose le compteur à la racine (hook `SessionEnd` + lecteur + table de prix par tier + config), sans écraser les hooks de test | **tôt**, juste après `cadrage-init` |
| 1 | `couts-rapport` | Restitue les 2 vues (réel vs simulation ventilée par phase/feature/tier + ligne Cowork) | à tout moment |
| 2 | `couts-total` | Produit un bilan unique partageable (total tokens, coût estimé, nb sessions) pour le chef d'équipe ; écrit `.factory/couts/bilan-couts.md` | à la demande |

## Attribution (deux familles + une ligne à part)
- **Amont** = par plugin : 4 totaux de projet (cadrage, architecture, design, assemblage). Pas de feature.
- **Feature** = par branche `NNN-…` : un total par feature (corrections/évolutions futures incluses via
  leur numéro de feature).
- **Cowork** = ligne globale lue plateforme (v0 : saisie manuelle), sans attribution fine.
On ne croise **jamais** l'amont et la feature dans une même case.

## Ce qu'il faut renseigner
`.factory/couts/cost-config.json` : nombre de développeurs par forfait Max, taux de change, et (quand
disponibles) les montants réels **API** + **Cowork** lus sur la Console (avec leur date). Le coût de
**simulation** se calcule tout seul.

## Les 4 pièges (gravés dans le code)
1. **Dédup** par `(message.id, requestId)` en gardant la **dernière** valeur (sinon total gonflé/faux) —
   au sein d'une session (streaming) **et globalement au rapport** (reprise/fork comptés une seule fois).
2. **Table de prix externe et datée** (`.factory/couts/price-table.json`), jamais en dur ; chaque coût porte sa date.
3. **Estimation ≠ réel** : le local est une estimation (simulation) ; « réel » = plateforme + abonnements.
4. **Discipline de branche** : l'attribution par feature dépend de travailler sur la bonne branche `NNN-`.

## Structure
```
couts/
├── .claude-plugin/plugin.json
├── skills/{couts-init, couts-rapport}/SKILL.md
├── references/   # turn_cost.py (hook SessionEnd) · cost_report.py · install_cost_hook.py · price-table.json · cost-config.json · OTEL.md
├── scripts/check_costs.py
└── README.md
```

## Portée v0
Mesure **à la fin de session** (hook `SessionEnd`, un enregistrement par message). Cowork = ligne globale
(pas d'attribution fine). On s'arrête à la **feature** (pas par tâche/fichier). Coût réel plateforme =
saisie manuelle (l'auto-pull via l'Admin Cost API Anthropic viendra ensuite ; rollup org via OpenTelemetry
documenté dans `references/OTEL.md`).
