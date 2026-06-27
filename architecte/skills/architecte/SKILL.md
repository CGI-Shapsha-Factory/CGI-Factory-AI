---
name: architecte
description: Construit le contrat technique (drivers, composants, stack, ADR, walking skeleton, diagrammes) en interactif.
---

# architecte

Cœur de la phase technique. **Discipline le raisonnement de l'architecte et grave
ses décisions en contrats traçables.** L'IA propose et structure ; **l'humain
tranche** (arbitrage des ADR). Ne décide jamais l'architecture à la place de
l'architecte.

## Porte d'entrée
`architecte-init` a tourné (le manifeste contient le bloc `architecture`). Sinon,
orienter en clair vers `/architecte:architecte-init`.

## Entrées (lues depuis le cadrage)
`factory-docs/work/` : `project-frame.md` (Q1–Q13 + *seeds qualité* Q2/Q6/Q7),
`product-brief.md`, `glossaire.md`, `spec-index.md` (use cases + walking skeleton
candidat + couverture), `*.brief.md`, `pre-constitution.md`. Conventions
d'interaction : `references/interactive-loop.md` et `references/ux-conventions.md`.

## Procédure — ordre imposé (chaque étape consomme la précédente)

### Étape 0 — Vérifier les réponses (ne rien re-demander d'inutile)
Charger `references/question-map.md`. Pour chaque question d'architecture,
**auto-remplir** depuis l'artefact de cadrage indiqué (avec `(src: …)`). Ne **poser
que les trous** via la boucle 3-options (`references/interactive-loop.md`) :
- **profil d'équipe** (taille, expertise langage/framework) — absent du cadrage ;
- toute réponse de cadrage restée `[À VALIDER]`/`deferred` et **bloquante**.
Si un trou bloquant est « passé », **ne pas démarrer la génération** : le signaler en
clair et s'arrêter. Écrire `architecture.team_profile` au manifeste.

### Étape 1 — Drivers & attributs de qualité
À partir des *seeds qualité* (Q2 charge, Q6 disponibilité, Q7 performance) + les
contraintes (légal, sécurité, données) : **classer les drivers par priorité** (ce
qui compte le plus pour CE produit) et **classer les attributs de qualité**, puis
formuler des **scénarios de qualité testables (QAW)**. Restituer en chat, faire
valider, puis écrire `factory-docs/work/drivers-quality.md` (gabarit
`templates/drivers-quality.md`). MAJ `architecture.drivers` / `.quality_attributes`.

### Étape 2 — Workflow composants (interactif)
Dériver une **liste de composants candidats** depuis le périmètre fonctionnel
(briefs + spec-index). **Afficher la liste en tableau dans le chat** (langage
produit : nom, rôle en une phrase). **Demander si ça convient ou s'il faut
modifier** ; appliquer les retours (ajout/fusion/suppression) ; **boucler jusqu'à
validation**. Puis écrire `factory-docs/work/components.md` (gabarit
`templates/components.md`). MAJ `architecture.components`.

### Étape 3 — Workflow stack technique (interactif)
Pour chaque domaine de décision (langage(s), framework(s), bibliothèques
principales, base de données, style d'API, communication asynchrone, déploiement,
observabilité), si la réponse n'est pas déjà dans le cadrage : **proposer 2–4
options avec avantages/inconvénients + une recommandation**, l'utilisateur tranche
(boucle 3-options). Respecter l'ordre des dépendances entre choix (langage avant
framework, etc.). **Validation finale** de la stack en chat. Écrire
`factory-docs/work/tech-stack.md` (gabarit `templates/tech-stack.md`, dont la
**matrice composant × techno** — une ligne par composant). MAJ `architecture.stack`.

### Étape 4 — Activer les conventions (vrais fichiers)
Pour chaque **langage retenu** à l'étape 3, copier le(s) fichier(s) de config
correspondant du catalogue `references/conventions/` vers le dossier `conventions/`
du projet :
- Python → `python/ruff.toml` ; TS/JS → `ts-js-biome/biome.json` (défaut) **ou**
  `ts-js-eslint/{eslint.config.js,.prettierrc}` (demander lequel) ; C →
  `c/.clang-format`.
- **Fallback (langage hors catalogue)** : ne pas inventer de config exotique —
  garder le `.editorconfig` universel, **avertir l'utilisateur** que ce langage n'a
  pas de convention prédéfinie, et **proposer** une convention générique (indentation,
  longueur de ligne, nommage) marquée `[À VALIDER]` pour relecture humaine.
Écrire/compléter `factory-docs/work/standards.md` (gabarit `templates/standards.md`)
qui **pointe vers `conventions/`** + couvre les standards non-formatage (erreurs,
logging, sécurité, tests, API, données, git, doc). MAJ `architecture.conventions_installed`.

### Étape 5 — ADR (arbitrage humain)
Pour chaque décision structurante (style d'archi, API, persistance, identité/authz,
multitenance, déploiement, observabilité…), produire un **ADR** (gabarit
`templates/adr.md`) dans `factory-docs/work/decisions/ADR-NNN-titre.md` : contexte,
décision, options, conséquences, déclencheur de revue. **C'est une porte d'arbitrage
humain** : l'architecte valide chaque ADR. MAJ `architecture.adrs[]`.

### Étape 6 — Walking skeleton + convergence (numérotation)
Désigner le **walking skeleton définitif** (la première tranche de bout en bout qui
dé-risque la stack ; confirmer/ajuster le candidat du spec-index). **Figer la liste
de features numérotées et séquencée** : **chaque** use case du `spec-index.md`
devient une feature numérotée (`UC… → 001, 002, …`). La liste est **complète** —
couverture 1:1, **aucun use case laissé de côté**, MVP **et** hors-MVP — ordonnée
selon les dépendances et le couplage technique. C'est la **convergence des deux
découpages**. L'ordre place en tête les features du **périmètre MVP** (celui défini
dans le `spec-index.md`), walking skeleton en premier ; les features hors MVP suivent
(numérotées et présentes, jamais omises). Mettre à jour la section Dépendances des
briefs en conséquence.

**Format — registre canonique.** `architecture.feature_sequence` est le **registre
canonique des features** : une liste d'**objets** `{id, ucs, name, mvp}` où **`ucs` est une
liste** de use cases du cadrage — ex. `{"id": "001", "ucs": ["UC2"], "name": "Recherche Q&A
sourcée", "mvp": true}`. Une feature de fabrication peut **bundler plusieurs use cases**
(fusion : `"ucs": ["UC5", "UC6"]`) ; un seul use case = liste à un élément. Les `ucs` portent
la correspondance **use case ↔ id** (le use case = identité fonctionnelle stable du cadrage)
pour que le designer et l'assembleur joignent les trois faces **par use case**. MAJ
`architecture.walking_skeleton` (= l'`id` du walking skeleton) / `.feature_sequence`.

> **Couverture complète exigée.** `architecte-coherence` (contrôle #3) échoue si un
> use case du `spec-index.md` n'a pas de feature correspondante dans
> `architecture.feature_sequence`. Séquencer le seul MVP n'est donc pas suffisant :
> figer toute la liste, le MVP n'étant qu'un sous-ensemble *ordonné en tête*, pas un
> filtre.

### Étape 7 — Diagrammes
Produire `factory-docs/work/diagrams.md` (gabarit `templates/diagrams.md`) :
C4 contexte, C4 conteneurs, flux d'un parcours critique, ERD, déploiement (Mermaid),
avec les noms réels (pas de placeholders).

### Étape 8 — Registre de risques
Produire `factory-docs/work/risks.md` (gabarit `templates/risks.md`) : risques
techniques, mitigations, spikes/POC nécessaires. MAJ `architecture.risks`.

## Porte de sortie
- Réponses vérifiées (rien de bloquant en suspens) ; `drivers-quality.md`,
  `components.md`, `tech-stack.md`, `standards.md`, ADR, `diagrams.md`, `risks.md`
  produits ; conventions par langage installées dans `conventions/` ;
  walking skeleton et séquence de features figés. `architecture.phase = "contrat"`.
- **Traçabilité** : chaque énoncé porte sa source `(src: …)` (artefact cadrage ou
  atelier/utilisateur). **Rien d'inventé** ; tout trou reste `[À VALIDER]`.

## Règles invariantes
- **Proposer, ne pas décider.** Les ADR sont arbitrés par l'humain ; les workflows
  composants/stack se valident en chat.
- **Pas de fuite de champ** ni de jargon en sortie utilisateur (voir
  `references/ux-conventions.md`). Refus en langage naturel.
- **Skill indépendant.** Lit/écrit le manifeste partagé.

Étape suivante : `/architecte:architecte-coherence` — valider la cohérence du contrat technique avant le passage à l'assembleur.
