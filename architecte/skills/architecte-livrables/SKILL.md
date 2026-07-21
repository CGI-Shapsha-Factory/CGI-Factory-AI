---
name: architecte-livrables
description: Produit les livrables dérivés du contrat technique - diagrammes, risques, impact design, fichiers d'environnement - puis balaie tout architecte-out/ avant la porte de cohérence.
---

# architecte-livrables

Dernière étape de construction du contrat technique, avant la porte de cohérence. L'IA
**produit les livrables dérivés** des décisions déjà prises - diagrammes, registre de risques,
handoff design, fichiers d'environnement - puis **balaie tout `architecte-out/`** pour ne rien
laisser d'indéfini. Ne décide jamais l'architecture à la place de l'architecte.

## Pré-requis (vérification silencieuse)
`architecte-stack` a tourné : la stack et le walking skeleton sont posés
(`architecture.stack` non vide, `architecture.walking_skeleton` défini). Vérifier sans
l'annoncer ; sinon, orienter en clair vers `/architecte:architecte-stack`.

## Entrées (relues des fichiers committés, jamais de la mémoire du chat)
`architecte-out/` : `composants.md`, `stack-technique.md`, `facteurs-et-qualite.md`,
`standards-ingenierie.md`, les ADR sous `decisions/ADR-*.md`. Gabarits `templates/` ;
catalogue `references/env-templates/` ; conventions d'interaction
`references/interactive-loop.md`, `references/ux-conventions.md`.

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
skill** existent déjà - `diagrammes.md` **et les images sous `diagrammes/`**, `risques.md`,
`impact-design.md` - proposer le choix **Repartir de zéro** (supprimer puis générer à neuf ; pour
les diagrammes, vider `diagrammes/` avant de re-rendre les images) ou **Garder les deux (versionner)**
(archiver l'existant sous `_archives/` - le dossier `diagrammes/` vers `_archives/diagrammes-v<N>/` -
puis régénérer au nom canonique en `version: N+1`) et **attendre** le choix. Les fichiers
d'environnement `.env*`/`.gitignore` restent **complétés, jamais écrasés** (règle propre à l'étape 4).
Premier passage (rien n'existe) : générer directement, sans porte.

## Procédure : ordre imposé (chaque étape consomme la précédente)

### Étape 1 : Diagrammes (+ images SVG/PNG)
Produire `architecte-out/diagrammes.md` (gabarit `templates/diagrammes.md`) :
C4 contexte, C4 conteneurs, flux d'un parcours critique, ERD, déploiement - en **syntaxe D2**
(moteur de layout **ELK** : routage orthogonal, sans chevauchement de flèches ni de libellés),
avec les noms réels (pas de placeholders). Garder les libellés de flèche courts là où plusieurs
flèches convergent (sinon les libellés se serrent). **Couleur de trait par entité source** : dans
les diagrammes **conteneurs**, **flux** et **déploiement**, chaque entité qui émet **plusieurs
flèches** reçoit une couleur dédiée, via un glob de connexion écrit **après** les connexions
ciblées - `(<source> -> **)[*].style.stroke: "<hex>"` (le double glob `**` est **obligatoire** :
avec un simple `*`, les cibles imbriquées dans un conteneur ne sont pas atteintes), chemin
**qualifié complet** si la source est imbriquée (`system.containerA`). Palette du gabarit, prise dans l'ordre ; jamais la même teinte pour
deux sources dont les flèches se croisent. La **même couleur** sert de **contour au rectangle
émetteur** - sur la déclaration du noeud, `style.stroke: "<même hex>"` + `style.stroke-width: 3` -
pour retrouver d'un coup d'oeil la boîte d'où part un faisceau ; les entités qui n'émettent rien
(bases, secrets, journalisation, systèmes externes) **gardent leur contour d'origine**. La couleur
**complète** les libellés, elle ne les remplace pas. **Pas de coloriage** sur le diagramme de
contexte ni sur l'ERD (sur une `sql_table`, D2 applique `stroke` au fond de l'en-tête).
Puis **générer les images** : lancer
`py -3 "${CLAUDE_PLUGIN_ROOT}/scripts/render_diagrams.py" <projet>/architecte-out/diagrammes.md`
(remplacer `py -3` par `python` si `py` est absent) - il rend un **SVG par diagramme** (source de
vérité, vectoriel) **+ un PNG best-effort** (nom déterministe `NN-slug.svg` / `NN-slug.png`) dans
**`architecte-out/diagrammes/`**. Le SVG est produit par le binaire **D2** (aucun navigateur requis) ;
le PNG rasterise le SVG via le **navigateur système** (Edge/Chrome) **sans télécharger Chromium**. Le
script respecte la CA d'entreprise **sans désactiver TLS** et **bascule automatiquement** (D2 ->
Kroki local) - **sans jamais demander de permission**. Les prérequis (binaire D2) ont normalement été
pré-installés par `architecte-init`. Confirmer en clair les images produites. **Si tout échoue malgré
les replis**, le dire en clair et continuer - ne jamais bloquer la phase pour ça ; le markdown reste la
source.

### Étape 2 : Registre de risques
Produire `architecte-out/risques.md` (gabarit `templates/risques.md`) : risques
techniques, mitigations, spikes/POC nécessaires. Mettre à jour le manifeste en silence.

### Étape 3 : Décisions à impact design (handoff vers le Designer)
**Synthétiser la tranche de l'architecture qui se voit à l'écran** - c'est le contrat propre
Architecte -> Designer (le designer ne doit pas fouiller tout le handoff ; l'architecte sait ce qui se
voit). Produire `architecte-out/impact-design.md` (gabarit `templates/impact-design.md`), par ordre
d'importance : **1.** stack front + approche de style (framework, lib de composants, stratégie CSS - *ce
qui rend le design system exécutable/synchronisable* ; **repris du composant front déclaré dans
`composants.md`/`stack-technique.md`, sans le redécider**) ; **2.** contrats transverses visibles
(multitenance/theming par tenant ; identité/rôles/autorisations : variantes par rôle, non autorisé,
connexion, session expirée ; navigation/routage) ; **3.** conventions d'API qui décident des états d'UI
(format d'erreur -> messages par champ, asynchrone, pagination/listes, cas vides) ; **4.** NFR qui touchent
l'UX (niveau d'accessibilité visé, cibles responsive/breakpoints, i18n, budget de performance). **Exclure**
le back/persistance/déploiement/ADR serveur. **Contenu seul** (aucune `(src:)`) ; **ne pas inventer** ;
**sans objet** si N/A. Mettre à jour le manifeste en silence.

### Étape 4 : Générer les fichiers d'environnement (automatique)
Une fois la stack et **toutes les dépendances externes connues** (API, services, bases, secrets),
**générer directement** les fichiers d'environnement - **sans demander** : à ce stade tout est
spécifié, on sait exactement quelles variables sont nécessaires. **Ne rien générer uniquement** s'il
n'y a **vraiment aucune** dépendance nécessitant une variable (ni base, ni service externe, ni secret
d'infra) - auquel cas le noter en clair.

**Déterminer les variables** depuis les artefacts (l'inventaire est déjà fait) :
- `stack-technique.md` - **Stockages** (chaque base/cache -> `DATABASE_URL`/`REDIS_URL`/...) et
  **Infrastructure** (fournisseur cloud, gestion des secrets, stockage objet) ;
- `composants.md` - **Services externes** : pour **chaque** API tierce / fournisseur d'auth, ajouter un
  **slot dédié** (`<SERVICE>_API_KEY` / `<SERVICE>_URL`) - pas seulement les variables génériques du
  gabarit ;
- ADR - cloud / identité-authz / observabilité.

**Écrire, à la racine du projet**, en partant du gabarit de la stack (`references/env-templates/` :
Python/Node/Vite/Go, Angular, .NET, Spring), **enrichi d'un slot par dépendance identifiée** ci-dessus :
- **`.env.example`** - **committé**, la référence documentée (chaque variable + un commentaire court) ;
- **`.env`** - **à remplir**, créé à la racine et **gitignoré** (Python/Node/Vite/Go ; Angular ->
  `src/environments/environment.ts` + `environment.prod.ts` ; .NET -> `appsettings*.json` ; Spring ->
  `application.yml` + `.env.example`).
- **Valeurs vides ou d'exemple, jamais de secret réel.** Angular/Vite (bundle client **public**) :
  **URLs publiques uniquement, aucun secret** (les secrets restent côté serveur).
- **`.gitignore`** (compléter, jamais réécrire) : le fichier **existe déjà** (première version générée
  par le cadrage, ligne `.factory/` posée par `architecte-init`). **Y ajouter** seulement les lignes
  manquantes pour **ignorer** `.env` et `.env.*.local` (sans dupliquer, en **préservant** tout le
  reste) et laisser **`.env.example` committé**. **Le créer uniquement s'il est absent** ; ne jamais
  l'écraser.

Confirmer en clair les fichiers créés. Mettre à jour le manifeste **en silence** - `env_files` porte la
**liste des fichiers écrits** (le garde-fou vérifie qu'ils existent) :
`{ "initialized": true, "stack": "<stack>", "files": [".env.example", ".env", ...], "gitignored": true }`
- ou, si vraiment aucune variable n'est nécessaire :
`{ "initialized": false, "reason": "aucune dépendance nécessitant des variables d'environnement" }`.

### Étape 5 : Enforcement (déjà posé par `architecte-init`)
**Rien à installer ici.** Les hooks de l'architecte - l'enforcement des tests et du formatage (hooks
`PostToolUse` `tests_guard.py` / `format_guard.py` + `lefthook.yml`) - sont **posés dès `architecte-init`**
(déterministe, à la racine). Se contenter de **vérifier** qu'ils sont bien là (manifeste
`test_enforcement: true`) et que la **stratégie de test** de `standards-ingenierie.md` (posée par
`architecte-stack`) reste cohérente avec ce qui est enforced. Si l'enforcement manque (init d'une version antérieure), le reposer via
`references/enforcement/install_test_hooks.py`. **Pas de protection de branche locale** : la règle "aucun
push direct sur `main`" est gérée par un **ruleset serveur GitHub** (require PR + review + CI) - à la
charge de l'équipe, **hors périmètre** de la Factory (qui ne pose aucun hook de branche local).

## Résolution des points avant de conclure
Avant de terminer, **balayer tous les fichiers `architecte-out/`** : pour **chaque**
point encore à définir ou à chiffrer, **poser la question** à l'utilisateur (un par
un - réponse recommandée + alternative + saisir, cf. `references/interactive-loop.md`)
et **écrire la réponse en place**. Ne **pas conclure** la phase tant qu'un point reste
indéfini. Aucun fichier annexe.

## Vérification avant de conclure (silencieuse)
- Réponses vérifiées (rien de bloquant en suspens) ; `facteurs-et-qualite.md`,
  `composants.md`, `stack-technique.md`, `standards-ingenierie.md`, ADR, `diagrammes.md` (+ images dans
  `diagrammes/`), `risques.md`, **`impact-design.md`** produits ; conventions par langage
  installées dans `conventions/` ; walking skeleton et séquence de features figés.
- Dans `diagrammes.md`, **chaque source émettant plusieurs flèches** des diagrammes conteneurs,
  flux et déploiement porte sa **couleur** - **sur ses flèches et sur son contour**, même valeur hex
  aux deux endroits (aucune source laissée au trait par défaut) ; contexte et ERD restent neutres.
- **Composant Frontend/UI présent** dans `composants.md` si le produit a des écrans ;
  **chaque techno de `stack-technique.md` porte une version exacte** (aucun "latest" / vide) ;
  `composants.md` et `stack-technique.md` **cohérents** (mêmes technos/versions, pas de stack
  contradictoire).
- **Front-matter présent** en tête de chaque fichier `architecte-out/` (`version:` entier,
  `date:` ISO `AAAA-MM-JJ`) ; ADR à `version: 1`.
- **`standards-ingenierie.md` porte la stratégie de test** (unitaires cas passant/échec/limite ; intégration
  API/front/batch avec mocks ; tests en même temps que le code) ; **enforcement posé** à la racine
  (`.claude/` + `lefthook.yml`) ; **fichiers d'environnement** initialisés ou explicitement déclinés.
- **Contenu seul** : aucune `(src:)`, aucun horodatage dans le corps, aucun nom de personne,
  **aucun marqueur résiduel** ; tout point a été tranché en session. (Le front-matter
  `version`/`date` est une métadonnée de document, pas de la provenance.)

## Règles invariantes
- **Contenu seul, rien d'indéfini.** Les livrables ne redécident rien (ils dérivent des
  contrats déjà tranchés) ; **aucun marqueur résiduel**, aucune `(src:)`, aucun horodatage dans
  le corps, aucun nom de personne - tout point se résout en session, en place.
- **Rien d'affiché de la mécanique.** Aucun nom de variable/clé manifeste, aucun
  identifiant codé, aucun tableau (voir `references/ux-conventions.md`). Le manifeste
  se met à jour en silence.
- **Skill indépendant.** Lit/écrit le manifeste partagé ; relit ses entrées depuis les
  fichiers committés.

À la fin, dire en clair **ce qui a été produit** (en prose, sans tableau, sans ligne
de manifeste) puis l'étape suivante.

Étape suivante : `/architecte:architecte-coherence` - valider la cohérence du contrat technique avant le passage à l'assembleur.
