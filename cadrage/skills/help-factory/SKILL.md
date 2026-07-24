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
| 0 | `cadrage-init` | crée `.factory/` + `cadrage-out/` + le manifeste | à lancer en premier |
| 0bis | `cadrage-ideation` | *(facultatif)* atelier d'idéation quand la matière est mince - le compte rendu nourrit l'extraction | manifeste existe |
| 1 | `cadrage-extraction` | dépouille les sources en capture + passe de découverte (19 questions) | manifeste + ≥1 source |
| 2 | `cadrage-vision` | synthétise la capture en vision produit (le quoi / le pourquoi) | capture existe |
| 3 | `cadrage-glossaire` | construit le langage métier du projet, validé en bloc | capture existe |
| 4 | `cadrage-decoupage` | découpage fonctionnel en use cases (par valeur) + carte de couplage | vision faite |
| 5 | `cadrage-demonstrateur-brief` | prompt Claude Design pour la maquette de validation | vision / retour dispo |
| 6 | `cadrage-retour-client` | ingère tout retour client (docs ou maquette) et met à jour le cadrage en place | retour ou nouveaux docs dispo |
| 7 | `cadrage-briefs` | brief auto-portant par feature | couplage arbitré + maquette validée |
| 8 | `cadrage-completude` | bilan Definition of Ready + résolution en session des points ouverts | *(rejouable)* - fin du cadrage |

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
| `designer-init` | installe les gabarits + sème la checklist de couverture + crée `designer-out/` | maquette + architecture validées |
| `designer-ingestion` | ingère les handoffs cadrage + architecte et pré-remplit la checklist | init fait |
| `designer-atelier` | déroule la checklist (fondation / expérience / technique) et arbitre les choix | **arbitrage des choix d'expérience** (humain) |
| `designer-prompt` | prompt Claude Design + rapport de couverture | couverture jugée suffisante |
| `designer-coherence` | valide l'export du design system + produit le handoff design | **validation du système généré** (humain) |

### Phase 4 : `assembleur` (convergence -> paquet SpecKit)
Lit les 3 contrats en parallèle, les converge, et produit un **paquet de handoff** dans `assembleur-out/` (il n'écrit jamais dans le repo cible).

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `assembleur-init` | vérifie les 3 dossiers de sortie amont + installe les gabarits + crée `assembleur-out/` | 3 dossiers amont présents |
| `assembleur-convergence` | converge les 3 contrats -> paquet SpecKit (pré-constitution, graines spec, feature-map...) | **garant de cohérence** (humain) |
| `premier-alimente-linear` | crée les tickets Linear : un `Feature` par feature + un `Task` par exigence | **point de gel** du registre de features |
| `install-speckit` | installe SpecKit dans le repo (`specify init`) | après l'alimentation Linear |
| `create-cowork-md` | génère `init-cowork.md` : le contexte de supervision du PO | à la demande |
| `creation-taches-par-phase-de-spec` | un sous-ticket `Task` par phase de `tasks.md` | après `/speckit.tasks` |
| `update-issue-linear` | met à jour l'état d'un ticket Linear | pendant la fabrication |
| `revue-gemini` | revue de code externe (Gemini) sur le diff de branche | **avant PR/merge** (consultatif) |

### Phase 5 : `validation` (recette fonctionnelle d'une feature livrée)
Quand une feature est livrée et déployée sur l'environnement de recette : dériver le plan de test
depuis les critères d'acceptation de sa spécification (un cas par critère, tracé), le jouer dans le
navigateur (extension Chrome en priorité, Playwright en repli, ou mission différée pour Claude
Cowork), et produire un rapport de recette tracé exigence par exigence. L'IA exécute et rapporte,
le testeur valide (porte de recette). Les écarts constatés se traitent ensuite côté `maintenance`.

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `validation-init` | installe les gabarits + enregistre l'environnement de recette | après la première feature livrée |
| `plan-de-validation` | dérive le plan de test de la spec : un cas par critère, tracé, jamais interprété | **plan validé par le testeur** (humain) |
| `execution-validation` | joue le plan dans le navigateur (Chrome / Playwright / mission Cowork) ; résultats + preuves | le testeur choisit l'outil ; l'IA constate |
| `rapport-de-validation` | rapport tracé critère par critère + tri des écarts vers `/maintenance:*` | **verdict de recette** (humain) |

### Phase 6 : `maintenance` (traitement des écarts après livraison)
Quand le PO ou la validation fonctionnelle constate un écart sur une feature livrée, tout devient
un objet suivi dans Linear (anomalie ou évolution), réalisé en orchestrant les commandes SpecKit
existantes. Frontière : avant livraison rien ne se trace, après livraison tout se trace.

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `maintenance-init` | installe les gabarits + vérifie le raccordement Linear | après la première feature livrée |
| `creation-anomalie` | le PO crée une anomalie complète dans Linear, rattachée à sa feature | **le PO qualifie la nature** (humain) |
| `correction-anomalie` | le développeur corrige : requalifie ou enquête code + correction + clôture tracée | **cause racine validée** (humain) |
| `creation-evolution` | le PO crée une évolution de spec précise et circonscrite | **le PO porte le périmètre** (humain) |
| `realisation-evolution` | le développeur réalise : spec -> plan -> `/speckit.implement` cadré -> non-régression | **plan validé avant le code** (humain) |

### Transversal : `couts` (mesure du coût de simulation)
Pas une phase : mesure **ce que coûterait la fabrication au tarif API** (estimation). À installer
**tôt** pour tout capter. **Simulation seule** (pas de coût réel).

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `couts-init` | pose le compteur (hook `SessionEnd` + table de prix) dans le dossier courant | **tôt** |
| `couts-rapport` | tableau par session (tokens + coût en euros), rapport versionné | à tout moment |
| `couts-total` | agrège toutes les sessions en un bilan partageable | pour le chef d'équipe |

**Handoff final** : l'équipe prend le paquet de `assembleur-out/` -> `/assembleur:premier-alimente-linear` (un ticket Linear `Feature` par feature) -> `specify init` -> `/speckit.constitution` (depuis `pre-constitution.md`) -> les `/speckit.specify` dans l'ordre du `feature-map.md` (walking skeleton d'abord) -> `/speckit.plan` -> `/speckit.tasks` -> `/assembleur:creation-taches-par-phase-de-spec` (un sous-ticket `Task` par phase) -> `/speckit.implement` (état des tickets via `/assembleur:update-issue-linear`).

**Fabrication en parallèle** : une branche = une feature = un développeur (numéro imposé par le registre, **jamais** d'auto-numérotation), **claim** du ticket `Feature` Linear avant de démarrer, l'avancement vit **dans Linear**, et les features **couplées** (même composant/état) se traitent **en séquence**. SpecKit offre aussi des portes de cohérence **natives optionnelles** (`/speckit.clarify`, `/speckit.analyze`). Règles complètes : `assembleur-out/attack-plan.md`.

**Repère** : pour savoir où tu en es dans une phase, lance son skill de bilan/cohérence
(`cadrage-completude`, `architecte-coherence`, `designer-coherence`, le rapport de cohérence de l'assembleur, ou `rapport-de-validation` côté validation).

## Étape suivante
"Étape suivante : `/cadrage:cadrage-init` pour démarrer depuis le début, ou lance directement la phase qui correspond à ton avancement - `/architecte:architecte-init`, `/designer:designer-init`, `/assembleur:assembleur-init`, `/validation:validation-init` (feature livrée à recetter) ou `/maintenance:maintenance-init` (écarts à traiter)."
