---
name: cadrage-demonstrateur-brief
description: Produit le prompt Claude Design de la maquette de validation (mode initial ou adaptatif).
---

# cadrage-demonstrateur-brief

Produit la **matière de travail** qui amorce ou fait évoluer le démonstrateur : un
prompt Claude Design. Le skill ne dessine rien ; il cadre ce que Claude Design
doit produire. Deux modes selon le moment de la boucle.

## Objectif

Donner un prompt prêt à coller dans Claude Design pour obtenir (mode initial) ou
faire évoluer (mode adaptatif) un démonstrateur qui sert à **valider la direction
produit avec le client**, pas à figer le design.

## Règle de calibrage — rendu professionnel

Le démonstrateur sert à **valider la direction produit avec le client** : il doit
**paraître fini et crédible**, comme un vrai produit — pas un wireframe. Le prompt
demande à Claude Design une **maquette propre et professionnelle** : vraie mise en
page, hiérarchie visuelle claire, espacements réguliers, contenu réaliste du domaine,
direction de marque violet sobre (#5336AB), sans emoji.

Ce **n'est pas** le design system définitif (il naît plus tard dans le plugin
`designer`) : on ne fige pas une charte exhaustive ni tous les composants. Mais le
rendu doit être **convaincant** — on valide la direction sur quelque chose qui a l'air
fini, pas sur un brouillon.

## Gabarit de référence

Le prompt s'appuie sur `references/demonstrateur-prompt.md` (gabarit statique, deux
variantes : initial et adaptatif). Le modèle **remplit tous les `<…>`** avec le
contenu réel tiré des entrées et produit un prompt **auto-portant** (Claude Design n'a
aucun contexte projet).

## Qualité du prompt à générer (consignes au modèle)

Un prompt médiocre donne une maquette médiocre. Pour produire un **prompt excellent** :
- **Lister explicitement les écrans à produire** (3 à 6), un par parcours clé du
  `spec-index.md`, avec pour chacun ce qu'on y fait.
- **Injecter du contenu réaliste du domaine** (libellés, noms, données plausibles tirés
  du `glossaire.md` et de la vision) — **jamais** de « lorem ipsum ».
- **Demander les états utiles** sur les écrans clés : contenu chargé, état vide (message
  + action), un cas d'erreur/chargement si pertinent.
- **Cadrer le style** : navigation persistante, hiérarchie typo, palette violet #5336AB
  sobre et aérée, responsive, ton conseil premium, aucun emoji.
- **Auto-portance** : tout le contexte nécessaire est dans le prompt ; aucune référence
  à un fichier ou au manifeste.

## Mode INITIAL (étape 3)

**Pré-requis (vérification silencieuse).** La vision est disponible (`product_brief`
existe). Le découpage fournit les parcours clés. Si la direction est claire, on
avance ; sinon on le dit en clair, sans exposer de mécanique interne de pré-requis.

**Entrée.** `cadrage-out/product-brief.md` et les parcours / activités utilisateur
du `cadrage-out/spec-index.md`.

**Sortie.** Un prompt Claude Design (variante **initial** du gabarit) pour un
**démonstrateur de validation de direction** : couvre les parcours clés (walking
skeleton + premiers use cases de valeur), matérialise le problème résolu et la valeur,
avec un **rendu propre et professionnel** (mise en page réelle, contenu réaliste,
direction de marque violet sobre #5336AB).

## Mode ADAPTATIF (étape 8b)

**Pré-requis (vérification silencieuse).** Un retour de démonstrateur a été ingéré
(`cadrage-retour-demonstrateur` a tourné ; `demonstrateur.iterations` contient
un retour récent) et la maquette courante est référencée
(`demonstrateur.external_ref`).

**Entrée.** L'état du démonstrateur courant (`demonstrateur.external_ref`,
`current_version`) et le transcript de retour, plus les `validation_points`
adressés.

**Sortie.** Un **prompt DELTA** (variante **adaptatif** du gabarit) : il référence
explicitement la maquette existante (« à partir de la maquette vX… »), décrit
**uniquement les changements** demandés par le client (écrans à corriger, parcours à
ajuster, éléments à retirer), et **préserve ce qui a été validé** (mise en page,
palette, niveau de finition). Pas de régénération à blanc — l'itération doit rester
rapide et ne pas casser l'acquis.

## Sauvegarde du prompt

Écrire le prompt dans `factory-prompts/<NNN>-<JJ-MM>-<nom>.md` où `NNN` est le
prochain numéro global (incrément du dernier `prompts[].n` du manifeste), `JJ-MM` la
date du jour, et `<nom>` le sujet (ex. `demonstrateur-initial`, `demonstrateur-delta-v2`).

**Le fichier sauvegardé ne contient QUE le corps du prompt prêt à coller** (le bloc de
code du gabarit, rempli) : **aucun titre, aucune ligne `Date : … | Mode : … | Version :
…`, aucun `---` d'en-tête** (cf. `references/ux-conventions.md`). La métadonnée (mode,
version, date, sujet) vit dans l'entrée `prompts[]` du manifeste, jamais dans le
fichier. L'utilisateur doit pouvoir ouvrir le fichier et tout copier sans rien nettoyer.

## Vérification (commune)

- Le prompt vise un **rendu propre et professionnel** (mise en page réelle, contenu
  réaliste, palette violet sobre), pas un wireframe.
- Le prompt est **auto-portant** : tout le contexte est dedans, aucun renvoi à un
  fichier.
- Mode initial : les **parcours clés sont couverts**, avec une liste d'écrans explicite.
- Mode adaptatif : le prompt est un **delta** référençant la maquette existante,
  **borné aux changements** du retour, sans repartir de zéro.
- Le fichier sauvegardé **ne contient que le prompt** (aucun titre/date/mode/version).
- Le prompt est **sauvegardé** sous `factory-prompts/` et tracé au manifeste.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- Ajoute une entrée `prompts[]` : `{ n, date, name, source: "demonstrateur-brief",
  path }` pointant le fichier sauvegardé.
- Ajoute / met à jour une entrée `demonstrateur.iterations[]` avec
  `brief_mode = "initial" | "adaptatif"`, `prompt_path` (le fichier sauvegardé)
  et, en adaptatif, `feedback_source` (réf du transcript de retour).
- **Ne touche pas** `demonstrateur.client_validated` (geste humain) ni
  `current_version` / `external_ref` (mis à jour par l'humain après génération de
  la maquette dans Claude Design).
- `updated_at`.

## Règles invariantes appliquées ici

- **Le plugin ne génère pas la maquette.** Il produit un prompt ; Claude Design
  produit la maquette.
- **Rendu professionnel, pas le design system final.** La maquette doit paraître
  crédible et finie pour valider la direction ; la charte exhaustive et les composants
  définitifs se figent plus tard, dans le plugin `designer`.
- **Fichier prompt propre.** Le fichier sauvegardé = corps seul, prêt à coller.
- **Proposer, ne pas décider.** Le prompt propose ; le client valide la maquette,
  hors plugin.
- **Skill indépendant.** Lit la vision / le retour et le manifeste, sans
  orchestrateur.

Étape suivante : `/cadrage:cadrage-retour-demonstrateur` — confronter la maquette au client puis ingérer son retour.
