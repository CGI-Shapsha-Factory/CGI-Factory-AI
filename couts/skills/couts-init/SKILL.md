---
name: couts-init
description: Pose le compteur de coûts (hook SessionEnd qui journalise à la fin de session, sans latence par tour + table de prix + config), à lancer tôt après cadrage-init.
---

# couts-init

Installe le **dispositif de mesure des coûts** à la racine du projet. À lancer **tôt** — juste après
`/cadrage:cadrage-init` — pour que **toutes les sessions** (chaque prompt → réponse, du cadrage au build
SpecKit) soient mesurées. Ce qui n'est pas installé avant une session n'est journalisé qu'a posteriori si le
transcript existe encore : ne pas tarder.

## Pré-requis (vérification silencieuse)
`.factory/` existe (cadrage-init a tourné). Sinon, orienter en clair vers `/cadrage:cadrage-init`.
**Idempotent** : n'installe que le manquant, ne réécrit rien.

## Ce que ça mesure (contexte)
Le compteur produit **un enregistrement par message** (= une requête/réponse API) : entrée + sortie +
**cache lu** + **cache écrit (5 min et 1 h, séparés)**, tarifés par **tier** (Haiku/Sonnet/Opus/Fable).
C'est le **coût de simulation** (estimation). Le **coût réel** (abonnements Max fixes + usages clé API +
Cowork) se saisit à la main dans la config. **Ne jamais confondre.**

**Pourquoi à la fin de session, pas par tour** : les hooks Claude Code sont **bloquants** — un hook lancé à
chaque tour rallonge chaque interaction (des retours réels rapportent +13-16 s/tour). Le hook `SessionEnd`
tire **une seule fois, à la fin** → **zéro latence pendant le dev**, tout en gardant la **granularité par
message** (relue du transcript complet).

## Procédure
1. **Copier le script** dans `.claude/hooks/` (créer les dossiers) :
   `references/turn_cost.py` → **`.claude/hooks/turn_cost.py`**.
2. **Enregistrer le hook (par fusion)** : lancer
   `python "${CLAUDE_PLUGIN_ROOT}/references/install_cost_hook.py" <racine-projet>` — il ajoute le hook
   **`SessionEnd`** dans `.claude/settings.json` **sans écraser** les hooks existants (ex.
   `Stop`/`PostToolUse` de test de l'architecte). Adapter `python` → `py -3` si besoin sur Windows.
3. **Table de prix datée** : `references/price-table.json` → `.factory/couts/price-table.json` (si absent).
   Structurée par **tier** (+ overrides de version) ; à mettre à jour à la main — chaque coût porte sa date.
4. **Config** : `references/cost-config.json` → `.factory/couts/cost-config.json` (si absent).
5. **Journal** : créer `.factory/couts/` (un fichier par session, réécrit à chaque fin de session).
   **Git-ignorer** en complétant le `.gitignore` à la racine (créer si absent) : ajouter la ligne
   `.factory/couts/` (données individuelles, jamais poussées). Confirmer en clair.
6. **Manifeste** (en silence) : bloc `costs` : `{ "installed": true, "hook": "SessionEnd",
   "price_table_date": "<date>", "gitignored": true }`.

## Après l'installation
Dire en clair ce qui a été posé, puis **rappeler de renseigner `.factory/couts/cost-config.json`** :
développeurs par forfait Max, taux de change, et (quand disponibles) montants réels API + Cowork lus sur la
Console. Sans ça, seul le coût de **simulation** sera chiffré.

## Reprise de session (gérée)
Si le développeur **reprend** une session : à la fin, le fichier de session est **réécrit** depuis le
transcript complet (même id → mise à jour, pas de doublon). Si la reprise crée un **nouvel id qui rejoue**
l'historique, chaque enregistrement porte sa clé `(message.id, requestId)` → `couts-rapport` **déduplique
globalement** (chaque requête comptée une seule fois).

## Porte de sortie
- `.claude/hooks/turn_cost.py` présent ; `.claude/settings.json` contient le hook `SessionEnd` du compteur
  (les autres hooks préservés).
- `.factory/couts/{price-table.json, cost-config.json}` présents ; `.factory/couts/` existe.
- `.gitignore` contient `.factory/couts/` (données individuelles, jamais poussées) ; manifeste avec le bloc `costs`.
- Vérifier : `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_costs.py" <racine>/.factory/manifest.json`
  (s'il est **introuvable** ou renvoie **exit 1**, le dire en clair — ne pas conclure « posé » sans cette vérif).

## Règles invariantes
- **Fin de session, pas par tour.** Le journal est écrit au `SessionEnd` → aucune latence pendant les tours ;
  la granularité par message est conservée (relue du transcript).
- **Estimation ≠ réel.** Le journal produit une estimation (simulation) ; « réel » = abonnements + plateforme.
- **Ne rien écraser.** L'installation du hook est une **fusion** dans `.claude/settings.json`.

Étape suivante : continuer le cadrage (`/cadrage:cadrage-extraction`). Le rapport est disponible à tout moment via `/couts:couts-rapport`. Pour produire un bilan partageable pour le chef d'équipe : `/couts:couts-total`.
