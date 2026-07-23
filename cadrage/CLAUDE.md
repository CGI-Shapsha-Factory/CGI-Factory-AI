# CLAUDE.md : plugin `cadrage`

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
python scripts/check_discovery.py <projet>/manifest.json
```
Tout JSON écrit par un skill (le manifeste runtime) doit reparser sans erreur.

## Distinction fondamentale
- Le **plugin** (`cadrage/`) = l'outil statique, réutilisable, sans données.
- Le **workspace + manifeste** = créés **dans le projet client** par `cadrage-init`.
  Le plugin lit/écrit ces fichiers ; il ne les contient pas.

## Les skills (9 du pipeline + `cadrage-ideation` facultatif + `help-factory`)
`help-factory` (hors pipeline) est l'**aide unique** de la Factory : elle affiche, de façon **statique** (rendu immédiat), la **carte des 6 plugins** (cadrage -> architecte -> designer -> assembleur -> SpecKit -> validation -> maintenance) avec **un tableau par plugin** (rôle de chaque skill, ordre, portes humaines). C'est la seule aide - il n'y a plus de `help-cadrage` (son détail est absorbé dans le tableau cadrage).

**Servie par un hook, pas par le modèle.** Le contenu étant 100 % statique, le faire ré-émettre par le modèle coûtait ~1000 tokens de sortie et ~34 s par invocation. Le plugin **embarque donc son propre hook** (seul de la Factory dans ce cas ; les hooks de `couts`/`architecte`/`assembleur` sont posés dans le `.claude/` du projet par un script d'init) :
- `hooks/hooks.json` - événement **`UserPromptExpansion`**, matcher regex `(^|:)help-factory$` (le nom de commande arrive tantôt `help-factory`, tantôt `cadrage:help-factory`). Auto-enregistré à l'installation du plugin, donc l'aide marche **partout, avant tout `-init`**.
- `scripts/help_factory_hook.py` - bloque l'expansion (`{"decision":"block","reason":<carte>}`) : le prompt **n'atteint jamais le modèle**, d'où zéro token de sortie et aucune latence de génération.
- **Source unique = le `SKILL.md`.** Le script en extrait tout ce qui suit le marqueur `## À afficher tel quel` (comparaison insensible aux accents). **Aucune duplication** : toute correction de la carte se fait dans le `SKILL.md`, jamais dans le script. Le corps du skill reste le **chemin de repli** si les hooks sont désactivés.
- **Le texte rendu par un hook n'est pas interprété comme du markdown** (vérifié à l'usage : tableaux pipe et `**` s'affichaient littéralement). Le script **redessine donc les tableaux en cadres ASCII** de 96 colonnes (`+-- Titre ---+`), nom de skill en colonne de 30, rôle habillé dans la cellule. Le `SKILL.md` reste écrit en markdown - c'est la conversion qui s'adapte, pas la source.
- **L'aide affichée ne montre que les skills et leur rôle.** Le rendu **ignore toute la prose** du `SKILL.md` (chapeau, handoff final, fabrication en parallèle, repère, étape suivante) ainsi que les colonnes `#` et `porte / ordre` : c'est un index consultable d'un coup d'oeil, pas un manuel. Le détail reste dans le `SKILL.md` (donc dans le chemin de repli) et dans les `<plugin>/CLAUDE.md`. Seuls les en-têtes `skill` et `porte...` sont reconnus par nom de colonne ; l'ordre des lignes fait foi.
- **La couleur de l'affichage n'est pas contrôlable** : c'est le style d'avis du harnais pour un prompt bloqué. Ne pas tenter de la forcer avec des séquences ANSI dans le `reason`.
- **Jamais bloquant** : fichier absent, marqueur introuvable ou toute exception -> `exit 0` **sans rien imprimer**, l'expansion normale reprend la main. La sortie est écrite en **octets UTF-8** (`sys.stdout.buffer`) car la console Windows est en cp1252 et ferait échouer l'encodage des accents.
- Toute évolution de l'aide doit s'accompagner d'un **bump de version** dans `.claude-plugin/plugin.json` : sans lui, la marketplace continue de servir la version en cache (c'est ce qui a fait traîner des noms de skills périmés côté utilisateurs).

| # | skill | rôle | porte |
|---|-------|------|-------|
| 0 | `cadrage-init` | crée `.factory/` (gabarits, git-ignoré) + `cadrage-out/` (docs) + le **manifeste committé** `manifest.json` **à la racine** (le nom du projet est demandé par `cadrage-extraction`) | aucune |
| 0bis | `cadrage-ideation` | **facultatif** - atelier d'idéation facilité (posture facilitateur : les idées viennent de l'utilisateur ; catalogue de techniques scriptées `references/techniques-ideation.md`, familles exploration + analytique dont pré-mortem, laddering, renversement d'hypothèses) ; le compte rendu (dont **hypothèses à vérifier** et **questions émergentes**) va dans `cadrage-out/source-contexte/ideation-<JJ-MM>.md`, repris comme source par `cadrage-extraction` (les deux dernières sections nourrissent Q19 et les points à creuser) ; n'écrit pas le manifeste, ne conditionne aucune porte | manifeste existe |
| 1 | `cadrage-extraction` | tour de table à chaud (brain dump + **pré-mortem / hypothèses**) puis matière brute (fichier/multi/dossier ; .txt/.md/.pdf/.docx) -> `capture-brute.md` (contenu, **sans horodatage ni src**) + **passe découverte** (19 questions, interactive) -> `project-frame.md` | manifeste existe + 1 source |
| 2 | `cadrage-vision` | capture -> `product-brief.md` (quoi/pourquoi, sans techno) | capture existe |
| 3 | `cadrage-glossaire` | langage ubiquitaire **du projet** (termes métier, pas les outils/acronymes) ; **affiché en chat, validé en bloc** | capture existe |
| 4 | `cadrage-decoupage` | découpage **fonctionnel** (use cases par valeur, **sans MVP**) + couplage (hypothèse) ; **table affichée en chat** ; arbitrage **en session, écrit en place** | `vision_complete` |
| 5 | `cadrage-demonstrateur-brief` | prompt Claude Design (initial/adaptatif, **rendu pro** via `references/demonstrateur-prompt.md`, **direction visuelle délibérée anti-slop - palette dérivée du domaine, jamais le violet/indigo par défaut**), sauvé sous `cadrage-out/prompts/` - **fichier = corps du prompt seul** | vision dispo / retour dispo |
| 6 | `cadrage-retour-demonstrateur` | ingère le retour client, résout/invalide | retour dispo |
| 7 | `cadrage-briefs` | brief auto-portant par feature (contrat central, 10 sections) | **arbitrage couplage + démonstrateur convergé** |
| 8 | `cadrage-completude` | **porte de complétude & cohérence ET point de résolution unique** : relit `cadrage-out/` **en parallèle** (fan-out `cadrage-reader`), **challenge** le pack fonctionnel en **4 lentilles** (Complétude / Cohérence / Qualité des exigences / Validation-prêt-architecte - ancré DoR, INVEST, ISO 29148, BABOK, DDD, MoSCoW, traçabilité ; `references/completude-checklist-guide.md`), rend le verdict Definition of Ready (prose, **jamais de tableau**), et **résout chaque écart comme une décision** (jamais un constat nu : "que veux-tu faire ?" + recommandée/alternative/saisie + application en place), puis relais vers l'architecte | aucune (rejouable) |

Flux : `cadrage-init` -> [`cadrage-ideation` facultatif si la matière est mince] -> `extraction` -> (`vision` ∥ `glossaire`) -> `decoupage` ->
**boucle démonstrateur** [`demonstrateur-brief` ⟳ `retour-demonstrateur` -> `completude`]
jusqu'à convergence -> **revue de couplage humaine** -> `briefs` -> `completude` -> **`/architecte:architecte-init`**.
`completude` est rejouable à tout moment (mesure le verdict **et** résout les points ouverts). Aide : `/cadrage:help-factory`.
**Plus de skill handoff** : l'architecte (puis l'assembleur) lisent directement les fichiers de `cadrage-out/` ; le handoff/convergence est le rôle de l'assembleur.

## Workspace du projet client
```
.factory/                          # caché, git-ignoré - gabarits seulement
└── cadrage/                       # gabarits FR du cadrage (copies projet)
manifest.json                      # contrat machine - COMMITTÉ à la racine, voyage avec le repo
cadrage-out/                       # documents générés, COMMITTÉ (à la racine)
├── source-contexte/               # matière brute déposée par l'utilisateur (facultatif)
├── maquette-de-claude-design/     # maquette du démonstrateur collée par l'utilisateur (vide au départ)
├── capture-brute, project-frame, product-brief, glossaire,
│   spec-index, coupling-map, completude-report
└── features-fonctionnels-brief/   # un brief par feature (<feature>.md)
cadrage-out/prompts/               # prompts générés, en <NNN>-<JJ-MM>-<nom>.md (fichiers plats)
```
Chaque plugin écrit dans son propre dossier de sortie à la racine (`cadrage-out/`,
`architecte-out/`, `designer-out/`, `assembleur-out/`) et lit ceux de l'amont.

## Schéma du manifeste (`manifest.json`)
Créé par `cadrage-init` uniquement. Blocs : `project`/dates ; `phase` ;
`sources[]` ; `artifacts{}` (capture_brute, project_frame, product_brief, glossaire,
spec_index{arbitrated}, briefs[]) ;
`demonstrateur{client_validated, iterations[]}` ; `validation_points[]` (boucle démonstrateur
uniquement - aucun point de découpage ouvert n'y est persisté) ; `prompts[]` ;
`discovery[]` (19 entrées Q1-Q19, statut answered|pending|deferred|na, **sans champ `source`**) + `discovery_complete` ;
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
- **Tout interactif.** Tout point à clarifier se pose **en session** ; rien d'"à valider"
  n'est stocké dans un fichier, à aucun niveau.
- **Idempotence.** `vision`/`glossaire`/`decoupage` rejoués corrigent en place.
- **Deux découpages.** Captation = découpage fonctionnel par valeur + couplage hypothèse
  (**sans MVP**) ; la liste numérotée/séquencée + walking skeleton se figent à l'**architecture**.
- **Contenu, pas provenance.** Aucun horodatage, aucun interlocuteur, aucune `(src:)`
  dans les artefacts.
- **Glossaire = termes du projet.** Le vocabulaire de construction du produit (entités,
  rôles, actions), pas les outils/acronymes de l'existant ; validé **en bloc**.
- **Aucune mécanique exposée.** Jamais de "porte d'entrée", gate, RGPD/conformité
  affichés à l'utilisateur ; **jamais de nom de variable** (`all_briefs_complete`,
  `cadrage_complete`...), **jamais d'identifiant codé** (`B1`, `A6`), **jamais de
  marqueur** `[À CHIFFRER]` - on reformule tout en langage naturel adapté au PO
  (cf. `references/ux-conventions.md`). **Seule exception : les use cases** - dans le
  découpage et la revue de couplage, on les nomme **intitulé complet en langage naturel
  suivi de `(UCn)`** (jamais un `UCn` nu), pour donner au PO un repère stable (§3ter).
- **Typographie humaine.** Aucun glyphe de style IA dans les artefacts, prompts et sorties : pas de tiret cadratin (em dash), de points de suspension unicode, de flèches unicode, de guillemets à chevrons, ni de coche/croix ; utiliser les équivalents clavier (cf. la section Typographie de `references/ux-conventions.md`).

## Conventions d'interaction (voir `references/`)
- **Boucle interactive** (`references/interactive-loop.md`) : une question à la fois, **toujours
  posée avec `AskUserQuestion`** - **exactement deux options** (la recommandée d'abord, puis
  l'alternative crédible), l'outil ajoutant lui-même la saisie libre en troisième ligne. **Jamais
  de question rédigée en prose dans le fil.** Un point non tranché est **omis**, jamais marqué. **Relance unique par défaut** : une réponse vague sur un point structurant est relancée **une seule
  fois** (coacher, pas quizzer) ; si l'utilisateur maintient, on écrit tel quel. **Sondage
  approfondi sur choix explicite** : sur un point structurant à enjeu fort resté mince, on peut
  proposer (deux options) de creuser ensemble - laddering court, plafond de trois crans,
  l'utilisateur peut clore à tout moment ; jamais sur le légal (Q8) ni sur un point laissé de
  côté. **Forks de conception** : à un choix de cadrage engageant (découper/fusionner,
  coupler/séparer, périmètre), chaque option **nomme son coût**, pas seulement recommandée vs
  alternative.
- **Pas de fuite de champ** (`references/ux-conventions.md`) : aucun nom d'attribut /
  clé JSON en sortie utilisateur ni dans les refus (table de correspondance fournie).
  Refus en langage naturel. Chaque skill finit par **une ligne "Étape suivante"**.
- **Langue** : **tout en français** - templates, artefacts, interaction, messages, descriptions de skills. (Les clés du manifeste et valeurs machine - `status`, `pending`, etc. - restent des identifiants.)
- **Porte de complétude** (`references/completude-checklist-guide.md`) : grille canonique de la
  porte `cadrage-completude`, ancrée DoR / INVEST / ISO-IEEE 29148 / BABOK / DDD / MoSCoW /
  traçabilité. Agent de lecture : `agents/cadrage-reader.md` (lecture complète + sortie structurée
  + signalement d'anomalies, dispatché en parallèle par `cadrage-completude`).
- **Porte de régénération** (`references/regeneration-gate.md`) : à la **relance** d'un skill de
  génération dont les sorties existent déjà, proposer le choix **Repartir de zéro** (supprimer +
  regénérer) ou **Garder les deux (versionner)** (archiver l'existant sous `_archives/`, regénérer
  au nom canonique) ; jamais d'écrasement sans choix explicite. Distinct du réjeu incrémental (fusion
  en place des corrections amont).

## Découverte (19 questions)
`references/discovery-questions.md` (lu par `cadrage-extraction`) ; statuts dans le
bloc `discovery` du manifeste ; garde-fou déterministe `scripts/check_discovery.py`.
Une question tranchée = `answered` (sans provenance écrite) ; laissée de côté =
`deferred` (rien d'écrit dans l'artefact). Q2/Q6/Q7 (charge/dispo/perf)
= *seeds qualité* pour le plugin `architecte`.

## Invocation (pas de `commands/`)
Chaque skill est invocable **directement** par l'utilisateur via `/cadrage:<skill>`
**et** auto-invocable par le modèle (via sa `description`). On n'utilise **pas** de
wrappers `commands/` : un command homonyme d'un skill crée une boucle infinie
(le command "lance le skill" qui re-résout vers le command). L'aide : `help-factory`
(aide unique : la carte des 6 plugins, un tableau par plugin).

## Contrat central
`templates/feature-brief.md` (10 sections, auto-portant). Produit par `cadrage-briefs`
(dans `cadrage-out/features-fonctionnels-brief/`), validé par `cadrage-completude`,
repris par l'architecte puis l'assembleur. **Ne pas modifier sa structure.**

## Pour modifier un skill
Chaque `SKILL.md` : objectif, entrées, pré-requis (vérification silencieuse), procédure,
sortie, "Mise à jour du manifeste". Préserver les pré-requis et la cohérence du schéma manifeste
(défini en entier dans `skills/cadrage-init/SKILL.md`, seul skill qui crée le manifeste).
