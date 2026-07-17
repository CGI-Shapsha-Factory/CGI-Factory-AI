---
name: cadrage-decoupage
description: Propose un découpage fonctionnel en use cases de valeur, plus une hypothèse de couplage.
---

# cadrage-decoupage

Troisième étape. Transforme la vision en une **proposition de découpage
fonctionnel** (use cases / capacités, par valeur), plus la carte de couplage
(hypothèse) qui sert d'appui à l'arbitrage humain. **Propose, ne décide pas.**

## Principe des deux découpages

La captation produit le **découpage fonctionnel** - ce que fait le produit et dans
quel ordre d'importance, **depuis la vision PO seule, sans stack ni architecture**.
La **liste de features numérotées et séquencée** (et le walking skeleton, qui
dé-risque la stack) se fige **en sortie d'architecture** : l'architecture confronte
cette coupe fonctionnelle aux contrats et au squelette technique. Ici, IDs (`UC...`)
et ordre sont **provisoires**, le couplage est une **hypothèse**.

## Objectif

Produire un **découpage fonctionnel** (use cases ordonnés par valeur, tranches
verticales) et une **carte de couplage** (hypothèse : états partagés,
parallélisme). La sortie est explicitement une **PROPOSITION** soumise à la revue
de couplage, jamais une décision.

## Entrée

- `cadrage-out/product-brief.md`
- `cadrage-out/glossaire.md`

Gabarits de sortie : `.factory/cadrage/spec-index.md` et
`.factory/cadrage/coupling-map.md` (copie installée par cadrage-init).

## Pré-requis (vérification silencieuse)

La vision produit est disponible (`product_brief` validé sur le plan direction).
Sinon, le dire en clair et proposer de faire la vision d'abord - sans afficher de
"porte". Si la direction produit est déjà claire dans la matière, on peut avancer.

## Méthode : trois passes

1. **Passe surface.** Lister les grandes capacités du périmètre IN. Vue à plat
   des activités utilisateur.
2. **Passe parcours.** Ordonner **par valeur/importance** (vision PO), via story
   mapping (backbone d'activités, puis tranches). L'ordre est fonctionnel, pas un
   ordre de fabrication technique. **Aucune notion de MVP / post-MVP.**
3. **Passe risque.** Repérer les zones de risque et de couplage **pressenties**
   (hypothèse), pour les signaler à l'architecture - sans trancher les frontières
   techniques ici.

**Règles de découpage :**
- Chaque use case est une **tranche verticale de valeur** : il livre de la valeur
  de bout en bout, jamais une couche technique (pas de "base de données" ou
  "API").
- **Préoccupations transverses ≠ use cases.** Identifier **d'abord** les concerns
  **transverses** - authentification, **droits / contrôle d'accès / filtrage par
  droits**, journalisation, audit, i18n, observabilité : ils traversent plusieurs use
  cases et ne livrent pas de valeur isolée. **Ne pas en faire des use cases** ; les
  noter comme **contraintes transverses** (dans `coupling-map.md` et le project-frame),
  reprises ensuite par l'architecte/designer sur toutes les features. **Ne jamais
  créer un use case "filtrage par droits" pour le supprimer ensuite.**
- **Walking skeleton candidat** : proposer un use case candidat pour la première
  tranche de bout en bout. Le walking skeleton **définitif** est désigné à
  l'architecture (il dé-risque la stack).
- **Calibrage 5 à 10 use cases** pour l'enveloppe de jours. Si la matière en
  produit moins ou plus, le dire, ne pas forcer artificiellement.

## Sorties

### `spec-index.md`
En tête, le bandeau en **langage clair** : "**Proposition fonctionnelle - revue
de couplage pas encore faite**" (cf. `references/ux-conventions.md`). L'artefact
peut conserver un champ machine (`arbitrated: false`) **non affiché** à
l'utilisateur ; tout texte adressé à l'utilisateur reste en clair. Un use
case par ligne : `id` (provisoire `UC...`), `nom`, `frontière IN`, `frontière OUT`,
`activités utilisateur couvertes`, `couplage pressenti (hypothèse)`. **Pas de champ
MVP.** Plus le walking skeleton **candidat** et la **section couverture du périmètre
IN** (chaque capacité IN du product-brief -> use case(s)). **Aucune provenance écrite**
(pas de `(src:)`) ; les frontières non tranchées par la matière sont **tranchées en
session** lors de la revue de couplage, pas marquées `[À VALIDER]`.

### `coupling-map.md`
États partagés entre features, couplages directs, vue de parallélisme (ce qui
peut avancer ensemble, ce qui doit attendre, chemin critique). Le walking skeleton
est défini dans le `spec-index.md` (source unique). **Pas de section "points à
arbitrer" persistée** : les arbitrages se font en session et les décisions sont
écrites **en place** dans la carte (cf. "Revue de couplage").

## Restituer le découpage en session (corr #10 + #11)

Une fois les use cases écrits dans le gabarit, **restituer la proposition dans le
chat sous forme de tableau à TROIS colonnes, en français Product Owner** :
- **Exactement trois colonnes : `Use case` · `Ce que ça permet` · `Pour qui`.** Pas de quatrième
  colonne (ni `MVP`, ni autre).
- **Parler valeur et usage**, pas technique (cf. `references/ux-conventions.md`,
  langage produit). Pour chaque use case : ce qu'il permet de faire et pour qui.
- **Aucune notion de MVP / post-MVP** : ne pas l'afficher, ne pas en parler.
- **Aucun nom de champ, aucune clé JSON, aucun nom d'attribut du manifeste** dans la
  sortie affichée (pas de `arbitrated`, pas de clés internes). **Les use cases, eux, se
  nomment par leur intitulé complet en langage naturel suivi de leur référence entre
  parenthèses** - `Intitulé complet du use case (UC1)`, **jamais un `UC1` nu** - pour que
  l'utilisateur garde un repère stable sans mémoriser les numéros (cf.
  `references/ux-conventions.md`, §3ter). Dans le tableau, la colonne `Use case` porte cet
  **intitulé complet suivi de `(UCn)`**.
- Présenter la proposition comme une **proposition** (pas une décision).
- **Demander à l'utilisateur si des modifications sont nécessaires** (reformuler,
  fusionner, scinder, réordonner). **Appliquer** les changements demandés dans
  l'artefact, puis enchaîner sur la suite.

## Vérification avant écriture

Avant d'écrire le manifeste, vérifier :
- **Chaque use case est une tranche verticale de valeur** (livre-t-il de la valeur
  de bout en bout ?). Pas de couche technique déguisée en use case.
- **Chaque use case a une frontière (IN/OUT) et son couplage pressenti (hypothèse).**
- **La carte de couplage (hypothèse) est produite.**
- **La couverture du périmètre IN est complète** : chaque capacité IN du
  product-brief est mappée à ≥1 use case ; une capacité non couverte est **tranchée
  en session** (on demande), pas marquée `[À VALIDER]`.
- **Aucune provenance écrite** (pas de `(src:)`), **aucune notion de MVP**.
- **L'arbitrage reste à faire.** La sortie porte la mention "proposition
  fonctionnelle - revue de couplage pas encore faite" (le champ machine
  `arbitrated` reste faux, non affiché) ; la numérotation/séquencement définitif
  et le walking skeleton relèvent de l'architecture ; revue de couplage humaine
  requise.

## Réjeu incrémental (idempotence)

Rejoué après une vision corrigée (retour de démonstrateur, point levé en session),
ce skill **met à jour le découpage en place** :
- **Préserve** la trace de ce qui était déjà arbitré et le contenu inchangé.
- **Applique** les déplacements de frontière, ajouts ou fusions de features que la
  vision corrigée impose.
- **Retire** les marqueurs résolus, **signale** les nouveaux.
- **N'écrase jamais en silence** une feature contredite : elle est marquée
  `[REMIS EN CAUSE]`, pas supprimée à la dérobée.

**Reset d'arbitrage (règle dure).** Si le réjeu **change matériellement** le
découpage - feature ajoutée, fusionnée, supprimée, ou frontière/dépendance
déplacée - le skill **repasse `spec_index.arbitrated` et
`definition_of_ready.decoupage_arbitrated` à `false`**, avec une note "arbitrage
à refaire suite à : <cause>". Un découpage qui a bougé n'est plus arbitré : la
revue de couplage humaine doit le re-trancher. Le skill ne maintient jamais un
drapeau "arbitré" sur une proposition modifiée. Un réjeu **sans** changement
matériel (reformulation, marqueur levé) laisse l'arbitrage en l'état.

## Mise à jour du manifeste

Read-modify-write puis revalidation JSON :
- `artifacts.spec_index.features = <nombre>`. **Pas de `.mvp_features`.**
- `.arbitrated` : `false` en première production (**toujours**) ; passe à `true`
  seulement après que l'utilisateur a tranché la revue de couplage **en session**
  (voir ci-dessous). En réjeu avec changement matériel, repasse à `false`.
- `definition_of_ready.decoupage_arbitrated` : passe à `true` **une fois que
  l'utilisateur a résolu les points en session** (décision humaine, légitime). En
  première production il reste `false` ; en réjeu avec changement matériel, remis à
  `false`.
- `phase = "decoupage"`.
- `updated_at` à l'horodatage courant.

> **Silencieux - jamais annoncé.** Ne **jamais** dire à l'utilisateur que le manifeste est mis à jour,
> ni citer un nom de champ ou une valeur `true`/`false` (interdit : "Manifeste à jour : phase:
> decoupage, decoupage_arbitrated: true", toute liste `champ: valeur`). Confirmer seulement, en clair,
> **ce qui a été produit** + la prochaine étape (cf. `references/ux-conventions.md`).

> **Aucun point ouvert n'est persisté** : pas de `validation_points[]` de découpage,
> pas de `[À VALIDER]` dans les artefacts. Tout point se tranche en session.

## Revue de couplage (arbitrage humain, conduit en session)

C'est **la revue de couplage** : l'arbitrage humain du découpage, **obligatoire avant
les briefs**. Elle se conduit **entièrement dans le chat** : le skill anime la revue,
l'humain tranche, le skill écrit la décision **en place**. **Ne jamais demander à
l'utilisateur d'ouvrir ou d'éditer un fichier markdown pour arbitrer** : les fichiers
`.md` ne servent qu'à **lire**, jamais de support de décision.

Déroulé :
1. **Poser les points d'arbitrage un par un**, via la boucle interactive
   (cf. `references/interactive-loop.md`). Pour chaque point (état partagé,
   couplage direct, ce qui peut avancer en parallèle, chemin critique) : exposer
   le point en langage clair et proposer **une décision recommandée** (suggestion,
   clairement étiquetée). **Chaque mention d'un use case - dans l'énoncé du point, dans la
   décision recommandée ET dans chaque option - le désigne par son intitulé complet en langage
   naturel suivi de sa référence entre parenthèses** (`l'ingestion documentaire (UC3)`),
   **jamais par un `UC3` nu** : l'utilisateur n'a ainsi pas à se rappeler quel numéro
   correspond à quelle capacité. L'utilisateur accepte ou donne la sienne. **Pas de menu
   numéroté** (pas de "3. Saisir ma décision"). **Attendre la réponse** avant le
   point suivant.
2. **Appliquer chaque décision EN PLACE** au fur et à mesure : modifier directement
   `coupling-map.md` (et `spec-index.md` si la frontière/dépendance bouge) pour y
   inscrire le résultat tranché. **Ne créer aucun journal d'arbitrage, n'écrire
   aucun point ouvert.** Un point que l'utilisateur ne tranche pas est simplement
   laissé tel quel dans l'hypothèse, sans marqueur.
3. **Une fois les points résolus**, passer `spec_index.arbitrated` et
   `definition_of_ready.decoupage_arbitrated` à `true`, **et mettre à jour les en-têtes
   de `spec-index.md` ET de `coupling-map.md`** -> "Revue de couplage close
   (AAAA-MM-JJ)". Si l'utilisateur n'a pas voulu trancher, la revue reste ouverte.

## Livrable visuel

La carte de découpage et dépendances (visualisation interactive pour la revue de
couplage) se génère dans Claude Design. Le prompt prêt à coller est dans
`references/carte-decoupage-prompt.md` (gabarit statique). Le prompt utilisé est
sauvegardé sous `cadrage-out/prompts/<NNN>-<JJ-MM>-carte-decoupage.md` et tracé dans
`prompts[]`. Le fichier sauvegardé ne contient **que le corps du prompt** (le bloc de
code du gabarit), sans titre/date/mode/version (cf. `references/ux-conventions.md`).

## Règles invariantes appliquées ici

- **Proposer, puis trancher en session.** La première sortie est une proposition
  (`arbitrated = false`) ; l'arbitrage se fait avec l'utilisateur dans le chat et
  les décisions sont écrites **en place**.
- **Rien d'ouvert persisté.** Aucun `[À VALIDER]`, aucun journal d'arbitrage, aucune
  notion de MVP. Pas de provenance écrite.
- **Tranches verticales.** Jamais de découpage en couches techniques.
- **Skill indépendant.** Pré-requis et mise à jour via le manifeste.

Étape suivante : `/cadrage:cadrage-demonstrateur-brief` - produire le prompt du démonstrateur. La maquette doit être **validée par le client** et la **revue de couplage** faite **avant** les briefs (ordre : découpage + revue de couplage -> boucle démonstrateur -> briefs).
