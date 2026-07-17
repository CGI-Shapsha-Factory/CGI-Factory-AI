---
name: cadrage-completude
description: Confronte le projet à la Definition of Ready et rend le verdict d'état.
---

# cadrage-completude

**Étape terminale du cadrage** (rejouable à tout moment). C'est la **porte de complétude et de
cohérence** du pack fonctionnel : elle **challenge** le cadrage (rien d'essentiel manquant, rien
qui se contredit, exigences bien formées, valeur réelle), **résout en session** ce qui peut
l'être, et rend le verdict : **le cadrage est-il terminé, prêt à passer à l'architecte ?** C'est
la vue cockpit et la dernière étape avant `/architecte:architecte-init`.

## Objectif

Produire un **rapport de complétude** honnête : statut par critère et le **verdict maître**. Le
skill mesure, il ne maquille pas. **Honnêteté absolue** : le verdict ne passe au vert **que si
tout est réellement vert**. Une question de découverte laissée de côté maintient le verdict au
**rouge**. Aucune résolution n'est fabriquée : il n'existe **aucun chemin "démo -> vert"**. Ce
qui peut être tranché se tranche **en session** (on pose la question), rien d'ouvert n'est listé
dans un fichier.

## Entrée

Le manifeste `manifest.json` et tous les artefacts qu'il référence (capture, project-frame,
product-brief, glossaire, spec-index, coupling-map, briefs).

## Pré-requis (vérification silencieuse)

**Aucun.** Invocable à tout moment pour prendre la température du projet.

## Porte de régénération (relance)
Avant de réécrire le rapport, appliquer `references/regeneration-gate.md`. Si `completude-report.md`
existe déjà, proposer **Repartir de zéro** (supprimer puis régénérer, `version: 1`) ou **Garder les
deux (versionner)** (archiver l'existant sous `_archives/completude-report-v<N>.md`, régénérer au nom
canonique en `version: N+1`) et **attendre** le choix. La résolution interactive des points ouverts
(qui corrige les contrats amont **en place**) n'est **pas** concernée par cette porte : elle ne vise
que la réécriture du rapport de ce skill. Premier passage : générer directement, sans porte.

## Étape 0 : Relecture parallèle exhaustive (ne rien manquer)

**Toujours (re)lire depuis les fichiers committés**, même si tu crois les avoir déjà lus dans
cette session - **jamais** t'appuyer sur la mémoire du chat (reproductible par n'importe qui, sur
une autre machine, après plusieurs jours). Dispatcher des sous-agents lecteurs
(`agentType: "cadrage-reader"`), **un par lot**, chacun avec un **schéma de sortie structuré**, en
**un seul message** (appels parallèles), puis synthétiser. Lots :
1. **Vision & cadre** - `cadrage-out/project-frame.md`, `cadrage-out/product-brief.md`. Extraire :
   objectifs, périmètre IN/OUT, critères de succès, contraintes.
2. **Domaine & découpage** - `cadrage-out/glossaire.md`, `cadrage-out/spec-index.md`,
   `cadrage-out/coupling-map.md`. Extraire : termes/définitions, use cases + walking skeleton
   candidat, couplages/dépendances.
3. **Briefs** - `cadrage-out/features-fonctionnels-brief/*.md`. Extraire, par feature : statut,
   sections présentes/absentes, user stories, critères d'acceptation, critères de succès, OUT,
   dépendances, termes employés.

*(Garde simple : peu à lire -> un seul lecteur ; beaucoup de briefs -> fan-out, plafonné à la
concurrence.)* **Passe de complétude** : vérifier qu'aucun fichier, use case, terme ou brief n'a
été manqué avant de challenger.

## Contrôles de cohérence : stricts et adversariaux

**Challenger, pas cocher.** Dérouler la **grille canonique** de
`references/completude-checklist-guide.md`, adaptée au cadrage (contrat *fonctionnel*, jamais
technique), en **quatre lentilles** - c'est ce qui rend le verdict honnête, au-delà de la simple
présence :

- **Lentille A - Complétude (rien d'essentiel manquant)** : chaque **use case a son brief** ;
  chaque **brief complet** (sections 1-9, section Trous vide, OUT non vide, critères de succès
  chiffrés ou "à préciser à l'architecture") ; le **glossaire couvre** tout terme employé dans
  les briefs ; les **seeds qualité** charge/disponibilité/performance sont captées ou différées
  (l'architecte en dépend) ; chaque **capacité du périmètre IN** est couverte par ≥1 use case.

- **Lentille B - Cohérence (rien ne se contredit)** : **langage ubiquitaire** cohérent (un terme
  = un sens ; un concept = un terme, pas de synonymes pour un même acteur) ; chaque **use case
  sert un objectif** de la vision ; **aucune fuite hors-périmètre** (rien du OUT en IN ; souhaits
  hors périmètre confirmés une fois, jamais poussés) ; **retour démonstrateur résolu** (aucun
  `[REMIS EN CAUSE]` ne survit) ; **dépendances cohérentes** (features citées existent, pas de
  cycle, aligné à la coupling-map) ; **thèse produit** (le product-brief se lit comme une thèse
  problème -> différenciation -> succès, pas comme un catalogue ; chaque profil utilisateur cité
  pèse sur au moins une décision du pack).

- **Lentille C - Qualité des exigences (bien formées)** : **user stories INVEST** (une story qui
  échoue à une lettre est reformulée/scindée/retirée) ; **critères d'acceptation testables**
  (Étant donné/Quand/Alors, pass-fail clair, atomiques, **mots vagues bannis**, ~1-3 par story -
  4+ = story trop grosse) ; **critères de succès mesurables** ou différés à l'architecture ;
  chaque exigence **nécessaire, non ambiguë, singulière, vérifiable**, au bon niveau (aucune
  solution technique prématurée) ; **pas de théâtre d'exigence** (attribut non-fonctionnel nu et
  générique sans seed de découverte -> raccordé, chiffré ou retiré ; "fini" flou dans un critère
  d'acceptation -> reformulé jusqu'à un pass-fail objectif).

- **Lentille D - Validation & prêt-architecte** : chaque **feature délivre de la valeur** (tracée
  à un objectif métier ; une feature bien écrite mais sans valeur = candidate au retrait) ;
  **traçabilité bidirectionnelle** objectifs <-> features (aucune feature orpheline, aucun objectif
  non couvert) ; **prêt pour l'architecte** - project-frame, product-brief, glossaire, spec-index
  (use cases + walking skeleton candidat + couplage) et briefs présents et mutuellement
  cohérents (l'architecte les lit **directement**, donc vérifiés en priorité).

Chaque écart relevé n'est **pas** listé comme un trou : il passe par la **résolution interactive**
ci-dessous (toujours une décision).

## Logique de validation (les 6 critères + verdict)

Calculer les booléens à partir de l'état réel des artefacts et du manifeste :

- **vision complète** - product brief : OUT non vide, critères de succès présents.
- **glossaire validé** - le glossaire a été **validé en bloc** par l'utilisateur.
- **découpage arbitré** - la revue de couplage a été tranchée en session (drapeau vrai).
- **tous les briefs complets** - tous les briefs au statut `complete`.
- **aucun trou de découverte bloquant** - **toute question de découverte `pending`/`deferred`**
  (bloc `discovery`) maintient le verdict au rouge - **vérifié (obligatoire)** par
  `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_discovery.py" --strict <racine>/manifest.json`
  (le mode `--strict` fait échouer aussi les questions `deferred`, pas seulement `pending` ; s'il est
  **introuvable** ou renvoie **exit 1**, **s'arrêter** et le dire en clair - jamais de vérification
  "à la main"). Une capacité du périmètre IN non couverte se **tranche en session**.
  **Exception - Q8 (contraintes légales / conformité / RGPD) :** optionnelle, gérée **manuellement
  par l'équipe** hors cadrage. Si elle a été laissée à l'équipe (statut `na`), elle **ne bloque
  pas** et n'est **jamais** re-poussée. **Ne jamais pousser la conformité** (cf.
  `references/ux-conventions.md` §2bis).
- **démonstrateur convergé** - **calculé** : `aucun validation_point bloquant ouvert` **ET**
  `demonstrateur.client_validated == true`. Le skill **lit** `client_validated` (geste humain à
  l'étape 10), il ne le force jamais.

Puis le **verdict maître**, ET strict des six critères : un seul non atteint suffit à le laisser au
rouge. **Les quatre lentilles ci-dessus alimentent ces critères** (une story non testable -> brief
non complet ; un objectif non couvert -> trou bloquant ; etc.).

**Honnêteté du verdict (non négociable).** Le verdict passe au vert **uniquement** si la totalité
des critères est verte. En particulier : une **question de découverte différée** reste un **trou
bloquant** (sauf Q8 `na`) ; **tout** point bloquant ouvert maintient le rouge ; **aucun chemin
"démo -> vert"** - on ne marque jamais un critère atteint à partir d'une valeur de démonstration
ou inventée. Le skill mesure l'état réel, il ne le maquille pas.

## Résolution interactive : TOUJOURS une décision, jamais un simple constat

Le skill enchaîne sur une **boucle interactive** pour trancher ce qui peut l'être, selon
`references/interactive-loop.md`. **C'est le point de résolution unique du cadrage.** Règle
centrale : **aucun écart n'est seulement annoncé** ("il manque X", "ce point est bloquant",
"il reste N points"). Pour **chaque** écart trouvé (trou, contradiction, exigence mal formée,
feature sans valeur), **une chose à la fois** :
1. **Énoncer en clair** ce qui est présent **et** ce qui manque / ce qui cloche - en prose, nom
   métier, **aucun nom de champ ni code** (seule exception : un use case, nommé "intitulé complet
   (UCn)").
2. Demander explicitement : **"que veux-tu faire ?"**
3. Proposer, **en prose (pas de menu numéroté)** : une **réponse recommandée** adaptée au contexte,
   une **alternative** plausible, et l'invitation à **saisir ta propre réponse**.
4. **Appliquer directement** le choix, **en place** dans l'artefact concerné de `cadrage-out/`
   (product-brief, spec-index, brief, glossaire...). **Aucun fichier annexe.**

**Si l'utilisateur ne tranche pas** un point : **on n'écrit rien** (le point est omis, jamais
marqué), il **ne débloque pas** le verdict (qui reste au rouge), et on peut le lui rappeler
**oralement** en fin de boucle. **L'utilisateur ne relit jamais les artefacts** : tout se règle
dans la décision.

**Prioriser** : d'abord ce qui **bloque un artefact**, ensuite le raffinement. **Questions
spécifiques et répondables** (pas "préciser le besoin" mais "quelle cible chiffrée de réduction
du temps de recherche ?"). **Plafonner à ~8-10 questions par session** pour ne pas noyer ; le
reste sera repris au prochain passage. On parcourt notamment : validation du glossaire (en bloc,
si pas encore faite) ; questions de découverte `pending`/`deferred` ; acquis `[REMIS EN CAUSE]` ;
souhaits hors périmètre (confirmés une fois) ; stories/critères mal formés (INVEST, mots vagues) ;
objectifs non couverts ou features orphelines.

> **Interdit explicite.** Afficher un écart ("il manque...", "bloquant", "il reste N points")
> **sans** l'accompagner immédiatement de la question **"que veux-tu faire ?"**, des propositions,
> et de l'application du choix. Un constat nu est une violation de ce skill.

**Rappels de la convention (rien n'est inventé) :** une réponse explicite -> décision humaine,
**aucune provenance écrite** ; un point non tranché reste "à confirmer", **ne débloque jamais** le
verdict, et **n'est écrit nulle part** ; **interdit** d'écrire une valeur "démo" comme un fait.

À la fin : "**Tout est complété - tu peux passer à l'étape suivante.**", ou rappeler oralement
combien de points restent à trancher (le verdict reste alors au rouge).

## Sortie : rapport écrit + affichage en session

**Toute la sortie utilisateur est en langage naturel français** : **jamais** de nom d'attribut ni
de clé manifeste (suivre `references/ux-conventions.md` - "le cadrage est terminé, prêt pour
l'architecte", "le glossaire est validé", "aucun point bloquant ouvert"... jamais
`cadrage_complete = false` ni un tableau de booléens). **Jamais d'identifiant codé** (`B1`, `A6`,
`UC1`... - hors "intitulé (UCn)"). **Jamais de marqueur `[À CHIFFRER]`** : "à préciser plus tard
avec l'équipe technique".

### 1. Rapport écrit : `cadrage-out/completude-report.md`
Écrire le **rapport complet**, **daté et marqué comme instantané** :
- **En-tête obligatoire** : "Rapport généré le `<updated_at>` à partir du manifeste - **le
  manifeste est la source de vérité** ; ce rapport est un instantané, **à régénérer après toute
  résolution de point**."
- Statut par critère (atteint / non atteint) avec la raison, en clair - incluant ce que les
  quatre lentilles ont trouvé et corrigé.
- **Verdict maître** bien visible, au vert seulement si tous les critères sont verts.

### 2. Affichage en session
Un **résumé d'état** - un court paragraphe "où en est le projet", pensé pour quelqu'un qui
reprend **après plusieurs jours** : en une lecture, il sait où il en est, ce qui reste à trancher,
la prochaine action, et le verdict en clair.

**JAMAIS de tableau.** Aucun tableau à colonnes, en particulier **aucune colonne "ce qui est
complet"**. Un paragraphe en prose. On parle de **ce qui reste**, en clair, sans identifiant codé.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- Met à jour tout le bloc `definition_of_ready` (les booléens, dont `demonstrateur_converged`, +
  `cadrage_complete`). **Seul ce skill met à jour ces drapeaux** : ne **jamais** les flipper
  ailleurs ni à la main après avoir résolu un point - **relancer `cadrage-completude`**, pour que
  le rapport écrit et le manifeste restent cohérents (jamais de manifeste "prêt" avec un rapport
  "pas prêt").
- `updated_at`.
- **Ne modifie pas** `decoupage_arbitrated` à la hausse : décision humaine ; le skill le lit.

> **Silencieux - jamais annoncé.** Ne **jamais** dire que le manifeste est mis à jour, ni citer un
> nom de champ ou `true`/`false`. Le verdict et l'état se disent **en clair** ("le cadrage est
> terminé, prêt pour l'architecte") - cf. `references/ux-conventions.md`.

## Livrable visuel

Le dashboard Definition of Ready (jauge de complétude, statut par critère, verdict maître, ce qui
manque) se génère dans Claude Design. Le prompt prêt à coller est dans
`references/dashboard-dor-prompt.md` (gabarit statique). Le prompt utilisé est sauvegardé sous
`cadrage-out/prompts/<NNN>-<JJ-MM>-dashboard-dor.md` et tracé dans `prompts[]`. Le fichier
sauvegardé ne contient **que le corps du prompt** (le bloc de code du gabarit), sans
titre/date/mode/version (cf. `references/ux-conventions.md`).

## Règles invariantes appliquées ici

- **Challenger, pas cocher.** On cherche ce qui manque, se contredit, est mal formé ou sans valeur
  - pas la simple présence (grille ancrée : DoR, INVEST, ISO/IEC/IEEE 29148, BABOK, DDD, MoSCoW,
  traçabilité - `references/completude-checklist-guide.md`).
- **Toujours une décision, jamais un constat.** Chaque écart -> question "que veux-tu faire ?" +
  réponse recommandée / alternative / saisie + application en place. Aucun "bloquant" nu.
  L'utilisateur ne relit rien.
- **Reflète l'état réel.** Le verdict ne passe au vert que sur du vert intégral. Aucun critère
  forcé, aucune résolution fabriquée, aucun chemin "démo -> vert".
- **Pas de fuite de nom d'attribut, d'identifiant codé, ni de jargon de porte.** Verdict et
  critères en clair (table `references/ux-conventions.md`) - jamais `cadrage_complete = false`,
  jamais `B1`/`UC1` nu, jamais `[À CHIFFRER]`, jamais "porte", ni tableau de booléens.
- **Rien d'ouvert persisté.** Aucune liste de trous écrite ; ce qui reste se tranche en session,
  les réponses sont appliquées **en place**.
- **Balayage typographie.** Vérifier qu'aucun artefact `cadrage-out/` (briefs, product-brief, glossaire, prompts) ne contient de glyphe de style IA (tiret cadratin, points de suspension unicode, flèches unicode, guillemets à chevrons, coche/croix) ; remplacer par l'équivalent clavier en place (cf. la section Typographie de `references/ux-conventions.md`).
- **Skill indépendant.** Lit et écrit le manifeste, sans orchestrateur.

**Handoff (avant de passer la main).** Committer `manifest.json` (verdict cadrage **scellé**)
**et** `cadrage-out/` - l'architecte lit le **repo committé**, pas ta session ni ta machine.

Étape suivante : `/architecte:architecte-init` - une fois le cadrage terminé, l'architecte lit directement les fichiers de `cadrage-out/` pour bâtir le contrat technique.
