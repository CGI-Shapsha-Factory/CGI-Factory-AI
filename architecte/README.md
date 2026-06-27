# architecte — contrat technique

Plugin Claude de la **phase architecture** d'un projet spec-driven. Il transforme
le besoin fonctionnel (sortie de `cadrage`) en **cadre technique**. Il ne décide pas
l'architecture à la place de l'architecte : il **discipline son raisonnement** et
**grave ses décisions en contrats traçables**. Portes humaines : l'**arbitrage des
ADR**, puis la **validation de cohérence**.

## Principe
L'IA propose et structure, **l'humain tranche**. Tout en **français**. Le plugin
ne contient **que des skills** (pas de commande slash). Il lit les artefacts de
cadrage et écrit dans le **workspace partagé** `factory-docs/`.

## Les 3 skills, dans l'ordre
| # | Skill | Rôle | Porte d'entrée |
|---|-------|------|----------------|
| 0 | `architecte-init` | Installe les gabarits d'archi, crée `conventions/` (`.editorconfig`), étend le manifeste (bloc `architecture`) | cadrage prêt |
| 1 | `architecte` | Vérifie les réponses (depuis cadrage) → drivers & attributs de qualité → **composants** (interactif) → **stack** (interactif) → conventions → **ADR** (arbitrage) → walking skeleton + numérotation → diagrammes → risques | init faite |
| 2 | `architecte-coherence` | **Validation de cohérence** (composants↔stack↔ADR↔diagrammes↔features) + rapport + garde-fou déterministe | contrat produit |

## Entrées (depuis `cadrage`)
`factory-docs/work/` : `project-frame.md` (Q1–Q13 + *seeds qualité*), `product-brief.md`,
`glossaire.md`, `spec-index.md`, `*.brief.md`, `pre-constitution.md`.

## Sorties (dans `factory-docs/work/`)
`drivers-quality.md`, `components.md`, `tech-stack.md`, `standards.md`,
`decisions/ADR-*.md`, `diagrams.md`, `risks.md`, `coherence-report.md` ; + le dossier
`conventions/` (à la racine du projet) avec les **vrais fichiers de config** par
langage ; + la **séquence de features numérotée** (convergence des deux découpages).

## Conventions de code (vrais fichiers)
Catalogue dans `references/conventions/` : Python → `ruff.toml` ; TS/JS → `biome.json`
(défaut) **ou** `eslint.config.js`+`.prettierrc` ; C → `.clang-format` ; socle
universel → `.editorconfig`. `architecte` copie les configs des langages retenus dans
`conventions/`. **Fallback** : langage inconnu → `.editorconfig` + avertissement +
convention générique `[À VALIDER]`.

## Vérification optimisée des réponses
`references/question-map.md` mappe chaque question d'architecture à un champ de
cadrage : ~16/17 sont déjà répondues ; seul le **profil d'équipe** est demandé.

## Structure
```
architecte/
├── .claude-plugin/plugin.json
├── skills/{architecte-init, architecte, architecte-coherence}/SKILL.md
├── templates/   # drivers-quality, components, tech-stack, standards, diagrams, adr, risks
├── references/  # interactive-loop, ux-conventions, question-map, conventions/ (catalogue)
├── scripts/check_architecture.py
└── README.md
```
