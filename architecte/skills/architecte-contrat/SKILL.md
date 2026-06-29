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
`cadrage-out/features-fonctionnels-brief/*.brief.md`. Conventions d'interaction :
`references/interactive-loop.md` et `references/ux-conventions.md`.

> **Règles transverses (toutes les étapes).** Restituer **en prose**, jamais en
> tableau. Désigner chaque chose par son **nom métier en clair** — jamais un code
> (`C1`, `UC1`, `P1`…). **Aucune provenance** écrite dans les artefacts (pas de
> `(src:)`, d'horodatage, de nom de personne). Mettre à jour le manifeste **en
> silence** : ne jamais narrer « MAJ `architecture.*` » ni un nom de variable. Toute
> valeur manquante se **résout en session** (cf. `references/interactive-loop.md`) et
> s'écrit **en place** — aucun marqueur n'est laissé dans un fichier final.

## Procédure — ordre imposé (chaque étape consomme la précédente)

### Étape 0 — Vérifier les réponses (ne rien re-demander d'inutile)
Charger `references/question-map.md`. **Auto-remplir en silence** chaque réponse
d'architecture depuis l'artefact de cadrage indiqué — **sans afficher de tableau**
question/source/réponse, sans identifiant `Qn`. Ne **poser que les trous**, en clair
et **un par un** (cf. `references/interactive-loop.md`) :
- **profil d'équipe** (taille, expertise langage/framework) — absent du cadrage ;
- tout point de cadrage resté à confirmer et **bloquant**.
Si un trou bloquant n'est pas tranché, **ne pas démarrer la génération** : le dire en
clair et s'arrêter. Écrire le profil d'équipe au manifeste (en silence).

### Étape 1 — Drivers & attributs de qualité
À partir des seeds qualité (charge, disponibilité, performance) + les contraintes
(légal, sécurité, données) : **classer les drivers par priorité** (ce qui compte le
plus pour CE produit) et **classer les attributs de qualité**, puis formuler des
**scénarios de qualité testables (QAW)**. Restituer **en prose** dans le chat (par
leur nom en clair), faire valider, puis écrire `architecte-out/drivers-quality.md`
(gabarit `templates/drivers-quality.md`). Mettre à jour le manifeste en silence.

### Étape 2 — Workflow composants (interactif)
Dériver une **liste de composants candidats** depuis le périmètre fonctionnel
(briefs + spec-index). **Restituer la liste en prose** (nom métier + rôle en une
phrase) — **jamais de tableau, jamais de code `C1`/`C2`**. **Demander si ça convient
ou s'il faut modifier** ; appliquer les retours (ajout/fusion/suppression) ; **boucler
jusqu'à validation**. Puis écrire `architecte-out/components.md` (gabarit
`templates/components.md`). Mettre à jour le manifeste en silence.

### Étape 3 — Workflow stack technique (interactif)
Pour chaque domaine de décision (langage(s), framework(s), bibliothèques
principales, base de données, style d'API, communication asynchrone, déploiement,
observabilité), si la réponse n'est pas déjà dans le cadrage : **proposer 2–4
options avec avantages/inconvénients + une recommandation**, l'utilisateur tranche
(boucle 3-options). Respecter l'ordre des dépendances entre choix (langage avant
framework, etc.). **Validation finale** de la stack en chat. Écrire
`architecte-out/tech-stack.md` (gabarit `templates/tech-stack.md`, dont la
**matrice composant × techno** — une ligne par composant). Mettre à jour le manifeste en silence.

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
Écrire/compléter `architecte-out/standards.md` (gabarit `templates/standards.md`)
qui **pointe vers `conventions/`** + couvre les standards non-formatage (erreurs,
logging, sécurité, tests, API, données, git, doc). Mettre à jour le manifeste en silence.

### Étape 5 — ADR (arbitrage humain)
Pour chaque décision structurante (style d'archi, API, persistance, identité/authz,
multitenance, déploiement, observabilité…), produire un **ADR** (gabarit
`templates/adr.md`) dans `architecte-out/decisions/ADR-NNN-titre.md` : contexte,
décision, options, conséquences, déclencheur de revue. **C'est une décision arbitrée
par l'humain** : l'architecte valide chaque ADR. Mettre à jour le manifeste en silence.

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
`python scripts/render_diagrams.py <projet>/architecte-out/diagrams.md` — il rend un
**PNG par diagramme** dans **`architecte-out/diagrammes/`** (via mermaid-cli `mmdc`,
ou `npx -y @mermaid-js/mermaid-cli` s'il n'est pas installé). Confirmer en clair les
images produites. **Si le rendu échoue** (outil indisponible), le dire en clair et
continuer — ne jamais bloquer la phase pour ça ; le markdown reste la source.

### Étape 8 — Registre de risques
Produire `architecte-out/risks.md` (gabarit `templates/risks.md`) : risques
techniques, mitigations, spikes/POC nécessaires. Mettre à jour le manifeste en silence.

### Étape 9 — Décisions à impact design (handoff vers le Designer)
**Synthétiser la tranche de l'architecture qui se voit à l'écran** — c'est le contrat propre
Architecte → Designer (le designer ne doit pas fouiller tout le handoff ; l'architecte sait ce qui se
voit). Produire `architecte-out/design-impact.md` (gabarit `templates/design-impact.md`), par ordre
d'importance : **1.** stack front + approche de style (framework, lib de composants, stratégie CSS — *ce
qui rend le design system exécutable/synchronisable*) ; **2.** contrats transverses visibles
(multitenance/theming par tenant ; identité/rôles/autorisations : variantes par rôle, non autorisé,
connexion, session expirée ; navigation/routage) ; **3.** conventions d'API qui décident des états d'UI
(format d'erreur → messages par champ, asynchrone, pagination/listes, cas vides) ; **4.** NFR qui touchent
l'UX (niveau d'accessibilité visé, cibles responsive/breakpoints, i18n, budget de performance). **Exclure**
le back/persistance/déploiement/ADR serveur. **Contenu seul** (aucune `(src:)`) ; **ne pas inventer** ;
**sans objet** si N/A. Mettre à jour le manifeste en silence.

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
- **Contenu seul** : aucune `(src:)`, aucun horodatage, aucun nom de personne, **aucun
  marqueur résiduel** ; tout point a été tranché en session.

## Règles invariantes
- **Proposer, ne pas décider.** Les ADR sont arbitrés par l'humain ; les workflows
  composants/stack se valident en chat.
- **Rien d'affiché de la mécanique.** Aucun nom de variable/clé manifeste, aucun
  identifiant codé, aucun tableau (voir `references/ux-conventions.md`). Le manifeste
  se met à jour en silence.
- **Skill indépendant.** Lit/écrit le manifeste partagé.

À la fin, dire en clair **ce qui a été produit** (en prose, sans tableau, sans ligne
de manifeste) puis l'étape suivante.

Étape suivante : `/architecte:architecte-coherence` — valider la cohérence du contrat technique avant le passage à l'assembleur.
