---
name: couts-rapport
description: Restitue le coût de simulation du projet - un tableau par session (tokens input/output + coût en euros), à partir du journal .factory/couts/.
---

# couts-rapport

Produit le **rapport de coût de simulation** à partir du journal (`.factory/couts/`). C'est une
**estimation** au tarif API ("combien cette fabrication coûterait en API"), **pas** un montant
facturé. Tout en **français**.

## Pré-requis (vérification silencieuse)
`couts-init` a tourné (`.factory/couts/` existe). Sinon, orienter en clair vers `/couts:couts-init`.

## Procédure
1. Lancer `python "${CLAUDE_PLUGIN_ROOT}/references/cost_report.py"` **sans argument de racine** (adapter
   `py -3` si besoin) - le script **localise tout seul** le journal (`.factory/couts/` contenant les
   `.jsonl`) depuis le dossier courant, en descendant au besoin ; **ne pas** passer le git root. Le
   script lit le journal, **déduplique globalement par clé `(message.id, requestId)`**
   (reprise/fork comptés une seule fois), agrège **par session**, valorise via la table de prix datée,
   convertit en euros avec le taux figé dans le script, et écrit un **nouveau fichier versionné**
   dans `.factory/couts/` (`rapport-couts.md`, puis `rapport-couts-2.md`, ... - jamais d'écrasement).
2. **Restituer le tableau** (une ligne par session) :

   | Session (début -> fin) | Tokens input | Tokens output | Coût (€) |
   |---|---|---|---|

   - **Session** : dates de début et de fin au format `JJ-MM`.
   - **Tokens input** : tokens d'entrée **bruts** (hors cache).
   - **Tokens output** : tokens de sortie.
   - **Coût (€)** : coût **complet** de simulation (input + output + cache lu + cache écrit, au tarif
     par tier), converti en euros.
   - Une **ligne Total** agrège les trois colonnes.

## Règles invariantes
- **Simulation seule.** C'est une **estimation** au tarif API, jamais un montant facturé.
- **Daté.** Le tableau renvoie à la date de la table de prix et au taux de change figé (comparable dans
  le temps).
- **Par session.** Pas de ventilation par phase, feature, ou tier - seulement le total par session.
- **Rien de la mécanique affiché.** Restitution en clair, en français.

**Versionnage** : chaque exécution écrit un **nouveau fichier**, jamais un écrasement -
`rapport-couts.md` au 1ᵉʳ run, puis `rapport-couts-2.md`, `rapport-couts-3.md`, ... Indiquer en clair
**le chemin du fichier écrit** (le script le renvoie).

Étape suivante : relancer ce rapport quand voulu (un nouveau fichier numéroté sera créé à chaque fois).
