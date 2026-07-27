---
name: cadrage-glossaire
description: Construit et valide le glossaire du langage ubiquitaire du projet, validé en bloc.
---

# cadrage-glossaire

Construit le **langage ubiquitaire du projet** : les termes qu'on utilisera tout
au long de la construction du produit. C'est la référence qui fixe **le mot à
employer** ("Dossier", "Note juridique", "Paralegal") pour qu'on ne parle
jamais d'un même concept avec deux mots différents.

## Objectif

Produire et maintenir un **glossaire des termes du projet** : les **entités et
concepts métier autour desquels le produit sera construit**. Il sert de référence
sémantique à toute la suite (vision, découpage, briefs) et de vocabulaire de
référence au développement.

**Ce qu'on retient / ce qu'on exclut.**
- **Retenir** : les termes du **domaine** qui deviendront des concepts du produit -
  entités, objets manipulés, rôles utilisateurs, actions métier (ex. "Dossier",
  "Note juridique", "Paralegal", "Réponse sourcée").
- **Exclure** : les **acronymes, outils et systèmes existants** qui décrivent le
  contexte ou l'infrastructure et **ne seront pas des composants du produit**
  (ex. "GED", "GED maison", "SharePoint", noms de logiciels en place). Ils ne
  font pas partie du langage de construction.

## Entrée

- `cadrage-out/capture-brute.md` (section 5, termes métier candidats,
  et le reste de la matière).
- `cadrage-out/product-brief.md` si présent (termes mobilisés par la
  vision).
- `cadrage-out/glossaire.md` existant, pour le mode **incrémental**.

Gabarit de sortie : `.factory/cadrage/glossaire.md` (copie installée par cadrage-init).

## Pré-requis (vérification silencieuse)

`artifacts.capture_brute` existe dans le manifeste. Sinon, indiquer en clair qu'il
faut d'abord faire l'extraction, sans afficher de "porte".

## Porte de régénération (relance)
Avant toute (re)génération, appliquer `references/regeneration-gate.md`. Si les sorties **de ce
skill** existent déjà, proposer le choix **Repartir de zéro** (supprimer puis générer à neuf,
`version: 1`) ou **Garder les deux (versionner)** (archiver l'existant sous `_archives/`, régénérer
au nom canonique en `version: N+1`) et **attendre** le choix. Premier passage (rien n'existe) :
générer directement, sans porte.

## Procédure

1. **Collecter les termes du projet** depuis la capture (section 5 en priorité,
   puis tout terme métier récurrent dans la matière) et la vision. **Filtrer** :
   ne garder que les **termes du domaine** qui deviendront des concepts du produit ;
   **écarter** les acronymes / outils / systèmes existants (GED, SharePoint...) qui
   décrivent le contexte et ne seront pas des composants (cf. "Ce qu'on retient /
   ce qu'on exclut").
2. **Définir chaque terme dans les mots du client.** La définition reprend la
   formulation de la source, elle ne la traduit pas en jargon technique. **Ne pas
   écrire de provenance** (ni horodatage, ni `(src: ...)`).
3. **Contrôle de dérive.** Si un terme apparaît avec **deux sens divergents** : ne
   pas trancher en silence. Le poser **avec `AskUserQuestion`** au moment de la validation en
   bloc - les **deux sens** en options, il choisit -, sans persister de marqueur.
4. **Mode incrémental.** Si un glossaire existe : conserver les définitions déjà
   validées, ajouter les nouveaux termes, et signaler toute nouvelle source qui
   contredirait une définition existante (`[REMIS EN CAUSE]`, pas écrasement).
5. **Afficher le glossaire en session, puis valider EN BLOC.**
   Une fois le glossaire généré et écrit dans `cadrage-out/glossaire.md` :
   - **Afficher le glossaire dans le chat sous forme de tableau en français**
     (terme, définition dans les mots du client) - en langage clair, sans exposer
     de nom de colonne du manifeste ni d'identifiant technique
     (cf. `references/ux-conventions.md`).
   - **Demander une seule validation pour l'ensemble avec `AskUserQuestion`** : "Ce glossaire te
     convient ?" - deux options, "je valide tout" (recommandé) et "des termes sont à corriger ou
     à retirer" ; la saisie libre sert à nommer directement ces termes.
     **Ne pas valider terme par terme.** S'il y a une ambiguïté de sens, la poser ensuite
     **avec `AskUserQuestion`** (les deux sens en options) - **un appel par sens ambigu**,
     jamais plusieurs questions dans le même appel.
   - **Appliquer les corrections demandées tout de suite**, puis marquer l'ensemble
     `validé` sur l'accord de l'utilisateur (décision humaine).
   - **Ne jamais inventer** une définition. À la fin, **proposer de continuer vers
     l'étape suivante** (le découpage).

### Structure de `glossaire.md`

Conforme à `.factory/cadrage/glossaire.md` : table (terme, définition dans les
mots du client, statut). **Pas de colonne source ni `structurant`**, pas de section
"oui/non". Une ambiguïté de sens se tranche en session, elle n'est pas persistée
comme conflit ouvert.

## Vérification avant écriture

Avant d'écrire le manifeste, vérifier :
- **Chaque terme retenu a une définition.** Pas de terme orphelin (sinon on le retire).
- **Aucun acronyme / outil de contexte** n'a survécu au filtre (GED, SharePoint...).
- **Aucune `(src:)` ni horodatage** dans l'artefact.

## Réjeu incrémental (idempotence)

> **Distinction avec la porte de régénération.** Ce réjeu **incrémental** (fusion ciblée de
> corrections amont, en place) est un flux distinct de la **relance complète** : il n'ouvre **pas**
> la porte de régénération. Celle-ci ne s'ouvre que pour une **régénération intégrale** du document
> demandée par l'utilisateur (cf. `references/regeneration-gate.md`).

Rejoué sur des entrées mises à jour - dont les retours de démonstrateur - ce
skill **met à jour le glossaire en place** :
- **Préserve** les termes déjà validés et leurs définitions.
- **Fusionne par identité de terme** : un terme déjà présent est mis à jour, pas
  dupliqué.
- **Applique** les corrections, **signale** les termes nouveaux.
- **N'écrase jamais en silence une définition contredite** : si un retour
  invalide une définition acquise, le terme est marqué `[REMIS EN CAUSE]` avec la
  raison et son ancienne définition conservée, pour relecture humaine.

Aucune duplication. Recompte `terms` / `validated_terms` sur l'état réconcilié.

> Ces règles de fusion sont aussi **exécutées inline** par `cadrage-retour-client`
> (mode projet), qui applique directement les décisions tranchées en session dans
> le glossaire. Ce bloc reste la source de vérité des règles.

## Passe d'attaque (avant de conclure)

Avant la mise à jour du manifeste, dérouler la passe d'attaque commune - protocole complet dans
`references/attaque-protocole.md` (périmètre, fan-out, consolidation, vérification, boucle de
questions, règles de correction). Résumé d'exécution :

1. **Attaquer.** Dispatcher des sous-agents (`agentType: "attacker-cadrage"`) sur le périmètre
   ci-dessous : un seul agent par défaut ; contenu volumineux -> 2 à 4 lots en **un seul
   message** (appels parallèles), chaque lot recevant aussi la base amont en entier. Chaque
   agent ne reçoit **que des fichiers** (jamais le fil ni les décisions de la session : le
   regard neuf est le mécanisme). Les agents relisent tout et renvoient leurs constats
   structurés ; ils attaquent, ils ne corrigent rien.
2. **Consolider et vérifier.** Fusionner les constats en un rapport unique de session
   (dédoublonné, trié par gravité), **jamais persisté, jamais montré en liste à
   l'utilisateur** ; puis vérifier chaque constat contre le fichier (la citation existe, le
   point n'est pas déjà résolu ni déjà tranché en séance) - constat invérifiable = écarté sans
   bruit.
3. **Résoudre un par un.** Pour chaque constat retenu : **une seule question ouverte en prose**
   dans le fil (ancrée sur les mots du projet, un point par message, jamais de liste de
   constats), attendre la réponse, appliquer la correction **en place** selon les règles de
   fusion du skill ("on garde tel quel" est une réponse légitime : aucune modification), puis
   passer au constat suivant. Aucun constat retenu laissé sans issue explicite ; une seule
   passe, pas de re-attaque après corrections.

Périmètre de cette passe :
- Sortie du skill : `cadrage-out/glossaire.md`.
- Base amont : `cadrage-out/capture-brute.md` et `cadrage-out/product-brief.md` (terme employé
  absent du glossaire, définition en décalage avec la matière, deux sens pour un même terme).
- Les corrections issues de la passe sont des décisions de l'utilisateur : elles ne remettent
  pas en cause la validation en bloc déjà donnée.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.glossaire.terms = <nombre total de termes>`.
- `artifacts.glossaire.validated_terms = <nombre de termes validés>`.
- `definition_of_ready.glossary_validated = true` une fois que l'utilisateur a
  **validé le glossaire en bloc** (décision humaine). Tant que la validation n'a pas
  eu lieu, c'est `false`. Le skill ne force jamais cette validation de lui-même.
- `updated_at` à l'horodatage courant.

> **Silencieux - jamais annoncé.** Ne **jamais** dire à l'utilisateur que le manifeste est mis à jour,
> ni citer un nom de champ ou une valeur `true`/`false` (interdit : "Manifeste à jour : ...,
> glossary_validated: true", toute liste `champ: valeur`). Confirmer seulement, en clair, **ce qui a
> été produit** ("le glossaire est validé") + la prochaine étape (cf. `references/ux-conventions.md`).

## Règles invariantes appliquées ici

- **Termes du projet, pas le contexte.** On retient le vocabulaire de construction
  du produit, on écarte les outils/acronymes de l'existant.
- **Ne pas inventer.** Aucune définition fabriquée.
- **Validation en bloc, humaine.** L'utilisateur valide l'ensemble en un échange ;
  `glossary_validated` ne s'allume pas tout seul.
- **Contenu, pas provenance.** Aucune `(src:)` dans l'artefact.

Étape suivante : `/cadrage:cadrage-decoupage` - découper la vision en use cases de valeur une fois le vocabulaire figé.
