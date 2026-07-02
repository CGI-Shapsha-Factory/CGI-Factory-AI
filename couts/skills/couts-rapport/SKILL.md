---
name: couts-rapport
description: Restitue les deux coûts du projet — réel (comptable) et simulation (estimation, ventilée par phase/feature + Cowork).
---

# couts-rapport

Produit les **deux restitutions** de coût à partir du journal (`.factory/couts/`) et de la config
(`.factory/couts/cost-config.json`). **Ne jamais présenter la simulation comme du réel.**

## Pré-requis (vérification silencieuse)
`couts-init` a tourné (`.factory/couts/` existe). Sinon, orienter en clair vers `/couts:couts-init`.

## Procédure
1. Lancer `python "${CLAUDE_PLUGIN_ROOT}/references/cost_report.py" <racine-projet>` (adapter `py -3` si
   besoin). Le script agrège les sessions du journal par attribution (phase amont / feature / autre),
   valorise via la table de prix datée, lit la config pour le coût réel, **déduplique globalement par clé
   `(message.id, requestId)`** (reprise/fork comptés une seule fois), et écrit `.factory/couts/rapport-couts.md`.
2. **Restituer en prose** (pas de tableau de variables, pas de jargon), en **deux blocs nettement
   séparés et étiquetés** :
   - **Coût réel (comptable)** : abonnements Max fixes + usages API réels + Cowork (les montants
     plateforme viennent de la config, saisis depuis la Console). C'est la vérité comptable.
   - **Coût de simulation (estimation)** : « combien la fabrication coûterait en API » — agrégé depuis les
     **enregistrements par message** (relus du transcript à la fin de session) et ventilé par **phase amont** (cadrage,
     architecture, design, assemblage), **par feature**, ligne **autre**, **ligne Cowork globale**, et
     **par tier de modèle** (Haiku/Sonnet/Opus/Fable). C'est le chiffre commercialement défendable.
3. Donner les montants en **euros** (et USD entre parenthèses), avec les **dates** (table de prix, taux
   de change). Signaler si le coût réel est incomplet (montants plateforme non renseignés dans la config).

## Si des montants réels manquent
Dire en clair qu'il faut compléter `.factory/couts/cost-config.json` : nombre de développeurs par forfait
Max, taux de change, et montants réels **API** + **Cowork** lus sur la Console Anthropic (avec leur date).
Le coût de **simulation**, lui, se calcule tout seul depuis le journal.

## Règles invariantes
- **Deux chiffres, jamais mélangés.** Le mot « réel » = abonnements + plateforme ; le journal local est
  une **estimation** (simulation).
- **Daté.** Chaque montant renvoie à une date de tarif et de change (comparable dans le temps).
- **Attribution : phase XOR feature.** On ne croise jamais l'amont et la feature dans une même case ;
  Cowork est une ligne globale non attribuée.
- **Rien de la mécanique affiché** : pas de nom de variable ni de clé manifeste ; restitution en clair.

Étape suivante : compléter les montants réels dans la config si besoin, puis relancer ce rapport quand voulu.
