---
name: cadrage-handoff
description: Assemble la pré-constitution, les briefs et le spec index, puis passe le relais à SpecKit.
---

# cadrage-handoff

Dernière étape. Matérialise la frontière : prépare la **pré-constitution**
(matière pour SpecKit) et sort les artefacts de fabrication (briefs, spec index)
vers le repo SpecKit, et produit le plan de séquencement des `/speckit.specify`.

## Objectif

Déposer dans le repo cible un **pack de fabrication cohérent** et le **plan
d'attaque** : quelles commandes `/speckit.specify` lancer, dans quel ordre.

## Entrée

- `factory-docs/work/product-brief.md`, `factory-docs/work/glossaire.md` et
  `factory-docs/work/project-frame.md` (pour la constitution).
- Les briefs `factory-docs/work/*.brief.md`.
- `factory-docs/work/spec-index.md` (arbitré).
- Le chemin du repo SpecKit cible.

## Pré-requis (vérification silencieuse)

Vérifier **en silence** que le projet est **« prêt pour SpecKit »** (verdict calculé
par `cadrage-completude`). Cette vérification ne s'affiche pas : aucun nom
d'attribut, aucun statut, aucun tableau de booléens.

Si le pack n'est pas prêt, ne pas afficher de refus technique : le dire **en clair**,
avec un message en français naturel (convention `references/ux-conventions.md`) :

> « Le pack n'est pas encore prêt : il reste des éléments à compléter avant le passage
> à SpecKit — on fait le point ? »

Puis renvoyer vers `cadrage-completude` pour mesurer en clair ce qui manque.

## Procédure

0. **Rafraîchir la complétude.** Relancer `cadrage-completude` pour régénérer
   `factory-docs/work/completude-report.md` à partir de l'état réel — le rapport livré doit
   **refléter le manifeste** (mêmes drapeaux, statuts de briefs à jour). Si rapport et manifeste
   **divergent** (ex. manifeste « prêt » mais rapport « pas prêt »), **ne pas faire le handoff** :
   recalculer d'abord.
1. **Dériver la pré-constitution** depuis le product brief, le glossaire, le
   project-frame et les contraintes, en suivant le gabarit
   `factory-docs/templates/pre-constitution.md` (Identité produit, Principes directeurs,
   Contraintes techniques & réglementaires ← project-frame, Langage ubiquitaire
   ← termes du glossaire validés, Non-périmètre global ← OUT vision).
   **Rien d'inventé** : tout vient des artefacts ; un manque se **tranche en session**
   (on pose la question), il n'est ni écrit ni marqué.
2. **Déposer la pré-constitution** dans `factory-docs/work/pre-constitution.md`. Elle
   sert de matière à `/speckit.constitution` ; la constitution finale est générée
   par SpecKit (ne pas écrire directement dans `<repo>/.specify/memory/`).
3. **Mettre les briefs à disposition** du repo (présents et complets).
4. **Fournir le spec index** comme document de suivi, reflétant le découpage
   arbitré.
5. **Produire le plan de séquencement** : d'abord `/speckit.constitution` à partir
   de la pré-constitution, puis la liste des `/speckit.specify`, **une par feature,
   dans l'ordre des dépendances** du spec index (walking skeleton en premier), avec
   les features parallélisables signalées.
6. **Exposer le handoff pour le Designer** (entrées de la phase design, cf. spec designer §4.1) :
   - la **liste des parcours / use cases** = le `spec-index.md` (déjà arbitré) ;
   - les **types de données / entités affichées à l'utilisateur** = les **termes**
     du `glossaire.md` (entités métier visibles) ;
   - la **maquette** (`demonstrateur`) est fournie comme **direction, pas comme cible** : le designer
     a autorité pour la faire évoluer.
   *(Rien de nouveau à produire : c'est un repère explicite sur ce que le designer consommera.)*

## Vérification avant écriture

- **Pré-constitution bien formée**, dérivée du product brief, du glossaire, du
  project-frame et des contraintes (traçable à ces sources).
- **Briefs présents et complets** dans le repo cible.
- **Spec index** reflétant le découpage arbitré.
- **Plan de séquencement produit** (`/speckit.constitution` puis `/speckit.specify`),
  ordonné par dépendances.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.pre_constitution.path` (`factory-docs/work/pre-constitution.md`) et
  `.status = "generated"`.
- `phase = "ready"`.
- `updated_at`.

## Frontière des artefacts

Documents de travail (vision, glossaire, pré-constitution) → restent côté
workspace `factory-docs/`. Artefacts de fabrication (briefs, spec index) →
markdown dans le repo SpecKit. La **constitution finale** est produite par SpecKit
à partir de la pré-constitution. Ce skill **est** la matérialisation de cette
frontière.

## Règles invariantes appliquées ici

- **Pré-requis « prêt pour SpecKit ».** Pas de handoff tant que le verdict n'est pas
  vert — vérifié en silence, jamais annoncé comme « porte ».
- **Ne pas inventer.** La pré-constitution dérive des artefacts ; aucun principe
  fabriqué, un manque se tranche en session, jamais écrit ni marqué.
- **Deux altitudes de validation.** Le handoff prépare la validation par feature
  (`/speckit.clarify`), il ne la porte pas.
- **Skill indépendant.** Pré-requis et mise à jour via le manifeste.

Étape suivante : en **Factory complète**, le pack continue vers `/architecte:architecte-init` (architecte → designer → assembleur produit la constitution finale convergée et fait le handoff SpecKit) ; en **cadrage autonome**, enchaîne directement `/speckit.constitution` puis les `/speckit.specify` dans l'ordre du plan.
