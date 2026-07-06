---
name: help-factory
description: Aide unique de la Factory — affiche la carte des 4 plugins (cadrage, architecte, designer, assembleur), un tableau par plugin avec le rôle de chaque skill, l'ordre et les portes humaines.
---

# help-factory

Skill d'aide — **l'unique aide de la Factory** (couvre les 4 plugins). Quand il est invoqué,
**affiche immédiatement le contenu ci-dessous TEL QUEL** (les 4 tableaux), sans rien recalculer.
Il **n'écrit aucun fichier** et ne modifie aucun manifeste.

## À afficher tel quel

**La Factory IA transforme un atelier en projet spec-driven, en 4 phases.** Chaque phase est un plugin
qui produit un *contrat* validé par un humain, puis passe le relais :
**`cadrage → architecte → designer → assembleur → SpecKit`**.
Chaque skill se termine par une ligne « **Étape suivante** » qui indique quoi lancer ensuite — tu avances
de proche en proche. Le design system naît dans **Claude Design** et passe au code via **`/design-sync`**.

### Phase 1 — `cadrage` (contrat fonctionnel)
De la matière brute (transcripts, docs) au pack fonctionnel repris par l'architecte.

| # | skill | rôle | porte / ordre |
|---|-------|------|---------------|
| 0 | `cadrage-init` | crée la mécanique `.factory/` + le dossier `cadrage-out/` + le manifeste | à lancer en premier |
| 1 | `cadrage-extraction` | dépouille les sources en capture (contenu, sans horodatage) + pose les 13 questions de découverte | manifeste + ≥1 source |
| 2 | `cadrage-vision` | synthétise la capture en vision produit (le quoi / le pourquoi) | capture existe |
| 3 | `cadrage-glossaire` | construit le langage métier du projet, validé en bloc | capture existe |
| 4 | `cadrage-decoupage` | découpage fonctionnel en use cases (par valeur) + carte de couplage | vision faite |
| 5 | `cadrage-demonstrateur-brief` | prompt Claude Design pour la maquette de validation | vision / retour dispo |
| 6 | `cadrage-retour-demonstrateur` | ingère le retour client sur la maquette, propage les corrections | retour dispo |
| 7 | `cadrage-clarification` | pose les questions restantes en session *(rejouable)* | ≥1 point à clarifier |
| 8 | `cadrage-briefs` | brief auto-portant par feature (dans `cadrage-out/features-fonctionnels-brief/`) | couplage arbitré + maquette validée |
| 9 | `cadrage-completude` | **étape terminale** : bilan + résolution en session, puis relais vers l'architecte | *(rejouable)* — fin du cadrage |

### Phase 2 — `architecte` (contrat technique)
Transforme le besoin fonctionnel en cadre technique et fige la séquence numérotée des features.

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `architecte-init` | crée `conventions/` + installe les gabarits + bloc manifeste | cadrage prêt |
| `architecte-contrat` | construit le contrat technique : drivers & attributs de qualité, composants, stack, ADR, walking skeleton, diagrammes (+ images PNG), *Décisions à impact design* | **arbitrage des ADR** (humain) |
| `architecte-coherence` | valide la cohérence du contrat technique (stricte, interactive) | **validation de cohérence** (humain) |

### Phase 3 — `designer` (contrat de design)
**Atelier de couverture** : ne génère pas le design system — il garantit que rien n'est oublié et prépare Claude Design.

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `designer-init` | installe les gabarits + sème la checklist de couverture + crée `prompts/designer/` | maquette validée + architecture validée + *Décisions à impact design* |
| `designer-atelier` | atelier de couverture (fondation / expérience / technique) → **prompt Claude Design** (corps seul, dans `prompts/designer/`) + rapport de couverture | **arbitrage des choix d'expérience** (humain) |
| `designer-coherence` | valide le design system généré par Claude Design + produit le handoff design (réf. + guidelines) | **validation du système généré** (humain) |

### Phase 4 — `assembleur` (convergence → paquet SpecKit)
Lit les 3 contrats en parallèle, les converge, et produit un **paquet de handoff** dans `assembleur-out/` (il n'écrit jamais dans le repo cible).

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `assembleur-init` | vérifie les 3 contrats validés + installe les gabarits + crée `assembleur-out/` | 3 contrats validés |
| `assembleur-convergence` | lit les 3 contrats **en parallèle** + converge + produit le paquet (pré-constitution, graines spec, carte des features, contexte technique, CLAUDE.md, mémoire) + résout les points en session | **garant de cohérence** (humain) |

### Transversal — `couts` (mesure du coût de simulation)
Pas une phase : mesure **ce que coûterait la fabrication au tarif API** (estimation). À installer
**tôt** pour tout capter. **Simulation seule** (pas de coût réel).

| skill | rôle | porte / ordre |
|-------|------|---------------|
| `couts-init` | pose le compteur (hook `SessionEnd` **en fin de session, sans latence par tour** + table de prix par tier) **dans le dossier courant**, sans question, sans écraser les hooks existants | **tôt** |
| `couts-rapport` | restitue un **tableau par session** (tokens input/output + coût en euros) ; écrit un rapport **versionné** (`rapport-couts.md`, puis `-2`, `-3`… — jamais d'écrasement) | à tout moment |

**Handoff final** : l'équipe prend le paquet de `assembleur-out/` → `/assembleur:premier-alimente-linear` (un ticket Linear `Feature` par feature) → `specify init` → `/speckit.constitution` (depuis `pre-constitution.md`) → les `/speckit.specify` dans l'ordre du `feature-map.md` (walking skeleton d'abord) → `/speckit.plan` → `/speckit.tasks` → `/assembleur:creation-task-linear` (un sous-ticket `Task` par phase) → `/speckit.implement` (état des tickets via `/assembleur:update-issue-linear`).

**Repère** : pour savoir où tu en es dans une phase, lance son skill de bilan/cohérence
(`cadrage-completude`, `architecte-coherence`, `designer-coherence`, ou le rapport de cohérence de l'assembleur).

## Étape suivante
« Étape suivante : `/cadrage:cadrage-init` pour démarrer depuis le début, ou lance directement la phase qui correspond à ton avancement — `/architecte:architecte-init`, `/designer:designer-init` ou `/assembleur:assembleur-init`. »
