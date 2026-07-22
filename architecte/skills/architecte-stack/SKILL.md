---
name: architecte-stack
description: Choisit la stack, active les conventions, arbitre les ADR et fige le walking skeleton et la séquence de features.
---

# architecte-stack

Cœur des décisions techniques. **Discipline le raisonnement de l'architecte et grave ses
décisions en contrats.** L'IA propose et structure ; **l'humain tranche** (choix de stack,
**arbitrage des ADR**). Ne décide jamais l'architecture à la place de l'architecte. Ce skill
choisit la **stack**, active les **conventions/linters**, consigne les **ADR** et fige le
**walking skeleton** + la séquence de features.

## Pré-requis (vérification silencieuse)
`architecte-fondations` a tourné : les composants sont produits (`architecte-out/composants.md`
présent, `architecture.components` non vide). Vérifier sans l'annoncer ; sinon, orienter en
clair vers `/architecte:architecte-fondations`.

## Entrées (relues des fichiers committés, jamais de la mémoire du chat)
`architecte-out/` : `facteurs-et-qualite.md` (drivers, attributs de qualité, contraintes),
`composants.md` (l'inventaire à câbler sur la stack). Le cadrage **au besoin** pour une
contrainte (`cadrage-out/project-frame.md`, `product-brief.md`, `spec-index.md`,
`coupling-map.md`). Conventions d'interaction : `references/interactive-loop.md`,
`references/ux-conventions.md` ; catalogues `references/conventions/`, gabarits `templates/`.

> **Règles transverses (toutes les étapes).** Restituer **en prose**, jamais en
> tableau. Désigner chaque chose par son **nom métier en clair** - jamais un code
> (`C1`, `UC1`, `P1`...). **Aucune provenance** écrite dans les artefacts (pas de
> `(src:)`, d'horodatage, de nom de personne). Mettre à jour le manifeste **en
> silence** : ne jamais narrer "MAJ `architecture.*`" ni un nom de variable, ni **aucune ligne de
> bilan** "Manifeste à jour : ..." / liste `champ: valeur` / `true`/`false` (l'utilisateur ne s'y
> intéresse pas). Toute
> valeur manquante se **résout en session** (cf. `references/interactive-loop.md`) et
> s'écrit **en place** - aucun marqueur n'est laissé dans un fichier final.
>
> **Versionnage des documents.** Chaque fichier écrit sous `architecte-out/` commence par un
> front-matter `--- version: N / date: AAAA-MM-JJ ---`. **Première** génération d'un document :
> `version: 1`. À chaque **régénération** : relire le `version:` existant et écrire **`N+1`**,
> avec `date:` = jour courant (format ISO `AAAA-MM-JJ`) - le helper
> `scripts/bump_doc_version.py <fichier>` calcule la prochaine version. **Exception ADR** : un ADR accepté est
> immuable - il **reste `version: 1`** et évolue via son champ `Statut` (+ un ADR successeur). Ce
> front-matter `version`/`date` est une **métadonnée de document** - il n'est **pas** visé par
> l'interdiction de provenance/horodatage (qui concerne le corps : pas de `(src:)`, pas
> d'horodatage épars, pas de nom de personne).

## Porte de régénération (relance)
Avant toute (re)génération, appliquer `references/regeneration-gate.md`. Si les sorties **de ce
skill** existent déjà, proposer le choix **Repartir de zéro** (supprimer puis générer à neuf,
`version: 1`) ou **Garder les deux (versionner)** (archiver l'existant sous `_archives/`, régénérer
au nom canonique en `version: N+1`) et **attendre** le choix - la porte se pose **avec `AskUserQuestion`** (deux options, cf. `references/regeneration-gate.md`). **Exception ADR** : un ADR accepté est
immuable ; la porte ne le supprime ni ne le versionne - il évolue via son champ `Statut` et un ADR
successeur (cf. la règle de versionnage des documents). Premier passage (rien n'existe) : générer
directement, sans porte.

## Procédure : ordre imposé (chaque étape consomme la précédente)

### Étape 1 : Workflow stack technique (interactif)
Domaines de décision : **langage(s), framework(s) back, framework front / bibliothèque de
composants / stratégie CSS-tokens, bibliothèques principales, base de données, style d'API,
communication asynchrone, fournisseur cloud, déploiement, observabilité**. Pour **chaque**
domaine (front et déploiement compris), **même si le cadrage suggère une piste** : poser la
question **avec `AskUserQuestion`** - **deux options réellement diverses**, la **recommandée**
d'abord, chacune portant ses avantages/inconvénients dans sa `description` ; une troisième piste
reste accessible par la saisie libre que l'outil ajoute. Puis
**attendre le choix explicite de l'utilisateur** avant de continuer. **Ne jamais
auto-sélectionner** une techno ni graver un choix non tranché.

**Anti-biais (obligatoire).** Un choix antérieur ne restreint pas silencieusement les suivants
à l'écosystème d'un même fournisseur : comme il n'y a que deux options, **l'option 2 est
obligatoirement hors de l'écosystème de l'option 1** - **interdit** de proposer deux options d'un
seul fournisseur (pas d'"Azure-vs-Azure"). Le **fournisseur cloud** et le **déploiement** sont des
**décisions ouvertes** à part entière : ne jamais les déduire d'une "infra existante" sauf si
l'utilisateur l'a **dit explicitement** - et alors, le lui **confirmer comme sa décision**, ne
pas l'affirmer.

**Expérience ≠ décision.** Si l'utilisateur mentionne connaître une techno ("je maîtrise
React"), **ne pas l'adopter d'office** : demander **avec `AskUserQuestion`** "Puisque tu connais
React, on part là-dessus ou on évalue d'autres options ?" - deux options, "on part sur React" et
"on évalue d'autres options". La décision finale vient **toujours** de lui.

Respecter l'ordre des dépendances entre choix (langage avant framework, etc.).
**Version exacte pour CHAQUE techno** : à la finalisation, chaque langage, framework,
bibliothèque, base et outil reçoit une **version exacte et épinglée** (ex. "PostgreSQL 17.2",
"React 19.1.0") - tranchée en session si inconnue ; **jamais** "latest" / "stable" / vide.
**Validation finale** de la stack en chat. Écrire `architecte-out/stack-technique.md` (gabarit
`templates/stack-technique.md`, dont la **matrice composant × techno** - une ligne par composant, **le
composant front inclus**). Mettre à jour le manifeste en silence.

### Étape 2 : Activer les conventions (vrais fichiers)
Pour chaque **langage retenu** au **workflow stack (étape 1)**, copier le(s) fichier(s) de config
correspondant du catalogue `references/conventions/` vers le dossier `conventions/`
du projet :
- Python -> `python/ruff.toml` ; TS/JS -> `ts-js-biome/biome.json` (défaut) **ou**
  `ts-js-eslint/{eslint.config.js,.prettierrc}` (demander lequel **avec `AskUserQuestion`**, Biome
  en recommandé) ; C ->
  `c/.clang-format`.
- **Fallback (langage hors catalogue)** : ne pas inventer de config exotique -
  garder le `.editorconfig` universel, **avertir l'utilisateur** que ce langage n'a
  pas de convention prédéfinie, et **proposer une convention générique** (indentation,
  longueur de ligne, nommage) ; la faire **trancher en session avec `AskUserQuestion`** (deux
  options : la convention recommandée et une alternative ; la saisie libre est ajoutée par
  l'outil), écrite en place.

**Installer l'outil retenu (best-effort, sans admin, non bloquant).** Après avoir écrit la config, poser
réellement l'outil : `python "${CLAUDE_PLUGIN_ROOT}/scripts/install_formatter.py" <racine> <clé>` où
`<clé>` ∈ `python` (-> `pip install ruff`) / `ts-js-biome` (-> `npm i -D @biomejs/biome`) / `ts-js-eslint`
(-> `npm i -D eslint prettier`) - **une invocation par langage/choix retenu**. Le script est **idempotent**
(saute si déjà installé), **sans droits admin** (pip `--user` en repli ; npm en **local**, jamais `-g` ;
crée `package.json` via `npm init -y` si absent), et **non bloquant** : si `pip`/`npm` manque ou si
l'install échoue, il l'indique **sans échouer** (l'équipe finira à la main). Adapter `python` -> `py -3`
si besoin. Confirmer **en clair** ce qui a été installé.
Écrire/compléter `architecte-out/standards-ingenierie.md` (gabarit `templates/standards-ingenierie.md`)
qui **pointe vers `conventions/`** + couvre les standards non-formatage (erreurs,
logging, sécurité, **stratégie de test**, API, données, git, doc). La **stratégie de test**
est concrète : unitaires par règle métier (cas passant / échec / limite) ; intégration
API/front/batch **avec dépendances externes mockées** ; **tests écrits en même temps que le
code**. Mettre à jour le manifeste en silence.

### Étape 3 : ADR (arbitrage humain)
Pour chaque décision structurante (style d'archi, API, persistance, identité/authz,
multitenance, **fournisseur cloud**, déploiement, observabilité...), produire un **ADR**
(gabarit `templates/adr.md`) dans `architecte-out/decisions/ADR-NNN-titre.md` : contexte,
décision, options **réellement présentées**, conséquences, déclencheur de revue.
**N'écrire un ADR qu'APRÈS que l'humain a explicitement tranché la décision** (à l'étape 1 -
workflow stack - ou ici) : l'ADR **consigne** un choix validé, il ne le **crée** pas. **Ne jamais** y inscrire
une décision non tranchée, une formule "décision non remise en question" sur un choix jamais
proposé, ni une **prémisse non énoncée** (composition d'équipe, infra existante...) - si une
prémisse manque, la **demander** d'abord **avec `AskUserQuestion`** (deux lectures plausibles en
options). Mettre à jour le manifeste en silence.

### Étape 4 : Walking skeleton + convergence (numérotation **proposée**)
Désigner le **walking skeleton définitif** (la première tranche de bout en bout qui
dé-risque la stack ; confirmer/ajuster le candidat du spec-index **avec `AskUserQuestion`** -
deux options : le candidat du spec-index en recommandé, et la tranche concurrente la plus
défendable). **Proposer la liste
de features numérotées et séquencée** : **chaque** use case du `spec-index.md`
devient une feature numérotée. La liste est **complète** - couverture 1:1, **aucun
use case laissé de côté** - ordonnée selon les **dépendances et le couplage
technique** (walking skeleton en premier). C'est la **convergence des deux
découpages**. Mettre à jour la section Dépendances des briefs en conséquence.

> **Proposition, pas verdict final.** Cette séquence est le **point de départ**. L'**arbitrage final**
> du découpage (découper une feature en deux, en fusionner deux) se fait dans l'**assembleur**
> (`assembleur-convergence`), qui **réécrit** `architecture.feature_sequence` avec la liste définitive ;
> elle est **figée à l'init Linear** (`premier-alimente-linear`). L'architecte fournit une base
> **complète et cohérente**, pas le registre gelé.

**Aucune notion de MVP / post-MVP.** On ne décide pas ce qui est MVP ou non : sauf si
la matière de cadrage le mentionne explicitement, cette distinction n'existe nulle
part. L'ordre est purement technique (dépendances), pas un filtre de périmètre.

**Format - séquence proposée.** `architecture.feature_sequence` est la **séquence de features
proposée** (registre que l'**assembleur** finalise et fige) : une liste d'**objets** `{id, ucs, name}`
où **`ucs` est une liste** de use cases du cadrage - ex. `{"id": "001", "ucs": ["UC2"], "name": "Recherche Q&A
sourcée"}`. Une feature de fabrication peut **bundler plusieurs use cases**
(fusion : `"ucs": ["UC5", "UC6"]`) ; un seul use case = liste à un élément. Les `ucs` portent
la correspondance **use case <-> id** (identité fonctionnelle stable du cadrage) pour que le
designer et l'assembleur joignent les trois faces **par use case**. Mettre à jour le
manifeste en silence (walking skeleton = l'`id` correspondant).

> **Couverture complète exigée.** `architecte-coherence` échoue si un use case du
> `spec-index.md` n'a pas de feature correspondante dans
> `architecture.feature_sequence` : figer **toute** la liste, sans en omettre aucune.

## Règles invariantes
- **Proposer, ne pas décider - jamais à la place de l'utilisateur.** Toute techno
  structurante (langage, framework, **front**, base, **cloud**, **déploiement**...) est
  **présentée en options + compromis**, puis **tranchée par l'humain** ; on **attend** sa
  décision avant d'écrire. **Aucun auto-choix**, **aucun biais** vers un fournisseur (jamais
  des options d'un seul écosystème) ; l'**expérience** de l'utilisateur avec une techno ne
  vaut pas décision (on lui demande). Les ADR ne consignent que des décisions validées.
- **Versions exactes épinglées** pour chaque techno (jamais "latest" / "stable" / vide).
- **Rien d'affiché de la mécanique.** Aucun nom de variable/clé manifeste, aucun
  identifiant codé, aucun tableau (voir `references/ux-conventions.md`). Le manifeste
  se met à jour en silence.
- **Skill indépendant.** Lit/écrit le manifeste partagé ; relit ses entrées depuis les
  fichiers committés.

À la fin, dire en clair **ce qui a été produit** (en prose, sans tableau, sans ligne
de manifeste) puis l'étape suivante.

Étape suivante : `/architecte:architecte-livrables` - produire les diagrammes, le registre de risques, le handoff design, les fichiers d'environnement et vérifier l'enforcement.
