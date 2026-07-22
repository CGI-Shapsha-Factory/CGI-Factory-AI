---
name: help-factory
description: Aide unique de la Factory - affiche la carte des 6 plugins (cadrage, architecte, designer, assembleur, validation, maintenance), un tableau par plugin avec le rôle de chaque skill, l'ordre et les portes humaines.
---

# help-factory

Skill d'aide - **l'unique aide de la Factory** (couvre les 6 plugins). Quand il est invoqué,
**affiche immédiatement le contenu ci-dessous TEL QUEL** (les tableaux), sans rien recalculer.
Il **n'écrit aucun fichier** et ne modifie aucun manifeste.

En temps normal ce corps n'est **jamais lu par le modèle** : le hook `UserPromptExpansion`
du plugin (`hooks/hooks.json` + `scripts/help_factory_hook.py`) intercepte la commande et rend
la carte directement à l'utilisateur, sans aucun token de sortie. Ce corps est le **chemin de
repli** quand les hooks sont désactivés - et la **source unique** du contenu, que le hook extrait
à partir du marqueur ci-dessous. Toute correction se fait donc ici, et nulle part ailleurs.

## À afficher tel quel

**La Factory IA transforme un atelier en projet spec-driven, en 4 phases amont + la recette (validation
fonctionnelle puis traitement des écarts).** Chaque phase est un plugin qui produit un *contrat* validé
par un humain, puis passe le relais :
**`cadrage -> architecte -> designer -> assembleur -> SpecKit -> validation -> maintenance`**.
Chaque skill se termine par une ligne "**Étape suivante**" qui indique quoi lancer ensuite - tu avances
de proche en proche. Le design system naît dans **Claude Design** ; son export est committé dans `designer-out/maquette-de-claude-design/` et sert de source à la fabrication.

### Phase 1 : `cadrage` (contrat fonctionnel)
De la matière brute (transcripts, docs) au pack fonctionnel repris par l'architecte.

| # | skill | rôle | porte / ordre |
|---|-------|------|---------------|
| 0 | `cadrage-init` | crée la mécanique `.factory/` + le dossier `cadrage-out/` + le manifeste | à lancer en premier |
| 0bis | `cadrage-ideation` | *(facultatif)* atelier d'idéation facilité quand la matière est mince - le compte rendu devient une source pour l'extraction | manifeste existe |
| 1 | `cadrage-extraction` | dépouille les sources en capture (contenu, sans horodatage) + pose les 19 questions de découverte | manifeste + ≥1 source |
| 2 | `cadrage-vision` | synthétise la capture en vision produit (le quoi / le pourquoi) | capture existe |
| 3 | `cadrage-glossaire` | construit le langage métier du projet, validé en bloc | capture existe |
| 4 | `cadrage-decoupage` | découpage fonctionnel en use cases (par valeur) + carte de couplage | vision faite |
| 5 | `cadrage-demonstrateur-brief` | prompt Claude Design pour la maquette de validation | vision / retour dispo |
| 6 | `cadrage-retour-demonstrateur` | ingère le retour client sur la maquette, propage les corrections | retour dispo |
| 7 | `cadrage-briefs` | brief auto-portant par feature (dans `cadrage-out/features-fonctionnels-brief/`) | couplage arbitré + maquette validée |
| 8 | `cadrage-completude` | **étape terminale ET point de résolution unique** : bilan + **résolution en session de tous les points ouverts**, puis relais vers l'architecte | *(rejouable)* - fin du cadrage |

### Phase 2 : `architecte` (contrat technique)
Transforme le besoin fonctionnel en cadre technique et fige la séquence numérotée des features.

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `architecte-init` | crée `conventions/` + installe les gabarits + bloc manifeste | cadrage prêt |
| `architecte-fondations` | lit le cadrage -> drivers & attributs de qualité -> composants (dont le frontend) | init faite |
| `architecte-stack` | stack (options + compromis) -> conventions -> **ADR** -> walking skeleton + séquence de features | **arbitrage des ADR** (humain) |
| `architecte-livrables` | diagrammes (+ images PNG) -> risques -> *Décisions à impact design* -> fichiers d'env -> vérif. enforcement | stack faite |
| `architecte-coherence` | valide la cohérence du contrat technique (stricte, interactive) | **validation de cohérence** (humain) |
| `gen-tests` | *(hors chaîne)* génère les tests manquants puis les exécute jusqu'à la suite verte | `/architecte:gen-tests [chemin]` |

### Phase 3 : `designer` (contrat de design)
**Atelier de couverture** : ne génère pas le design system - il garantit que rien n'est oublié et prépare Claude Design.

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `designer-init` | installe les gabarits + sème la checklist de couverture + crée `designer-out/` (`prompts/`, `maquette-de-claude-design/`) | maquette validée + architecture validée + *Décisions à impact design* |
| `designer-ingestion` | ingère les handoffs cadrage + architecte **en parallèle** et pré-remplit la checklist de couverture (mécanique, sans décision) | init fait |
| `designer-atelier` | déroule la checklist (fondation / expérience / technique) + résout en session tout point resté à traiter | **arbitrage des choix d'expérience** (humain) |
| `designer-prompt` | une fois la couverture suffisante -> **prompt Claude Design** (corps seul, dans `designer-out/prompts/`) + rapport de couverture | couverture jugée suffisante |
| `designer-coherence` | valide le design system (export committé dans `designer-out/maquette-de-claude-design/`) + produit le handoff design (réf. + guidelines) | **validation du système généré** (humain) |

### Phase 4 : `assembleur` (convergence -> paquet SpecKit)
Lit les 3 contrats en parallèle, les converge, et produit un **paquet de handoff** dans `assembleur-out/` (il n'écrit jamais dans le repo cible).

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `assembleur-init` | vérifie que les 3 dossiers de sortie amont (`cadrage-out/`, `architecte-out/`, `designer-out/`) existent et sont complets (pas de statut de validation exigé) + installe les gabarits + crée `assembleur-out/` | 3 dossiers de sortie amont présents |
| `assembleur-convergence` | lit les 3 contrats **en parallèle** + converge + produit le paquet (pré-constitution, graines spec, carte des features, contexte technique, CLAUDE.md, mémoire) + résout les points en session | **garant de cohérence** (humain) |
| `premier-alimente-linear` | crée les tickets Linear : un `Feature` par feature + un sous-ticket `Task` par exigence fonctionnelle, tout en Backlog | **point de gel** du registre de features |
| `install-speckit` | installe SpecKit dans le repo (`uv` sans admin, `specify init` non interactif) pour lancer les `/speckit.*` | après l'alimentation Linear |
| `create-cowork-md` | génère `init-cowork.md` à la racine : le contexte de supervision du PO (liens GitHub + Linear) | à la demande |
| `creation-task-linear` | après `/speckit.tasks` : un sous-ticket `Task` par phase de `tasks.md`, rattaché au ticket `Feature` | `tasks.md` existe |
| `update-issue-linear` | met à jour l'état d'un ticket quand tu signales une tâche terminée ou avancée | à la demande, pendant la fabrication |
| `revue-gemini` | **relecteur externe avant PR/merge** : un reviewer Gemini par dimension (sécurité, correction, perf, architecture, qualité, tests) sur le diff de branche, agrégé par sévérité. Contre l'excès de confiance de Claude sur son propre code | **avant d'ouvrir ou de merger** (consultatif) |

### Phase 5 : `validation` (recette fonctionnelle d'une feature livrée)
Quand une feature est livrée et déployée sur l'environnement de recette : dériver le plan de test
depuis les critères d'acceptation de sa spécification (un cas par critère, tracé), le jouer dans le
navigateur (extension Chrome en priorité, Playwright en repli, ou mission différée pour Claude
Cowork), et produire un rapport de recette tracé exigence par exigence. L'IA exécute et rapporte,
le testeur valide (porte de recette). Les écarts constatés se traitent ensuite côté `maintenance`.

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `validation-init` | installe les gabarits + bloc manifeste + enregistre l'adresse de l'environnement de recette + signale l'amont manquant (`specs/`, Linear, maintenance) | après la première feature livrée |
| `plan-de-validation` | dérive le plan de test depuis `specs/<feature>/spec.md` : un cas par critère d'acceptation, tracé à sa source, critère non testable marqué "à clarifier" (jamais interprété), données de test collectées en session | **plan validé par le testeur** (humain) |
| `execution-validation` | joue le plan dans le navigateur contre l'environnement de recette (choix de l'outil à chaque lancement : extension Chrome recommandée / Playwright / mission Cowork) ; résultats + preuves au format commun | le testeur choisit l'outil ; l'IA constate |
| `rapport-de-recette` | rapport tracé (critère -> cas -> verdict -> preuve), tri de chaque écart avec le testeur (anomalie -> `/maintenance:creation-anomalie`, spec en cause -> `/maintenance:creation-evolution`, flou -> clarifier ou suivi Linear), scénarios rejouables de non-régression, puis verdict de recette (rapport + commentaire Linear) | **verdict de recette** (humain) |

### Phase 6 : `maintenance` (traitement des écarts après livraison)
Quand le PO ou la validation fonctionnelle constate un écart sur une feature livrée, tout devient
un objet suivi dans Linear (anomalie ou évolution), réalisé en orchestrant les commandes SpecKit
existantes. Frontière : avant livraison rien ne se trace, après livraison tout se trace.

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `maintenance-init` | installe les gabarits + bloc manifeste + vérifie le raccordement Linear (labels `Anomalie`/`Evolution`, statut "Requalifiée en évolution") | après la première feature livrée |
| `creation-anomalie` | le PO crée une anomalie complète dans Linear (attendu, constaté, critère en échec, reproduction), rattachée au ticket de sa feature | **le PO qualifie la nature** (humain) |
| `correction-anomalie` | le développeur corrige : requalifie si le code respecte la spec (sans créer l'évolution), sinon enquête code + correction + clôture avec trace à jour | **cause racine validée** (humain) |
| `creation-evolution` | le PO crée une évolution portant un écart de spécification précis et circonscrit (jamais une réécriture) | **le PO porte le périmètre** (humain) |
| `realisation-evolution` | le développeur réalise, chirurgical : spec d'abord -> `/speckit.clarify` -> plan -> `/speckit.implement` cadré -> non-régression prouvée | **plan validé avant le code** (humain) |

### Transversal : `couts` (mesure du coût de simulation)
Pas une phase : mesure **ce que coûterait la fabrication au tarif API** (estimation). À installer
**tôt** pour tout capter. **Simulation seule** (pas de coût réel).

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `couts-init` | pose le compteur (hook `SessionEnd` **en fin de session, sans latence par tour** + table de prix par tier) **dans le dossier courant**, sans question, sans écraser les hooks existants | **tôt** |
| `couts-rapport` | restitue un **tableau par session** (tokens input/output, cache lu/écrit + coût en euros) ; écrit un rapport **versionné** (`rapport-couts.md`, puis `-2`, `-3`... - jamais d'écrasement) | à tout moment |
| `couts-total` | agrège toutes les sessions locales en un seul bilan partageable (total tokens, coût estimé, nombre de sessions) | pour le chef d'équipe |

**Handoff final** : l'équipe prend le paquet de `assembleur-out/` -> `/assembleur:premier-alimente-linear` (un ticket Linear `Feature` par feature) -> `specify init` -> `/speckit.constitution` (depuis `pre-constitution.md`) -> les `/speckit.specify` dans l'ordre du `feature-map.md` (walking skeleton d'abord) -> `/speckit.plan` -> `/speckit.tasks` -> `/assembleur:creation-task-linear` (un sous-ticket `Task` par phase) -> `/speckit.implement` (état des tickets via `/assembleur:update-issue-linear`).

**Fabrication en parallèle** : une branche = une feature = un développeur (numéro imposé par le registre, **jamais** d'auto-numérotation), **claim** du ticket `Feature` Linear avant de démarrer, l'avancement vit **dans Linear**, et les features **couplées** (même composant/état) se traitent **en séquence**. SpecKit offre aussi des portes de cohérence **natives optionnelles** (`/speckit.clarify`, `/speckit.analyze`). Règles complètes : `assembleur-out/attack-plan.md`.

**Repère** : pour savoir où tu en es dans une phase, lance son skill de bilan/cohérence
(`cadrage-completude`, `architecte-coherence`, `designer-coherence`, le rapport de cohérence de l'assembleur, ou `rapport-de-recette` côté validation).

## Étape suivante
"Étape suivante : `/cadrage:cadrage-init` pour démarrer depuis le début, ou lance directement la phase qui correspond à ton avancement - `/architecte:architecte-init`, `/designer:designer-init`, `/assembleur:assembleur-init`, `/validation:validation-init` (feature livrée à recetter) ou `/maintenance:maintenance-init` (écarts à traiter)."
