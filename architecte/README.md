# architecte : contrat technique

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

## Les 6 skills, dans l'ordre
| # | Skill | Rôle | Porte d'entrée |
|---|-------|------|----------------|
| 0 | `architecte-init` | Installe les gabarits d'archi, crée `conventions/` (`.editorconfig`), étend le manifeste (bloc `architecture`) **+ pose les hooks de l'architecte** (enforcement des tests + formatage `PostToolUse` ; pas de protection de branche locale - gérée côté GitHub) | cadrage prêt |
| 1 | `architecte-fondations` | Vérifie les réponses (depuis cadrage, fan-out `architecte-reader`) -> **drivers & attributs de qualité** (deux tableaux) -> **composants** (dont le **frontend**, interactif) | init faite |
| 2 | `architecte-stack` | **stack** (interactif : **options + compromis + arbitrage humain**, **versions exactes**) -> conventions (vrais fichiers) -> **ADR** (arbitrage, consigné après décision) -> walking skeleton + numérotation + séquence de features | fondations faites |
| 3 | `architecte-livrables` | diagrammes (rendu robuste) -> risques -> **impact-design** (handoff designer) -> **fichiers d'env** -> vérification de l'enforcement, puis balayage final de `architecte-out/` | stack faite |
| 4 | `architecte-coherence` | **Validation de cohérence** (composants<->stack<->ADR<->diagrammes<->features) + rapport + garde-fou déterministe | contrat produit |
| - | `gen-tests` | **Hors chaîne** : génère les tests manquants (pytest/jest/vitest/go) pour les sources qui n'en ont pas, **puis les exécute et itère jusqu'à la suite verte** | `/architecte:gen-tests [chemin]` |

## Entrées (depuis `cadrage`)
`cadrage-out/` : `project-frame.md` (Q1-Q13 + *seeds qualité*), `product-brief.md`,
`glossaire.md`, `spec-index.md`, et les briefs sous
`cadrage-out/features-fonctionnels-brief/*.md`.

## Sorties (dans `architecte-out/`)
`facteurs-et-qualite.md`, `composants.md`, `stack-technique.md`, `standards-ingenierie.md`,
`decisions/ADR-*.md`, `diagrammes.md` (+ images PNG dans `diagrammes/`), `risques.md`,
`impact-design.md`, `coherence-report.md` ; + le dossier `conventions/` (à la racine du
projet) avec les **vrais fichiers de config** par langage ; + la **séquence de features
numérotée** (convergence des deux découpages). Chaque document porte un **front-matter
`version`/`date`** (compteur d'itération ; les ADR restent en version 1, immuables).

## Garanties (retours de test)
- **Frontend porté par l'architecte** : dès qu'il y a des écrans, `composants.md` contient un
  composant Frontend/UI avec sa stack ; le designer garde le design system **visuel**.
- **Aucune décision à ta place** : chaque techno (langage, framework, **front**, base,
  **cloud**, **déploiement**) est présentée en options + compromis, **tu tranches** ; pas de
  biais fournisseur, et l'expérience avec une techno ne vaut pas décision.
- **Versions exactes** : toute techno de `stack-technique.md` porte une version épinglée (jamais
  "latest") - vérifié par le garde-fou déterministe.
- **Diagrammes fiables sans intervention** : rendu auto-installé (mermaid-cli + navigateur
  système, CA d'entreprise respectée **sans** désactiver TLS), replis automatiques, zéro prompt.
- **Drivers ≠ attributs de qualité** : les drivers sont les **objectifs métier + contraintes +
  risques** ; les attributs de qualité sont les **-ilités mesurées qui en découlent** (cible +
  scénario) - pas de doublon entre les deux.
- **Tests & environnement** : stratégie de test concrète dans `standards-ingenierie.md` (unitaires
  passant/échec/limite, intégration **mockée**, **tests écrits avec le code**), **posée en dur** par
  des hooks Claude Code + pre-commit à la racine ; fichiers d'environnement **optionnels** selon la
  stack (placeholders `.env`/Angular/...).

## Conventions de code (vrais fichiers)
Catalogue dans `references/conventions/` : Python -> `ruff.toml` ; TS/JS -> `biome.json`
(défaut) **ou** `eslint.config.js`+`.prettierrc` ; C -> `.clang-format` ; socle
universel -> `.editorconfig`. `architecte-stack` copie les configs des langages retenus dans
`conventions/`. **Fallback** : langage inconnu -> `.editorconfig` + avertissement +
convention générique `[À VALIDER]`.

## Vérification optimisée des réponses
`references/question-map.md` mappe chaque question d'architecture à un champ de
cadrage : ~16/17 sont déjà répondues ; seul le **profil d'équipe** est demandé.

## Structure
```
architecte/
├── .claude-plugin/plugin.json
├── agents/      # architecte-reader (lecteur parallèle du cadrage / d'architecte-out)
├── skills/{architecte-init, architecte-fondations, architecte-stack, architecte-livrables, architecte-coherence, gen-tests}/SKILL.md
├── templates/   # facteurs-et-qualite, components, stack-technique, standards, diagrams, adr, risks, impact-design
├── references/  # interactive-loop, ux-conventions, question-map, coherence-checklist-guide, conventions/, env-templates/, enforcement/ (catalogues)
├── scripts/     # check_architecture · render_diagrams · provision_render · install_formatter · bump_doc_version
└── README.md
```
