# Mapping — 3 contrats → paquet de handoff SpecKit

Référence clé lue par `assembleur-convergence`. Indique **comment chaque face alimente le
paquet `assembleur-out/`**, et comment ce paquet alimente SpecKit (vérifié sur la structure
SpecKit réelle).

## Principe — paquet seul (l'assembleur n'écrit PAS dans le repo SpecKit)
L'assembleur produit un **paquet de handoff** dans `assembleur-out/`. C'est **l'équipe** qui
lance SpecKit avec ce paquet comme matière : `specify init`, puis `/speckit.constitution` (depuis
`pre-constitution.md`), puis `/speckit.specify` par feature (depuis les graines). L'assembleur ne
crée **jamais** `.specify/memory/constitution.md` ni `specs/NNN/spec.md` — ce sont des fichiers que
SpecKit génère.

```
assembleur-out/
├── pre-constitution.md       -> matière de /speckit.constitution (format constitution.md)
├── features/NNN-…spec-seed.md-> matière de /speckit.specify  (format spec.md)
├── feature-map.md            -> ordre + couplage des /speckit.specify
├── technical-context.md      -> matière du Technical Context de /speckit.plan
├── CLAUDE.md                 -> CLAUDE.md projet (instructions de fabrication)
├── ci/tests.yml              -> backstop CI diff-coverage (required status check)
├── memory/{MEMORY,domain,architecture,design,features}.md
├── coherence-report.md
└── attack-plan.md
```

## Graine `spec.md` (par feature) — où va chaque face
| Section SpecKit | Source (face) |
|---|---|
| **User Scenarios & Testing** (User Stories P1/P2/P3, Given/When/Then, Edge Cases) | fonctionnel : brief cadrage + parcours |
| **Functional Requirements** (FR-001…) | fonctionnel : brief cadrage |
| **Success Criteria** (SC-001…, mesurables, techno-agnostiques) | technique : scénarios qualité architecte + design : cibles a11y |
| **Key Entities** | langage ubiquitaire (`memory/domain.md`) |
| **Assumptions** | points tranchés en session (aucun marqueur résiduel) |
| *Annexe — Face technique* | architecte → nourrit `technical-context.md` / le *Technical Context* du futur `plan.md` |
| *Annexe — Face design* | designer → `memory/design.md` (états, a11y) |

## `pre-constitution.md` — principes convergés (non négociables)
- **Fonctionnel** (cadrage) : identité produit, hors-périmètre, langage ubiquitaire.
- **Technique** (architecte) : stack imposée, règles dérivées des ADR, cibles d'attributs de
  qualité, conventions, walking-skeleton-first.
- **Design** (designer) : tout écran dérive du design system synchronisé, aucune valeur de style
  en dur, états couverts, contrat d'erreur, accessibilité au niveau visé.
- **Tests** (architecte + enforcement) : tests écrits avec le code ; unitaires par règle métier
  (passant/échec/limite) ; intégration mockée ; appliqué par hooks + pre-commit + **CI diff-coverage requis**.
- **Gouvernance** : procédure d'amendement, versioning (1.0.0 à la ratification), revue de conformité.

## Jointure des 3 faces — clé = use case (`uc`)
`architecture.feature_sequence` est le **registre canonique** (objets `{id, ucs, name}`, `ucs` =
liste ; une feature peut bundler plusieurs use cases). La **clé de jointure** est le **use case** :
- cadrage → `artifacts.briefs[].id ∈ feature.ucs` (chemin = `.path`) ; parcours/use cases du cadrage ;
- designer → **contrat global** (design system synchronisé + guidelines appliqués à tous les écrans,
  pas de jointure par feature) ;
- architecte → le registre `feature_sequence`.

> Règle de couverture : **chaque** feature de la `feature_sequence` a sa graine dans `features/` ;
> le **walking skeleton** est la feature `001`.
