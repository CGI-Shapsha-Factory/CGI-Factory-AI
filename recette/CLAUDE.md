# CLAUDE.md — plugin `recette`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`recette` plugin** (this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`recette` = **phase 5** de la Factory (après livraison). Les 4 contrats amont (cadrage, architecte,
designer, assembleur) **amorcent** un projet ; `recette` couvre ce qui se passe **après qu'une
feature est livrée et mise en recette** par le PO. Contrairement à l'assembleur, ces skills
**travaillent dans le repo cible** (ils corrigent du code et éditent des specs SpecKit) — c'est un
plugin de reprise, pas d'amorçage.

**La frontière qui structure tout : la livraison (la PR / le merge au code de référence).** Avant :
on est en fabrication, rien ne se trace. Après : tout écart constaté devient un **objet suivi dans
Linear**. Deux natures, deux sens de travail opposés :
- **Anomalie** — le code viole une spec correcte → réparer le code pour rejoindre la spec (spec inchangée).
- **Évolution** — le code respecte la spec mais la spec était fausse/incomplète → changer la spec d'abord, le code suit.

## Langue & invocation
- **Tout en français** (skills, références, interaction). Seuls les identifiants/valeurs machine et
  noms d'outils/formats (`spec.md`, `constitution.md`, SpecKit, `/speckit.*`, `feature:<id>`) restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/recette:<skill>` + auto par le modèle.
- Aucun skill ne porte le nom `recette` (éviter la collision plugin/skill).

## Les 4 skills (matrice PO × développeur, anomalie × évolution)

| | Le PO crée dans Linear | Le développeur réalise |
|---|---|---|
| **Anomalie** | `anomalie-creer` | `anomalie-corriger` |
| **Évolution** | `evolution-creer` | `evolution-realiser` |

- `anomalie-creer` — **le PO** produit une anomalie **complète** (comportement attendu vs constaté,
  cas/critère qui échoue, étapes de repro) et **bien rattachée** à sa feature (label `feature:<id>`),
  dans Linear. **Double déclencheur** : appelable par un humain **ou** par l'outil de recette
  (extension navigateur) qui passe une **anomalie candidate** — une seule porte de création.
- `anomalie-corriger` — **le développeur** prend l'anomalie, **tranche anomalie vs évolution
  déguisée** (si le code est conforme à la spec, il **requalifie automatiquement** : état Linear
  « Requalifiée en évolution » + **commentaire** explicatif, sans créer l'évolution — c'est au PO),
  fait l'**analyse d'impact** (par la feature), mène l'**enquête dans le code** (pas de clarification
  de besoin), **corrige**, et **referme proprement** (garde-fou `check_recette.py`).
- `evolution-creer` — **le PO** produit une évolution **bornée** portant un **écart de spec précis**
  (« on change telle exigence »), pas une réécriture, dans Linear.
- `evolution-realiser` — **le développeur** trie **propre-à-la-feature vs vérité partagée**, fait le
  **reopen tracé**, met à jour **la spec d'abord**, puis **guide** le cycle SpecKit
  (`/speckit.clarify` → `/speckit.plan` → **porte plan humaine** → `/speckit.tasks` →
  `/speckit.implement` cadré), **prouve la non-régression**, et **referme proprement**.

## Frontière SpecKit (handoff guidé)
Comme le reste de la Factory : **c'est l'équipe qui lance les `/speckit.*`**. Aucun skill ne les
invoque programmatiquement. Les skills **préparent** les artefacts (spec-delta, périmètre),
**gèrent les portes humaines**, puis **indiquent la commande exacte à taper**. Le contrôle
chirurgical vient de la **spec/plan/tâches resserrées + la porte plan**, pas de qui appuie sur
entrée. Un skill **refuse de passer la main à un `implement` non cadré**.

Fichiers SpecKit d'une feature (générés dans le repo cible) : `specs/<NNN>-<slug>/{spec.md, plan.md,
tasks.md}` — une feature se retrouve par `specs/<id>-*/` (le slug vient de la branche).

## Aucun hook nouveau
La **non-régression** réutilise l'enforcement de test de l'**architecte**
(`architecte/references/enforcement/` : `tests_guard.py` en `Stop`/`PostToolUse` + `lefthook` +
**backstop CI diff-coverage** `ci/tests.yml`). `evolution-realiser` **s'assure** que cet enforcement
est installé (réinstallation idempotente) et **exécute** la suite ; il ne réinvente rien.

## Le bloc manifeste `recette`
Écriture read-modify-write + revalidation JSON, **en silence**. Séparé de `linear.issues[]` (features)
pour ne pas casser `check_linear.py`. Schéma :
```json
"recette": {
  "phase": "active", "team": null, "project": null,
  "anomalies": [
    { "feature": "002", "title": "…", "identifier": "ENG-321", "issue_id": "…",
      "url": "https://linear.app/…", "state": "draft|in_progress|requalified|done",
      "requalified_to": null,
      "trace": { "spec_verified": false, "tasks_updated": false, "linear_synced": false } }
  ],
  "evolutions": [
    { "feature": "002", "title": "…", "identifier": "ENG-322", "issue_id": "…",
      "url": "https://linear.app/…", "state": "draft|in_progress|done",
      "reopened": true,
      "perimeter": { "requirements": ["FR-004"], "files": ["specs/002-*/spec.md"] },
      "trace": { "spec_updated": false, "plan_regenerated": false, "tasks_regenerated": false,
                 "linear_synced": false, "non_regression_passed": false } }
  ]
}
```
- `feature` = un `id` de `architecture.feature_sequence` (le lien qui porte l'analyse d'impact).
- `state` : `draft` (préparé, pas encore dans Linear), `in_progress`, puis fermeture — anomalie
  `done` **ou** `requalified` (requalifiée en évolution), évolution `done`.
- `trace` : ce que `check_recette.py` vérifie à la fermeture (règle d'or « pas de clôture sans trace »).

## Interface anti-écrasement (dépendance §11, compagnon séparé)
Ces skills **consomment** un marqueur de cycle de vie par feature (non encore construit par un plugin
compagnon) : à terme `architecture.feature_sequence[].lifecycle` ∈ `fabrication|delivered|recette|reopened`
+ `reopened_by`. En attendant, les skills **dégradent proprement** : si le marqueur existe et dit
`fabrication`, refuser la création ; sinon, procéder. `evolution-realiser` matérialise le **reopen
tracé** (champ `reopened` sur l'objet évolution). Le **mécanisme complet** de protection anti-écrasement
est un **problème compagnon** à traiter séparément.

## Conventions partagées
`references/interactive-loop.md`, `references/ux-conventions.md`, `references/recette-linear-guide.md`
(usage du MCP linear-prism pour la recette : détection, installation, `save_issue` création **et** mise
à jour d'état, labels `anomaly`/`evolution`, statut « Requalifiée en évolution », `save_comment` pour
la requalification, relations d'issues, mode brouillon). Garde-fou déterministe :
`scripts/check_recette.py` (lien feature valide, identifiant Linear, **trace de clôture complète**).

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python scripts/check_recette.py <projet>/.factory/manifest.json
```

## Invariants
**Deux natures, deux sens** (anomalie = code→spec ; évolution = spec→code) ; **proposer / pas
décider** (le PO tranche la nature à la création, le développeur valide la cause racine et le plan) ;
**rien laissé indéfini** ; **ne jamais écraser** (rouvrir une feature livrée est volontaire et tracé) ;
**vérité partagée → escalade** (constitution / ADR successeur / glossaire, jamais réglée dans la
feature) ; **jamais de clôture sans trace à jour** (spec + tâches + Linear) ; **la spec commande**
(plan et tâches régénérés, jamais édités à la main) ; restitutions en prose, manifeste mis à jour en silence.
