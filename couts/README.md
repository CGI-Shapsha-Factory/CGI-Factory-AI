# couts — mesure des coûts de la Factory

Plugin Claude qui mesure **ce que coûte la fabrication d'un logiciel par la Factory**. Il produit
**deux chiffres, jamais mélangés** :

- **Coût réel (comptable)** — abonnements Max fixes + usages clé API réels + Cowork (lus sur la Console
  Anthropic). Ce que le projet a réellement coûté.
- **Coût de simulation (estimation)** — les tokens des sessions valorisés au tarif API : « combien la
  fabrication coûterait en API ». Le chiffre **commercialement défendable**, ventilé par phase et par feature.

## Principe
Un hook **`SessionEnd`** lit le transcript à la fin de chaque session, extrait les **4 catégories de
tokens** (entrée, sortie, lecture cache, écriture cache 5min/1h), **déduplique**, valorise via une **table
de prix datée**, **attribue** la session à la **phase amont** (le plugin qui tourne) **ou** à la **feature**
(la branche `NNN-`), et écrit **un fichier par session** dans `.factory/costs/`. Aucune saisie humaine :
l'attribution se lit dans le contexte (skill invoqué, branche git).

## Les 2 skills
| # | Skill | Rôle | Quand |
|---|-------|------|-------|
| 0 | `couts-init` | Pose le compteur à la racine (hook `SessionEnd` + lecteur + table de prix + config), sans écraser les hooks de test | **tôt**, juste après `cadrage-init` |
| 1 | `couts-rapport` | Restitue les 2 vues (réel vs simulation ventilée par phase/feature + ligne Cowork) | à tout moment |

## Attribution (deux familles + une ligne à part)
- **Amont** = par plugin : 4 totaux de projet (cadrage, architecture, design, assemblage). Pas de feature.
- **Feature** = par branche `NNN-…` : un total par feature (corrections/évolutions futures incluses via
  leur numéro de feature).
- **Cowork** = ligne globale lue plateforme (v0 : saisie manuelle), sans attribution fine.
On ne croise **jamais** l'amont et la feature dans une même case.

## Ce qu'il faut renseigner
`.factory/cost/cost-config.json` : nombre de développeurs par forfait Max, taux de change, et (quand
disponibles) les montants réels **API** + **Cowork** lus sur la Console (avec leur date). Le coût de
**simulation** se calcule tout seul.

## Les 4 pièges (gravés dans le code)
1. **Dédup** par `(message.id, requestId)` en gardant la **dernière** valeur (sinon total gonflé/faux).
2. **Table de prix externe et datée** (`.factory/cost/price-table.json`), jamais en dur ; chaque coût porte sa date.
3. **Estimation ≠ réel** : le local est une estimation (simulation) ; « réel » = plateforme + abonnements.
4. **Discipline de branche** : l'attribution par feature dépend de travailler sur la bonne branche `NNN-`.

## Structure
```
couts/
├── .claude-plugin/plugin.json
├── skills/{couts-init, couts-rapport}/SKILL.md
├── references/   # session_cost.py (hook) · cost_report.py · install_cost_hook.py · price-table.json · cost-config.json
├── scripts/check_costs.py
└── README.md
```

## Portée v0
Mesure à la **fin de session** (pas en temps réel). Cowork = ligne globale (pas d'attribution fine). On
s'arrête à la **feature** (pas par tâche/fichier). Coût réel plateforme = saisie manuelle (l'auto-pull via
l'Admin Cost API Anthropic viendra ensuite).
