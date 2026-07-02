---
name: couts-init
description: Pose le compteur de coûts du projet (hook SessionEnd + lecteur + table de prix + config), à lancer tôt après cadrage-init.
---

# couts-init

Installe le **dispositif de mesure des coûts** à la racine du projet. À lancer **tôt** — juste après
`/cadrage:cadrage-init` — pour que **toutes** les sessions soient mesurées (cadrage → build SpecKit).
Ce qui n'est pas mesuré avant l'installation est perdu : ne pas tarder.

## Pré-requis (vérification silencieuse)
`.factory/` existe (cadrage-init a tourné). Sinon, orienter en clair vers `/cadrage:cadrage-init`.
**Idempotent** : ne réécrit aucun fichier existant ; n'installe que le manquant.

## Ce que ça mesure (contexte)
Le compteur produit le **coût de simulation** : les tokens de chaque session, valorisés au tarif API
(estimation). Le **coût réel** (abonnements Max fixes + usages clé API + Cowork) se saisit à la main
dans la config (lu sur la Console Anthropic). **Ne jamais confondre les deux.**

## Procédure
1. **Copier le lecteur** : `references/session_cost.py` → **`.claude/hooks/session_cost.py`** (créer les
   dossiers). C'est le hook `SessionEnd` : à chaque fin de session il lit le transcript, extrait les 4
   catégories de tokens, déduplique, valorise, attribue et journalise.
2. **Enregistrer le hook (par fusion)** : lancer
   `python "${CLAUDE_PLUGIN_ROOT}/references/install_cost_hook.py" <racine-projet>` — il ajoute l'événement
   `SessionEnd` dans `.claude/settings.json` **sans écraser** les hooks existants (ex. `Stop`/`PostToolUse`
   de test posés par l'architecte). Adapter `python` → `py -3` si besoin sur Windows.
3. **Installer la table de prix datée** : `references/price-table.json` → `.factory/cost/price-table.json`
   (si absent). À mettre à jour à la main quand les tarifs changent — chaque coût journalisé porte sa date.
4. **Installer la config** : `references/cost-config.json` → `.factory/cost/cost-config.json` (si absent).
5. **Créer le journal** : dossier `.factory/costs/` (un fichier par session y sera écrit).
6. **`.gitattributes`** (racine) : ajouter `.factory/costs/**/*.jsonl merge=union` (filet anti-conflit
   pour le journal partagé entre développeurs).
7. **Manifeste** (en silence) : ajouter le bloc `costs` : `{ "installed": true, "hook": "SessionEnd",
   "price_table_date": "<date de la table>" }`.

## Après l'installation
Dire en clair ce qui a été posé, puis **rappeler de renseigner `.factory/cost/cost-config.json`** :
le nombre de développeurs par forfait Max, le taux de change, et (quand disponibles) les montants réels
API + Cowork lus sur la Console. Sans ça, seul le coût de **simulation** sera chiffré.

## Porte de sortie
- `.claude/hooks/session_cost.py` présent ; `.claude/settings.json` contient un hook `SessionEnd`
  (les autres hooks préservés).
- `.factory/cost/{price-table.json, cost-config.json}` présents ; `.factory/costs/` existe.
- `.gitattributes` contient la ligne `merge=union` du journal ; manifeste avec le bloc `costs`.
- Rien d'existant n'a été écrasé (idempotence). Vérifier : `python scripts/check_costs.py <racine>/.factory/manifest.json`.

## Règles invariantes
- **Estimation ≠ réel.** Le journal produit une estimation (simulation) ; le mot « réel » est réservé
  aux abonnements + à la plateforme.
- **Poser tôt.** Le hook ne mesure que les sessions postérieures à son installation.
- **Ne rien écraser.** L'installation du hook est une **fusion** dans `.claude/settings.json`.

Étape suivante : continuer le cadrage (`/cadrage:cadrage-extraction`). Le rapport est disponible à tout moment via `/couts:couts-rapport`.
