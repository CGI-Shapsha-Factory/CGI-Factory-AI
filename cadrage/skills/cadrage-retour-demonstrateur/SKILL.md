---
name: cadrage-retour-demonstrateur
description: Ingère le retour client sur la maquette et propage les corrections.
---

# cadrage-retour-demonstrateur

Le pivot de la boucle. Transforme un retour client sur la maquette en corrections
propagées : des points résolus, des acquis remis en cause, des artefacts à
rejouer, des points neufs. C'est la variante d'entrée typée « retour de
démonstrateur » de l'ingestion.

## Objectif

Faire **converger** la cadrage à partir des réactions du client au
démonstrateur, en distinguant ce qui **complète** de ce qui **contredit**.

## Entrée

- Le **transcript de retour**, déclaré comme source de type `retour` (retour de
  démonstrateur) — distinct d'un transcript d'atelier classique.
- Le registre `validation_points` du manifeste (points ouverts à confronter).
- L'état `demonstrateur` du manifeste (`current_version`, `external_ref`).

## Pré-requis (vérification silencieuse)

**Un retour de démonstrateur est disponible** (une source de type `retour` est
déclarée). Sinon, indiquer en clair qu'il faut d'abord un transcript de retour, sans
exposer de mécanique interne de pré-requis.

## Traitement — capter ET invalider

1. **Rapprocher.** Pour chaque réponse du client, retrouver le(s) point(s)
   ouvert(s) correspondants dans `validation_points`. Marquer `answered`,
   consigner la réponse dans `answer`. Un point **non couvert** par le retour
   **reste `open`** — jamais comblé.
2. **Détecter les invalidations.** Un élément **déjà capté** (vision, glossaire,
   découpage) que le client **remet en cause** au vu de la maquette : créer / mettre
   à jour un `validation_point` de type `contradiction`, statut `invalidated`,
   pointant l'artefact et l'élément concerné. **Ne pas écraser** l'acquis ni le
   garder en silence : il sera marqué `[REMIS EN CAUSE]` dans son artefact au
   réjeu (voir étape 3).
3. **Marquer les artefacts affectés à rejouer.** Le skill **ne réécrit pas
   lui-même** vision / glossaire / découpage (skills indépendants, pas
   d'orchestrateur). Il identifie les artefacts touchés et **recommande
   explicitement** de relancer les skills idempotents concernés
   (`cadrage-vision`, `cadrage-glossaire`, `cadrage-decoupage`), qui
   appliqueront corrections et `[REMIS EN CAUSE]` en place (bloc idempotence).
4. **Faire émerger les nouveaux points.** Toute nouvelle question ou souhait né du
   retour → nouveau `validation_point` (`open`), qui repart vers
   `cadrage-clarification`.

## Vérification

- Les **points adressés** par le client sont `answered` dans le registre, avec
  leur réponse.
- Les **invalidations** sont `invalidated` et signalées (jamais d'écrasement
  silencieux).
- Les **artefacts affectés** sont identifiés et le réjeu des skills idempotents
  est recommandé (pas de mise à jour à l'aveugle).
- Les **nouveaux points** sont inscrits au registre, `open`.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `sources[]` : ajout du transcript de retour (`type = "retour"`).
- `validation_points[]` : résolutions (`answered`), invalidations (`invalidated`),
  nouveaux points (`open`).
- `demonstrateur.iterations[]` : met à jour l'itération courante avec les compteurs
  `resolved`, `invalidated`, `new_points`, et `feedback_source`.
- **Ne touche pas** `demonstrateur.client_validated` (geste humain) — **et ce geste exige une
  maquette réelle** : `client_validated` ne peut passer à vrai **que si `demonstrateur.external_ref`
  est non nul** (une maquette a été générée et référencée). Une validation **verbale** (« tout est
  ok ») **sans maquette référencée** ne converge PAS : **demander d'abord la référence de la
  maquette** (lien Claude Design) avant d'enregistrer la validation. Pas de maquette → pas de
  convergence. **Aucune validation fantôme.**
- `updated_at`.

## Règles invariantes appliquées ici

- **Capter ET invalider.** La nouveauté de la boucle : le skill sait remettre en
  cause un acquis, pas seulement ajouter. Sinon la cadrage accumule des couches
  contradictoires au lieu de converger.
- **Marquer, ne pas inventer.** Un point non couvert reste ouvert.
- **Proposer, ne pas décider.** Le skill signale les contradictions ; l'humain
  tranche (en réjeu / revue), et le client valide la maquette.
- **Skill indépendant.** Il propage via le registre et recommande les réjeux ; il
  n'orchestre pas les autres skills.

Étape suivante : `/cadrage:cadrage-clarification` — regrouper les points résolus, contredits et neufs en une liste à reboucler.
