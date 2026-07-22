---
name: assembleur-convergence
description: Lit les 3 contrats (cadrage/architecte/designer) en parallèle, les converge, et produit le paquet de handoff SpecKit dans assembleur-out/ (pré-constitution, graines spec, feature-map, contexte technique, mémoire, CLAUDE.md).
---

# assembleur-convergence

Cœur de la phase convergence. **Lit les trois contrats, les converge, et produit un
paquet complet de handoff** que l'équipe donnera à SpecKit. L'IA propose et
structure ; **l'humain tranche** - c'est le **garant de cohérence**.

**Le paquet est produit UNIQUEMENT dans `assembleur-out/`.** Ce skill **n'écrit
jamais** dans un repo cible : il ne crée pas `.specify/`, pas de `specs/NNN/spec.md`,
pas de fichier que SpecKit génère lui-même. Il prépare la matière ; l'équipe lance
SpecKit avec ce paquet comme contexte.

## Pré-requis (vérification silencieuse)
`assembleur-init` a tourné (le manifeste contient le bloc `assembly`) et les trois
contrats amont sont présents (`cadrage-out/`, `architecte-out/`, `designer-out/`).
Vérifier sans l'annoncer ; sinon, orienter en clair vers `/assembleur:assembleur-init`.

## Porte de régénération (relance)
Avant toute (re)génération, appliquer `references/regeneration-gate.md`. Si le paquet **de ce skill**
existe déjà dans `assembleur-out/` (`pre-constitution.md`, `features/<id>-*.md`, `feature-map.md`,
`technical-context.md`, `coherence-report.md`, `attack-plan.md`), proposer le choix **Repartir de
zéro** (supprimer puis régénérer, `version: 1`) ou **Garder les deux (versionner)** (archiver
l'existant sous `_archives/`, régénérer au nom canonique en `version: N+1`) et **attendre** le choix.
**La porte couvre aussi le déploiement `.claude/`** : si `.claude/CLAUDE.md` ou `.claude/memory/`
existent déjà, poser le même choix **avant** de les réécrire (Repartir de zéro = les régénérer ;
Garder les deux = archiver l'existant sous `.claude/_archives/` puis régénérer au nom canonique) -
ils peuvent porter des **modifications manuelles de l'équipe** et ne sont jamais écrasés en silence.
Les autres écritures **hors `assembleur-out/`** (Linear, `specify init`, `init-cowork.md`) gardent
leurs propres règles d'idempotence et ne sont **pas** concernées par cette porte.
Premier passage (rien n'existe) : générer directement, sans porte.

## Étape 1 : Lecture parallèle des 3 contrats (map-reduce)

**Toujours (re)lire les 3 contrats depuis les fichiers committés** via les agents, **même si tu crois
les avoir déjà lus plus tôt dans cette session**. **Ne jamais** t'appuyer sur la mémoire du chat ni
prendre le raccourci "déjà en contexte" : le skill doit produire **le même paquet quel que soit
l'historique de conversation** (exécution **indépendante et reproductible** - autre personne, autre
session, même repo).

Pour aller vite et ne pas saturer le contexte, **dispatcher en parallèle** des
sous-agents lecteurs (`agentType: "contract-reader"`), **un par lot**, chacun avec un
**schéma de sortie structuré**. Lancer les **5 lots en un seul message** (appels
parallèles) puis synthétiser leurs retours :

1. **Fonctionnel** - lire `cadrage-out/product-brief.md`, `cadrage-out/project-frame.md`, et les
   briefs de feature **désignés par le manifeste** : `artifacts.briefs[]` donne, pour chaque
   feature, son **identifiant de use case** (`id` = `UC...`) et le **chemin** de son brief
   (`.path`) - ouvrir chaque brief par ce chemin, et **clé chaque extraction par son `id` de use
   case**, jamais par l'intitulé ni par le numéro `Feature 00X` de l'en-tête (numérotation
   provisoire du cadrage, renumérotée plus tard par le registre final). Si `artifacts.briefs[]`
   est **absent ou vide**, le **dire en clair** et demander à l'humain d'apparier briefs et use
   cases - **jamais** d'appariement par ressemblance de titre en silence.
   Extraire : identité produit
   (problème + objectif), **critères de succès du produit (métriques d'usage chiffrées)**,
   hors-périmètre global, contraintes (légales/sécurité/données),
   et - depuis `project-frame.md` - les réponses de découverte qui pèsent sur la fabrication :
   **cible d'hébergement/déploiement (Q11), budget infra (Q12), responsable d'exploitation (Q10),
   disponibilité/perf visées (Q6/Q7)** ; et **par use case** : user stories, critères d'acceptation
   (Given/When/Then), **critères de succès mesurables avec leur cible chiffrée - repris tous, y
   compris ceux laissés "cible à préciser à l'architecture"**, **et le hors-périmètre local (ce que la feature
   ne fait pas)**.
2. **Domaine** - lire `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`,
   `cadrage-out/coupling-map.md`. Extraire : langage ubiquitaire + entités clés ; la
   liste des use cases ; le **couplage / les dépendances** entre features ; le walking
   skeleton candidat.
3. **Technique** - lire `architecte-out/stack-technique.md`, `composants.md`, `standards-ingenierie.md`,
   `facteurs-et-qualite.md`, et `architecte-out/diagrammes.md` (si présent). Extraire le **Technical
   Context** (langage/version, dépendances, stockage, tests, plateforme cible, objectifs de perf,
   contraintes, échelle), les cibles qualité, les conventions, et - depuis les diagrammes - le
   **modèle de données (ERD : entités + relations/cardinalités)** et la **topologie de déploiement**.
4. **Décisions** - lire `architecte-out/decisions/ADR-*.md`, `architecte-out/impact-design.md`, et
   `architecte-out/risques.md` (si présent). Extraire : les principes techniques **non négociables**
   (issus des ADR), les décisions à impact design, et le **registre de risques + spikes / POC-avant-
   engagement** (avec le lien de dé-risquage du walking skeleton).
5. **Design** - lire `designer-out/design-guidelines.md`, `designer-out/coverage-report.md`.
   Extraire : la **règle design** (tout écran dérive de l'export committé du design system,
   aucun style en dur), les **états** par écran, les **patterns d'erreur**, le **niveau
   d'accessibilité** visé, et les **décisions d'expérience arbitrées à l'atelier** (navigation /
   organisation de l'information, tailles d'écran et points de bascule, langues, theming par
   client, ton des textes, confirmations et retours d'action, budget de performance UI) -
   chacune renvoyée `"absent"` si le rapport de couverture ne la tranche pas, jamais déduite.

Lire aussi le manifeste (`artifacts.briefs[]` = `{id, name, path, status}`,
`architecture.feature_sequence` = `{id, ucs, name}`,
`walking_skeleton`, `design.design_system_ref`). Chaque lot renvoie un **extrait
structuré complet** (fidèle sur le fond, organisé) - jamais un résumé qui coupe, jamais
un dump brut. La jointure des faces se fait **par use case** : la face fonctionnelle
d'une feature du registre, ce sont les briefs dont l'`id` appartient à ses `ucs`. Cette
appartenance est la **seule** clé d'appariement autorisée - ni l'intitulé métier, ni le
numéro `Feature 00X` de l'en-tête d'un brief, ni le nom du fichier.

**Passe de complétude (exactitude).** Avant de synthétiser, recouper les retours : chaque
use case du `spec-index` a-t-il sa matière fonctionnelle, technique et design ? chaque brief
de `artifacts.briefs[]` a-t-il bien été ouvert par son `.path` et rendu sous son `id` ?
chaque feature porte-t-elle son **hors-périmètre local** ? **chaque critère de succès chiffré
d'un brief est-il remonté** (aucun perdu, aucun arrondi) ? les **entités et relations du modèle de données (ERD)**
sont-elles capturées, les **contraintes de déploiement/hébergement** présentes, les **risques/spikes**
remontés ? les **décisions d'expérience** (navigation, tailles d'écran, langues, ton) sont-elles
reprises ou explicitement marquées absentes ? un lot est-il revenu incomplet ? deux lots se
contredisent-ils ? **Relire** le lot concerné
si un trou ou une contradiction apparaît. Ne synthétiser que sur des retours complets.

## Étape 2 : Produire le paquet `assembleur-out/`

**Étape 2.0 - Arbitrage du registre de features (autorité finale de l'assembleur).** La
`architecture.feature_sequence` reçue de l'architecte est une **proposition**. C'est **ici** que le
découpage en features devient **définitif** : présenter la séquence proposée et, avec l'humain ("l'IA
propose, l'humain tranche"), **arbitrer** si besoin - **découper** une feature en deux, **fusionner**
deux features (une seule entrée, `ucs` = liste des use cases concernés). Puis **réécrire**
`architecture.feature_sequence` avec la liste **finale**, renumérotée **contiguë** `001...00N` dans
l'ordre de fabrication (walking skeleton = `001`). **Chaque entrée porte ses `ucs`**, et avant
d'écrire, vérifier que l'union des `ucs` du registre **couvre exactement** l'ensemble des
`artifacts.briefs[].id` : aucun use case orphelin (brief sans feature), aucun use case fantôme
(feature qui référence un `id` sans brief). Tout écart se **tranche avec l'humain ici**, jamais
plus tard. Les graines, la `feature-map` et Linear en
**découlent** (couverture 1:1 sur ce registre final). Ce registre est **figé à l'init Linear**
(`premier-alimente-linear`) - après, plus de découpage/fusion ni de renumérotation. Manifeste mis à
jour en silence.

À partir des extractions **et du registre final ci-dessus**, écrire (gabarits dans `.factory/assembleur/`) :

- **`pre-constitution.md`** (gabarit `pre-constitution.md`) - **mappe 1:1 le
  `constitution.md` SpecKit** : principes non négociables P1..Pn (fonctionnel : identité,
  hors-périmètre, langage ; technique : stack, règles ADR, cibles qualité, conventions,
  contraintes d'hébergement/souveraineté/budget infra (<- découverte), walking-skeleton-first ;
  **design § non négociable** : tout écran dérive du design
  system synchronisé, aucun style en dur, chaque écran couvre ses états, les erreurs
  suivent le contrat, accessibilité au niveau visé ; **tests : écrits avec le code, unitaires
  passant/échec/limite, intégration mockée**) + gouvernance + footer
  version/ratification. **Prêt pour `/speckit.constitution`, sans contexte supplémentaire.**
- **`features/<id>-<slug>.md`** (gabarit `spec-seed.md`), une par feature de
  la séquence (walking skeleton d'abord) - **mappe le `spec.md` SpecKit** : User Scenarios
  (P1/P2/P3, Given/When/Then), Functional Requirements (FR-xxx), Key Entities (<- domaine,
  **relations <- ERD**), Success Criteria (SC-xxx mesurables <- **critères de succès chiffrés du
  brief de ses use cases**, complétés par les cibles qualité + a11y ; aucune cible du brief
  écartée), **Hors
  périmètre (cette feature)** (<- hors-périmètre local du brief), Assumptions (**absorbe les
  risques/spikes de la feature**), + annexes face technique / face design. Le `<slug>` est un **slug git/SpecKit-safe** (`[a-z0-9-]` : minuscules,
  tirets, ASCII, ≤ ~4 mots) dérivé de l'intitulé métier. **`<id>-<slug>` EST le nom canonique** du
  répertoire SpecKit (`specs/<id>-<slug>/`) **et** de la branche git de la feature - jamais
  d'auto-numérotation SpecKit (collision entre développeurs). Reporter **le même `<id>-<slug>`** dans
  la colonne "Répertoire / branche SpecKit" de `feature-map.md`.
- **`feature-map.md`** (gabarit `feature-map.md`) - la **liste numérotée et séquencée** +
  le **couplage / les dépendances** + le walking skeleton. C'est l'info de découpage que
  SpecKit doit connaître pour ordonner les `/speckit.specify`.
- **`technical-context.md`** (gabarit `technical-context.md`) - le **Technical Context**
  projet (mappe la section du `plan.md` SpecKit), **enrichi d'une section modèle de données (ERD)
  et d'une section déploiement/hébergement** (topologie + réponses de découverte : hébergement,
  budget infra, exploitation, disponibilité).
- **`.claude/memory/`** (écrit **directement dans le `.claude/` du projet**, PAS dans `assembleur-out/`)
  - contexte durable (convention `MEMORY.md`) : `MEMORY.md` (index concis : des **pointeurs en liens
  Markdown** `[titre](chemin) - accroche`, jamais des chemins bruts entre backticks ; **ne lie en dur
  que ses voisins de `memory/`** - `domain.md`, `architecture.md`, `design.md`, `features.md` (chemin =
  **nom nu**, **jamais** `memory/domain.md`), car ce sont les seuls fichiers qui **voyagent avec**
  l'index ; les fichiers du paquet `assembleur-out/` - contexte technique, carte des features,
  pré-constitution - sont cités **en texte simple**, jamais en lien `../` cassable), `domain.md`
  (langage ubiquitaire + entités - **remplace l'ancien GLOSSARY**), `architecture.md` (stack,
  composants, digest ADR, conventions, cibles qualité - **chaque section pointe le fichier complet
  d'`architecte-out/`** : `composants.md`, `decisions/`, `standards-ingenierie.md`,
  `facteurs-et-qualite.md`), `design.md` (réf. design system + guidelines : états, erreurs, a11y,
  **et les décisions d'expérience de l'atelier** - navigation, tailles d'écran, langues, ton -
  "sans objet" ou "non tranché" si l'atelier ne les a pas décidées, jamais inventées ; renvoi vers
  `designer-out/design-guidelines.md` et `coverage-report.md`), `features.md` (séquence + couplage +
  walking skeleton + pointeurs des 3 faces).
- **`.claude/CLAUDE.md`** (gabarit `project-claude-md.md`, écrit **directement dans le `.claude/` du
  projet**) - instructions projet **< 200 lignes** pour la fabrication : identité, principes, la
  **règle design** (export committé), où vivent conventions/constitution, la séquence de features, les
  commandes build/test (depuis la stack), **+ l'`@import` de l'index mémoire** : une ligne
  `@memory/MEMORY.md` **jamais entre backticks** (un `@import` backtiqué est traité comme du texte
  littéral -> non importé). `MEMORY.md` (chargé à chaque session) pointe vers les fichiers thématiques,
  lus **à la demande**. `CLAUDE.md` et `memory/` sont **co-localisés dans `.claude/`** - l'`@import` et
  les liens résolvent en relatif (`.claude/CLAUDE.md` -> `.claude/memory/MEMORY.md`).
- **`attack-plan.md`** (gabarit `attack-plan.md`) - l'ordre de fabrication : `specify init`,
  puis `/speckit.constitution` (depuis `pre-constitution.md`), puis `/speckit.specify` par
  feature dans l'ordre des dépendances (walking skeleton d'abord), puis `/speckit.plan` ->
  `/speckit.tasks`. Le gabarit porte aussi les **règles de fabrication parallèle** (multi-dev,
  intégration/merge, intendance de la constitution, rappel des portes natives optionnelles), **selon
  `references/fabrication-parallele.md`** - sans jamais réécrire SpecKit : la séquence `/speckit.*`
  reste celle de SpecKit. Il **surface les spikes / le dé-risquage** (depuis le registre de risques
  architecte) dans la séquence de fabrication.

**Déploiement `.claude/` (exception bornée au "paquet seul").** `CLAUDE.md` et le dossier `memory/`
sont les **seuls** artefacts écrits **hors `assembleur-out/`** : ils vont **directement dans le
`.claude/` du projet** (à la racine du dossier de travail courant), pour être **actifs immédiatement**
(Claude Code les charge dès la session suivante) sans copie manuelle. Créer `.claude/` et `.claude/memory/`
s'ils manquent ; ne pas toucher au reste de `.claude/` (hooks, settings). Tout le reste du paquet reste
dans `assembleur-out/`.

**Contenu seul** : aucune `(src:)`, aucun horodatage, aucun nom de personne dans le paquet.

## Étape 3 : Cohérence (décision humaine : garant de cohérence)
Vérifier **strictement** que chaque feature part avec ses **3 faces complètes et non
contradictoires** : 3 faces présentes ; couverture inverse **vérifiée sur les `ucs`, jamais sur
les intitulés** (aucun `artifacts.briefs[].id` hors du registre, chaque feature a sa graine) ;
**chaque critère de succès chiffré des briefs a son SC dans la graine correspondante** ;
non-contradiction (design system couvre les états requis ;
pas de parcours sans FR ni de FR sans parcours ; pas de terme de glossaire en conflit ;
les cibles qualité/perf sont tenables par la stack/déploiement). Écrire
`assembleur-out/coherence-report.md` (prose, sans marqueur résiduel). Lancer le garde-fou
(**obligatoire**) : `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_assembly.py" <racine>/manifest.json`.
S'il est **introuvable** (chemin plugin non résolu) ou renvoie **exit 1**, **s'arrêter** et **dire en
clair** ce qui manque - **jamais** de vérification "à la main" silencieuse.

**Récapitulatif de validation (obligatoire, juste avant la question).** Ne **jamais** poser la
question de validation "à sec" : le garant doit **voir ce qu'il approuve**. Afficher d'abord un
récapitulatif clair et présentable de ce qui a été convergé -
- une phrase de contexte (le produit + le nombre de features) ;
- un **tableau de synthèse, une ligne par feature** : intitulé métier **en clair** (jamais un
  identifiant `001` / `UC1`), les **3 faces** (fonctionnel / technique / design - `Oui` couverte, ou
  "sans objet" **motivé** en une poignée de mots, ex. "pas d'écran direct"), le **verdict de
  cohérence** (cohérente / à revoir) et un éventuel **point d'attention** ;
- une ligne sur le **paquet produit** (pré-constitution, graines spec, carte des features, contexte
  technique, mémoire, CLAUDE.md).

**Puis** poser la question de validation. Le tableau reste en **langage naturel** au service de la
lisibilité de la porte : **noms en clair uniquement**, aucune clé manifeste, aucun booléen brut. L'humain
valide. Ne **jamais** valider la cohérence de soi-même.

## Étape 4 : Résolution interactive des points (obligatoire avant de conclure)
Balayer **tout le paquet** : pour **chaque** marqueur `[À VALIDER]` / `[À CHIFFRER]` /
`NEEDS CLARIFICATION` restant, **poser la question** à l'utilisateur - **un par un**,
réponse recommandée (adaptée au projet) + alternative + saisir, cf.
`references/interactive-loop.md` - et **écrire la réponse en place** dans le fichier
concerné. **Aucun fichier annexe.** **Ne pas conclure** tant qu'un marqueur subsiste.

## Vérification avant de conclure
- Le paquet est complet dans `assembleur-out/` : `pre-constitution.md`, `features/` (≥1
  graine, une par feature de la séquence), `feature-map.md`, `technical-context.md`,
  `coherence-report.md`, `attack-plan.md`.
- `CLAUDE.md` et `memory/` (MEMORY.md + thématiques) sont écrits dans **`.claude/`** du projet.
- **Aucun marqueur résiduel**, aucune `(src:)`, **rien écrit hors `assembleur-out/` - sauf**
  `.claude/CLAUDE.md` et `.claude/memory/` (déploiement).
- Mettre à jour le manifeste **en silence**.

## Règles invariantes
- **Paquet seul (une exception bornée).** N'écrit que dans `assembleur-out/`, jamais un fichier que
  SpecKit génère - **sauf** `CLAUDE.md` et `memory/`, écrits **directement dans `.claude/` du projet**
  (déploiement, pour qu'ils soient actifs sans copie manuelle).
- **Proposer, ne pas décider.** La cohérence est validée par l'humain.
- **Rien laissé indéfini.** Tout marqueur se résout en session, en place, avant d'avancer.
- **Balayage typographie.** Vérifier que le paquet `assembleur-out/` et les fichiers déployés dans `.claude/` (CLAUDE.md, memory/) ne contiennent aucun glyphe de style IA (tiret cadratin, points de suspension unicode, flèches unicode, guillemets à chevrons, coche/croix) ; remplacer par l'équivalent clavier en place (cf. la section Typographie de `references/ux-conventions.md`).
- **Rien de la mécanique affiché.** Aucun nom de variable/clé manifeste ; **seul tableau autorisé :
  le récapitulatif de la porte de validation** (noms en clair, pas de booléen brut) ; manifeste mis à
  jour en silence (voir `references/ux-conventions.md`).
- **Lecture depuis les fichiers, jamais depuis la session.** Les 3 contrats sont **toujours** (re)lus
  depuis les fichiers committés via les 5 agents, indépendamment de ce qui est déjà en contexte - pas
  de raccourci "déjà lu en session" (exécution reproductible par n'importe qui).

À la fin, dire en clair **ce qui a été produit** (en prose) et **la prochaine étape**.

**Handoff (avant de passer la main).** Committer `manifest.json` **et** `assembleur-out/` (le
paquet) - l'équipe qui lance SpecKit part du **repo committé**, pas de ta session.

Étape suivante : `/assembleur:premier-alimente-linear` crée un ticket Linear par feature (confirmation ticket par ticket) ; puis `/assembleur:install-speckit` pose SpecKit dans le repo (`specify init`, sans manip). Ensuite l'équipe fabrique feature par feature : `/speckit.constitution` depuis `pre-constitution.md`, puis les `/speckit.specify` dans l'ordre du `feature-map.md` (walking skeleton d'abord).
