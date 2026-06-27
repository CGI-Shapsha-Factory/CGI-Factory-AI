# CLAUDE.md — plugin `cadrage`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`cadrage` plugin** (this directory). For the factory-wide overview see
`../CLAUDE.md`.

## Ce qu'est le plugin
`cadrage` industrialise la **phase amont** (contrat fonctionnel) d'un projet
spec-driven : il transforme la **matière brute** d'un atelier (transcripts, docs)
en un pack prêt pour **SpecKit** — pré-constitution, brief par feature, spec index.
Ce n'est **pas un projet applicatif** : ce sont des **skills Markdown** + un
`plugin.json`. Pas de build, pas de lint, pas de tests unitaires.

## Vérifications (à la place des tests)
```bash
# manifeste du plugin
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
# chaque skill a un frontmatter name
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
# garde-fou découverte (sur le manifeste d'un projet)
python scripts/check_discovery.py <projet>/factory-docs/manifest.json
```
Tout JSON écrit par un skill (le manifeste runtime) doit reparser sans erreur.

## Distinction fondamentale
- Le **plugin** (`cadrage/`) = l'outil statique, réutilisable, sans données.
- Le **workspace + manifeste** = créés **dans le projet client** par `cadrage-init`.
  Le plugin lit/écrit ces fichiers ; il ne les contient pas.

## Les skills (11 du pipeline + `help-cadrage` + `help-factory`)
`help-cadrage` (hors pipeline) affiche à l'utilisateur le rôle de chaque skill de **cadrage** et l'ordre d'exécution. `help-factory` (hors pipeline) affiche la **carte des 4 plugins** de la Factory (cadrage → architecte → designer → assembleur → SpecKit), l'ordre des skills et les portes humaines — c'est l'unique vue d'ensemble inter-plugins, volontairement hébergée ici à côté de `help-cadrage`.

| # | skill | rôle | porte |
|---|-------|------|-------|
| 0 | `cadrage-init` | crée `factory-docs/{templates,work}` + manifeste ; **demande project/client** | aucune |
| 1 | `cadrage-extraction` | matière brute (fichier/multi/dossier ; .txt/.md/.pdf/.docx) → `capture-brute.md` + **passe découverte** (13 questions, boucle 3-options) → `project-frame.md` | manifeste existe + 1 source |
| 2 | `cadrage-vision` | capture → `product-brief.md` (quoi/pourquoi, sans techno) | capture existe |
| 3 | `cadrage-glossaire` | langage ubiquitaire sourcé ; **affiché en chat, validé terme par terme** | capture existe |
| 4 | `cadrage-decoupage` | découpage **fonctionnel** (use cases par valeur) + couplage (hypothèse) ; **table affichée en chat** ; arbitrage **en session** | `vision_complete` |
| 5 | `cadrage-demonstrateur-brief` | prompt Claude Design (initial/adaptatif), sauvé sous `factory-prompts/` | vision dispo / retour dispo |
| 6 | `cadrage-retour-demonstrateur` | ingère le retour client, résout/invalide | retour dispo |
| 7 | `cadrage-clarification` | agrège les points ouverts → liste de balayage | ≥1 point ouvert |
| 8 | `cadrage-briefs` | brief auto-portant par feature (contrat central, 10 sections) | **arbitrage couplage + démonstrateur convergé** |
| 9 | `cadrage-completude` | confronte à la Definition of Ready ; rapport + **tableau + résumé d'état** en chat ; résolution interactive | aucune (rejouable) |
| 10 | `cadrage-handoff` | pré-constitution + briefs + spec index → repo SpecKit + plan de séquencement ; **expose le handoff designer** (parcours = spec-index, entités affichées = glossaire, maquette = direction) | **prêt pour SpecKit** |

Flux : `cadrage-init` → `extraction` → (`vision` ∥ `glossaire`) → `decoupage` →
**boucle démonstrateur** [`demonstrateur-brief` ⟳ `clarification` → `retour-demonstrateur`]
jusqu'à convergence → **revue de couplage humaine** → `briefs` → `completude` → `handoff`.
`completude` et `clarification` sont rejouables à tout moment. Aide : `/cadrage:help-cadrage`.

## Workspace du projet client (structure plate)
```
factory-docs/
├── manifest.json     # état machine du projet
├── templates/        # gabarits FR installés (copies projet)
└── work/             # TOUS les artefacts à plat : capture-brute, project-frame,
                      #   product-brief, glossaire, spec-index, coupling-map,
                      #   arbitrage-log, 00X-*.brief.md, pre-constitution, completude-report
factory-prompts/      # prompts générés, en <NNN>-<JJ-MM>-<nom>/
```
Pas de sous-dossiers numérotés. Le pack SpecKit du handoff se dépose dans le **repo cible**.

## Schéma du manifeste (`factory-docs/manifest.json`)
Créé par `cadrage-init` uniquement. Blocs : `project`/`client`/dates ; `phase` ;
`sources[]` ; `artifacts{}` (capture_brute, project_frame, product_brief, glossaire,
spec_index{arbitrated}, arbitrage_log{entries}, briefs[], pre_constitution) ;
`demonstrateur{client_validated, iterations[]}` ; `validation_points[]` ; `prompts[]` ;
`discovery[]` (13 entrées Q1–Q13, statut answered|pending|deferred|na) + `discovery_complete` ;
`definition_of_ready{}` (6 booléens) + `ready_for_speckit`. Écriture = read-modify-write
+ revalidation JSON.

## Invariants (à respecter dans tout skill)
- **Proposer, ne pas décider.** Aucun skill ne passe une gate humaine à vrai
  (`decoupage_arbitrated`, `client_validated`, `ready_for_speckit`).
- **Marquer, ne pas inventer.** Sans trace source → `[À VALIDER]` / `[NON COUVERT EN ATELIER]`.
  Un retour peut invalider un acquis → `[REMIS EN CAUSE]`. **Jamais de valeur démo factuelle.**
- **Idempotence.** `vision`/`glossaire`/`decoupage` rejoués corrigent en place.
- **Deux découpages.** Captation = découpage fonctionnel par valeur + couplage hypothèse ;
  la liste numérotée/séquencée + walking skeleton se figent à l'**architecture**.
- **Traçabilité.** Chaque énoncé porte sa `(src:)`.
- **Terme structurant** = mobilisé par la vision ou nom/frontière d'un use case ;
  `glossary_validated` = tous les `structural = yes` validés.
- **Complétude honnête.** Le verdict ne passe au vert que si **tout** est vert ;
  un point passé/bloquant reste rouge. Pas de chemin « démo → vert ».

## Conventions d'interaction (voir `references/`)
- **Boucle 3-options** (`references/interactive-loop.md`) : une question à la fois —
  réponse recommandée / passer / saisir. Jamais de liste de trous en bloc.
- **Pas de fuite de champ** (`references/ux-conventions.md`) : aucun nom d'attribut /
  clé JSON en sortie utilisateur ni dans les refus (table de correspondance fournie).
  Refus en langage naturel. Chaque skill finit par **une ligne « Étape suivante »**.
- **Langue** : **tout en français** — templates, artefacts, interaction, messages, descriptions de skills. (Les clés du manifeste et valeurs machine — `status`, `pending`, etc. — restent des identifiants.)

## Découverte (13 questions)
`references/discovery-questions.md` (lu par `cadrage-extraction`) ; statuts dans le
bloc `discovery` du manifeste ; garde-fou déterministe `scripts/check_discovery.py`
(échoue tant qu'une question reste `pending`/`deferred`). Q2/Q6/Q7 (charge/dispo/perf)
= *seeds qualité* pour le plugin `architecte`.

## Invocation (pas de `commands/`)
Chaque skill est invocable **directement** par l'utilisateur via `/cadrage:<skill>`
**et** auto-invocable par le modèle (via sa `description`). On n'utilise **pas** de
wrappers `commands/` : un command homonyme d'un skill crée une boucle infinie
(le command « lance le skill » qui re-résout vers le command). L'aide : `help-cadrage`
(détail de la phase cadrage) et `help-factory` (vue d'ensemble des 4 plugins de la Factory).

## Contrat central
`templates/feature-brief.md` (10 sections, auto-portant). Produit par `cadrage-briefs`,
validé par `cadrage-completude`, consommé par SpecKit. **Ne pas modifier sa structure.**

## Pour modifier un skill
Chaque `SKILL.md` : objectif, entrées, porte d'entrée, procédure, sortie, « Mise à
jour du manifeste ». Préserver les portes et la cohérence du schéma manifeste
(défini en entier dans `skills/cadrage-init/SKILL.md`, seul skill qui crée le manifeste).
