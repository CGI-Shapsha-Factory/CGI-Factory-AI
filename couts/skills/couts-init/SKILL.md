---
name: couts-init
description: Pose le compteur de coûts EN TEMPS RÉEL (hook Stop par tour + SessionEnd de réconciliation + lecteur + table de prix + config), à lancer tôt après cadrage-init.
---

# couts-init

Installe le **dispositif de mesure des coûts en temps réel** à la racine du projet. À lancer **tôt** —
juste après `/cadrage:cadrage-init` — pour que **tous les tours** (chaque prompt → réponse) soient mesurés,
du cadrage au build SpecKit. Ce qui n'est pas mesuré avant l'installation est perdu : ne pas tarder.

## Pré-requis (vérification silencieuse)
`.factory/` existe (cadrage-init a tourné). Sinon, orienter en clair vers `/cadrage:cadrage-init`.
**Idempotent** : n'installe que le manquant, ne réécrit rien.

## Ce que ça mesure (contexte)
À **chaque tour** (prompt → réponse), le compteur relève les tokens de ce tour et les journalise
**immédiatement** : entrée + sortie + **cache lu** + **cache écrit (5min et 1h, séparés)**, tarifés par
**tier** (Haiku/Sonnet/Opus/Fable). C'est le **coût de simulation** (estimation). Le **coût réel**
(abonnements Max fixes + usages clé API + Cowork) se saisit à la main dans la config. **Ne jamais confondre.**
Remarque : le compte exact des tokens d'entrée (historique + cache) n'est connu qu'**à la réponse**
(côté serveur) — on mesure donc chaque tour juste après sa réponse, pas à l'envoi du prompt.

## Procédure
1. **Copier le lecteur** : `references/turn_cost.py` → **`.claude/hooks/turn_cost.py`** (créer les dossiers).
2. **Enregistrer les hooks (par fusion)** : lancer
   `python "${CLAUDE_PLUGIN_ROOT}/references/install_cost_hook.py" <racine-projet>` — il ajoute, **sans
   écraser** les hooks existants (ex. `Stop`/`PostToolUse` de test de l'architecte) :
   - **`Stop` → `turn_cost.py turn`** : mesure **en temps réel, une ligne par tour** (notre hook ne bloque
     jamais ; il coexiste avec le `Stop` de test qui, lui, peut bloquer) ;
   - **`SessionEnd` → `turn_cost.py reconcile`** : backstop qui rattrape un tour éventuellement raté.
   Adapter `python` → `py -3` si besoin sur Windows.
3. **Table de prix datée** : `references/price-table.json` → `.factory/cost/price-table.json` (si absent).
   Structurée par **tier** (+ overrides de version) ; à mettre à jour à la main — chaque coût porte sa date.
4. **Config** : `references/cost-config.json` → `.factory/cost/cost-config.json` (si absent).
5. **Journal + état** : créer `.factory/costs/` (une ligne par tour, un fichier par session).
   Ajouter au `.gitignore` (racine) : `.factory/costs/.state/` (curseur local par session, **non partagé**)
   et `.factory/costs/**/*.jsonl merge=union` (filet anti-conflit du journal partagé).
6. **Manifeste** (en silence) : bloc `costs` : `{ "installed": true, "hooks": ["Stop", "SessionEnd"],
   "price_table_date": "<date>" }`.

## Après l'installation
Dire en clair ce qui a été posé, puis **rappeler de renseigner `.factory/cost/cost-config.json`** :
développeurs par forfait Max, taux de change, et (quand disponibles) montants réels API + Cowork lus sur la
Console. Sans ça, seul le coût de **simulation** sera chiffré.

## Porte de sortie
- `.claude/hooks/turn_cost.py` présent ; `.claude/settings.json` contient les hooks `Stop` **et**
  `SessionEnd` du compteur (les autres hooks préservés).
- `.factory/cost/{price-table.json, cost-config.json}` présents ; `.factory/costs/` existe.
- `.gitignore` ignore `.factory/costs/.state/` ; manifeste avec le bloc `costs`.
- Vérifier : `python scripts/check_costs.py <racine>/.factory/manifest.json`.

## Règles invariantes
- **Temps réel, par tour.** Chaque tour est mesuré immédiatement après sa réponse (hook `Stop`), pas en fin
  de session ; le `SessionEnd` ne sert que de réconciliation.
- **Estimation ≠ réel.** Le journal produit une estimation (simulation) ; « réel » = abonnements + plateforme.
- **Ne rien écraser.** L'installation des hooks est une **fusion** dans `.claude/settings.json`.

Étape suivante : continuer le cadrage (`/cadrage:cadrage-extraction`). Le rapport est disponible à tout moment via `/couts:couts-rapport`.
