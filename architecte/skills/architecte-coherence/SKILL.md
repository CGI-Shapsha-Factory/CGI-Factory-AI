---
name: architecte-coherence
description: Valide la cohérence du contrat technique et prépare le passage à l'assembleur.
---

# architecte-coherence

Dernière étape de la phase technique : la **porte de validation de cohérence** (def :
"la porte humaine est l'arbitrage des ADR, puis la validation de cohérence").
**Tout** doit être vérifié **avant de passer au designer** : le contrat technique tient
ensemble, sans contradiction ni trou, et chaque exigence est bien formée. On ne **coche pas
une présence** - on **challenge** chaque contrat contre les autres et contre le cadrage.
La grille de vérification est **ancrée dans des méthodes reconnues** (ATAM, scénarios qualité
6-parties, revue ADR, traçabilité bidirectionnelle, walking skeleton, risque-driven, arc42,
AWS Well-Architected) : voir `references/coherence-checklist-guide.md`.

## Pré-requis (vérification silencieuse)
Le contrat technique a été produit (le bloc `architecture` est rempli). Vérifier sans
l'annoncer ; sinon, orienter en clair vers `/architecte:architecte-fondations`.

## Étape 0 : Relecture parallèle exhaustive (ne rien manquer)
**Toujours (re)lire depuis les fichiers committés**, même si tu crois les avoir déjà lus dans
cette session - **jamais** t'appuyer sur la mémoire du chat (exécution reproductible par
n'importe qui, sur une autre machine). Dispatcher des sous-agents lecteurs
(`agentType: "architecte-reader"`), **un par lot**, chacun avec un **schéma de sortie
structuré**, en **un seul message** (appels parallèles), puis synthétiser. Lots :
1. **Architecture** - tout `architecte-out/` : `facteurs-et-qualite.md`, `composants.md`,
   `stack-technique.md`, `standards-ingenierie.md`, `decisions/ADR-*.md`, `diagrammes.md`
   (+ `diagrammes/*.png`), `risques.md`, `impact-design.md` ; le dossier `conventions/`.
2. **Cadrage (jointure aval)** - `cadrage-out/spec-index.md`, `cadrage-out/glossaire.md`,
   les briefs sous `cadrage-out/features-fonctionnels-brief/*.md`.

*(Garde simple : peu à lire -> un seul lecteur ; sinon fan-out, plafonné à la concurrence.)*
**Passe de complétude** : après synthèse, vérifier qu'aucun fichier, entité, use case, ADR ou
décision n'a été manqué avant de challenger.

## Contrôles de cohérence : stricts et adversariaux
**Challenger, pas cocher.** Dérouler la **grille canonique** de
`references/coherence-checklist-guide.md` : **35 items cochables** (`CHK001`+) répartis en
**trois lentilles** (chaque item porte sa dimension et sa source de traçabilité).

**Un item à la fois, dans l'ordre.** Un item dont la réponse est "non" ou "je ne sais pas"
**reste décoché** et devient une décision en session ; il ne se coche qu'une fois la correction
appliquée en place. Un item sans objet se coche **avec sa raison**. Les codes `CHK` sont
**internes** : jamais montrés à l'utilisateur (voir `ux-conventions.md`). Résumé des lentilles :

- **Lentille A - Cohérence (rien ne se contredit)** : points de sensibilité et de compromis
  tous **classés risque/non-risque** (aucun non classé ; risques en thèmes rattachés à un
  driver) ; **ADR non contradictoires** (deux ADR acceptés ne se contredisent jamais ; un ADR
  remplacé est `superseded` + lié, jamais réécrit en silence ; chaque ADR porte rationale +
  options + conséquences) ; **contradictions inter-artefacts** (drivers ⨉ stack ⨉ ADR ⨉
  déploiement - ex. hébergement UE vs service hors UE, cible de dispo tenue par le
  déploiement) ; **cohérence de nommage** (alignement glossaire) ; **diagrammes C4 <->
  inventaire réel** des composants (frontières cohérentes, PNG présents).

- **Lentille B - Consistance (traçabilité bidirectionnelle, aucun orphelin)** : **sens avant**
  - chaque driver / attribut de qualité / contrainte de brief / entité du glossaire est adressé
  par ≥1 composant et/ou ADR ; **sens arrière** - chaque composant remonte à un besoin (sinon
  **orphelin**) ; **use cases <-> features** en couverture 1:1 ; **composant <-> stack** (technos +
  versions exactes concordantes, composant Frontend/UI présent si écrans) ; **conventions <->
  stack** (chaque langage a son fichier).

- **Lentille C - Complétude (exigences bien formées)** : **scénarios qualité 6-parties** avec
  **mesure de réponse chiffrée et testable** (rejeter "scalable/robuste" sans mesure) ;
  **drivers ≠ attributs de qualité** (distincts, non redondants, dérivés) ; **walking skeleton
  valide** (bout en bout réel, vrais composants, build/deploy/test automatiques, frappe
  l'intégration la plus risquée **sans stub**) ; **registre de risques non vide et fermé**
  (impact + mitigation proportionnée + déclencheur ; high-risk sécurité/fiabilité traités avant
  le handoff ; spikes bloquants avant la 1re feature) ; **impact-design complet** (la tranche
  qui se voit - contrat consommé par le designer, donc prioritaire) ; **aucun marqueur résiduel
  & front-matter valide** ; **passe finale "ce qui manque / ce qui peut casser"**.

Garde-fou déterministe (**obligatoire, jamais sauté**) : lancer
`python "${CLAUDE_PLUGIN_ROOT}/scripts/check_architecture.py" <racine>/manifest.json` - il
échoue notamment s'il reste un marqueur, si un composant n'a pas de techno, si un langage n'a
pas son fichier de conventions, si une techno de `stack-technique.md` n'a pas de version exacte,
si un fichier `architecte-out/` n'a pas son front-matter `version`/`date`, si la stratégie de
test est incomplète, ou si les fichiers d'env / l'enforcement manquent. Si le script est
**introuvable** (chemin plugin non résolu) ou renvoie **exit 1**, **s'arrêter** et **rapporter
en clair** ce qui manque - **ne jamais** basculer en vérification "à la main". *(Le script
couvre la présence ; les lentilles A/B/C ci-dessus sont le jugement qu'il ne peut pas faire.)*

## Résolution interactive : TOUJOURS une décision, jamais un simple constat
Tout point relevé - **bloquant ou non** - n'est **jamais** seulement affiché. Pour **chaque**
anomalie (quelque chose qui **manque**, se **contredit**, ou "se passe"), dérouler la boucle
`references/interactive-loop.md`, **un point à la fois**, ainsi :
1. **Énoncer en clair** ce qui est présent **et** ce qui manque / ce qui se passe - en prose,
   nom métier, **aucun nom de champ ni code** (`C1`/`UC1`/`ADR A6`...).
2. Demander explicitement : **"que veux-tu faire ?"**
3. Proposer **trois choix** : **(a)** une action concrète **recommandée** adaptée au contexte,
   **(b)** une **alternative** plausible, **(c)** **"saisir ta propre réponse"**.
4. **Appliquer directement** le choix retenu, **en place** dans le fichier `architecte-out/`
   concerné. **Aucun fichier annexe.**

**L'utilisateur ne va jamais ouvrir ni relire les artefacts** : tout se règle **dans la
décision**. D'abord **énumérer tout ce qui a été trouvé**, puis les dérouler **un par un**
jusqu'à ce qu'il ne reste **rien**.

> **Interdit explicite.** Écrire "ce point est bloquant" / "il manque X" / "il reste N
> points" **sans** l'accompagner immédiatement de la question **"que veux-tu faire ?"**, des
> **trois choix**, et de l'**application** du choix. Un constat nu est une violation de ce skill.

**Ne pas passer** à `/designer:designer-init` tant qu'il reste un point, un marqueur, ou un
choix non appliqué.

## Sortie
- Un **rapport de cohérence** `architecte-out/coherence-report.md` : ce qui a été vérifié
  (les trois lentilles) et ce qui a été **corrigé** en session, en clair - **sans marqueur
  résiduel**. Front-matter `version`/`date` comme tout artefact.
- En chat : un **court bilan en prose** (pas de tableau, pas de nom de variable, pas
  d'identifiant codé), puis la confirmation que **tout est résolu** - jamais un constat de trou
  sans décision associée.
- **Décision humaine** : l'architecte **valide** la cohérence (geste humain). Le skill ne valide
  jamais de lui-même ; il le **propose**, l'humain confirme.

## Mise à jour du manifeste (en silence)
Une fois la validation humaine actée, mettre à jour le manifeste **sans le narrer**
(jamais "je passe `coherence_validated = true` et `phase = "valide"`").

## Handoff (vers l'assembleur / le designer)
Une fois validé, le contrat technique prêt à transmettre comprend : les ADR et contrats
transverses, les normes (`standards-ingenierie.md` + `conventions/`), les diagrammes, le walking
skeleton et la **séquence de features numérotée** (convergence des deux découpages), le registre
de risques, et les **Décisions à impact design** (`impact-design.md`, consommées par le
designer). La phase design exige le cadrage **ET** l'architecture validés : c'est pourquoi
`impact-design.md` est vérifié **en priorité** ci-dessus. (L'assembleur coud ensuite ces contrats
par feature, une fois le contrat de design figé.)

## Règles invariantes
- **Challenger, pas cocher.** Cohérence stricte et adversariale, ancrée méthodes ; on cherche ce
  qui **manque** et ce qui se **contredit**, pas la simple présence.
- **Toujours une décision, jamais un constat.** Chaque point -> question "que veux-tu faire ?"
  + trois choix (recommandée / alternative / saisie) + application en place. Aucun "bloquant"
  nu. L'utilisateur ne relit rien : tout se règle dans la décision.
- **Remonter tout, résoudre un par un.** Énumérer chaque point trouvé, puis les dérouler un à un
  jusqu'à zéro. Aucun marqueur ne survit.
- **Balayage typographie.** Vérifier qu'aucun artefact `architecte-out/` ne contient de glyphe de style IA (tiret cadratin, points de suspension unicode, flèches unicode, guillemets à chevrons, coche/croix) ; remplacer par l'équivalent clavier en place (cf. la section Typographie de `references/ux-conventions.md`).
- **L'humain valide.** La cohérence n'est jamais auto-validée par l'IA.
- **Rien de la mécanique affiché.** Aucun nom de variable/clé manifeste, aucun identifiant codé,
  aucun tableau (voir `references/ux-conventions.md`). Manifeste mis à jour en silence ; à
  l'utilisateur, seulement le bilan en clair et la suite.

**Handoff (avant de passer la main).** Committer `manifest.json` (avec la cohérence **scellée**)
**et** `architecte-out/` - la phase suivante lit le **repo committé**, pas ta session ni ta machine. Un
manifeste non re-committé après la validation ferait échouer `designer-init` (flag à `false`) sur un autre poste.

Étape suivante : `/designer:designer-init` - démarrer le contrat de design (la phase design exige le cadrage ET l'architecture validés). Ou corriger d'abord les points signalés en relançant le skill concerné (`/architecte:architecte-fondations`, `/architecte:architecte-stack` ou `/architecte:architecte-livrables`).
