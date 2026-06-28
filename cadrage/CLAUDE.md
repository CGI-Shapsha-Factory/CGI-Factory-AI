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

## Les skills (11 du pipeline + `help-factory`)
`help-factory` (hors pipeline) est l'**aide unique** de la Factory : elle affiche, de façon **statique** (rendu immédiat), la **carte des 4 plugins** (cadrage → architecte → designer → assembleur → SpecKit) avec **un tableau par plugin** (rôle de chaque skill, ordre, portes humaines). C'est la seule aide — il n'y a plus de `help-cadrage` (son détail est absorbé dans le tableau cadrage).

| # | skill | rôle | porte |
|---|-------|------|-------|
| 0 | `cadrage-init` | crée `factory-docs/{templates,work}` + manifeste (le nom du projet est demandé par `cadrage-extraction`) | aucune |
| 1 | `cadrage-extraction` | matière brute (fichier/multi/dossier ; .txt/.md/.pdf/.docx) → `capture-brute.md` (contenu, **sans horodatage ni src**) + **passe découverte** (13 questions, interactive) → `project-frame.md` | manifeste existe + 1 source |
| 2 | `cadrage-vision` | capture → `product-brief.md` (quoi/pourquoi, sans techno) | capture existe |
| 3 | `cadrage-glossaire` | langage ubiquitaire **du projet** (termes métier, pas les outils/acronymes) ; **affiché en chat, validé en bloc** | capture existe |
| 4 | `cadrage-decoupage` | découpage **fonctionnel** (use cases par valeur, **sans MVP**) + couplage (hypothèse) ; **table affichée en chat** ; arbitrage **en session, écrit en place** | `vision_complete` |
| 5 | `cadrage-demonstrateur-brief` | prompt Claude Design (initial/adaptatif, **rendu pro** via `references/demonstrateur-prompt.md`), sauvé sous `factory-prompts/` — **fichier = corps du prompt seul** | vision dispo / retour dispo |
| 6 | `cadrage-retour-demonstrateur` | ingère le retour client, résout/invalide | retour dispo |
| 7 | `cadrage-clarification` | repose en session, une à une, les questions restées sans réponse | questions ouvertes |
| 8 | `cadrage-briefs` | brief auto-portant par feature (contrat central, 10 sections) | **arbitrage couplage + démonstrateur convergé** |
| 9 | `cadrage-completude` | confronte à la Definition of Ready ; rapport + **tableau + résumé d'état** en chat ; résolution interactive | aucune (rejouable) |
| 10 | `cadrage-handoff` | pré-constitution + briefs + spec index → repo SpecKit + plan de séquencement ; **expose le handoff designer** (parcours = spec-index, entités affichées = glossaire, maquette = direction) | **prêt pour SpecKit** |

Flux : `cadrage-init` → `extraction` → (`vision` ∥ `glossaire`) → `decoupage` →
**boucle démonstrateur** [`demonstrateur-brief` ⟳ `clarification` → `retour-demonstrateur`]
jusqu'à convergence → **revue de couplage humaine** → `briefs` → `completude` → `handoff`.
`completude` et `clarification` sont rejouables à tout moment. Aide : `/cadrage:help-factory`.

## Workspace du projet client (structure plate)
```
factory-docs/
├── manifest.json     # état machine du projet
├── templates/        # gabarits FR installés (copies projet)
└── work/             # TOUS les artefacts à plat : capture-brute, project-frame,
                      #   product-brief, glossaire, spec-index, coupling-map,
                      #   00X-*.brief.md, pre-constitution, completude-report
factory-prompts/      # prompts générés, en <NNN>-<JJ-MM>-<nom>/
```
Pas de sous-dossiers numérotés. Le pack SpecKit du handoff se dépose dans le **repo cible**.

## Schéma du manifeste (`factory-docs/manifest.json`)
Créé par `cadrage-init` uniquement. Blocs : `project`/dates ; `phase` ;
`sources[]` ; `artifacts{}` (capture_brute, project_frame, product_brief, glossaire,
spec_index{arbitrated}, briefs[], pre_constitution) ;
`demonstrateur{client_validated, iterations[]}` ; `validation_points[]` (boucle démonstrateur
uniquement — aucun point de découpage ouvert n'y est persisté) ; `prompts[]` ;
`discovery[]` (13 entrées Q1–Q13, statut answered|pending|deferred|na, **sans champ `source`**) + `discovery_complete` ;
`definition_of_ready{}` (6 booléens) + `ready_for_speckit`. Écriture = read-modify-write
+ revalidation JSON.

## Invariants (à respecter dans tout skill)
- **Proposer, trancher en session.** Les gates humaines (`decoupage_arbitrated`,
  `client_validated`, `ready_for_speckit`) ne s'allument pas toutes seules ; mais
  l'arbitrage de couplage se conduit **avec l'utilisateur dans le chat** et les
  décisions sont écrites **en place** (pas de journal séparé).
- **Ne rien inventer, ne rien persister d'ouvert.** On ne s'appuie que sur la matière ;
  un point non tranché est **omis** (jamais `[À VALIDER]` dans un artefact). Seul
  `[REMIS EN CAUSE]` survit (un acquis contredit par un retour). **Jamais de valeur démo.**
- **Tout interactif.** Tout point à clarifier se pose **en session** ; rien d'« à valider »
  n'est stocké dans un fichier, à aucun niveau.
- **Idempotence.** `vision`/`glossaire`/`decoupage` rejoués corrigent en place.
- **Deux découpages.** Captation = découpage fonctionnel par valeur + couplage hypothèse
  (**sans MVP**) ; la liste numérotée/séquencée + walking skeleton se figent à l'**architecture**.
- **Contenu, pas provenance.** Aucun horodatage, aucun interlocuteur, aucune `(src:)`
  dans les artefacts.
- **Glossaire = termes du projet.** Le vocabulaire de construction du produit (entités,
  rôles, actions), pas les outils/acronymes de l'existant ; validé **en bloc**.
- **Aucune mécanique exposée.** Jamais de « porte d'entrée », gate, RGPD/conformité
  affichés à l'utilisateur (cf. `references/ux-conventions.md`).

## Conventions d'interaction (voir `references/`)
- **Boucle interactive** (`references/interactive-loop.md`) : une question à la fois —
  réponse recommandée puis l'utilisateur accepte ou saisit la sienne (**pas de menu
  numéroté**). Un point non tranché est **omis**, jamais marqué.
- **Pas de fuite de champ** (`references/ux-conventions.md`) : aucun nom d'attribut /
  clé JSON en sortie utilisateur ni dans les refus (table de correspondance fournie).
  Refus en langage naturel. Chaque skill finit par **une ligne « Étape suivante »**.
- **Langue** : **tout en français** — templates, artefacts, interaction, messages, descriptions de skills. (Les clés du manifeste et valeurs machine — `status`, `pending`, etc. — restent des identifiants.)

## Découverte (13 questions)
`references/discovery-questions.md` (lu par `cadrage-extraction`) ; statuts dans le
bloc `discovery` du manifeste ; garde-fou déterministe `scripts/check_discovery.py`.
Une question tranchée = `answered` (sans provenance écrite) ; laissée de côté =
`deferred` (rien d'écrit dans l'artefact). Q2/Q6/Q7 (charge/dispo/perf)
= *seeds qualité* pour le plugin `architecte`.

## Invocation (pas de `commands/`)
Chaque skill est invocable **directement** par l'utilisateur via `/cadrage:<skill>`
**et** auto-invocable par le modèle (via sa `description`). On n'utilise **pas** de
wrappers `commands/` : un command homonyme d'un skill crée une boucle infinie
(le command « lance le skill » qui re-résout vers le command). L'aide : `help-factory`
(aide unique : la carte des 4 plugins, un tableau par plugin).

## Contrat central
`templates/feature-brief.md` (10 sections, auto-portant). Produit par `cadrage-briefs`,
validé par `cadrage-completude`, consommé par SpecKit. **Ne pas modifier sa structure.**

## Pour modifier un skill
Chaque `SKILL.md` : objectif, entrées, pré-requis (vérification silencieuse), procédure,
sortie, « Mise à jour du manifeste ». Préserver les pré-requis et la cohérence du schéma manifeste
(défini en entier dans `skills/cadrage-init/SKILL.md`, seul skill qui crée le manifeste).
