---
name: rapport-de-validation
description: Assemble le rapport de recette tracé exigence par exigence, trie chaque écart avec le testeur (anomalie, évolution ou critère flou, renvoi vers les skills maintenance), recueille le verdict humain de la porte de recette et produit le rapport en PDF.
---

# rapport-de-validation

Bras "restitution et porte" de la validation fonctionnelle : croise le plan de test et les
résultats d'exécution en un **rapport de recette tracé exigence par exigence**, trie chaque
écart **avec le testeur** (bug, spécification en cause, ou critère flou), et soumet le
**verdict de la porte de recette** à la validation humaine. **Le skill rapporte et oriente ; le
testeur est juge et valideur.**

## Objectif
Produire `validation-out/<feature>/rapport-de-validation.pdf` - un **document présentable**
(A4 paysage : verdict, chiffres clés, matrice critère -> cas -> verdict -> preuve -> décision,
écarts détaillés avec leur capture, bloc de signature) - et inscrire le verdict humain dans ce
rapport et dans Linear.

Le skill **n'écrit ni HTML ni CSS** : il assemble les **données** du rapport dans
`.factory/validation/rapport-<feature>.json` (mécanique cachée, git-ignorée, régénérable),
puis `scripts/build_rapport_pdf.py` les met en page avec le gabarit
`rapport-de-validation.html`. Toute la mise en forme vit dans le gabarit, jamais dans la
session.

## Pré-requis (vérification silencieuse)
- Le plan existe (`validation-out/<feature>/plan-de-test.md`) et au moins un fichier de
  résultats existe (`validation-out/<feature>/resultats/execution-*.md`). **Sinon : refuser en
  nommant le fichier manquant, puis - sans jamais s'arrêter là - poser une question
  `AskUserQuestion` avec les issues réellement praticables** (cf. la règle "jamais de
  cul-de-sac" de `references/interactive-loop.md`), établies à partir de ce qui existe
  vraiment dans `validation-out/` et `specs/` :
  - une feature a déjà son plan mais aucun résultat -> "jouer l'exécution de <feature>"
    (`/validation:execution-validation`), en premier avec la mention "(recommandé)" ;
  - une feature n'a pas encore de plan -> "écrire le plan de test de <feature>"
    (`/validation:plan-de-validation`) ;
  - une autre feature a bien ses deux fichiers -> "assembler plutôt le bilan de <feature>",
    et le skill reprend son cours sur celle-là ;
  - rien n'existe encore dans `validation-out/` -> une option par feature livrée, la plus
    pertinente à démarrer en premier.
- S'il y a plusieurs fichiers de résultats, demander lequel fait foi **avec `AskUserQuestion`**
  (une option par fichier, chacune identifiée par son **outil et sa version** - lus dans le nom
  `execution-<outil>-<NN>.md` - la version la plus haute en premier avec la mention
  "(recommandé)", accompagnée de sa synthèse chiffrée).
- `specs/<feature>/spec.md` accessible (pour citer les critères dans le tri des écarts).
- Le traitement des écarts passe par le plugin maintenance : si le bloc `maintenance` du manifeste
  manque, signaler qu'il faudra lancer `/maintenance:maintenance-init` avant de créer le premier
  ticket (on peut quand même assembler le rapport).
- **Le rendu PDF a besoin de Chrome (ou Chromium, ou Edge) installé.** Ne **jamais** bloquer
  là-dessus en début de skill : le tri des écarts et le verdict se font d'abord ; l'absence de
  navigateur ne se traite qu'au moment du rendu (cf. Étape 4).

## Procédure

### Étape 1 : assembler les données de la matrice
Une entrée **par critère** du plan, dans l'ordre du plan : **ce qui est vérifié** (la phrase
reprise de la vue d'ensemble du plan, jamais une référence de spécification nue), le cas de
test, le verdict de l'exécution, la preuve, la **Source** (référence compacte) et la décision.
Aucun critère ne disparaît : un cas absent des résultats apparaît "non exécuté" et compte comme
un écart à trier.

Écrire ces données dans `.factory/validation/rapport-<feature>.json` (créer le dossier s'il
manque). Structure attendue par le script - les champs vides sont omis, jamais inventés :

```json
{
  "projet": "(nom du projet, depuis le manifeste)",
  "feature": { "numero": "001", "intitule": "(intitulé de la feature)",
               "sous_titre": "(facultatif, sinon dérivé)" },
  "recette": { "date": "JJ-MM-AAAA", "environnement": "(URL testée)",
               "outil": "(outil d'exécution, en toutes lettres)",
               "outil_court": "(2 ou 3 mots, pour l'en-tête)",
               "fichier_resultats": "resultats/execution-<outil>-<NN>.md",
               "executions_confirmatives": ["(les autres exécutions au même résultat)"],
               "plan": "plan-de-test.md", "specification": "specs/<feature>/spec.md",
               "testeur": "(nom, ou vide si le visa est manuscrit)" },
  "chiffres": { "criteres": 0, "cas": 0, "ok": 0, "ecarts": 0, "non_testable": 0 },
  "synthese": ["(un paragraphe factuel)", "(...)"],
  "encadre_synthese": "(facultatif : une phrase de contexte)",
  "encadre_matrice": "(facultatif : où sont rangées les preuves)",
  "cas": [ { "ref": "TC-001-001", "phrase": "(ce qui est vérifié)",
             "verdict": "OK | KO | NON TESTABLE | NON EXECUTE",
             "preuve": "(nom du fichier de capture)", "source": "(référence compacte)",
             "decision": "(vide, ou Anomalie / Evolution / Clarifié / Sans suite)" } ],
  "ecarts": [ { "ref": "TC-001-009", "titre": "(le comportement attendu, en une phrase)",
                "nature": "Anomalie", "attendu": "(...)", "constate": "(...)",
                "criteres_echec": "(les critères cités)", "nature_motif": "(pourquoi cette nature)",
                "diagnostic": "(console, réseau, reproductibilité)", "suite": "(le ticket ou la décision)",
                "preuve_image": "resultats/preuves-<outil>-<NN>/<capture>.png",
                "legende": "(ce que montre la capture)" } ],
  "verdict": { "valeur": "(rempli à l'Étape 3, jamais avant)", "note": "(...)",
               "aside_libelle": "Réserves ouvertes", "aside_valeur": "(...)" }
}
```

Dans les textes, seules trois marques sont interprétées : `**gras**`, `` `code` `` et le retour
à la ligne. **Aucune balise HTML** : le script échappe tout le reste.

Si `validation-out/<feature>/rapport-de-validation.pdf` existe déjà, poser la **porte de
régénération avec `AskUserQuestion`** avant d'écrire, en nommant le fichier - **deux options
explicites, la saisie libre restant ouverte** (le "Other" de l'outil) : **repartir de zéro**
(supprimer le rapport existant puis regénérer au nom canonique) ou **garder les deux
(versionner)** (archiver l'existant sous
`validation-out/<feature>/_archives/rapport-de-validation-v<N>.pdf`, `N` = index croissant, puis
regénérer au nom canonique, qui porte toujours la version la plus récente). La **saisie libre**
est la troisième voie : le testeur précise une autre consigne (renommer l'existant, garder tel
quel et s'arrêter) et le skill **l'applique** ; **jamais d'écrasement ni de suppression sans un
geste explicite** (une consigne non actionnable se re-demande).

### Étape 2 : trier chaque écart avec le testeur (un par un)
Pour chaque verdict KO, NON TESTABLE ou non exécuté : présenter le constat factuel (constaté vs
attendu, preuve) face au critère cité, puis laisser le testeur trancher la **nature avec
`AskUserQuestion`** - les quatre options ci-dessous, celle qui paraît la plus juste en premier
avec la mention "(recommandé)" et la raison dans sa description (cf.
`references/interactive-loop.md` ; plusieurs écarts peuvent être regroupés dans un même appel,
une question par écart, chaque question rappelant l'identifiant du cas et le constat en une
ligne). Les natures possibles (cf. `references/regles-validation.md`) :
- **Anomalie** (la spécification est bonne, le logiciel ne la respecte pas) -> "Veux-tu créer
  l'anomalie dans Linear ?" - question posée **avec `AskUserQuestion`**. Si oui : préparer le contenu (comportement attendu depuis le
  critère, comportement constaté et étapes de reproduction depuis le déroulé effectif,
  critère de recette en échec) et enchaîner sur `/maintenance:creation-anomalie` avec ce contenu
  pré-rempli - la création passe par **sa** porte (complétude, rattachement au ticket
  Feature, confirmation humaine), jamais en direct d'ici.
- **Évolution** (le logiciel respecte sa spécification, mais elle est fausse ou incomplète au
  regard du vrai besoin) -> "Veux-tu tracer cette évolution ?" - question posée **avec
  `AskUserQuestion`**. Si oui : orienter vers
  `/maintenance:creation-evolution` (geste du PO, avec sa proposition d'écart de spécification) -
  jamais de création automatique.
- **Critère flou** (NON TESTABLE) -> demander **avec `AskUserQuestion`** : clarifier la lecture
  observable en session (elle s'écrit dans le plan pour la prochaine exécution), ou tracer un
  ticket Linear de suivi sur la feature (sous-ticket du ticket `Feature`, **sans label de recette** - cf.
  `references/regles-validation.md`, section Linear).
- **Sans suite** : le testeur peut décider de ne pas donner suite ; sa décision s'écrit telle
  quelle dans le rapport.
Chaque décision prise alimente les données : la colonne `decision` du cas concerné, et une
entrée dans `ecarts` (avec l'identifiant Linear natif du ticket créé, s'il y en a un). Un écart
que le testeur laisse de côté reste **sans décision** : on le lui rappelle oralement, et la
porte de recette n'est pas franchissable tant qu'il en reste.

### Étape 3 : la porte de recette (verdict humain)
Quand tous les écarts sont triés : afficher le récapitulatif final (la matrice en tableau
court + la synthèse en prose) et poser **la** question **avec `AskUserQuestion`** : "Quel est
ton verdict de recette pour cette feature ?" - trois options, "livraison validée", "validée
avec réserves" et "refusée", chacune décrite par ce qu'elle implique concrètement pour cette
feature (ce qui reste ouvert, ce qui repart en correction). Le verdict le plus cohérent avec
les résultats peut être placé en premier avec la mention "(recommandé)" et son argument dans la
description, mais **le skill ne prononce jamais le verdict lui-même** : il attend le choix.

Le verdict choisi, sa date et ses réserves (tickets Linear restant ouverts) s'écrivent alors
dans le bloc `verdict` des données. **Ce bloc n'est rempli que par ce geste** : tant que le
testeur n'a pas tranché, il reste vide et le script refuse de produire le PDF.

### Étape 4 : produire le PDF
Lancer le rendu déterministe :
```bash
python <plugin>/scripts/build_rapport_pdf.py manifest.json <feature>
```
Il écrit `validation-out/<feature>/rapport-de-validation.pdf` et affiche le nombre de pages.
**Lire sa sortie** : une ligne "attention" signale une capture introuvable ou une page qui
déborde (raccourcir le texte concerné ou baisser `lignes_par_page` dans les données, puis
relancer). Ne jamais annoncer un rapport livré sans que le script ait confirmé l'écriture.

Si le script échoue faute de navigateur : **le dire clairement**, laisser les données en place
(rien n'est perdu, le tri et le verdict sont déjà dedans), afficher ce qu'il faut installer, et
poser **avec `AskUserQuestion`** ce que le testeur veut faire - installer Chrome puis relancer
le rendu (en premier), ou reprendre plus tard. **Jamais de cul-de-sac.**

### Étape 5 : tracer dans Linear
Déposer un commentaire de synthèse sur le ticket `Feature` de la feature (résolu par le numéro
en tête de titre via `list_issues({team, label Feature})` ; `save_comment` avec le verdict, les
compteurs et le chemin du PDF). Le **statut** du ticket, lui, n'est **jamais déduit du
verdict** : poser une question `AskUserQuestion` - "laisser le statut tel quel" (en premier
avec la mention "(recommandé)") ou passer le ticket à l'un des états réellement disponibles,
une option par état pertinent résolu via `list_issue_statuses`. N'appliquer que sur ce choix
explicite, et vérifier l'état retourné (un état non résolu est ignoré en silence par Linear).
Si le MCP `linear-prism` est muet : le verdict reste dans le rapport, signaler que le
commentaire Linear attendra et afficher l'installation du MCP (section Linear de
`references/regles-validation.md`).

Le verdict ne s'écrit **jamais dans le manifeste** : le rapport committé voyage avec le repo,
l'avancement vit dans Linear.

## Vérification avant de conclure
Lancer le garde-fou déterministe et s'arrêter s'il échoue :
```bash
python <plugin>/scripts/check_validation.py manifest.json <feature>
```
(Pour la feature : plan présent et tracé, et si les données du rapport existent, le **PDF**
produit - le PDF n'étant écrit qu'après le verdict, sa présence atteste la porte de recette.)

## Règles invariantes
- **La validation détecte, la maintenance traite.** Aucune anomalie ni évolution n'est créée ici
  en direct : toujours via les skills maintenance et leurs portes.
- **Le tri d'un écart et le verdict sont humains.** Le skill propose et pré-remplit ; le
  testeur tranche. Pas de porte de recette tant qu'un écart n'est pas trié.
- **Le PDF n'existe qu'après le verdict.** On n'imprime pas un rapport dont la porte n'a pas
  été franchie ; le script refuse d'ailleurs de le faire.
- **Jamais de mise en forme écrite en session.** Le skill remplit des données ; le gabarit et le
  script font la mise en page. Ne jamais fabriquer de HTML, de CSS ni de commande Chrome à la
  main, et ne jamais retoucher le gabarit pour un rapport particulier.
- **Traçabilité totale** : aucun critère du plan n'est absent de la matrice.
- Manifeste silencieux, restitutions en prose, typographie humaine (cf.
  `references/ux-conventions.md`) - y compris dans les données du rapport : guillemets droits,
  tiret simple, "..." en trois points, jamais de flèche unicode ni de coche/croix.
- **Mécanique interne silencieuse** : ne jamais annoncer au testeur le fichier de données de
  `.factory/` (dossier caché, git-ignoré, sans intérêt pour lui) ; on lui confirme le PDF.
- **Toujours afficher la phrase "Étape suivante"** avec ses branches en fin d'exécution, en la
  cadrant sur le verdict qui vient d'être prononcé (cf. la section 5 de
  `references/ux-conventions.md`).
- **Jamais de cul-de-sac, et toute question passe par `AskUserQuestion`.** Fichier de résultats,
  nature de chaque écart, verdict de recette, changement de statut Linear, échec du rendu **et
  les réponses libres** (texte d'un constat, motif d'une réserve) - pour celles-ci, les options
  portent les formulations plausibles et la saisie libre reste ouverte. **Aucune question
  rédigée en prose dans le fil.** Un refus se termine par une question proposant les issues
  réellement praticables (cf. `references/interactive-loop.md`).

**Étape suivante : selon le verdict - livraison validée, `/validation:plan-de-validation` pour recetter la feature livrée suivante. Validée avec réserves ou refusée : `/maintenance:creation-anomalie` ou `/maintenance:creation-evolution` pour les écarts triés qui n'ont pas encore leur ticket, puis `/maintenance:correction-anomalie` (ou `/maintenance:realisation-evolution`) côté développeur, et enfin `/validation:execution-validation` pour rejouer les cas en échec et lever les réserves.**
