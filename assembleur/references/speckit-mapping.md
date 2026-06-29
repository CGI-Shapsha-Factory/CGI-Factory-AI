# Mapping — 3 contrats → projet SpecKit

Référence clé lue par le skill `assembleur`. Indique **comment chaque face alimente les
fichiers SpecKit** (vérifié sur la structure SpecKit réelle).

## Cible SpecKit — ORDRE : `specify init --ai claude` d'ABORD, puis l'assembleur écrit dedans
> `specify init` est une **précondition** (lancée par l'équipe avant la convergence, vérifiée par
> `assembleur-init`). Il pose le runtime (`.specify/scripts`, `templates`, `.claude/commands/speckit.*`)
> **et un gabarit** de constitution ; l'assembleur écrit **ensuite** et **remplace** ce gabarit par la
> constitution convergée. **Ne jamais relancer `specify init` après l'assembleur** (il écraserait la
> constitution).

```
<repo>/
├── .specify/
│   ├── memory/constitution.md     <- assembleur (constitution convergée)
│   ├── templates/  scripts/  extensions/
├── specs/NNN-feature/
│   ├── spec.md                    <- assembleur (seed 3-faces)
│   ├── plan.md  tasks.md          <- générés ensuite par /speckit.plan, /speckit.tasks
├── CLAUDE.md                      <- assembleur (section <!-- SPECKIT START/END --> + factory)
├── GLOSSARY.md  MEMORY.md         <- assembleur
└── .claude/commands/speckit.*     <- posés par specify init
```

## `spec.md` (par feature) — où va chaque face
| Section SpecKit | Source (face) |
|---|---|
| **User Scenarios & Testing** (User Stories P1/P2/P3, Given/When/Then, Edge Cases) | fonctionnel : brief cadrage + **parcours designer** |
| **Functional Requirements** (FR-001…) | fonctionnel : brief cadrage |
| **Success Criteria** (SC-001…, mesurables, techno-agnostiques) | technique : **scénarios qualité (QS) architecte** + design : **cibles a11y** |
| **Key Entities** | glossaire consolidé |
| **Assumptions** | trous `[À VALIDER]` → `NEEDS CLARIFICATION` |
| *Annexe — Face technique* (composants/stack/ADR) | architecte → nourrit le *Technical Context* du futur `plan.md` |
| *Annexe — Face design* (parcours/composants/tokens/états/a11y) | designer → guide l'implémentation UI |

## `constitution.md` — principes convergés (non négociables)
- **Fonctionnel** (cadrage) : identité produit, hors-périmètre, langage ubiquitaire.
- **Technique** (architecte) : stack imposée, règles dérivées des ADR, cibles d'attributs de
  qualité, conventions (`conventions/`), walking-skeleton-first.
- **Design** (designer) : principes de design, **accessibilité WCAG 2.2 AA**, discipline des
  tokens (aucune valeur brute), « fige le système, pas les écrans ».
- **Gouvernance** : procédure d'amendement, versioning (1.0.0 à la ratification), revue de conformité.

## `plan.md` (généré ensuite par l'équipe via /speckit.plan)
La **Constitution Check** y vérifie le respect des principes ci-dessus ; le **Technical
Context** reprend les annexes technique/design du `spec.md`.

## Jointure des 3 faces — clé = use case (`uc`)
`architecture.feature_sequence` est le **registre canonique** (objets `{id, ucs, name}`,
`ucs` = liste ; une feature peut bundler plusieurs use cases). La **clé de jointure** entre
les trois contrats est le **use case** (stable malgré la renumérotation/le réordonnancement
de l'architecte) :
- cadrage → `artifacts.briefs[].id ∈ feature.ucs` (chemin = `.path`) ; les **parcours/use cases**
  viennent du cadrage (`spec-index.md`) ;
- designer → **contrat global** : `design.design_system_ref` (système synchronisé via `/design-sync`) +
  `design-guidelines.md` (états, patterns d'erreur, socle a11y) appliqués à tous les écrans (pas de
  jointure par feature côté design) ;
- architecte → le registre `feature_sequence` (donne l'`id` final **et** les `ucs`).
L'assembleur joint, pour chaque feature, **tous** ses `ucs` (faces fonctionnelle/technique), et applique
la face design **globale** ; puis pose `feature_faces[].feature = id` (face complète seulement si tous
les `ucs` sont couverts et que le design system + guidelines s'appliquent).

> Règle de couverture : **chaque** use case / feature de la `feature_sequence` (architecte) a
> son `spec.md` ; le **walking skeleton** est la feature `001`.
