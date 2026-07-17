# Mapping : 3 contrats -> paquet de handoff SpecKit

Référence clé lue par `assembleur-convergence`. Indique **comment chaque face alimente le
paquet `assembleur-out/`**, et comment ce paquet alimente SpecKit (vérifié sur la structure
SpecKit réelle).

## Principe : paquet seul (l'assembleur n'écrit PAS dans le repo SpecKit)
L'assembleur produit un **paquet de handoff** dans `assembleur-out/`, **plus** un déploiement direct de
`CLAUDE.md` + `memory/` dans le `.claude/` du projet (seule exception à "paquet seul" : ces deux-là
doivent être actifs sans copie manuelle). C'est **l'équipe** qui lance SpecKit avec ce paquet comme
matière : `specify init`, puis `/speckit.constitution` (depuis `pre-constitution.md`), puis
`/speckit.specify` par feature (depuis les graines). L'assembleur ne crée **jamais**
`.specify/memory/constitution.md` ni `specs/NNN/spec.md` - ce sont des fichiers que SpecKit génère.
Le **numéro** `NNN` d'une feature est l'`id` du registre canonique : le basename `NNN-slug` de la graine
**est** le nom du répertoire SpecKit et de la branche git, et `/speckit.specify` est lancé avec
`SPECIFY_FEATURE_DIRECTORY=specs/NNN-slug` (**jamais** d'auto-numérotation SpecKit - collision entre
développeurs ; garde-fou `check_speckit_alignment.py`). Voir `feature-map.md`, `attack-plan.md` et - pour
les règles multi-développeurs consolidées - `fabrication-parallele.md`.

```
assembleur-out/
├── pre-constitution.md       -> matière de /speckit.constitution (format constitution.md)
├── features/NNN-....md         -> matière de /speckit.specify  (format spec.md)
├── feature-map.md            -> ordre + couplage des /speckit.specify
├── technical-context.md      -> Technical Context de /speckit.plan (+ modèle de données ERD + déploiement)
├── coherence-report.md
└── attack-plan.md

.claude/                      (déploiement direct dans le projet - actif sans copie manuelle)
├── CLAUDE.md                 -> CLAUDE.md projet (instructions de fabrication, @import memory/MEMORY.md)
└── memory/{MEMORY,domain,architecture,design,features}.md
```

## Graine `spec.md` (par feature) : où va chaque face
| Section SpecKit | Source (face) |
|---|---|
| **User Scenarios & Testing** (User Stories P1/P2/P3, Given/When/Then, Edge Cases) | fonctionnel : brief cadrage + parcours |
| **Functional Requirements** (FR-001...) | fonctionnel : brief cadrage |
| **Success Criteria** (SC-001..., mesurables, techno-agnostiques) | technique : scénarios qualité architecte + design : cibles a11y |
| **Key Entities** | langage ubiquitaire (`memory/domain.md`) + **relations <- ERD (`diagrammes.md`)** |
| **Hors périmètre (cette feature)** | fonctionnel : hors-périmètre local du brief |
| **Assumptions** | points tranchés en session (aucun marqueur résiduel) + **risques/spikes (`risques.md`)** |
| *Annexe - Face technique* | architecte -> nourrit `technical-context.md` / le *Technical Context* du futur `plan.md` |
| *Annexe - Face design* | designer -> `memory/design.md` (états, a11y) |

## `pre-constitution.md` : principes convergés (non négociables)
- **Fonctionnel** (cadrage) : identité produit, hors-périmètre, langage ubiquitaire.
- **Technique** (architecte) : stack imposée, règles dérivées des ADR, cibles d'attributs de
  qualité, conventions, contraintes d'hébergement/souveraineté/budget infra (<- découverte),
  walking-skeleton-first.
- **Design** (designer) : tout écran dérive du design system synchronisé, aucune valeur de style
  en dur, états couverts, contrat d'erreur, accessibilité au niveau visé.
- **Tests** (architecte + enforcement) : tests écrits avec le code ; unitaires par règle métier
  (passant/échec/limite) ; intégration mockée ; appliqué par hooks + pre-commit au moment du développement.
- **Gouvernance** : procédure d'amendement, versioning (1.0.0 à la ratification), revue de conformité.

## Jointure des 3 faces : clé = use case (`uc`)
`architecture.feature_sequence` est le **registre canonique** (objets `{id, ucs, name}`, `ucs` =
liste ; une feature peut bundler plusieurs use cases). La **clé de jointure** est le **use case** :
- cadrage -> `artifacts.briefs[].id ∈ feature.ucs` (chemin = `.path`) ; parcours/use cases du cadrage ;
- designer -> **contrat global** (design system synchronisé + guidelines appliqués à tous les écrans,
  pas de jointure par feature) ;
- architecte -> le registre `feature_sequence`.

> Règle de couverture : **chaque** feature de la `feature_sequence` a sa graine dans `features/` ;
> le **walking skeleton** est la feature `001`.
