---
name: cadrage-completude
description: Confronte le projet à la Definition of Ready et rend le verdict d'état.
---

# cadrage-completude

**Étape terminale du cadrage** (rejouable à tout moment). Mesure l'état du pack
amont, résout en session ce qui peut l'être, et rend le verdict : **le cadrage
est-il terminé, prêt à passer à l'architecte ?** C'est la vue cockpit et la
dernière étape avant `/architecte:architecte-init`.

## Objectif

Produire un **rapport de complétude** honnête : statut par critère et le **verdict
maître**. Le skill mesure, il ne maquille pas. **Honnêteté absolue** : le verdict ne
passe au vert **que si tout est réellement vert**. Une question de découverte laissée
de côté maintient le verdict au **rouge**. Aucune résolution n'est fabriquée : il
n'existe **aucun chemin « démo → vert »**. Ce qui peut être tranché se tranche **en
session** (on pose la question), rien d'ouvert n'est listé dans un fichier.

## Entrée

Le manifeste `.factory/manifest.json` et tous les artefacts qu'il
référence (capture, vision, glossaire, spec index, briefs).

## Pré-requis (vérification silencieuse)

**Aucun.** Invocable à tout moment pour prendre la température du projet.

## Logique de validation

Calculer les booléens à partir de l'état réel des artefacts et du manifeste :

- **`vision_complete`** — product brief : OUT non vide, critères de succès présents.
- **`glossary_validated`** — le glossaire a été **validé en bloc** par l'utilisateur.
- **`decoupage_arbitrated`** — la revue de couplage a été tranchée en session (drapeau vrai).
- **`all_briefs_complete`** — tous les briefs au statut `complete`.
- **`no_blocking_gaps`** — **toute question de découverte `pending`/`deferred`**
  (bloc `discovery` du manifeste) maintient le verdict au rouge — **vérifié (obligatoire)** par
  `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_discovery.py" <racine>/.factory/manifest.json` (s'il est
  **introuvable** ou renvoie **exit 1**, **s'arrêter** et le dire en clair — jamais de vérification « à
  la main »). Une capacité du périmètre IN non couverte se **tranche en session**.
  **Exception — Q8 (contraintes légales / conformité / RGPD) :** optionnelle, gérée **manuellement par
  l'équipe** hors cadrage. Si elle a été laissée à l'équipe (statut `na`), elle **ne bloque pas** le
  verdict et n'est **jamais** re-poussée. **Ne jamais pousser la conformité** (cf.
  `references/ux-conventions.md` §2bis).
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
  reste un **trou bloquant** et maintient le verdict au rouge — **sauf Q8 (légal / conformité /
  RGPD) laissée à l'équipe (`na`)**, qui est optionnelle, gérée hors cadrage, et **ne bloque pas** ;
- **tout** point bloquant ouvert maintient le verdict au rouge ;
- **aucun chemin « démo → vert »** n'existe : on ne marque jamais un critère comme
  atteint à partir d'une valeur de démonstration, d'exemple ou inventée. On ne
  fabrique aucune résolution. Le skill mesure l'état réel, il ne le maquille pas.

## Sortie — rapport écrit + affichage en session

Le skill produit **deux choses** : un rapport complet écrit sur disque, et un
affichage immédiat en session. **Toute la sortie utilisateur est en langage
naturel français** : on n'affiche **jamais** de nom d'attribut ni de clé du
manifeste (suivre la table de correspondance de `references/ux-conventions.md` — on
dit « le cadrage est terminé, prêt pour l'architecte », « le glossaire est validé »,
« aucun point bloquant ouvert »… jamais `cadrage_complete = false` ni un tableau de
booléens bruts). **Jamais d'identifiant codé** (`B1`, `B2`, `A6`, `UC1`…) : on nomme
chaque chose en clair. **Jamais de marqueur `[À CHIFFRER]`** : on dit « à préciser
plus tard avec l'équipe technique ».

### 1. Rapport écrit — `cadrage-out/completude-report.md`

Écrire le **rapport complet** dans ce fichier, **daté et marqué comme instantané** :
- **En-tête obligatoire** : « Rapport généré le `<updated_at>` à partir du manifeste — **le
  manifeste est la source de vérité** ; ce rapport est un instantané, **à régénérer après toute
  résolution de point**. »
- Statut par critère (atteint / non atteint) avec la raison, en clair.
- **Verdict maître** bien visible, au vert seulement si tous les critères sont verts
  (voir la règle d'honnêteté ci-dessus).

### 2. Affichage en session

En plus du fichier, **afficher directement dans la conversation** un **résumé
d'état du projet** — un court paragraphe « où en est le projet », pensé pour
quelqu'un qui reprend **après plusieurs jours** : en une lecture, il sait où il en
est, ce qui reste à trancher, et quelle est la prochaine action. Donner le verdict
en clair (« le cadrage est terminé, prêt pour l'architecte » ou « pas encore prêt,
il reste… »).

**JAMAIS de tableau.** Ne produis **aucun tableau à colonnes**, et en particulier
**aucune colonne « ce qui est complet »**. Un paragraphe en prose, point. Ne liste
pas non plus les critères réussis : on parle de **ce qui reste**, en clair, sans
identifiant codé.

## Résolution interactive en session

Le skill enchaîne sur une **boucle interactive** pour trancher ce qui peut l'être
tout de suite, selon `references/interactive-loop.md` (**une question à la fois, une
réponse recommandée + réponse libre, pas de menu numéroté** ; on attend la réponse
avant la suivante). On parcourt ainsi :

- **Validation du glossaire** si elle n'a pas encore eu lieu : proposer la validation
  en bloc (pas terme par terme).
- **Questions de découverte restées sans réponse** : les reposer une à une.
- **Points bloquants** : ne pas se contenter de les énoncer. Pour **chaque** point
  bloquant, **poser la question** correspondante à l'utilisateur (en clair, sans code
  ni jargon), une à la fois, jusqu'à ce que toute l'information nécessaire soit là.
- **Confirmation des éléments signalés** : tout point « à confirmer » est confirmé ou
  modifié en session.

**Appliquer les réponses EN PLACE.** Dès qu'une réponse débloque ou corrige quelque
chose, **modifier directement l'artefact concerné** dans `cadrage-out/` (product-brief,
spec-index, brief, glossaire…). **Ne créer aucun nouveau fichier** pour stocker les
réponses obtenues ; rien n'est mis de côté dans un journal.

Rappels de la convention (rien n'est inventé) :
- Une réponse explicite (recommandée acceptée ou saisie) → décision **humaine**.
  **Aucune provenance écrite.**
- Un point que l'utilisateur ne tranche pas reste « à confirmer », **ne débloque
  jamais** le verdict, et **n'est écrit nulle part**.
- **Interdit** d'écrire une valeur « démo » comme un fait.

À la fin de la boucle : « **Tout est complété — tu peux passer à l'étape
suivante.** », ou rappeler oralement combien de points restent à trancher (le
verdict reste alors au rouge).

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- Met à jour tout le bloc `definition_of_ready` (les booléens, dont
  `demonstrateur_converged`, + `cadrage_complete`). **Seul ce skill met à jour ces drapeaux** :
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
utilisé est sauvegardé sous `cadrage-out/prompts/<NNN>-<JJ-MM>-dashboard-dor.md` et tracé
dans `prompts[]`. Le fichier sauvegardé ne contient **que le corps du prompt** (le
bloc de code du gabarit), sans titre/date/mode/version (cf. `references/ux-conventions.md`).

## Règles invariantes appliquées ici

- **Reflète l'état réel.** Le verdict ne passe au vert que sur du vert intégral.
  Aucun critère forcé, aucune résolution fabriquée, aucun chemin « démo → vert ».
  Une réponse différée ou un trou bloquant ouvert maintient le verdict au rouge.
- **Pas de fuite de nom d'attribut, d'identifiant codé, ni de jargon de porte.**
  Verdict et critères en clair, en français (table de `references/ux-conventions.md`) —
  jamais `cadrage_complete = false`, jamais `B1`/`UC1`, jamais `[À CHIFFRER]`, jamais
  « porte », ni tableau de booléens bruts. Les clés du manifeste restent internes.
- **Rien d'ouvert persisté.** Aucune liste de trous écrite ; ce qui reste se tranche
  en session, et les réponses sont appliquées **en place** dans `cadrage-out/`.
- **Skill indépendant.** Lit et écrit le manifeste, sans orchestrateur.

**Handoff (avant de passer la main).** Committer `.factory/manifest.json` (verdict cadrage **scellé**)
**et** `cadrage-out/` — l'architecte lit le **repo committé**, pas ta session ni ta machine.

Étape suivante : `/architecte:architecte-init` — une fois le cadrage terminé, l'architecte lit directement les fichiers de `cadrage-out/` pour bâtir le contrat technique.
