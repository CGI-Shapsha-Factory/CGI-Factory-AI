---
name: couts-init
description: Pose le compteur de coûts de SIMULATION (hook SessionEnd + table de prix) directement dans le dossier courant. Aucune question, aucun pré-requis : installe et confirme, en français.
---

# couts-init

Installe le **dispositif de mesure du coût de simulation** dans le **dossier où la session est
lancée** (le dossier courant). Autonome : ne dépend d'aucune autre phase, fonctionne même dans un
dossier vide. À lancer une fois, tôt, pour que **toutes les sessions lancées dans ce dossier** soient
mesurées.

## Règles d'interaction (impératif)
- **Tout en français** avec l'utilisateur.
- **Ne jamais poser de question** d'emplacement ni proposer d'options : installer **directement**.
- **Ne jamais décrire la mécanique interne** (scripts, hooks, versions, chemins, éventuels
  décalages de nommage). Pas de liste de fichiers, pas de note technique, pas d'exposé de "blocage".
- **Confirmation finale courte**, en français, sans détail.

## Ce que ça mesure
Le compteur produit **un enregistrement par message** (une requête/réponse API) et l'estime au **tarif
API** (table de prix datée), converti en euros. C'est le **coût de simulation** ("combien cette
fabrication coûterait au tarif API"), **pas** un montant facturé. Rien n'est jamais saisi à la main.

**Pourquoi à la fin de session, pas par tour** : les hooks Claude Code sont **bloquants** - un hook par
tour rallonge chaque interaction. Le hook `SessionEnd` tire **une seule fois, à la fin** -> **zéro
latence pendant le dev**, tout en gardant la granularité par message (relue du transcript).

## Emplacement d'installation (impératif)
**La racine d'installation est le dossier courant** (celui où tourne la session) - **jamais** un
dossier parent, **jamais** un `.factory/` / `factory-docs/` situé plus haut. Tout est posé sous ce
dossier :
- `.claude/hooks/turn_cost.py`
- `.claude/settings.json` (hook `SessionEnd`, par fusion)
- `.factory/couts/price-table.json`
- `.factory/couts/` (le journal - un `.jsonl` par session)
- `.gitignore` (pour ignorer tout `.factory/`)

Le compteur est **ancré sur son propre emplacement** : il n'écrit que dans le `.factory/couts/` du
dossier où il est posé, et ne mesure **que** les sessions lancées dans ce dossier.

## Procédure (idempotent : n'installe que le manquant)
1. **Copier le compteur + enregistrer le hook (déterministe, par fusion, sans écraser l'existant)** :
   lancer `python "${CLAUDE_PLUGIN_ROOT}/references/install_cost_hook.py"` **sans argument** (il cible
   le dossier courant). Le script fait les deux gestes lui-même : il copie `turn_cost.py` ->
   `<dossier courant>/.claude/hooks/` puis ajoute le hook `SessionEnd` dans `.claude/settings.json`
   (commande ancrée sur `${CLAUDE_PROJECT_DIR}`, lanceur Python détecté à l'installation). Adapter
   `python` -> `py -3` si besoin sur Windows pour lancer l'installeur lui-même.
2. **Table de prix datée** : `references/price-table.json` -> `.factory/couts/price-table.json`
   (si absent).
3. **Journal** : créer `.factory/couts/` ; **git-ignorer tout `.factory/`** en ajoutant la ligne
   `.factory/` au `.gitignore` du dossier courant (le créer si absent ; ne pas dupliquer si déjà
   présent). Tout `.factory/` est local, non versionné.
4. **Manifeste (optionnel, silencieux)** : si `<dossier courant>/manifest.json` existe, y
   ajouter le bloc `costs` `{ "installed": true, "hook": "SessionEnd", "price_table_date": "<date>",
   "gitignored": true }`. **S'il n'existe pas, ne rien créer** - l'outil fonctionne sans.

## Reprise de session (gérée)
À chaque fin de session, le fichier de la session est **réécrit** depuis le transcript complet (même id
-> mise à jour, pas de doublon). Un nouvel id qui rejoue l'historique est **dédupliqué globalement** au
rapport (chaque requête comptée une seule fois).

## Porte de sortie (vérification silencieuse)
- `.claude/hooks/turn_cost.py` présent ; `.claude/settings.json` contient le hook `SessionEnd` du
  compteur (les autres hooks préservés).
- `.factory/couts/price-table.json` présent ; `.factory/couts/` existe ; `.gitignore` couvre
  `.factory/` (donc `.factory/couts/`).
- Vérifier : `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_costs.py" <dossier courant>/manifest.json`
  (exit 0 attendu ; s'il renvoie exit 1, corriger le manquant sans l'exposer en détail).

## Règles invariantes
- **Simulation seule.** Aucun coût réel, aucune saisie manuelle, aucun fichier de config.
- **Dossier courant.** Installation et mesure sont confinées au dossier où la session est lancée.
- **Fin de session, pas par tour.** Zéro latence pendant les tours ; granularité par message conservée.
- **Ne rien écraser.** L'enregistrement du hook est une **fusion** dans `.claude/settings.json`.
- **Interaction en français, sans mécanique exposée.**

Confirmation à donner (courte, français) : "Dispositif de mesure des coûts installé dans ce dossier.
Rapport disponible via `/couts:couts-rapport`."
