---
name: anomalie-corriger
description: Le développeur prend une anomalie Linear, vérifie que c'en est bien une (sinon la requalifie en évolution automatiquement, avec commentaire), analyse l'impact par la feature, mène l'enquête dans le code, corrige, et referme proprement — garde-fou de clôture.
---

# anomalie-corriger

**Le développeur corrige une anomalie.** À lancer quand un développeur prend en charge une anomalie
créée par le PO. Le skill prend l'anomalie, **vérifie que c'en est bien une**, trouve la **cause
racine** avec le développeur, **corrige** dans le respect des règles du projet, et **referme
proprement**.

## Objectif
Faire **rejoindre le code à sa spécification** (la spec est juste, le code est en faute), puis
refermer l'anomalie **seulement** quand la spécification, les tâches et Linear reflètent l'état.
Cas particulier : reconnaître une **évolution déguisée** et refermer l'anomalie **sans** la corriger.

## Frontière (exception assumée)
La correction **modifie le code du repo cible** (métier normal de l'outil de développement,
automatique). Les écritures **Linear** (état, commentaire) et le bloc `recette` du manifeste passent
par le **MCP `linear-prism`** — voir `references/recette-linear-guide.md`. La **spécification ne
change pas** ici (elle était juste).

## Pré-requis (vérification silencieuse)
Lire `.factory/manifest.json` : le bloc `recette` liste les anomalies (`recette.anomalies[]`). MCP
détecté (`list_teams`) ; **une correction a besoin du MCP** (pas de mode brouillon utile) → si absent,
afficher les instructions d'installation et demander de relancer.

## Étape 1 — Récupérer l'anomalie et la prendre en charge
Depuis l'**identifiant** (ou un mot-clé) : la retrouver dans `recette.anomalies[]`, sinon
`list_issues({query, team})` (label `anomaly`). `get_issue({id})` pour **lire tout son contenu**.
Confirmer l'objet, puis **passer l'anomalie en cours** (`save_issue({id, state: "started"})`) et
consigner `state: "in_progress"` en silence.

## Étape 2 — Le tri le plus important : anomalie ou évolution déguisée ?
Comparer le **comportement constaté** à la **spécification de la feature** (`specs/<feature>-*/spec.md`,
et le brief fonctionnel). Deux issues :

- **Le logiciel ne respecte pas sa spécification** → **vraie anomalie**, continuer à l'Étape 3.
- **Le logiciel respecte sa spécification** mais la spécification était insuffisante → **ce n'est pas
  une anomalie**. **Requalifier automatiquement** (le constat est technique et clair) :
  1. `save_issue({id, state: "Requalifiée en évolution"})` (état de type `canceled` — cf. pré-requis
     d'équipe du guide) ;
  2. `save_comment({issueId, body})` expliquant **pourquoi ce n'est pas un défaut** (« le code est
     conforme à la spécification ; voici le cas d'usage que la spécification ne couvrait pas : … ») ;
  3. **Ne pas créer l'évolution** — c'est au **PO** d'ouvrir l'évolution (il porte le périmètre).
     Consigner `state: "requalified"` + `trace.linear_synced` en silence, et **s'arrêter** en le
     disant en clair. Étape suivante : le PO ouvre l'évolution avec `/recette:evolution-creer`.

## Étape 3 — Analyse d'impact (par la feature)
Grâce au **rattachement à la feature** (`feature`), lire le bloc `architecture` du manifeste
(composants, données, ADR par feature) et **repérer les features qui partagent** ces composants /
données. **Signaler en clair** celles qui pourraient être touchées par la correction (éviter une
régression ailleurs).
- **Tri de la règle d'or** : si la correction touche une **vérité partagée** (donnée métier partagée,
  règle d'erreur générale, décision d'architecture commune, terme du glossaire), **alerter** qu'elle
  doit **remonter au niveau central** (constitution / **ADR successeur** / glossaire), pas être réglée
  dans cette seule feature.

## Étape 4 — Enquête technique dans le code (avec le développeur)
Trouver la cause d'une anomalie = **comprendre pourquoi le code dévie de sa spécification**. C'est une
**enquête dans le code** (lire le code existant, proposer des hypothèses, les vérifier), **pas** une
clarification de besoin. Mener l'enquête jusqu'à ce que la **cause racine soit validée par le
développeur** (l'IA aide à chercher, l'humain valide — cf. `interactive-loop.md`).

## Étape 5 — Corriger le code
**Corriger le code** pour qu'il respecte la spécification, dans le respect des **règles déjà gravées**
(la constitution / les consignes du projet, les standards de l'architecte). Le skill **ne crée pas**
de nouvelle règle : il rappelle et fait respecter celles qui existent. **La spécification ne change
pas** (elle était juste). Les **tests** accompagnent la correction (l'enforcement de test de
l'architecte s'applique : cas passant/échec, non-régression).

## Étape 6 — Refermer proprement (garde-fou de clôture)
**Ne pas autoriser la clôture** tant que les trois ne sont pas faits :
- la **spécification** de la feature reflète bien le comportement (**inchangée** ici, mais **vérifiée**) ;
- les **tâches** portent la **trace de la correction** ;
- l'anomalie dans **Linear** est mise à jour.

Consigner la `trace` (`spec_verified`, `tasks_updated`, `linear_synced`) en silence, puis lancer le
garde-fou :
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/check_recette.py" <racine>/.factory/manifest.json
```
**Garde-fou déterministe (anti-contournement, obligatoire).** Si le script est **introuvable**
(chemin plugin non résolu) ou renvoie **exit 1**, **s'arrêter** et **dire en clair** ce qui manque —
**jamais** de vérification « à la main ». Une fois vert, passer l'anomalie à **terminé**
(`save_issue({id, state: "<type completed>"})`, `state: "done"` dans le manifeste).

## Vérification avant de conclure
- Le code respecte la spécification ; la cause racine a été **validée par le développeur**.
- `check_recette.py` renvoie **OK** (trace de clôture complète).
- `get_issue` reflète l'état **terminé** (ou **requalifié**). Restitution **en prose**, **une** phrase de suite.

## Règles invariantes
- **Anomalie = code→spec.** On répare le code ; la spécification ne change pas.
- **Requalification tracée, jamais de création d'évolution.** Le skill ferme et explique ; le PO décide du périmètre.
- **Enquête dans le code, pas de clarification de besoin.** Le besoin est clair, le code est en faute.
- **Vérité partagée → escalade.** Jamais réglée dans une seule feature.
- **Jamais de clôture sans trace.** Garde-fou déterministe, fail-loud, jamais contourné à la main.
- **Manifeste en silence.** Restitution en prose.

Étape suivante : reprendre l'anomalie suivante, ou — si requalifiée — le PO ouvre l'évolution avec `/recette:evolution-creer`.
