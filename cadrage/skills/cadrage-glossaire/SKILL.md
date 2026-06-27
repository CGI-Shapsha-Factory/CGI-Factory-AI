---
name: cadrage-glossaire
description: Construit et valide le glossaire du langage ubiquitaire, terme par terme.
---

# cadrage-glossaire

Construit le langage ubiquitaire : le vocabulaire du client, figé dans ses mots,
sourcé, sans dérive. C'est le garde-fou qui empêche deux personnes de parler du
même mot avec deux sens différents.

## Objectif

Produire et maintenir un **glossaire sourcé et sans conflit**, qui sert de
référence sémantique à toute la suite du pipeline (vision, découpage, briefs).

## Entrée

- `factory-docs/work/capture-brute.md` (section 5, termes métier candidats,
  et le reste de la matière).
- `factory-docs/work/product-brief.md` si présent (termes mobilisés par la
  vision).
- `factory-docs/work/glossaire.md` existant, pour le mode **incrémental**.

Gabarit de sortie : `factory-docs/templates/glossaire.md` (copie installée par cadrage-init).

## Porte d'entrée

**`artifacts.capture_brute` existe** dans le manifeste. Sinon, **refuse d'agir**
et oriente vers `cadrage-extraction`.

## Procédure

1. **Collecter les termes candidats** depuis la capture (section 5 en priorité,
   puis tout terme métier récurrent dans la matière) et la vision.
2. **Définir chaque terme dans les mots du client.** La définition reprend la
   formulation de la source, elle ne la traduit pas en jargon technique. Joindre
   la **source** (page / fichier + repère).
3. **Statut.** Tout terme nouveau est au statut **`proposé`**. Le passage à
   `validé` est une décision humaine (le client ou l'expert métier confirme) — le
   skill ne valide jamais un terme de lui-même.
3b. **Marquer `structurant`.** Un terme est `structurant = oui` s'il est mobilisé
   par la vision produit (`product-brief.md`) **ou** sert de nom / frontière d'un
   use case du découpage (`spec-index.md`) ; sinon `non`. C'est ce qui rend la gate
   `glossary_validated` mécanique.
4. **Contrôle de dérive.** Si un terme apparaît avec **deux définitions
   divergentes** selon les sources ou interlocuteurs : ne pas en choisir une,
   **signaler le conflit** en section « Ambiguïtés et conflits », avec les deux
   sources, et marquer `[À VALIDER]`. Jamais de définition dupliquée et
   silencieusement divergente.
5. **Terme sans définition captée.** Le lister en « Termes candidats non
   définis », marqué `[À VALIDER]`. Ne pas inventer de définition.
6. **Mode incrémental.** Si un glossaire existe : conserver les termes `validé`
   tels quels, ajouter les nouveaux candidats, et signaler toute nouvelle source
   qui contredirait une définition existante (conflit, pas écrasement).
7. **Afficher le glossaire en session, puis valider terme par terme (corr #9).**
   Une fois le glossaire généré et écrit dans `factory-docs/work/glossaire.md` :
   - **Afficher le glossaire dans le chat sous forme de tableau en français**
     (terme, définition dans les mots du client, source) — en langage clair, sans
     exposer de nom de colonne du manifeste ni d'identifiant technique
     (cf. `references/ux-conventions.md`).
   - **Valider terme par terme via la boucle interactive**
     (cf. `references/interactive-loop.md`) : **un terme à la fois**, et pour
     chacun trois options — (1) **valider** la définition proposée, (2)
     **modifier** (l'utilisateur reformule, on applique la correction
     immédiatement dans l'artefact), (3) **passer pour l'instant** (le terme reste
     `proposé` / `[À VALIDER]` et demeure un point ouvert). **Attendre la réponse**
     avant de passer au terme suivant.
   - **Appliquer les changements demandés tout de suite** : un terme validé par
     l'utilisateur passe `proposé → validé` (décision humaine, `src:
     atelier/utilisateur`) ; une reformulation remplace la définition et garde la
     source.
   - **Ne jamais inventer ni trancher** : aucune définition fabriquée, aucun
     conflit résolu par le skill. Un terme passé reste un trou.
   - À la fin, **proposer de continuer vers l'étape suivante** (le découpage).

### Structure de `glossaire.md`

Conforme à `factory-docs/templates/glossaire.md` : table (terme, définition dans les
mots du client, source, `structurant`, statut), section « Ambiguïtés et conflits
signalés », section « Termes candidats non définis ».

## Porte de sortie

Avant d'écrire le manifeste, vérifier :
- **Chaque terme a une définition ET une source.** Aucun terme orphelin de l'une
  ou de l'autre (sinon il va en « candidats non définis » marqué `[À VALIDER]`).
- **Les ambiguïtés et conflits sont signalés**, pas tranchés.
- **Aucune définition dupliquée divergente** — c'est le contrôle de dérive, il
  doit passer.

## Réjeu incrémental (idempotence)

Rejoué sur des entrées mises à jour — dont les retours de démonstrateur — ce
skill **met à jour le glossaire en place** :
- **Préserve** les termes au statut `validé` et leurs définitions.
- **Fusionne par identité de terme** : un terme déjà présent est mis à jour, pas
  dupliqué.
- **Applique** les corrections, **retire** les marqueurs résolus, **signale** les
  termes nouveaux.
- **N'écrase jamais en silence une définition contredite** : si un retour
  invalide une définition acquise, le terme est marqué `[REMIS EN CAUSE]` avec la
  raison et son ancienne définition conservée, pour arbitrage humain — règle
  « capter et invalider ». Un conflit n'est jamais tranché par le skill.

Aucune duplication. Recompte `terms` / `validated_terms` sur l'état réconcilié.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.glossaire.terms = <nombre total de termes>`.
- `artifacts.glossaire.validated_terms = <nombre de termes au statut validé>`.
- `definition_of_ready.glossary_validated = true` **si et seulement si** tous les
  termes marqués `structurant = oui` (mobilisés par la vision ou servant de nom /
  frontière d'un use case du découpage) sont au statut `validé`. Les termes non
  structurants n'empêchent pas la gate. Tant qu'un terme structurant reste
  `proposé`, c'est `false`. Le skill ne force jamais cette porte.
- `validation_points[]` : ajouter les conflits et termes non définis, `status =
  "open"`, `raised_by = "glossaire"`.
- `updated_at` à l'horodatage courant.

## Règles invariantes appliquées ici

- **Marquer, ne pas inventer.** Aucune définition fabriquée ; les termes non
  définis et les conflits sont marqués, jamais comblés.
- **Proposer, ne pas décider.** Le passage `proposé → validé` est humain. Le
  skill ne valide pas, et `glossary_validated` ne s'allume pas tout seul.
- **Skill indépendant.** Porte d'entrée et mise à jour via le manifeste.

Étape suivante : `/cadrage:cadrage-decoupage` — découper la vision en use cases de valeur une fois le vocabulaire figé.
