---
name: architecte-contrat
description: Construit le contrat technique (drivers, composants, stack, ADR, walking skeleton, diagrammes) en interactif.
---

# architecte-contrat

Cœur de la phase technique. **Discipline le raisonnement de l'architecte et grave
ses décisions en contrats.** L'IA propose et structure ; **l'humain tranche**
(arbitrage des ADR). Ne décide jamais l'architecture à la place de l'architecte.

## Pré-requis (vérification silencieuse)
`architecte-init` a tourné (le manifeste contient le bloc `architecture`). Vérifier
sans l'annoncer ; sinon, orienter en clair vers `/architecte:architecte-init`.

## Entrées (lues depuis le cadrage)
`cadrage-out/` : `project-frame.md`, `product-brief.md`, `glossaire.md`,
`spec-index.md` (use cases + walking skeleton candidat + couverture), les briefs sous
`cadrage-out/features-fonctionnels-brief/*.md`. Conventions d'interaction :
`references/interactive-loop.md` et `references/ux-conventions.md`.

> **Règles transverses (toutes les étapes).** Restituer **en prose**, jamais en
> tableau. Désigner chaque chose par son **nom métier en clair** — jamais un code
> (`C1`, `UC1`, `P1`…). **Aucune provenance** écrite dans les artefacts (pas de
> `(src:)`, d'horodatage, de nom de personne). Mettre à jour le manifeste **en
> silence** : ne jamais narrer « MAJ `architecture.*` » ni un nom de variable, ni **aucune ligne de
> bilan** « Manifeste à jour : … » / liste `champ: valeur` / `true`/`false` (l'utilisateur ne s'y
> intéresse pas). Toute
> valeur manquante se **résout en session** (cf. `references/interactive-loop.md`) et
> s'écrit **en place** — aucun marqueur n'est laissé dans un fichier final.
>
> **Versionnage des documents.** Chaque fichier écrit sous `architecte-out/` commence par un
> front-matter `--- version: N / date: AAAA-MM-JJ ---`. **Première** génération d'un document :
> `version: 1`. À chaque **régénération** : relire le `version:` existant et écrire **`N+1`**,
> avec `date:` = jour courant (format ISO `AAAA-MM-JJ`) — le helper
> `scripts/bump_doc_version.py <fichier>` calcule la prochaine version. **Exception ADR** : un ADR accepté est
> immuable — il **reste `version: 1`** et évolue via son champ `Statut` (+ un ADR successeur). Ce
> front-matter `version`/`date` est une **métadonnée de document** — il n'est **pas** visé par
> l'interdiction de provenance/horodatage (qui concerne le corps : pas de `(src:)`, pas
> d'horodatage épars, pas de nom de personne).

## Procédure — ordre imposé (chaque étape consomme la précédente)

### Étape 0 — Lire le cadrage en parallèle (exhaustif), puis vérifier
**Lire tout le cadrage pertinent, en parallèle, pour ne rien manquer.** Dispatcher des
sous-agents lecteurs (`agentType: "architecte-reader"`), **un par lot**, chacun avec un
**schéma de sortie structuré**, en **un seul message** (appels parallèles) — puis
synthétiser leurs retours. Lots :
1. **Vision & cadre** — `cadrage-out/product-brief.md`, `cadrage-out/project-frame.md`.
   Extraire : identité produit, périmètre IN/OUT, contraintes (légales/sécurité/données),
   seeds qualité (charge, disponibilité, performance), réponses de cadrage (Q1–Q13).
2. **Domaine & découpage** — `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`,
   `cadrage-out/coupling-map.md`. Extraire : entités/langage, use cases + frontières,
   walking skeleton candidat, couplages/dépendances.
3. **Briefs** — `cadrage-out/features-fonctionnels-brief/*.md`. Extraire, par feature :
   user stories, critères d'acceptation/succès, contraintes héritées.

*(Garde simple : s'il n'y a quasiment rien à lire, un seul lecteur suffit ; au-delà,
fan-out. Plafonné à la concurrence — au-delà, mettre en lot.)*

**Passe de complétude** : après synthèse, vérifier que rien n'a été manqué ni contredit
(au besoin, relire un lot). Le `references/question-map.md` sert ensuite à savoir **quelle
réponse vient déjà du cadrage** : ne **poser que les trous**, en clair et **un par un**
(cf. `references/interactive-loop.md`), **sans tableau** ni identifiant `Qn` :
- **profil d'équipe** (taille, expertise langage/framework) — absent du cadrage ;
- tout point de cadrage resté à confirmer et **bloquant**.
Si un trou bloquant n'est pas tranché, **ne pas démarrer la génération** : le dire en
clair et s'arrêter. Écrire le profil d'équipe au manifeste (en silence).

### Étape 1 — Drivers & attributs de qualité (deux temps liés)
À partir des seeds qualité (charge, disponibilité, performance) + les contraintes
(légal, sécurité, données) :
1. **Identifier les drivers** = ce qui **oriente** l'architecture : **objectifs métier**,
   **contraintes** (légales / organisationnelles / techniques / d'usage) et **risques
   majeurs**, classés par priorité. **Jamais une -ilité** ici.
2. **En dériver les attributs de qualité** = les **-ilités mesurables** (ISO 25010 :
   fiabilité, sécurité, performance, disponibilité, maintenabilité…) **issues** de ces
   drivers, chacune avec une **cible chiffrée** et **reliée au driver dont elle découle** ;
   puis formuler les **scénarios de qualité testables (QAW)**.
**Les deux ne se recouvrent pas** : un attribut de qualité qui répète un driver — ou une
-ilité listée comme driver — est une **erreur à corriger**. **Restituer dans le chat sous forme de DEUX
tableaux clairs** (noms en clair, jamais de code) :
- **Drivers** — colonnes **`#`** (priorité) · **`Driver`** · **`Conséquence pour l'architecture`**.
- **Attributs de qualité** — colonnes **`Attribut`** · **`Cible`** (chiffrée) · **`Scénario (QAW)`** · **`Driver source`**.

*(Exception assumée à la règle « pas de tableau » — cf. `references/ux-conventions.md` §4 : drivers et
attributs de qualité se lisent bien mieux en tableau.)* Faire valider, puis écrire
`architecte-out/drivers-quality.md` (gabarit `templates/drivers-quality.md`). Mettre à jour le manifeste
en silence.

### Étape 2 — Workflow composants (interactif)
Dériver une **liste de composants candidats** depuis le périmètre fonctionnel
(briefs + spec-index). **Dès que le produit a un écran utilisateur, la liste inclut
TOUJOURS un composant Frontend/UI** (l'application qui rend les écrans) — composant
technique à part entière, au même titre que le back, les workers, la base. L'existence
du plugin designer **ne dispense pas** de l'architecture front : le designer produit le
design system **visuel**, pas le **composant technique** front (porté ici + sa stack à
l'étape 3). **Restituer la liste sous forme de TABLEAU clair** — deux colonnes : **`Composant`**
(nom métier) et **`Rôle`** (ce qu'il fait, en une phrase) ; **jamais de texte brut en liste**,
**jamais de code `C1`/`C2`** ni d'identifiant technique. *(Exception assumée à la règle « pas de
tableau » — cf. `references/ux-conventions.md` §4 : les composants se lisent bien mieux en tableau.)*
**Demander si ça convient ou s'il faut modifier** ; appliquer les retours (ajout/fusion/suppression) ;
**boucler jusqu'à validation**. Puis écrire `architecte-out/components.md` (gabarit
`templates/components.md`). Mettre à jour le manifeste en silence.

### Étape 3 — Workflow stack technique (interactif)
Domaines de décision : **langage(s), framework(s) back, framework front / bibliothèque de
composants / stratégie CSS-tokens, bibliothèques principales, base de données, style d'API,
communication asynchrone, fournisseur cloud, déploiement, observabilité**. Pour **chaque**
domaine (front et déploiement compris), **même si le cadrage suggère une piste** : **proposer
2 à 4 options réellement diverses avec avantages/inconvénients + une recommandation**, puis
**attendre le choix explicite de l'utilisateur** avant de continuer. **Ne jamais
auto-sélectionner** une techno ni graver un choix non tranché.

**Anti-biais (obligatoire).** Un choix antérieur ne restreint pas silencieusement les suivants
à l'écosystème d'un même fournisseur : pour chaque domaine, présenter **au moins une alternative
crédible hors de cet écosystème** — **interdit** de ne proposer que des options d'un seul
fournisseur (pas d'« Azure-vs-Azure »). Le **fournisseur cloud** et le **déploiement** sont des
**décisions ouvertes** à part entière : ne jamais les déduire d'une « infra existante » sauf si
l'utilisateur l'a **dit explicitement** — et alors, le lui **confirmer comme sa décision**, ne
pas l'affirmer.

**Expérience ≠ décision.** Si l'utilisateur mentionne connaître une techno (« je maîtrise
React »), **ne pas l'adopter d'office** : demander « Puisque tu connais React, on part là-dessus
ou on évalue d'autres options ? ». La décision finale vient **toujours** de lui.

Respecter l'ordre des dépendances entre choix (langage avant framework, etc.).
**Version exacte pour CHAQUE techno** : à la finalisation, chaque langage, framework,
bibliothèque, base et outil reçoit une **version exacte et épinglée** (ex. « PostgreSQL 17.2 »,
« React 19.1.0 ») — tranchée en session si inconnue ; **jamais** « latest » / « stable » / vide.
**Validation finale** de la stack en chat. Écrire `architecte-out/tech-stack.md` (gabarit
`templates/tech-stack.md`, dont la **matrice composant × techno** — une ligne par composant, **le
composant front inclus**). Mettre à jour le manifeste en silence.

### Étape 4 — Activer les conventions (vrais fichiers)
Pour chaque **langage retenu** à l'étape 3, copier le(s) fichier(s) de config
correspondant du catalogue `references/conventions/` vers le dossier `conventions/`
du projet :
- Python → `python/ruff.toml` ; TS/JS → `ts-js-biome/biome.json` (défaut) **ou**
  `ts-js-eslint/{eslint.config.js,.prettierrc}` (demander lequel) ; C →
  `c/.clang-format`.
- **Fallback (langage hors catalogue)** : ne pas inventer de config exotique —
  garder le `.editorconfig` universel, **avertir l'utilisateur** que ce langage n'a
  pas de convention prédéfinie, et **proposer une convention générique** (indentation,
  longueur de ligne, nommage) ; la faire **trancher en session** (recommandée +
  alternative + saisir), écrite en place.

**Installer l'outil retenu (best-effort, sans admin, non bloquant).** Après avoir écrit la config, poser
réellement l'outil : `python "${CLAUDE_PLUGIN_ROOT}/scripts/install_formatter.py" <racine> <clé>` où
`<clé>` ∈ `python` (→ `pip install ruff`) / `ts-js-biome` (→ `npm i -D @biomejs/biome`) / `ts-js-eslint`
(→ `npm i -D eslint prettier`) — **une invocation par langage/choix retenu**. Le script est **idempotent**
(saute si déjà installé), **sans droits admin** (pip `--user` en repli ; npm en **local**, jamais `-g` ;
crée `package.json` via `npm init -y` si absent), et **non bloquant** : si `pip`/`npm` manque ou si
l'install échoue, il l'indique **sans échouer** (l'équipe finira à la main). Adapter `python` → `py -3`
si besoin. Confirmer **en clair** ce qui a été installé.
Écrire/compléter `architecte-out/standards.md` (gabarit `templates/standards.md`)
qui **pointe vers `conventions/`** + couvre les standards non-formatage (erreurs,
logging, sécurité, **stratégie de test**, API, données, git, doc). La **stratégie de test**
est concrète : unitaires par règle métier (cas passant / échec / limite) ; intégration
API/front/batch **avec dépendances externes mockées** ; **tests écrits en même temps que le
code**. Mettre à jour le manifeste en silence.

### Étape 5 — ADR (arbitrage humain)
Pour chaque décision structurante (style d'archi, API, persistance, identité/authz,
multitenance, **fournisseur cloud**, déploiement, observabilité…), produire un **ADR**
(gabarit `templates/adr.md`) dans `architecte-out/decisions/ADR-NNN-titre.md` : contexte,
décision, options **réellement présentées**, conséquences, déclencheur de revue.
**N'écrire un ADR qu'APRÈS que l'humain a explicitement tranché la décision** (à l'étape 3
ou ici) : l'ADR **consigne** un choix validé, il ne le **crée** pas. **Ne jamais** y inscrire
une décision non tranchée, une formule « décision non remise en question » sur un choix jamais
proposé, ni une **prémisse non énoncée** (composition d'équipe, infra existante…) — si une
prémisse manque, la **demander** d'abord. Mettre à jour le manifeste en silence.

### Étape 6 — Walking skeleton + convergence (numérotation)
Désigner le **walking skeleton définitif** (la première tranche de bout en bout qui
dé-risque la stack ; confirmer/ajuster le candidat du spec-index). **Figer la liste
de features numérotées et séquencée** : **chaque** use case du `spec-index.md`
devient une feature numérotée. La liste est **complète** — couverture 1:1, **aucun
use case laissé de côté** — ordonnée selon les **dépendances et le couplage
technique** (walking skeleton en premier). C'est la **convergence des deux
découpages**. Mettre à jour la section Dépendances des briefs en conséquence.

**Aucune notion de MVP / post-MVP.** On ne décide pas ce qui est MVP ou non : sauf si
la matière de cadrage le mentionne explicitement, cette distinction n'existe nulle
part. L'ordre est purement technique (dépendances), pas un filtre de périmètre.

**Format — registre canonique.** `architecture.feature_sequence` est le **registre
canonique des features** : une liste d'**objets** `{id, ucs, name}` où **`ucs` est une
liste** de use cases du cadrage — ex. `{"id": "001", "ucs": ["UC2"], "name": "Recherche Q&A
sourcée"}`. Une feature de fabrication peut **bundler plusieurs use cases**
(fusion : `"ucs": ["UC5", "UC6"]`) ; un seul use case = liste à un élément. Les `ucs` portent
la correspondance **use case ↔ id** (identité fonctionnelle stable du cadrage) pour que le
designer et l'assembleur joignent les trois faces **par use case**. Mettre à jour le
manifeste en silence (walking skeleton = l'`id` correspondant).

> **Couverture complète exigée.** `architecte-coherence` échoue si un use case du
> `spec-index.md` n'a pas de feature correspondante dans
> `architecture.feature_sequence` : figer **toute** la liste, sans en omettre aucune.

### Étape 7 — Diagrammes (+ images PNG)
Produire `architecte-out/diagrams.md` (gabarit `templates/diagrams.md`) :
C4 contexte, C4 conteneurs, flux d'un parcours critique, ERD, déploiement (Mermaid),
avec les noms réels (pas de placeholders).
Puis **générer les images** : lancer
`py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/render_diagrams.py" <projet>/architecte-out/diagrams.md`
(remplacer `py -3` par `python` si `py` est absent) — il rend un **PNG par diagramme** (nom
déterministe `NN-slug.png`) dans **`architecte-out/diagrammes/`**. Le script **installe
silencieusement ce qui manque** (mermaid-cli épinglé, **sans télécharger Chromium** — il
réutilise le navigateur système), respecte la CA d'entreprise **sans désactiver TLS**, et
**bascule automatiquement** entre méthodes de rendu (mermaid-cli → npx → Kroki local) — **sans
jamais demander de permission**. Les prérequis ont normalement été pré-installés par
`architecte-init`. Confirmer en clair les images produites. **Si tout échoue malgré les replis**,
le dire en clair et continuer — ne jamais bloquer la phase pour ça ; le markdown reste la source.

### Étape 8 — Registre de risques
Produire `architecte-out/risks.md` (gabarit `templates/risks.md`) : risques
techniques, mitigations, spikes/POC nécessaires. Mettre à jour le manifeste en silence.

### Étape 9 — Décisions à impact design (handoff vers le Designer)
**Synthétiser la tranche de l'architecture qui se voit à l'écran** — c'est le contrat propre
Architecte → Designer (le designer ne doit pas fouiller tout le handoff ; l'architecte sait ce qui se
voit). Produire `architecte-out/design-impact.md` (gabarit `templates/design-impact.md`), par ordre
d'importance : **1.** stack front + approche de style (framework, lib de composants, stratégie CSS — *ce
qui rend le design system exécutable/synchronisable* ; **repris du composant front déclaré dans
`components.md`/`tech-stack.md`, sans le redécider**) ; **2.** contrats transverses visibles
(multitenance/theming par tenant ; identité/rôles/autorisations : variantes par rôle, non autorisé,
connexion, session expirée ; navigation/routage) ; **3.** conventions d'API qui décident des états d'UI
(format d'erreur → messages par champ, asynchrone, pagination/listes, cas vides) ; **4.** NFR qui touchent
l'UX (niveau d'accessibilité visé, cibles responsive/breakpoints, i18n, budget de performance). **Exclure**
le back/persistance/déploiement/ADR serveur. **Contenu seul** (aucune `(src:)`) ; **ne pas inventer** ;
**sans objet** si N/A. Mettre à jour le manifeste en silence.

### Étape 10 — Générer les fichiers d'environnement (automatique)
Une fois la stack et **toutes les dépendances externes connues** (API, services, bases, secrets),
**générer directement** les fichiers d'environnement — **sans demander** : à ce stade tout est
spécifié, on sait exactement quelles variables sont nécessaires. **Ne rien générer uniquement** s'il
n'y a **vraiment aucune** dépendance nécessitant une variable (ni base, ni service externe, ni secret
d'infra) — auquel cas le noter en clair.

**Déterminer les variables** depuis les artefacts (l'inventaire est déjà fait) :
- `tech-stack.md` — **Stockages** (chaque base/cache → `DATABASE_URL`/`REDIS_URL`/…) et
  **Infrastructure** (fournisseur cloud, gestion des secrets, stockage objet) ;
- `components.md` — **Services externes** : pour **chaque** API tierce / fournisseur d'auth, ajouter un
  **slot dédié** (`<SERVICE>_API_KEY` / `<SERVICE>_URL`) — pas seulement les variables génériques du
  gabarit ;
- ADR — cloud / identité-authz / observabilité.

**Écrire, à la racine du projet**, en partant du gabarit de la stack (`references/env-templates/` :
Python/Node/Vite/Go, Angular, .NET, Spring), **enrichi d'un slot par dépendance identifiée** ci-dessus :
- **`.env.example`** — **committé**, la référence documentée (chaque variable + un commentaire court) ;
- **`.env`** — **à remplir**, créé à la racine et **gitignoré** (Python/Node/Vite/Go ; Angular →
  `src/environments/environment.ts` + `environment.prod.ts` ; .NET → `appsettings*.json` ; Spring →
  `application.yml` + `.env.example`).
- **Valeurs vides ou d'exemple, jamais de secret réel.** Angular/Vite (bundle client **public**) :
  **URLs publiques uniquement, aucun secret** (les secrets restent côté serveur).
- **`.gitignore`** (compléter, jamais réécrire) : le fichier **existe déjà** (première version générée
  par le cadrage, ligne `.factory/` posée par `architecte-init`). **Y ajouter** seulement les lignes
  manquantes pour **ignorer** `.env` et `.env.*.local` (sans dupliquer, en **préservant** tout le
  reste) et laisser **`.env.example` committé**. **Le créer uniquement s'il est absent** ; ne jamais
  l'écraser.

Confirmer en clair les fichiers créés. Mettre à jour le manifeste **en silence** — `env_files` porte la
**liste des fichiers écrits** (le garde-fou vérifie qu'ils existent) :
`{ "initialized": true, "stack": "<stack>", "files": [".env.example", ".env", …], "gitignored": true }`
— ou, si vraiment aucune variable n'est nécessaire :
`{ "initialized": false, "reason": "aucune dépendance nécessitant des variables d'environnement" }`.

### Étape 11 — Enforcement (déjà posé par `architecte-init`)
**Rien à installer ici.** Tous les hooks de l'architecte — l'enforcement des tests (hook `PostToolUse`
`tests_guard.py` + `lefthook.yml`) **et** la protection de branche locale (`.githooks/` + `core.hooksPath`
+ hook `SessionStart` de réactivation) — sont **posés dès `architecte-init`** (déterministe, à la racine).
Se contenter de **vérifier** qu'ils sont bien là (manifeste `test_enforcement: true` + `branch_protection`)
et que la **stratégie de test** de `standards.md` (Étape 4) reste cohérente avec ce qui est enforced. Si
l'enforcement manque (init d'une version antérieure), le reposer via les deux scripts du catalogue
`references/enforcement/` (`install_test_hooks.py`, `install_branch_protection.py`). *(L'enforcement est
**au moment du dev** (hooks `PostToolUse` + pre-commit), contournable avec `--no-verify` ; la seule
barrière non contournable multi-personnes serait un **ruleset serveur GitHub** — à la charge de
l'équipe, **hors périmètre** de la Factory qui ne produit aucune CI.)*

## Résolution des points avant de conclure
Avant de terminer, **balayer tous les fichiers `architecte-out/`** : pour **chaque**
point encore à définir ou à chiffrer, **poser la question** à l'utilisateur (un par
un — réponse recommandée + alternative + saisir, cf. `references/interactive-loop.md`)
et **écrire la réponse en place**. Ne **pas conclure** la phase tant qu'un point reste
indéfini. Aucun fichier annexe.

## Vérification avant de conclure (silencieuse)
- Réponses vérifiées (rien de bloquant en suspens) ; `drivers-quality.md`,
  `components.md`, `tech-stack.md`, `standards.md`, ADR, `diagrams.md` (+ images dans
  `diagrammes/`), `risks.md`, **`design-impact.md`** produits ; conventions par langage
  installées dans `conventions/` ; walking skeleton et séquence de features figés.
- **Composant Frontend/UI présent** dans `components.md` si le produit a des écrans ;
  **chaque techno de `tech-stack.md` porte une version exacte** (aucun « latest » / vide) ;
  `components.md` et `tech-stack.md` **cohérents** (mêmes technos/versions, pas de stack
  contradictoire).
- **Front-matter présent** en tête de chaque fichier `architecte-out/` (`version:` entier,
  `date:` ISO `AAAA-MM-JJ`) ; ADR à `version: 1`.
- **`standards.md` porte la stratégie de test** (unitaires cas passant/échec/limite ; intégration
  API/front/batch avec mocks ; tests en même temps que le code) ; **enforcement posé** à la racine
  (`.claude/` + `lefthook.yml`) ; **fichiers d'environnement** initialisés ou explicitement déclinés.
- **Contenu seul** : aucune `(src:)`, aucun horodatage dans le corps, aucun nom de personne,
  **aucun marqueur résiduel** ; tout point a été tranché en session. (Le front-matter
  `version`/`date` est une métadonnée de document, pas de la provenance.)

## Règles invariantes
- **Proposer, ne pas décider — jamais à la place de l'utilisateur.** Toute techno
  structurante (langage, framework, **front**, base, **cloud**, **déploiement**…) est
  **présentée en options + compromis**, puis **tranchée par l'humain** ; on **attend** sa
  décision avant d'écrire. **Aucun auto-choix**, **aucun biais** vers un fournisseur (jamais
  des options d'un seul écosystème) ; l'**expérience** de l'utilisateur avec une techno ne
  vaut pas décision (on lui demande). Les ADR ne consignent que des décisions validées.
- **Rien d'affiché de la mécanique.** Aucun nom de variable/clé manifeste, aucun
  identifiant codé, aucun tableau (voir `references/ux-conventions.md`). Le manifeste
  se met à jour en silence.
- **Skill indépendant.** Lit/écrit le manifeste partagé.

À la fin, dire en clair **ce qui a été produit** (en prose, sans tableau, sans ligne
de manifeste) puis l'étape suivante.

Étape suivante : `/architecte:architecte-coherence` — valider la cohérence du contrat technique avant le passage à l'assembleur.
