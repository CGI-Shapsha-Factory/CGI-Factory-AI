---
name: cadrage-decoupage
description: Propose un découpage fonctionnel en use cases de valeur, plus une hypothèse de couplage.
---

# cadrage-decoupage

Troisième étape. Transforme la vision en une **proposition de découpage
fonctionnel** (use cases / capacités, par valeur), plus la carte de couplage
(hypothèse) qui sert d'appui à l'arbitrage humain. **Propose, ne décide pas.**

## Principe des deux découpages

La captation produit le **découpage fonctionnel** — ce que fait le produit et dans
quel ordre d'importance, **depuis la vision PO seule, sans stack ni architecture**.
La **liste de features numérotées et séquencée** (et le walking skeleton, qui
dé-risque la stack) se fige **en sortie d'architecture** : l'architecture confronte
cette coupe fonctionnelle aux contrats et au squelette technique. Ici, IDs (`UC…`)
et ordre sont **provisoires**, le couplage est une **hypothèse**.

## Objectif

Produire un **découpage fonctionnel** (use cases ordonnés par valeur, tranches
verticales) et une **carte de couplage** (hypothèse : états partagés,
parallélisme). La sortie est explicitement une **PROPOSITION** soumise à la revue
de couplage, jamais une décision.

## Entrée

- `factory-docs/work/product-brief.md`
- `factory-docs/work/glossaire.md`

Gabarits de sortie : `factory-docs/templates/spec-index.md` et
`factory-docs/templates/coupling-map.md` (copie installée par cadrage-init).

## Porte d'entrée

**`definition_of_ready.vision_complete == true`** (équivalent : `product_brief`
au statut validé sur le plan direction). Sinon, **refuse d'agir** et oriente vers
`cadrage-vision`.

## Méthode — trois passes

1. **Passe surface.** Lister les grandes capacités du périmètre IN. Vue à plat
   des activités utilisateur.
2. **Passe parcours.** Ordonner **par valeur/importance** (vision PO), via story
   mapping (backbone d'activités, puis tranches). En déduire la frontière du MVP.
   L'ordre est fonctionnel, pas un ordre de fabrication technique.
3. **Passe risque.** Repérer les zones de risque et de couplage **pressenties**
   (hypothèse), pour les signaler à l'architecture — sans trancher les frontières
   techniques ici.

**Règles de découpage :**
- Chaque use case est une **tranche verticale de valeur** : il livre de la valeur
  de bout en bout, jamais une couche technique (pas de « base de données » ou
  « API »).
- **Préoccupations transverses ≠ use cases.** Identifier **d'abord** les concerns
  **transverses** — authentification, **droits / contrôle d'accès / filtrage par
  droits**, journalisation, audit, i18n, observabilité : ils traversent plusieurs use
  cases et ne livrent pas de valeur isolée. **Ne pas en faire des use cases** ; les
  noter comme **contraintes transverses** (dans `coupling-map.md` et le project-frame),
  reprises ensuite par l'architecte/designer sur toutes les features. **Ne jamais
  créer un use case « filtrage par droits » pour le supprimer ensuite.**
- **Walking skeleton candidat** : proposer un use case candidat pour la première
  tranche de bout en bout. Le walking skeleton **définitif** est désigné à
  l'architecture (il dé-risque la stack).
- **Calibrage 5 à 10 use cases** pour l'enveloppe de jours. Si la matière en
  produit moins ou plus, le dire, ne pas forcer artificiellement.

## Sorties

### `spec-index.md`
En tête, le bandeau en **langage clair** : « **Proposition fonctionnelle — revue
de couplage pas encore faite** » (cf. `references/ux-conventions.md`). L'artefact
peut conserver un champ machine (`arbitrated: false`) **non affiché** à
l'utilisateur ; tout texte adressé à l'utilisateur reste en clair. Un use
case par ligne : `id` (provisoire `UC…`), `nom`, `frontière IN`, `frontière OUT`,
`activités utilisateur couvertes (source)`, `couplage pressenti (hypothèse)`,
`MVP oui/non`. Plus la frontière du MVP (par valeur), le walking skeleton
**candidat**, et la **section couverture du périmètre IN** (chaque capacité IN du
product-brief → use case(s) ; capacité non couverte = `[À VALIDER]` bloquant).
Chaque énoncé porte sa **source** ; marquer `[À VALIDER]` toute frontière ou
couplage non tranché par la matière.

### `coupling-map.md`
États partagés entre features, couplages directs, vue de parallélisme (ce qui
peut avancer ensemble, ce qui doit attendre, chemin critique), et la liste des
points à arbitrer en revue de couplage. Le walking skeleton est défini dans le
`spec-index.md` (source unique) ; la coupling-map n'en reprend que les couplages
à arbitrer en premier.

## Restituer le découpage en session (corr #10 + #11)

Une fois les use cases écrits dans le gabarit, **restituer la proposition dans le
chat sous forme de tableau, en français Product Owner** :
- **Parler valeur et usage**, pas technique (cf. `references/ux-conventions.md`,
  langage produit). Pour chaque use case : ce qu'il permet de faire, pour qui,
  quelle valeur, et s'il est dans le MVP ou non.
- **Aucun nom de champ, aucune clé JSON, aucun identifiant technique** dans la
  sortie affichée : pas de `UC…`, pas de `arbitrated`, pas de noms d'attributs du
  manifeste. Les identifiants provisoires restent **internes à l'artefact** ; à
  l'écran on nomme le use case par son intitulé métier.
- Présenter la proposition comme une **proposition** (pas une décision), avec la
  frontière du MVP exprimée en valeur.
- **Demander à l'utilisateur si des modifications sont nécessaires** (reformuler,
  fusionner, scinder, déplacer la frontière du MVP). **Appliquer** les
  changements demandés dans l'artefact, puis enchaîner sur la suite.

## Porte de sortie

Avant d'écrire le manifeste, vérifier :
- **Chaque use case est une tranche verticale de valeur** (livre-t-il de la valeur
  de bout en bout ?). Pas de couche technique déguisée en use case.
- **Chaque use case a une frontière (IN/OUT) et son couplage pressenti (hypothèse).**
- **La carte de couplage (hypothèse) est produite.**
- **La frontière du MVP est marquée** (par valeur).
- **La couverture du périmètre IN est complète** : chaque capacité IN du
  product-brief est mappée à ≥1 use case ; toute capacité non couverte est un trou
  **bloquant** `[À VALIDER]`.
- **Chaque énoncé porte sa source** ; sinon `[À VALIDER]`.
- **L'arbitrage reste à faire.** La sortie porte la mention « proposition
  fonctionnelle — revue de couplage pas encore faite » (le champ machine
  `arbitrated` reste faux, non affiché) ; la numérotation/séquencement définitif
  et le walking skeleton relèvent de l'architecture ; revue de couplage humaine
  requise.

## Réjeu incrémental (idempotence)

Rejoué après une vision corrigée (retour de démonstrateur, clarification levée),
ce skill **met à jour le découpage en place** :
- **Préserve** la trace de ce qui était déjà arbitré et le contenu inchangé.
- **Applique** les déplacements de frontière, ajouts ou fusions de features que la
  vision corrigée impose.
- **Retire** les marqueurs résolus, **signale** les nouveaux.
- **N'écrase jamais en silence** une feature contredite : elle est marquée
  `[REMIS EN CAUSE]`, pas supprimée à la dérobée.

**Reset d'arbitrage (règle dure).** Si le réjeu **change matériellement** le
découpage — feature ajoutée, fusionnée, supprimée, ou frontière/dépendance
déplacée — le skill **repasse `spec_index.arbitrated` et
`definition_of_ready.decoupage_arbitrated` à `false`**, avec une note « arbitrage
à refaire suite à : <cause> ». Un découpage qui a bougé n'est plus arbitré : la
revue de couplage humaine doit le re-trancher. Le skill ne maintient jamais un
drapeau « arbitré » sur une proposition modifiée. Un réjeu **sans** changement
matériel (reformulation, marqueur levé) laisse l'arbitrage en l'état.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.spec_index.features = <nombre>`, `.mvp_features = <nombre MVP>`.
- `.arbitrated` : `false` en première production (**toujours**) ; en réjeu, remis
  à `false` si changement matériel, sinon laissé tel quel (voir Réjeu incrémental).
  Le skill ne le passe **jamais** à `true` de lui-même.
- `definition_of_ready.decoupage_arbitrated` : le skill **ne le passe jamais à
  vrai**. En première production il reste `false` ; en réjeu, il est remis à
  `false` si le découpage a changé matériellement, sinon laissé en l'état. Seul
  l'humain le passe à `true`, en revue de couplage.
- `phase = "decoupage"`.
- `validation_points[]` : ajouter les points d'arbitrage et les frontières
  `[À VALIDER]`, `status = "open"`, `raised_by = "decoupage"`.
- `updated_at` à l'horodatage courant.

## Revue de couplage (arbitrage humain, conduit en session — corr #12)

C'est **la revue de couplage** : l'arbitrage humain du découpage, **obligatoire avant
les briefs**. C'est une **décision humaine**, mais elle se conduit **entièrement dans
le chat** : le skill anime la revue, l'humain tranche, le skill écrit ensuite la trace. **Ne jamais demander à l'utilisateur d'ouvrir ou
d'éditer un fichier markdown pour arbitrer** : les fichiers `.md` ne servent qu'à
**lire** la documentation, jamais de support de décision.

Déroulé :
1. **Poser les points d'arbitrage un par un**, via la boucle interactive
   (cf. `references/interactive-loop.md`). Pour chaque point (état partagé,
   couplage direct, ce qui peut avancer en parallèle, chemin critique) : exposer
   le point en langage clair et proposer **trois options** — (1) **décision
   recommandée** (suggestion, clairement étiquetée comme telle), (2) **passer pour
   l'instant** (reste un point ouvert, ne débloque aucune gate), (3) **saisir ma
   décision**. **Attendre la réponse** avant le point suivant.
2. **Collecter les décisions de l'utilisateur en session**, point par point, sans
   rien inventer ni trancher à sa place (cf. `references/interactive-loop.md`,
   « capter, ne pas combler »).
3. **Une fois les décisions recueillies**, le skill **écrit le journal**
   `factory-docs/work/arbitrage-log.md` (append-only : date, décision,
   use cases/états concernés, raison pour chaque point arbitré) et incrémente
   `artifacts.arbitrage_log.entries` dans le manifeste.
4. **Poser ensuite les drapeaux d'arbitrage** : si l'utilisateur a effectivement
   tranché la revue, passer `spec_index.arbitrated` et
   `definition_of_ready.decoupage_arbitrated` à `true`, **et mettre à jour les en-têtes de
   `spec-index.md` ET de `coupling-map.md`** → « Revue de couplage close (AAAA-MM-JJ) » (ne jamais
   laisser « revue pas encore faite » sur un découpage arbitré). S'il reste des points
   passés/ouverts, ils demeurent **bloquants** et la revue n'est pas close. Sans
   cet arbitrage humain, `cadrage-briefs` refusera de tourner.

Le journal est **append-only** : il survit aux réjeux de découpage qui
réinitialisent l'arbitrage, gardant la mémoire des décisions passées.

## Livrable visuel

La carte de découpage et dépendances (visualisation interactive pour la revue de
couplage) se génère dans Claude Design. Le prompt prêt à coller est dans
`references/carte-decoupage-prompt.md` (gabarit statique). Le prompt utilisé est
sauvegardé sous `factory-prompts/<NNN>-<JJ-MM>-carte-decoupage/` et tracé dans
`prompts[]`.

## Règles invariantes appliquées ici

- **Proposer, ne pas décider.** Le cœur de ce skill. `arbitrated` reste faux,
  toujours. La sortie est une proposition, pas une décision.
- **Marquer, ne pas inventer.** Frontières et dépendances non tranchées →
  `[À VALIDER]`.
- **Tranches verticales.** Jamais de découpage en couches techniques.
- **Skill indépendant.** Porte d'entrée et mise à jour via le manifeste.

Étape suivante : `/cadrage:cadrage-demonstrateur-brief` — produire le prompt du démonstrateur. La maquette doit être **validée par le client** et la **revue de couplage** faite **avant** les briefs (ordre : découpage + revue de couplage → boucle démonstrateur → briefs).
