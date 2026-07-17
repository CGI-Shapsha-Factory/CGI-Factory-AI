# Règles de la validation fonctionnelle : place dans la chaîne, règles d'or, tri des écarts

Référence partagée des 3 skills métier (`plan-de-validation`, `execution-validation`,
`bilan-validation`). Chaque skill y renvoie au lieu de dupliquer.

## La place de la validation dans la chaîne
La validation fonctionnelle intervient **après la livraison d'une feature** (fabrication
SpecKit terminée, feature intégrée au code de référence et déployée sur l'environnement de
recette) et **avant** son acceptation. Elle répond à la question : "le logiciel livré
fait-il ce que sa spécification promet ?" - critère par critère, preuve à l'appui.

La validation **détecte et trace** ; elle ne **traite** jamais un écart :
- le **traitement** des écarts est le rôle exclusif du plugin `recette` (création d'une
  anomalie ou d'une évolution dans Linear, correction côté développeur, requalification) ;
- la validation **prépare le contenu** d'un écart (comportement attendu, constaté, étapes de
  reproduction depuis le déroulé capturé) et **renvoie** vers `/recette:creation-anomalie` ou
  `/recette:creation-evolution` - la création reste la porte de création unique de la recette,
  avec ses portes de complétude et sa validation humaine.

Le déclenchement est **toujours manuel** (le testeur lance les skills) : aucune validation
ne part seule sur un push, un merge ou un déploiement.

## Un cas par critère, tracé, jamais interprété
- **Un cas de test par critère d'acceptation** de la spécification (`specs/<feature>/spec.md` :
  scénarios Given/When/Then des user stories, exigences fonctionnelles, critères de succès
  mesurables observables dans le navigateur, cas limites). Identifiant stable
  `TC-<feature>-NNN`, et chaque cas **cite son critère source** : c'est la colonne vertébrale
  du rapport tracé exigence par exigence.
- **Un critère non testable n'est jamais interprété.** Ambigu ("rapide", "convivial"), non
  observable dans le navigateur, ou impossible sans donnée manquante : il est marqué
  `A CLARIFIER` dans le plan, avec la raison, et le testeur décide de la suite (clarifier en
  session la lecture observable du critère, ou tracer le flou dans Linear). Deviner l'intention
  d'un critère flou produit des faux verdicts dans les deux sens.
- **La spécification reste intacte.** La validation lit `spec.md`, elle ne l'écrit jamais :
  clarifier un critère **dans le plan de test** précise sa lecture observable ; changer le
  critère **lui-même** passe par une évolution de recette (geste PO, via SpecKit).

## Le tri des écarts : bug, spécification en cause, ou critère flou
À l'issue de l'exécution, chaque écart est trié **avec le testeur**, un par un, selon la
distinction fondamentale de la recette :
- **Critère non respecté (anomalie)** : la spécification est bonne, le logiciel ne la respecte
  pas. -> proposer de créer l'anomalie via `/recette:creation-anomalie`, contenu pré-rempli
  depuis le déroulé capturé. Le code sera réparé ; la spécification ne change pas.
- **Critère faux ou incomplet (évolution)** : le logiciel fait ce qui est écrit, mais ce qui
  est écrit ne correspond pas au vrai besoin. -> proposer d'ouvrir la boucle de retour vers la
  spécification via `/recette:creation-evolution` (geste du PO, jamais automatique).
- **Critère flou (non testable)** : impossible de trancher tant que le critère n'est pas
  clair. -> proposer de clarifier la lecture observable en session, ou de tracer le point dans
  Linear pour suivi.
Dans les trois cas, le skill **oriente et propose** ("Veux-tu créer l'anomalie ?", "Veux-tu
tracer cette évolution ?") ; il ne crée jamais un ticket sans accord explicite.

## L'IA exécute et rapporte, l'humain valide
- **Constats automatisés** : dérouler un cas de test, constater OK / KO / NON TESTABLE,
  capturer les preuves, assembler le rapport, consolider les scénarios rejouables, déposer un
  commentaire de synthèse dans Linear.
- **Gestes humains, jamais automatisés** : valider le plan de test avant exécution ; trier un
  écart (anomalie / évolution / flou) ; décider de créer un ticket ; et surtout **le verdict
  de la porte de recette** (valider la livraison, valider avec réserves, refuser) - sur ce
  premier projet, en mode sans orchestrateur, **le testeur est juge et valideur** de chaque
  validation. Le skill ne prononce jamais le verdict lui-même.
- Le verdict s'inscrit dans le **rapport committé** (il voyage avec le repo) et dans **Linear**
  (commentaire sur le ticket Feature ; changement de statut seulement sur confirmation).
  **Jamais dans le manifeste** : l'avancement vit dans Linear.

## Fiabilité d'exécution (contre les faux verdicts)
- **Relance unique avec tri avant de conclure KO** : sur un échec, distinguer d'abord
  "lenteur / chargement" (attendre puis rejouer l'étape une fois), "élément introuvable"
  (re-repérer l'élément par son libellé une fois), "vrai écart" (le comportement observé
  contredit le résultat attendu). Un seul cycle de relance ; au deuxième échec, le verdict
  KO est posé avec les preuves.
- **Budget d'étapes borné par cas** : un cas qui dépasse largement ses étapes prévues (repère :
  plus du double) s'arrête et sort en NON TESTABLE avec la raison, au lieu d'errer.
- **Preuve à chaque verdict** : capture d'écran au point de vérification ; sur KO, joindre en
  plus le déroulé effectif complet et ce que la console ou le réseau montrent d'anormal.
- **Jamais d'action destructive ni de donnée réelle** : on ne teste qu'avec les données de
  test du plan ; toute action irréversible sur l'environnement (suppression, paiement, envoi
  externe) exige une confirmation du testeur avant d'être jouée.

## Linear : détection et installation du MCP (auto-portant)
Tout dialogue Linear (retrouver le ticket `Feature`, ticket de suivi, commentaire de
synthèse) passe par le **MCP du plugin `linear-prism`**. Avant toute écriture : sonder
`list_teams`. S'il ne répond pas, **ne rien créer ni commenter** - signaler en clair et
afficher l'installation :
1. Ajouter la marketplace : `/plugin marketplace add shinpr/linear-prism`
2. Installer le plugin : `/plugin install linear-prism@linear-prism`
3. Redémarrer Claude Code (pour charger le serveur MCP).
4. S'authentifier : `/mcp` -> serveur `linear` -> login OAuth.
Patrons d'usage (les mêmes que la recette) : ticket `Feature` résolu par
`list_issues({team, label Feature})` avec le numéro de registre en tête de titre ; états
changés par **nom** résolu via `list_issue_statuses` en vérifiant l'état retourné (un état
non résolu est ignoré en silence) ; `save_comment` pour la trace ; lire avant d'écrire
(idempotence). Un ticket de suivi de critère flou est un sous-ticket du ticket `Feature`,
**sans label de recette** (jamais `Anomalie`/`Evolution`, ni `Feature`/`Task`).

## Scénarios rejouables (le capital de non-régression)
Le déroulé **effectif** de chaque cas OK est consolidé en scénario rejouable
(`validation-out/<feature>/scenarios/TC-*.md`) : étapes en **langage naturel**, précises et
auto-portantes, rejouables par n'importe quel outil d'exécution (extension Chrome, Playwright,
Cowork) sans dépendre d'un sélecteur technique. C'est la bibliothèque de non-régression que
la recette rejoue : `realisation-evolution` (prouver que l'ancien comportement tient) et
`correction-anomalie` (vérifier qu'une correction n'a rien cassé autour).
