---
name: assembleur-convergence
description: Lit les 3 contrats (cadrage/architecte/designer) en parallèle, les converge, et produit le paquet de handoff SpecKit dans assembleur-out/ (pré-constitution, graines spec, feature-map, contexte technique, mémoire, CLAUDE.md).
---

# assembleur-convergence

Cœur de la phase convergence. **Lit les trois contrats, les converge, et produit un
paquet complet de handoff** que l'équipe donnera à SpecKit. L'IA propose et
structure ; **l'humain tranche** — c'est le **garant de cohérence**.

**Le paquet est produit UNIQUEMENT dans `assembleur-out/`.** Ce skill **n'écrit
jamais** dans un repo cible : il ne crée pas `.specify/`, pas de `specs/NNN/spec.md`,
pas de fichier que SpecKit génère lui-même. Il prépare la matière ; l'équipe lance
SpecKit avec ce paquet comme contexte.

## Pré-requis (vérification silencieuse)
`assembleur-init` a tourné (le manifeste contient le bloc `assembly`) et les trois
contrats amont sont présents (`cadrage-out/`, `architecte-out/`, `designer-out/`).
Vérifier sans l'annoncer ; sinon, orienter en clair vers `/assembleur:assembleur-init`.

## Étape 1 — Lecture parallèle des 3 contrats (map-reduce)

**Toujours (re)lire les 3 contrats depuis les fichiers committés** via les agents, **même si tu crois
les avoir déjà lus plus tôt dans cette session**. **Ne jamais** t'appuyer sur la mémoire du chat ni
prendre le raccourci « déjà en contexte » : le skill doit produire **le même paquet quel que soit
l'historique de conversation** (exécution **indépendante et reproductible** — autre personne, autre
session, même repo).

Pour aller vite et ne pas saturer le contexte, **dispatcher en parallèle** des
sous-agents lecteurs (`agentType: "contract-reader"`), **un par lot**, chacun avec un
**schéma de sortie structuré**. Lancer les **5 lots en un seul message** (appels
parallèles) puis synthétiser leurs retours :

1. **Fonctionnel** — lire `cadrage-out/product-brief.md`, `cadrage-out/project-frame.md`,
   `cadrage-out/features-fonctionnels-brief/*.brief.md`. Extraire : identité produit
   (problème + objectif), hors-périmètre global, contraintes (légales/sécurité/données),
   et **par feature** : user stories, critères d'acceptation (Given/When/Then), critères
   de succès mesurables.
2. **Domaine** — lire `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`,
   `cadrage-out/coupling-map.md`. Extraire : langage ubiquitaire + entités clés ; la
   liste des use cases ; le **couplage / les dépendances** entre features ; le walking
   skeleton candidat.
3. **Technique** — lire `architecte-out/tech-stack.md`, `components.md`, `standards.md`,
   `drivers-quality.md`. Extraire le **Technical Context** (langage/version, dépendances,
   stockage, tests, plateforme cible, objectifs de perf, contraintes, échelle), les
   cibles qualité, et les conventions.
4. **Décisions** — lire `architecte-out/decisions/ADR-*.md`, `architecte-out/design-impact.md`.
   Extraire : les principes techniques **non négociables** (issus des ADR) et les
   décisions à impact design.
5. **Design** — lire `designer-out/design-guidelines.md`, `designer-out/coverage-report.md`.
   Extraire : la **règle design** (tout écran dérive de l'export committé du design system,
   aucun style en dur), les **états** par écran, les **patterns d'erreur**, le **niveau
   d'accessibilité** visé.

Lire aussi le manifeste (`architecture.feature_sequence` = `{id, ucs, name}`,
`walking_skeleton`, `design.design_system_ref`). Chaque lot renvoie un **extrait
structuré complet** (fidèle sur le fond, organisé) — jamais un résumé qui coupe, jamais
un dump brut. La jointure des faces se fait **par use case** (`ucs`).

**Passe de complétude (exactitude).** Avant de synthétiser, recouper les retours : chaque
use case du `spec-index` a-t-il sa matière fonctionnelle, technique et design ? un lot
est-il revenu incomplet ? deux lots se contredisent-ils ? **Relire** le lot concerné si
un trou ou une contradiction apparaît. Ne synthétiser que sur des retours complets.

## Étape 2 — Produire le paquet `assembleur-out/`

À partir des extractions, écrire (gabarits dans `.factory/templates/`) :

- **`pre-constitution.md`** (gabarit `pre-constitution.md`) — **mappe 1:1 le
  `constitution.md` SpecKit** : principes non négociables P1..Pn (fonctionnel : identité,
  hors-périmètre, langage ; technique : stack, règles ADR, cibles qualité, conventions,
  walking-skeleton-first ; **design § non négociable** : tout écran dérive du design
  system synchronisé, aucun style en dur, chaque écran couvre ses états, les erreurs
  suivent le contrat, accessibilité au niveau visé ; **tests : écrits avec le code, unitaires
  passant/échec/limite, intégration mockée, backstop CI diff-coverage**) + gouvernance + footer
  version/ratification. **Prêt pour `/speckit.constitution`, sans contexte supplémentaire.**
- **`features/<id>-<feature>.spec-seed.md`** (gabarit `spec-seed.md`), une par feature de
  la séquence (walking skeleton d'abord) — **mappe le `spec.md` SpecKit** : User Scenarios
  (P1/P2/P3, Given/When/Then), Functional Requirements (FR-xxx), Key Entities (← domaine),
  Success Criteria (SC-xxx mesurables ← cibles qualité + a11y), Assumptions, + annexes face
  technique / face design. Le `<feature>` est l'intitulé métier en clair.
- **`feature-map.md`** (gabarit `feature-map.md`) — la **liste numérotée et séquencée** +
  le **couplage / les dépendances** + le walking skeleton. C'est l'info de découpage que
  SpecKit doit connaître pour ordonner les `/speckit.specify`.
- **`technical-context.md`** (gabarit `technical-context.md`) — le **Technical Context**
  projet (mappe la section du `plan.md` SpecKit).
- **`ci/tests.yml`** (gabarit `ci-tests.yml`) — workflow CI lançant les tests + un **gate
  diff-coverage requis** (couverture des lignes modifiées) : le **backstop non contournable** de la
  règle « tests écrits avec le code ». Produit **dans le paquet** ; l'équipe le pose comme *required
  status check* (l'assembleur n'écrit jamais dans le repo cible).
- **`memory/`** — contexte durable (convention `MEMORY.md`) : `MEMORY.md` (index concis,
  pointeurs), `domain.md` (langage ubiquitaire + entités — **remplace l'ancien GLOSSARY**),
  `architecture.md` (stack, composants, digest ADR, conventions, cibles qualité),
  `design.md` (réf. design system + guidelines : états, erreurs, a11y), `features.md`
  (séquence + couplage + walking skeleton + pointeurs des 3 faces).
- **`CLAUDE.md`** (gabarit `project-claude-md.md`) — instructions projet **< 200 lignes**
  pour la fabrication : identité, principes, la **règle design** (export committé), où vivent
  conventions/constitution, la séquence de features, les commandes build/test (depuis la
  stack), **+ l'`@import` de l'index mémoire** : une ligne `@memory/MEMORY.md` **jamais entre
  backticks** (un `@import` backtiqué est traité comme du texte littéral → non importé). `MEMORY.md`
  (chargé à chaque session) pointe vers les fichiers thématiques, lus **à la demande**. `CLAUDE.md`
  et `memory/` sont posés **à la racine** du repo de fabrication (les `@imports` sont relatifs).
- **`attack-plan.md`** (gabarit `attack-plan.md`) — l'ordre de fabrication : `specify init`,
  puis `/speckit.constitution` (depuis `pre-constitution.md`), puis `/speckit.specify` par
  feature dans l'ordre des dépendances (walking skeleton d'abord), puis `/speckit.plan` →
  `/speckit.tasks`.

**Contenu seul** : aucune `(src:)`, aucun horodatage, aucun nom de personne dans le paquet.

## Étape 3 — Cohérence (décision humaine : garant de cohérence)
Vérifier **strictement** que chaque feature part avec ses **3 faces complètes et non
contradictoires** : 3 faces présentes ; couverture inverse (aucun use case orphelin,
chaque feature a sa graine) ; non-contradiction (design system couvre les états requis ;
pas de parcours sans FR ni de FR sans parcours ; pas de terme de glossaire en conflit ;
les cibles qualité/perf sont tenables par la stack/déploiement). Écrire
`assembleur-out/coherence-report.md` (prose, sans marqueur résiduel). Lancer le garde-fou
(**obligatoire**) : `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_assembly.py" <racine>/.factory/manifest.json`.
S'il est **introuvable** (chemin plugin non résolu) ou renvoie **exit 1**, **s'arrêter** et **dire en
clair** ce qui manque — **jamais** de vérification « à la main » silencieuse. **Restituer en prose** ;
l'humain valide. Ne **jamais** valider la cohérence de soi-même.

## Étape 4 — Résolution interactive des points (obligatoire avant de conclure)
Balayer **tout le paquet** : pour **chaque** marqueur `[À VALIDER]` / `[À CHIFFRER]` /
`NEEDS CLARIFICATION` restant, **poser la question** à l'utilisateur — **un par un**,
réponse recommandée (adaptée au projet) + alternative + saisir, cf.
`references/interactive-loop.md` — et **écrire la réponse en place** dans le fichier
concerné. **Aucun fichier annexe.** **Ne pas conclure** tant qu'un marqueur subsiste.

## Vérification avant de conclure
- Le paquet est complet dans `assembleur-out/` : `pre-constitution.md`, `features/` (≥1
  graine, une par feature de la séquence), `feature-map.md`, `technical-context.md`,
  `memory/` (MEMORY.md + thématiques), `CLAUDE.md`, `ci/tests.yml`, `coherence-report.md`, `attack-plan.md`.
- **Aucun marqueur résiduel**, aucune `(src:)`, **rien écrit hors `assembleur-out/`**.
- Mettre à jour le manifeste **en silence**.

## Règles invariantes
- **Paquet seul.** N'écrit que dans `assembleur-out/` ; jamais dans un repo cible, jamais
  un fichier que SpecKit génère.
- **Proposer, ne pas décider.** La cohérence est validée par l'humain.
- **Rien laissé indéfini.** Tout marqueur se résout en session, en place, avant d'avancer.
- **Rien de la mécanique affiché.** Aucun nom de variable/clé manifeste, aucun tableau ;
  manifeste mis à jour en silence (voir `references/ux-conventions.md`).
- **Lecture depuis les fichiers, jamais depuis la session.** Les 3 contrats sont **toujours** (re)lus
  depuis les fichiers committés via les 5 agents, indépendamment de ce qui est déjà en contexte — pas
  de raccourci « déjà lu en session » (exécution reproductible par n'importe qui).

À la fin, dire en clair **ce qui a été produit** (en prose) et **la prochaine étape**.

**Handoff (avant de passer la main).** Committer `.factory/manifest.json` **et** `assembleur-out/` (le
paquet) — l'équipe qui lance SpecKit part du **repo committé**, pas de ta session.

Étape suivante : `/assembleur:premier-alimente-linear` crée un ticket Linear par feature (confirmation ticket par ticket) ; puis `/assembleur:install-speckit` pose SpecKit dans le repo (`specify init`, sans manip). Ensuite l'équipe fabrique feature par feature : `/speckit.constitution` depuis `pre-constitution.md`, puis les `/speckit.specify` dans l'ordre du `feature-map.md` (walking skeleton d'abord).
