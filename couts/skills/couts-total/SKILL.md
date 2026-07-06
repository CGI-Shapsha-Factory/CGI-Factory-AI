---
name: couts-total
description: Aggregates all local sessions into one shareable summary file (total tokens, estimated cost, session count) for the team lead.
---

# couts-total

Produit **un seul fichier** (`.factory/couts/bilan-couts.md`) résumant **l'ensemble des sessions**
locales mesurées par le hook `SessionEnd`. Ce fichier est conçu pour être transmis au **chef d'équipe**
quand il demande « qu'as-tu consommé ? ».

**Contenu du bilan** : dev, période, nombre de sessions, total tokens (split 5 catégories sur 1 ligne),
coût estimé € (USD) daté, disclaimer estimation.

> **Note** : `.factory/couts/` est **git-ignoré** — les données sont **individuelles** et ne sont
> jamais poussées. Ce bilan est le mécanisme de partage prévu (remis à la main, e-mail, etc.).
>
> **Pas de pré-requis** : si `.factory/couts/` n'existe pas encore, le script le crée automatiquement
> et produit un bilan vide (aucun enregistrement). Aucun besoin de lancer `couts-init` d'abord.

## Procédure

1. Lancer le script de bilan **sans argument de racine** — il localise tout seul le journal
   (`.factory/couts/` contenant les `.jsonl`) depuis le dossier courant, en descendant au besoin :
   ```
   python "${CLAUDE_PLUGIN_ROOT}/references/cost_total.py"
   ```
   (Adapter `python` → `py -3` si besoin sur Windows.) **Ne pas** passer le git root : le script
   trouve le dossier d'install couts, même s'il est un sous-dossier du dépôt git.

2. Afficher en chat le contenu produit (sessions, total tokens + split, coût estimé).

3. Indiquer en clair **le chemin absolu du fichier** `.factory/couts/bilan-couts.md` — c'est ce
   fichier qu'on transmet au chef d'équipe.

## Règles invariantes
- **Estimation ≠ réel.** Ce fichier contient un coût de *simulation* (tokens × tarif API). Ne jamais
  le présenter comme un montant facturé.
- **Données locales uniquement.** Le dossier `.factory/couts/` étant git-ignoré, ce bilan ne couvre
  que les sessions de **ce développeur** sur **ce poste**. Pour un rollup organisation, voir
  `references/OTEL.md`.
- **Un seul fichier.** Le script écrase `bilan-couts.md` à chaque run — le fichier reflète toujours
  l'état courant du journal local.

Étape suivante : remettre `.factory/couts/bilan-couts.md` au chef d'équipe.
