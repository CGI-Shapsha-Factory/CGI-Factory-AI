# architecte — contrat technique

Plugin Claude de la **phase architecture** d'un projet spec-driven. Il transforme
le besoin fonctionnel (sortie de `cadrage`) en **cadre technique**. Il ne décide pas
l'architecture à la place de l'architecte : il **discipline son raisonnement** et
**grave ses décisions en contrats traçables**. Portes humaines : l'**arbitrage des
ADR**, puis la **validation de cohérence**.

## Principe
L'IA propose et structure, **l'humain tranche**. Tout en **français**. Le plugin
ne contient **que des skills** (pas de commande slash). Il lit les artefacts de
cadrage depuis `cadrage-out/` et écrit ses propres sorties dans `architecte-out/`
(manifeste et gabarits dans `.factory/`).

## Les 3 skills, dans l'ordre
| # | Skill | Rôle | Porte d'entrée |
|---|-------|------|----------------|
| 0 | `architecte-init` | Installe les gabarits d'archi, crée `conventions/` (`.editorconfig`), étend le manifeste (bloc `architecture`) **+ pose tous les hooks de l'architecte** (enforcement des tests `PostToolUse` + protection de branche `.githooks/`/`SessionStart`) | cadrage prêt |
| 1 | `architecte-contrat` | Vérifie les réponses (depuis cadrage) → drivers & attributs de qualité → **composants** (dont le **frontend**, interactif) → **stack** (interactif : **options + compromis + arbitrage humain**, **versions exactes**) → conventions → **ADR** (arbitrage, consigné après décision) → walking skeleton + numérotation → diagrammes (rendu robuste) → risques → **fichiers d'env (optionnel)** *(l'enforcement est déjà posé par `architecte-init`)* | init faite |
| 2 | `architecte-coherence` | **Validation de cohérence** (composants↔stack↔ADR↔diagrammes↔features) + rapport + garde-fou déterministe | contrat produit |

## Entrées (depuis `cadrage`)
`cadrage-out/` : `project-frame.md` (Q1–Q13 + *seeds qualité*), `product-brief.md`,
`glossaire.md`, `spec-index.md`, et les briefs sous
`cadrage-out/features-fonctionnels-brief/*.md`.

## Sorties (dans `architecte-out/`)
`drivers-quality.md`, `components.md`, `tech-stack.md`, `standards.md`,
`decisions/ADR-*.md`, `diagrams.md` (+ images PNG dans `diagrammes/`), `risks.md`,
`design-impact.md`, `coherence-report.md` ; + le dossier `conventions/` (à la racine du
projet) avec les **vrais fichiers de config** par langage ; + la **séquence de features
numérotée** (convergence des deux découpages). Chaque document porte un **front-matter
`version`/`date`** (compteur d'itération ; les ADR restent en version 1, immuables).

## Garanties (retours de test)
- **Frontend porté par l'architecte** : dès qu'il y a des écrans, `components.md` contient un
  composant Frontend/UI avec sa stack ; le designer garde le design system **visuel**.
- **Aucune décision à ta place** : chaque techno (langage, framework, **front**, base,
  **cloud**, **déploiement**) est présentée en options + compromis, **tu tranches** ; pas de
  biais fournisseur, et l'expérience avec une techno ne vaut pas décision.
- **Versions exactes** : toute techno de `tech-stack.md` porte une version épinglée (jamais
  « latest ») — vérifié par le garde-fou déterministe.
- **Diagrammes fiables sans intervention** : rendu auto-installé (mermaid-cli + navigateur
  système, CA d'entreprise respectée **sans** désactiver TLS), replis automatiques, zéro prompt.
- **Drivers ≠ attributs de qualité** : les drivers sont les **objectifs métier + contraintes +
  risques** ; les attributs de qualité sont les **-ilités mesurées qui en découlent** (cible +
  scénario) — pas de doublon entre les deux.
- **Tests & environnement** : stratégie de test concrète dans `standards.md` (unitaires
  passant/échec/limite, intégration **mockée**, **tests écrits avec le code**), **posée en dur** par
  des hooks Claude Code + pre-commit à la racine ; fichiers d'environnement **optionnels** selon la
  stack (placeholders `.env`/Angular/…).

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
├── skills/{architecte-init, architecte-contrat, architecte-coherence}/SKILL.md
├── templates/   # drivers-quality, components, tech-stack, standards, diagrams, adr, risks, design-impact
├── references/  # interactive-loop, ux-conventions, question-map, conventions/, env-templates/, enforcement/ (catalogues)
├── scripts/     # check_architecture · render_diagrams · provision_render · bump_doc_version
└── README.md
```
