---
name: evolution-realiser
description: Le développeur réalise une évolution sur une feature livrée sans déborder — trie propre-à-la-feature vs vérité partagée, reopen tracé, met à jour la spec d'abord, guide le cycle SpecKit (clarify/plan/porte/tasks/implement cadré), prouve la non-régression, referme proprement.
---

# evolution-realiser

**Le développeur réalise une évolution.** À lancer quand un développeur prend en charge une évolution
créée par le PO. Réaliser une évolution sur une feature **déjà livrée**, **sans dérive**, en mettant à
jour **la spécification d'abord** et **le code ensuite**, et surtout **sans déborder** sur ce qui
marchait déjà. C'est le point le plus sensible du dispositif (cf. le comportement chirurgical, §7 de
la spécification de cadrage).

## Objectif
Faire évoluer **spec puis code** de façon **cohérente et circonscrite**, prouver que **l'ancien n'a
pas cassé**, et refermer **seulement** quand spec + tâches + Linear + non-régression sont en place.

## Frontière (exception assumée)
L'évolution **modifie le repo cible** : la **spécification** (`specs/<id>-*/spec.md`) puis le **code**
(via SpecKit). Les écritures **Linear** et le bloc `recette` passent par le MCP `linear-prism`. **C'est
l'équipe qui lance les `/speckit.*`** : ce skill **prépare et guide** (handoff guidé), il n'invoque
jamais SpecKit programmatiquement — voir `references/recette-linear-guide.md`.

## Pré-requis (vérification silencieuse)
Lire `.factory/manifest.json` : l'évolution est dans `recette.evolutions[]` ; le repo porte SpecKit
(`specs/<id>-*/`). MCP détecté. **Enforcement de test présent** dans le repo cible (l'architecte l'a
posé en fabrication : `.claude/hooks/tests_guard.py` + backstop CI `ci/tests.yml`) → s'il **manque**,
le dire en clair et orienter vers sa réinstallation (via l'architecte) ; **ne pas le réinventer**.

## Étape 1 — Récupérer l'évolution et la prendre en charge
Depuis l'identifiant : la retrouver (`recette.evolutions[]` / `list_issues` label `evolution`),
`get_issue` pour lire **la proposition de changement de spécification**. Confirmer l'objet, passer
**en cours** (`save_issue({id, state: "started"})`, `state: "in_progress"` en silence).

## Étape 2 — Tri : propre à la feature, ou vérité partagée ?
À un niveau **au-dessus** de la correction :
- **Propre à la feature** (sa spécification et son code changent, rien d'autre) → continuer ici.
- **Vérité partagée** (contrat partagé par plusieurs features : donnée métier, règle d'erreur,
  décision d'architecture, terme du glossaire) → **ne pas traiter seul** : **signaler** qu'elle doit
  **remonter au niveau central** et impliquer l'amont (**architecte** via un **ADR successeur**,
  **cadrage**) et l'**assembleur**. Sans ce tri, ce skill deviendrait une porte par laquelle on
  modifierait des contrats partagés feature par feature — la dérive qu'on veut éviter. **S'arrêter** ici.

## Étape 3 — Reopen tracé (le geste volontaire)
Pour une évolution **propre à la feature**, c'est ici que se matérialise « **rouvrir une feature
livrée** ». Le skill **lève délibérément** la protection de la feature — légitime, car c'est une
évolution **décidée par le PO**, pas une réécriture accidentelle. Consigner le reopen en silence
(`reopened: true` sur l'objet évolution ; à terme le marqueur `reopened_by` côté cycle de vie de la
feature, quand le plugin compagnon existera).

## Étape 4 — Discipline 1 : borner le changement dans la spécification (d'abord)
Mettre à jour **la spécification d'abord** (`specs/<id>-*/spec.md`), en n'écrivant que **l'écart
prévu** par le PO (l'exigence qui change), **jamais** une réécriture. Consigner `spec_updated` en
silence et le `perimeter` (exigences visées).

## Étape 5 — Cycle SpecKit guidé (l'équipe lance, le skill cadre)
Le skill **prépare le contexte** et **indique la commande exacte** à taper, **attend** le résultat,
puis enchaîne. Il **refuse** de passer la main à un `implement` non cadré.

1. **Clarifier la nouvelle intention** — indiquer de lancer **`/speckit.clarify`** (toute intention
   nouvelle contient des zones floues ; c'est le **bon** usage : préciser un besoin nouveau, à ne pas
   confondre avec l'enquête code d'une anomalie). Graver les réponses dans la spec.
2. **Discipline 2 : passer par le plan, et le faire valider.** Indiquer de lancer **`/speckit.plan`**.
   **Porte plan humaine** : présenter en clair **ce que le plan annonce toucher**. Si le plan annonce
   **beaucoup plus** que l'écart attendu (« dix fichiers pour une petite évolution »), c'est le
   **signal d'alerte** — on le voit **avant** que le code ne bouge. Ne pas continuer tant que le
   développeur **n'a pas validé** le périmètre. Consigner `plan_regenerated`. (Optionnel :
   **`/speckit.analyze`** pour vérifier la cohérence spec/plan/tâches avant le code.)
3. Indiquer de lancer **`/speckit.tasks`** (régénère les tâches depuis la spec — « la spécification
   commande, le reste se régénère »). Consigner `tasks_regenerated`.
4. **Discipline 3 : implémentation cadrée, pas en grand.** Indiquer de lancer **`/speckit.implement`**
   en **rappelant le périmètre** (les exigences qui changent, les fichiers du plan validé) et la
   consigne de **ne toucher que ça**. Le cadrage est porté par la spec/plan/tâches **resserrées** ; le
   skill **ne passe pas la main** à un implement ouvert qui repasserait sur toute la feature.

## Étape 6 — Discipline 4 : prouver la non-régression
L'évolution n'est finie que quand le **nouveau** comportement marche **et** que l'**ancien** n'a pas
cassé :
- les **tests existants** de la feature **passent** (l'enforcement de l'architecte s'applique :
  `tests_guard` en `Stop`/`PostToolUse`, et le **backstop CI diff-coverage** sur les lignes modifiées) ;
- l'**analyse d'impact** (par la feature — composants/données partagés, bloc `architecture`) confirme
  que **rien d'autre** n'a été abîmé.
Consigner `non_regression_passed` seulement quand c'est vrai.

## Étape 7 — Refermer proprement (garde-fou de clôture)
**Ne pas conclure** tant que : la **spécification** reflète l'évolution, le **plan et les tâches** sont
régénérés, **Linear** suit, et **rien d'autre n'a cassé**. Lancer le garde-fou :
```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/check_recette.py" <racine>/.factory/manifest.json
```
**Garde-fou déterministe (anti-contournement, obligatoire).** Si le script est **introuvable** ou
renvoie **exit 1**, **s'arrêter** et **dire en clair** ce qui manque — **jamais** de vérification « à
la main ». Une fois vert, passer l'évolution à **terminé** (`save_issue({id, state: "<type
completed>"})`, `state: "done"`).

## Vérification avant de conclure
- La spécification et le code ont évolué de façon **cohérente et circonscrite** ; le plan validé n'a
  pas débordé ; la non-régression est **prouvée**.
- `check_recette.py` renvoie **OK** (les 5 traces de clôture sont vraies).
- Restitution **en prose**, **une** phrase de suite.

## Règles invariantes
- **La spec commande, le reste se régénère.** On ne modifie **jamais** le plan ni les tâches à la
  main ; on change la spec puis on régénère.
- **Chirurgical par construction.** Borner (spec) → plan validé → implement cadré → non-régression prouvée.
- **Reopen volontaire et tracé.** Rouvrir une feature livrée n'est jamais un effet de bord silencieux.
- **Vérité partagée → escalade** (ADR successeur / cadrage / assembleur), jamais réglée dans la feature.
- **Handoff SpecKit guidé.** L'équipe lance les `/speckit.*` ; le skill cadre, ne les invoque jamais lui-même.
- **Jamais de clôture sans trace ni non-régression.** Garde-fou déterministe, fail-loud, jamais contourné.
- **Manifeste en silence.** Restitution en prose.

Étape suivante : reprendre l'évolution suivante, ou revenir à la fabrication normale de la feature.
