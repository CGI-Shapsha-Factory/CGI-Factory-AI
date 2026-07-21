---
name: bilan-validation
description: Assemble le rapport de recette tracé exigence par exigence, trie chaque écart avec le testeur (anomalie, évolution ou critère flou, renvoi vers les skills maintenance), consolide les scénarios de non-régression et recueille le verdict humain de la porte de recette.
---

# bilan-validation

Bras "restitution et porte" de la validation fonctionnelle : croise le plan de test et les
résultats d'exécution en un **rapport de recette tracé exigence par exigence**, trie chaque
écart **avec le testeur** (bug, spécification en cause, ou critère flou), consolide les
scénarios rejouables de non-régression, et soumet le **verdict de la porte de recette** à la
validation humaine. **Le skill rapporte et oriente ; le testeur est juge et valideur.**

## Objectif
Produire `validation-out/<feature>/rapport-de-recette.md` (matrice critère -> cas -> verdict
-> preuve -> décision), `validation-out/<feature>/scenarios/TC-*.md` (non-régression), et
inscrire le verdict humain dans le rapport et dans Linear.

## Pré-requis (vérification silencieuse)
- Le plan existe (`validation-out/<feature>/plan-de-test.md`) et au moins un fichier de
  résultats existe (`validation-out/<feature>/resultats/execution-*.md`) ; sinon refuser en
  nommant le fichier manquant et renvoyer vers le skill amont.
- S'il y a plusieurs fichiers de résultats, prendre le plus récent et le confirmer au testeur
  (suggestion) ; il peut en désigner un autre.
- `specs/<feature>/spec.md` accessible (pour citer les critères dans le tri des écarts).
- Le traitement des écarts passe par le plugin maintenance : si le bloc `maintenance` du manifeste
  manque, signaler qu'il faudra lancer `/maintenance:maintenance-init` avant de créer le premier
  ticket (on peut quand même assembler le rapport).

## Procédure

### Étape 1 : assembler la matrice de traçabilité
Depuis le gabarit `.factory/validation/rapport-de-recette.md` : une ligne **par critère** du
plan (critère source -> cas de test -> verdict de l'exécution -> preuve). Aucun critère ne
disparaît : un cas absent des résultats apparaît "non exécuté" et compte comme un écart à
trier. Si un rapport existe déjà pour la feature, appliquer la porte de régénération
(repartir de zéro ou archiver sous `_archives/`). Écrire aussi la synthèse chiffrée, en prose.

### Étape 2 : trier chaque écart avec le testeur (un par un)
Pour chaque verdict KO, NON TESTABLE ou non exécuté (boucle interactive, cf.
`references/interactive-loop.md`), présenter le constat factuel (constaté vs attendu, preuve)
face au critère cité, proposer un tri en suggestion, et laisser le testeur trancher la
**nature** (cf. `references/regles-validation.md`) :
- **Anomalie** (la spécification est bonne, le logiciel ne la respecte pas) -> "Veux-tu créer
  l'anomalie dans Linear ?" Si oui : préparer le contenu (comportement attendu depuis le
  critère, comportement constaté et étapes de reproduction depuis le déroulé effectif,
  critère de recette en échec) et enchaîner sur `/maintenance:creation-anomalie` avec ce contenu
  pré-rempli - la création passe par **sa** porte (complétude, rattachement au ticket
  Feature, confirmation humaine), jamais en direct d'ici.
- **Évolution** (le logiciel respecte sa spécification, mais elle est fausse ou incomplète au
  regard du vrai besoin) -> "Veux-tu tracer cette évolution ?" Si oui : orienter vers
  `/maintenance:creation-evolution` (geste du PO, avec sa proposition d'écart de spécification) -
  jamais de création automatique.
- **Critère flou** (NON TESTABLE) -> proposer de clarifier la lecture observable en session
  (elle s'écrit dans le plan pour la prochaine exécution), ou de tracer un ticket Linear de
  suivi sur la feature (sous-ticket du ticket `Feature`, **sans label de recette** - cf.
  `references/regles-validation.md`, section Linear).
- **Sans suite** : le testeur peut décider de ne pas donner suite ; sa décision s'écrit telle
  quelle dans le rapport.
Chaque décision prise est reportée dans le rapport (colonne "Décision sur l'écart" + bloc
"Écarts et suites données", avec l'identifiant Linear natif des tickets créés). Un écart que
le testeur laisse de côté reste **sans décision** dans la matrice : on le lui rappelle
oralement, et la porte de recette n'est pas franchissable tant qu'il en reste.

### Étape 3 : consolider les scénarios de non-régression
Pour chaque cas **OK**, écrire `validation-out/<feature>/scenarios/TC-<feature>-<NNN>.md`
depuis le gabarit `.factory/validation/scenario-rejouable.md` : le **déroulé effectif** (tel
que joué), les préconditions et données, le résultat attendu observable - en langage naturel
auto-portant, rejouable par n'importe quel outil. Ne pas réécrire un scénario existant dont le
déroulé n'a pas changé. Lister les scénarios dans le rapport. C'est la bibliothèque que la
maintenance rejoue en non-régression (`realisation-evolution`, `correction-anomalie`).

### Étape 4 : la porte de recette (verdict humain)
Quand tous les écarts sont triés : afficher le récapitulatif final (la matrice en tableau
court + la synthèse en prose) et poser **la** question : "Quel est ton verdict de recette
pour cette feature - livraison validée, validée avec réserves, ou refusée ?" (suggestion
argumentée possible, mais **le skill ne prononce jamais le verdict lui-même**). Puis :
1. inscrire le verdict, la date et les réserves (tickets Linear restant ouverts) dans la
   section "Verdict de recette" du rapport - cette section n'existe remplie que par ce geste ;
2. **Linear** : déposer un commentaire de synthèse sur le ticket `Feature` de la feature
   (résolu par le numéro en tête de titre via `list_issues({team, label Feature})` ;
   `save_comment` avec le verdict, les compteurs et le chemin du rapport). Si le testeur
   souhaite aussi changer le statut du ticket, le faire **sur confirmation explicite
   seulement**, par le nom d'état résolu via `list_issue_statuses` et en vérifiant l'état
   retourné (un état non résolu est ignoré en silence par Linear). Si le MCP `linear-prism`
   est muet : le verdict reste dans le rapport, signaler que le commentaire Linear attendra
   et afficher l'installation du MCP (section Linear de `references/regles-validation.md`).
Le verdict ne s'écrit **jamais dans le manifeste** : le rapport committé voyage avec le repo,
l'avancement vit dans Linear.

## Vérification avant de conclure
Lancer le garde-fou déterministe et s'arrêter s'il échoue :
```bash
python <plugin>/scripts/check_validation.py manifest.json <feature>
```
(Pour la feature : plan présent et tracé, et si le rapport existe, son verdict **rempli** -
la seule présence du titre de section ne suffit pas.)

## Règles invariantes
- **La validation détecte, la maintenance traite.** Aucune anomalie ni évolution n'est créée ici
  en direct : toujours via les skills maintenance et leurs portes.
- **Le tri d'un écart et le verdict sont humains.** Le skill propose et pré-remplit ; le
  testeur tranche. Pas de porte de recette tant qu'un écart n'est pas trié.
- **Traçabilité totale** : aucun critère du plan n'est absent de la matrice.
- Manifeste silencieux, restitutions en prose, typographie humaine (cf.
  `references/ux-conventions.md`).

Étape suivante : selon le verdict - `/maintenance:correction-anomalie` côté développeur si des anomalies ont été créées, `/validation:plan-de-validation` pour la feature livrée suivante, ou une nouvelle exécution après correction pour lever les réserves.
