---
name: cadrage-vision
description: Synthétise la capture en un product brief (le quoi et le pourquoi).
---

# cadrage-vision

Deuxième étape de la ligne de production. Élève la capture brute à une vision
produit : le problème, les objectifs, le périmètre, les critères de succès. Le
quoi et le pourquoi, jamais le comment.

## Objectif

Produire un **product brief auto-portant de niveau produit**, lisible par un
comité, qui synthétise la capture sans la trahir et sans rien ajouter qui ne soit
dans la matière.

## Entrée

`cadrage-out/capture-brute.md` et `cadrage-out/project-frame.md`
(pour reprendre Q1 qui utilise, Q3 rôles, Q9 type de projet, ainsi que les réponses
produit de la découverte : Q14 problème et coût du statu quo, Q15 pourquoi maintenant,
Q17 signaux de succès - reprises comme **suggestions pré-remplies** des sections
Problème, Objectif business et Critères de succès, à confirmer en session, jamais
reposées à froid). Le gabarit de sortie
est `.factory/cadrage/product-brief.md` (copie installée par cadrage-init).

## Pré-requis (vérification silencieuse)

`artifacts.capture_brute` existe dans le manifeste (le fichier est présent).
Sinon, l'indiquer en clair et poser la suite **avec `AskUserQuestion`** - deux options,
"faire l'extraction d'abord" (recommandé) et "vérifier le dossier de travail" - sans
afficher de "porte".

## Porte de régénération (relance)
Avant toute (re)génération, appliquer `references/regeneration-gate.md`. Si les sorties **de ce
skill** existent déjà, proposer le choix **Repartir de zéro** (supprimer puis générer à neuf,
`version: 1`) ou **Garder les deux (versionner)** (archiver l'existant sous `_archives/`, régénérer
au nom canonique en `version: N+1`) et **attendre** le choix. Premier passage (rien n'existe) :
générer directement, sans porte.

## Procédure

1. **Lire** la capture brute, le `project-frame.md` (Q1/Q3/Q9 + Q14/Q15/Q17) et le manifeste.
2. **Remplir le product brief** section par section, en n'utilisant **que** la
   matière de la capture. **Aucune provenance écrite** (pas de `(src:)`, pas
   d'horodatage) ; un élément non soutenu par la matière est **omis** ou **demandé
   en session**, jamais marqué `[À VALIDER]`.
3. **Périmètre OUT (forcé non vide).** Lister les exclusions explicites de la
   capture. S'il n'y en a pas, **les faire trancher en session avec `AskUserQuestion`**. Pour une
   frontière de périmètre qui **engage vraiment la suite**, la poser comme un **fork de
   conception** (cf. `references/interactive-loop.md`) : deux options qui **nomment chacune leur
   coût** - "Exclure X du périmètre (ce que ça ferme, le risque)" contre "Garder X (le coût, le
   délai que ça ajoute)" -, la saisie libre pour une autre lecture. Pour des exclusions
   secondaires sans réel enjeu, deux exclusions plausibles suffisent, une par option.
   OUT ne doit jamais rester vide ; on n'y écrit que ce qui est confirmé.
4. **Critères de succès produit.** Traduire les objectifs en métriques d'usage
   (pas de code). Si une cible n'a pas été captée, écrire le critère et préciser
   en clair "cible à préciser à l'architecture" (pas de marqueur).
5. **Hypothèse produit initiale.** Formuler l'hypothèse centrale en précisant
   qu'elle **se valide par le prototype** (boucle démonstrateur), jamais comme
   acquise.
6. **Demander, ne pas inventer.** Tout élément essentiel absent de la capture est **posé en
   session avec `AskUserQuestion`** (deux options : la lecture recommandée et l'alternative
   crédible) ; s'il n'est pas tranché, il est **omis** (pas de marqueur, pas de section
   "Trous").

### Sections du product brief

Conformes à `.factory/cadrage/product-brief.md` : Problème, Objectif business,
Parties prenantes et rôles, Périmètre IN, Non-périmètre OUT (non vide),
Contraintes, Critères de succès produit, Hypothèse produit initiale.

## Vérification avant écriture

Avant d'écrire le manifeste, vérifier :
- **Toutes les sections présentes.**
- **Non-périmètre OUT non vide.**
- **Hypothèse produit** présentée comme à valider par le prototype, jamais validée.
- **Aucune `(src:)`, aucun `[À VALIDER]`** dans l'artefact ; un essentiel manquant
  a été posé en session (sinon omis).

### Direction produit tenue ?

La vision est complète quand les essentiels sont là : problème, objectif business,
au moins une partie prenante porteuse du besoin, périmètre IN non vide, OUT non
vide. Un essentiel manquant se **demande en session** ; tant qu'il manque, la
vision n'est pas complète.

## Réjeu incrémental (idempotence)

> **Distinction avec la porte de régénération.** Ce réjeu **incrémental** (fusion ciblée de
> corrections amont, en place) est un flux distinct de la **relance complète** : il n'ouvre **pas**
> la porte de régénération. Celle-ci ne s'ouvre que pour une **régénération intégrale** du document
> demandée par l'utilisateur (cf. `references/regeneration-gate.md`).

Rejoué sur des entrées mises à jour - typiquement une correction issue d'un
retour client (`cadrage-retour-client`) - ce skill **met à
jour le product brief en place**, il ne le régénère pas à l'aveugle :
- **Préserve** le contenu déjà validé ou inchangé.
- **Applique** les corrections venues des entrées mises à jour.
- **Pose en session** les éléments essentiels nouvellement manquants.
- **N'écrase jamais en silence un élément contredit** : un acquis remis en cause
  par un retour est marqué `[REMIS EN CAUSE]` avec sa raison, puis tranché par
  l'humain - jamais supprimé ni réécrit en douce.

Réconciliation par identité de section / de point : aucune duplication. Recalcule
`vision_complete` à partir de l'état réconcilié.

> Ces règles de fusion sont aussi **exécutées inline** par `cadrage-retour-client`
> (mode projet), qui applique directement les décisions tranchées en session dans
> le product brief. Ce bloc reste la source de vérité des règles.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.product_brief.status` (`draft` par défaut ; `validated` reste réservé
  à la validation humaine).
- `definition_of_ready.vision_complete = true` **si et seulement si** : les
  essentiels sont présents (problème, objectif business, partie prenante porteuse,
  IN non vide) **ET** OUT non vide **ET** critères de succès présents. Sinon `false`.
- `phase = "vision"` (si la phase courante est `extraction`).
- `updated_at` à l'horodatage courant.

> **Silencieux - jamais annoncé.** Ne **jamais** dire à l'utilisateur que le manifeste est mis à jour,
> ni citer un nom de champ ou une valeur `true`/`false` (interdit : "Manifeste à jour : phase: vision,
> vision_complete: true", toute liste `champ: valeur`). Confirmer seulement, en clair, **ce qui a été
> produit** + la prochaine étape (cf. `references/ux-conventions.md`).

## Livrable visuel

Le canvas vision produit (synthèse visuelle d'une page, lisible par un comité) se
génère dans Claude Design à partir du product brief. Le prompt prêt à coller est
dans `references/canvas-vision-prompt.md` (gabarit statique). Le prompt
effectivement utilisé est sauvegardé sous `cadrage-out/prompts/<NNN>-<JJ-MM>-canvas-vision.md`
et tracé dans `prompts[]` du manifeste. Le fichier sauvegardé ne contient **que le
corps du prompt** (le bloc de code du gabarit), sans titre/date/mode/version
(cf. `references/ux-conventions.md`). C'est un livrable de communication, pas
une porte - il n'altère pas les autres champs du manifeste.

## Règles invariantes appliquées ici

- **Demander, ne pas inventer.** OUT proposé est tranché en session, jamais
  présenté comme acté. Aucun objectif ou critère fabriqué. Pas de `(src:)`.
- **Hypothèse à éprouver, jamais validée.** Deux altitudes de validation : la
  direction produit se valide par le prototype, hors plugin.
- **Skill indépendant.** Pré-requis vérifié via le manifeste, pas via un
  orchestrateur.

Étape suivante : `/cadrage:cadrage-glossaire` - fixer le vocabulaire du projet porté par la vision avant le découpage.
