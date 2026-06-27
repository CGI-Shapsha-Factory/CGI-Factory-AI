---
name: cadrage-completude
description: Confronte le projet à la Definition of Ready et rend le verdict d'état.
---

# cadrage-completude

Cinquième étape (rejouable à tout moment). Mesure l'état du pack amont contre la
Definition of Ready et rend le verdict « prêt pour SpecKit ». C'est la vue
cockpit.

## Objectif

Produire un **rapport de complétude** honnête : statut par critère, liste
actionnable de ce qui manque, et le **verdict maître**. Le skill mesure, il ne
maquille pas. **Honnêteté absolue** : le verdict ne passe au vert **que si tout
est réellement vert**. Une réponse de découverte différée, ou n'importe quel trou
bloquant ouvert, maintient le verdict au **rouge**. Aucune résolution n'est
fabriquée : il n'existe **aucun chemin « démo → vert »**.

## Entrée

Le manifeste `factory-docs/manifest.json` et tous les artefacts qu'il
référence (capture, vision, glossaire, spec index, briefs).

## Porte d'entrée

**Aucune.** Invocable à tout moment pour prendre la température du projet.

## Logique de validation

Calculer les booléens à partir de l'état réel des artefacts et du manifeste :

- **`vision_complete`** — product brief : OUT non vide, critères de succès
  présents, aucun trou bloquant.
- **`glossary_validated`** — tous les termes marqués `structurant = oui` dans le
  glossaire (mobilisés par la vision ou servant de nom / frontière d'un use case)
  sont au statut `validé`.
- **`decoupage_arbitrated`** — un humain a arbitré le découpage (drapeau vrai).
- **`all_briefs_complete`** — tous les briefs au statut `complete`.
- **`no_blocking_gaps`** — aucun artefact ne porte un trou classé **bloquant**, et
  **aucun `validation_point` bloquant n'est `open`** (les `[À CHIFFRER]` et les
  `[À VALIDER]` non bloquants n'empêchent pas le ET). En particulier, **toute
  capacité du périmètre IN non couverte** (section couverture du `spec-index.md`)
  est un trou bloquant, et **toute question de découverte `pending`/`deferred`**
  (bloc `discovery` du manifeste) est un trou bloquant — vérifiable par
  `scripts/check_discovery.py`.
- **`demonstrateur_converged`** — **calculé** : `aucun validation_point bloquant
  ouvert` **ET** `demonstrateur.client_validated == true`. Le skill **lit**
  `client_validated` (geste humain à l'étape 10), il ne le force jamais. Un projet
  sans boucle démonstrateur n'est convergé que lorsque le client a validé la
  maquette.

Puis le **verdict maître**, ET strict des six critères ci-dessus : un seul critère
non atteint suffit à le laisser au rouge. (La logique interne est documentée dans
`cadrage-init`, schéma du manifeste ; elle n'est jamais affichée telle quelle.)

**Honnêteté du verdict (non négociable).** Le verdict passe au vert **uniquement**
si la totalité des critères est verte. En particulier :
- une **question de découverte différée** (« à confirmer » / passée pour l'instant)
  reste un **trou bloquant** et maintient le verdict au rouge ;
- **tout** point bloquant ouvert maintient le verdict au rouge ;
- **aucun chemin « démo → vert »** n'existe : on ne marque jamais un critère comme
  atteint à partir d'une valeur de démonstration, d'exemple ou inventée. On ne
  fabrique aucune résolution. Le skill mesure l'état réel, il ne le maquille pas.

## Sortie — rapport écrit + affichage en session

Le skill produit **deux choses** : un rapport complet écrit sur disque, et un
affichage immédiat en session. **Toute la sortie utilisateur est en langage
naturel français** : on n'affiche **jamais** de nom d'attribut ni de clé du
manifeste (suivre la table de correspondance de `references/ux-conventions.md` — on
dit « prêt pour SpecKit », « le glossaire est validé », « aucun point bloquant
ouvert »… jamais `ready_for_speckit = false` ni un tableau de booléens bruts).

### 1. Rapport écrit — `factory-docs/work/completude-report.md`

Écrire le **rapport complet** dans ce fichier, **daté et marqué comme instantané** :
- **En-tête obligatoire** : « Rapport généré le `<updated_at>` à partir du manifeste — **le
  manifeste est la source de vérité** ; ce rapport est un instantané, **à régénérer après toute
  résolution de point**. »
- Statut par critère (atteint / non atteint) avec la raison, en clair.
- **Verdict maître** bien visible, au vert seulement si tous les critères sont verts
  (voir la règle d'honnêteté ci-dessus).
- Liste de **ce qui manque**, actionnable, chaque manque relié à l'étape/skill qui
  le résout.
- Tableau des features : par feature, statut du brief et nombre de trous restants.

### 2. Affichage en session

En plus du fichier, **afficher directement dans la conversation** :

**(a) Tableau de synthèse à trois colonnes** (français, langage naturel) :

| Ce qui manque | Ce qu'il faut corriger | Ce qui est complet |
|---|---|---|

- *Ce qui manque* : éléments absents à produire (briefs non écrits, point de
  cadrage sans réponse, capacité du périmètre non couverte…).
- *Ce qu'il faut corriger* : éléments présents mais à reprendre (trou bloquant à
  lever, terme de glossaire à valider, point à clarifier…).
- *Ce qui est complet* : critères déjà verts.

**(b) Résumé d'état du projet** — un court paragraphe « où en est le projet »
pensé pour quelqu'un qui reprend **après plusieurs jours** : en une lecture, il
sait où il en est, ce qui bloque encore, et quelle est la prochaine action. Donner
le verdict en clair (« prêt pour SpecKit » ou « pas encore prêt, il reste… »).

## Résolution interactive en session

Plutôt qu'une **liste statique** de trous, le skill enchaîne sur une **boucle
interactive** pour résoudre ce qui peut l'être tout de suite, selon la convention
partagée `references/interactive-loop.md` (**une question à la fois, trois options :
réponse recommandée / passer pour l'instant / saisir ma réponse** ; on attend la
réponse avant la question suivante). On parcourt ainsi :

- **Validation du glossaire terme par terme** : chaque terme structurant non encore
  validé est présenté isolément pour confirmation (ou modification).
- **Résolution des trous bloquants** : chaque trou bloquant ouvert est traité en
  conversation via la boucle à trois options.
- **Confirmation des éléments signalés** : tout point marqué « à confirmer » /
  « à clarifier » est confirmé ou modifié.

Rappels de la convention (rien n'est inventé) :
- Réponse via *recommandée* ou *saisir* → décision **humaine**, tracée
  `(src: atelier/utilisateur)`.
- *Passer pour l'instant* → reste « à confirmer », **demeure un trou bloquant** et
  **ne débloque jamais** le verdict.
- **Interdit** d'écrire une valeur « démo » / aléatoire comme un fait : la seule
  façon de remplir un trou est un choix explicite de l'utilisateur.

À la fin de la boucle : « **Tout est complété — tu peux passer à l'étape
suivante.** », ou indiquer combien de points ont été **passés** et restent
bloquants (auquel cas le verdict reste au rouge).

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- Met à jour tout le bloc `definition_of_ready` (les booléens, dont
  `demonstrateur_converged`, + `ready_for_speckit`). **Seul ce skill met à jour ces drapeaux** :
  ne **jamais** les flipper ailleurs ni à la main après avoir résolu un point — **relancer
  `cadrage-completude`**, pour que le rapport écrit et le manifeste restent cohérents (jamais de
  manifeste « prêt » avec un rapport « pas prêt »).
- `updated_at`.
- **Ne modifie pas** `decoupage_arbitrated` à la hausse : il reflète une décision
  humaine ; le skill le lit, il ne l'invente pas.

## Livrable visuel

Le dashboard Definition of Ready (jauge de complétude, statut par critère,
verdict maître, ce qui manque) se génère dans Claude Design. Le prompt prêt à
coller est dans `references/dashboard-dor-prompt.md` (gabarit statique). Le prompt
utilisé est sauvegardé sous `factory-prompts/<NNN>-<JJ-MM>-dashboard-dor/` et tracé
dans `prompts[]`.

## Règles invariantes appliquées ici

- **Reflète l'état réel.** Le verdict ne passe au vert que sur du vert intégral.
  Aucun critère forcé, aucune résolution fabriquée, aucun chemin « démo → vert ».
  Une réponse différée ou un trou bloquant ouvert maintient le verdict au rouge.
- **Pas de fuite de nom d'attribut.** Verdict et critères sont affichés en clair,
  en français (table de `references/ux-conventions.md`) — jamais
  `ready_for_speckit = false` ni un tableau de booléens bruts. Les clés du
  manifeste restent internes (mises à jour ci-dessus).
- **Porte maîtresse.** Le verdict « prêt pour SpecKit » conditionne le handoff.
- **Skill indépendant.** Lit et écrit le manifeste, sans orchestrateur.

Étape suivante : `/cadrage:cadrage-handoff` — assembler le pack et passer à SpecKit une fois le verdict au vert.
