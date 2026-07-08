# CLAUDE.md — plugin `cadrage`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`cadrage` plugin** (this directory). For the factory-wide overview see
`../CLAUDE.md`.

## Ce qu'est le plugin
`cadrage` industrialise la **phase amont** (contrat fonctionnel) d'un projet
spec-driven : il transforme la **matière brute** d'un atelier (transcripts, docs)
en un **pack fonctionnel** (vision, glossaire, découpage, brief par feature) repris en aval par l'architecte.
Ce n'est **pas un projet applicatif** : ce sont des **skills Markdown** + un
`plugin.json`. Pas de build, pas de lint, pas de tests unitaires.

## Vérifications (à la place des tests)
```bash
# manifeste du plugin
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
# chaque skill a un frontmatter name
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
# garde-fou découverte (sur le manifeste d'un projet)
python scripts/check_discovery.py <projet>/.factory/manifest.json
```
Tout JSON écrit par un skill (le manifeste runtime) doit reparser sans erreur.

## Distinction fondamentale
- Le **plugin** (`cadrage/`) = l'outil statique, réutilisable, sans données.
- Le **workspace + manifeste** = créés **dans le projet client** par `cadrage-init`.
  Le plugin lit/écrit ces fichiers ; il ne les contient pas.

## Les skills (10 du pipeline + `help-factory`)
`help-factory` (hors pipeline) est l'**aide unique** de la Factory : elle affiche, de façon **statique** (rendu immédiat), la **carte des 4 plugins** (cadrage → architecte → designer → assembleur → SpecKit) avec **un tableau par plugin** (rôle de chaque skill, ordre, portes humaines). C'est la seule aide — il n'y a plus de `help-cadrage` (son détail est absorbé dans le tableau cadrage).

| # | skill | rôle | porte |
|---|-------|------|-------|
| 0 | `cadrage-init` | crée `.factory/` (manifeste + gabarits) + `cadrage-out/` (le nom du projet est demandé par `cadrage-extraction`) | aucune |
| 1 | `cadrage-extraction` | matière brute (fichier/multi/dossier ; .txt/.md/.pdf/.docx) → `capture-brute.md` (contenu, **sans horodatage ni src**) + **passe découverte** (13 questions, interactive) → `project-frame.md` | manifeste existe + 1 source |
| 2 | `cadrage-vision` | capture → `product-brief.md` (quoi/pourquoi, sans techno) | capture existe |
| 3 | `cadrage-glossaire` | langage ubiquitaire **du projet** (termes métier, pas les outils/acronymes) ; **affiché en chat, validé en bloc** | capture existe |
| 4 | `cadrage-decoupage` | découpage **fonctionnel** (use cases par valeur, **sans MVP**) + couplage (hypothèse) ; **table affichée en chat** ; arbitrage **en session, écrit en place** | `vision_complete` |
| 5 | `cadrage-demonstrateur-brief` | prompt Claude Design (initial/adaptatif, **rendu pro** via `references/demonstrateur-prompt.md`), sauvé sous `cadrage-out/prompts/` — **fichier = corps du prompt seul** | vision dispo / retour dispo |
| 6 | `cadrage-retour-demonstrateur` | ingère le retour client, résout/invalide | retour dispo |
| 7 | `cadrage-clarification` | repose en session, une à une, les questions restées sans réponse | questions ouvertes |
| 8 | `cadrage-briefs` | brief auto-portant par feature (contrat central, 10 sections) | **arbitrage couplage + démonstrateur convergé** |
| 9 | `cadrage-completude` | **étape terminale** : bilan Definition of Ready (résumé en prose, **jamais de tableau**) + résolution interactive en place, puis relais vers l'architecte | aucune (rejouable) |

Flux : `cadrage-init` → `extraction` → (`vision` ∥ `glossaire`) → `decoupage` →
**boucle démonstrateur** [`demonstrateur-brief` ⟳ `clarification` → `retour-demonstrateur`]
jusqu'à convergence → **revue de couplage humaine** → `briefs` → `completude` → **`/architecte:architecte-init`**.
`completude` et `clarification` sont rejouables à tout moment. Aide : `/cadrage:help-factory`.
**Plus de skill handoff** : l'architecte (puis l'assembleur) lisent directement les fichiers de `cadrage-out/` ; le handoff/convergence est le rôle de l'assembleur.

## Workspace du projet client
```
.factory/                          # caché — la mécanique interne
├── manifest.json                  # état machine du projet
└── cadrage/                       # gabarits FR du cadrage (copies projet)
cadrage-out/                       # documents générés par le cadrage (à la racine)
├── source-contexte/               # matière brute déposée par l'utilisateur (facultatif)
├── maquette-de-claude-design/     # maquette du démonstrateur collée par l'utilisateur (vide au départ)
├── capture-brute, project-frame, product-brief, glossaire,
│   spec-index, coupling-map, completude-report
└── features-fonctionnels-brief/   # un brief par feature (<feature>.md)
cadrage-out/prompts/               # prompts générés, en <NNN>-<JJ-MM>-<nom>.md (fichiers plats)
```
Chaque plugin écrit dans son propre dossier de sortie à la racine (`cadrage-out/`,
`architecte-out/`, `designer-out/`, `assembleur-out/`) et lit ceux de l'amont.

## Schéma du manifeste (`.factory/manifest.json`)
Créé par `cadrage-init` uniquement. Blocs : `project`/dates ; `phase` ;
`sources[]` ; `artifacts{}` (capture_brute, project_frame, product_brief, glossaire,
spec_index{arbitrated}, briefs[]) ;
`demonstrateur{client_validated, iterations[]}` ; `validation_points[]` (boucle démonstrateur
uniquement — aucun point de découpage ouvert n'y est persisté) ; `prompts[]` ;
`discovery[]` (13 entrées Q1–Q13, statut answered|pending|deferred|na, **sans champ `source`**) + `discovery_complete` ;
`definition_of_ready{}` (6 booléens) + `cadrage_complete`. Écriture = read-modify-write
+ revalidation JSON.

## Invariants (à respecter dans tout skill)
- **Proposer, trancher en session.** Les gates humaines (`decoupage_arbitrated`,
  `client_validated`, `cadrage_complete`) ne s'allument pas toutes seules ; mais
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
  affichés à l'utilisateur ; **jamais de nom de variable** (`all_briefs_complete`,
  `cadrage_complete`…), **jamais d'identifiant codé** (`B1`, `A6`), **jamais de
  marqueur** `[À CHIFFRER]` — on reformule tout en langage naturel adapté au PO
  (cf. `references/ux-conventions.md`). **Seule exception : les use cases** — dans le
  découpage et la revue de couplage, on les nomme **intitulé complet en langage naturel
  suivi de `(UCn)`** (jamais un `UCn` nu), pour donner au PO un repère stable (§3ter).

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
`templates/feature-brief.md` (10 sections, auto-portant). Produit par `cadrage-briefs`
(dans `cadrage-out/features-fonctionnels-brief/`), validé par `cadrage-completude`,
repris par l'architecte puis l'assembleur. **Ne pas modifier sa structure.**

## Pour modifier un skill
Chaque `SKILL.md` : objectif, entrées, pré-requis (vérification silencieuse), procédure,
sortie, « Mise à jour du manifeste ». Préserver les pré-requis et la cohérence du schéma manifeste
(défini en entier dans `skills/cadrage-init/SKILL.md`, seul skill qui crée le manifeste).
