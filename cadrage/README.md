# Cadrage Amont

Plugin Claude qui **industrialise la phase amont d'un projet spec-driven**. Il
transforme de la matière brute — transcripts Notion, fichiers texte — en un **pack
fonctionnel** repris par l'architecte : vision, glossaire, découpage, un brief par
feature. Tout est écrit dans `cadrage-out/` (la mécanique interne vit dans `.factory/`).

Il couvre deux travaux distincts : **capter la vision produit**, puis la
**découper en features cohérentes et fabricables**.

> Le plugin n'est pas un outil de saisie. La matière existe déjà dans les
> transcripts. Les skills transforment, valident et structurent — ils ne
> ressaisissent rien.

## Principe : une ligne de production, un manifeste partagé

Chaque skill fait une chose et est **invocable seul**. La cohérence ne vient pas
d'un orchestrateur, elle vient d'un fichier d'état unique, le **manifeste**
(`manifest.json`), que tous les skills lisent et mettent à
jour en read-modify-write. Chaque skill vérifie ses **pré-requis** en silence avant
d'agir et contrôle sa sortie avant d'écrire le manifeste — sans jamais exposer de
« porte » à l'utilisateur.

## Les dix skills, dans l'ordre du pipeline

| # | Skill | Rôle | Pré-requis |
|---|-------|------|----------------|
| 0 | `cadrage-init` | Amorce `.factory/` (gabarits, git-ignoré) + `cadrage-out/` (**+ manifeste committé**) + `cadrage-out/prompts/` | aucune (projet vierge) |
| 1 | `cadrage-extraction` | Matière brute → `capture-brute.md` (contenu, sans horodatage ni src) + **passe découverte** (13 questions, interactif) → `project-frame.md` | manifeste existe + une source déclarée |
| 2 | `cadrage-vision` | Capture → `product-brief.md` (le quoi, le pourquoi) | capture_brute existe |
| 3 | `cadrage-glossaire` | Construit le langage ubiquitaire **du projet** (termes métier, pas les outils/acronymes), validé en bloc | capture_brute existe |
| 4 | `cadrage-decoupage` | Vision → découpage **fonctionnel** (use cases par valeur) + couplage (**hypothèse**) | vision_complete |
| 5 | `cadrage-demonstrateur-brief` | Prompt Claude Design du démonstrateur (mode initial / adaptatif) | vision dispo. / retour dispo. |
| 6 | `cadrage-retour-demonstrateur` | Ingère le retour client, résout et **invalide** les points | retour disponible |
| 7 | `cadrage-clarification` | Repose en session les questions restées sans réponse | ≥1 point à clarifier |
| 8 | `cadrage-briefs` | Un brief auto-portant par feature (contrat central) | **decoupage_arbitrated ET demonstrateur_converged** |
| 9 | `cadrage-completude` | **Étape terminale** : bilan Definition of Ready + résolution en session, puis relais vers l'architecte | aucune |
| — | `help-factory` | Aide unique : carte des 4 plugins, un tableau par plugin (rôle, ordre, décisions humaines) | aucune |

Flux nominal : extraction → vision & glossaire → decoupage → **prompt
démonstrateur → maquette (Claude Design) → balayage client → atelier de
validation → retour → réjeu incrémental → prompt adaptatif → maquette**, en
boucle jusqu'à `demonstrateur_converged` → **revue de couplage humaine** → briefs
→ completude → **`/architecte:architecte-init`**. Il n'y a **plus de skill handoff** :
l'architecte (puis l'assembleur) lisent directement les fichiers de `cadrage-out/`.

### La boucle démonstrateur (incrémentale)

La cadrage n'est pas linéaire : le client réagit à un démonstrateur, ses
réactions sont des exigences déguisées qui raffinent **ou contredisent** la
vision, et on régénère la maquette jusqu'à convergence. Le plugin outille ce
cycle **sans jamais générer la maquette lui-même** (ce geste reste dans Claude
Design). Deux propriétés clés :

- **Idempotence.** Rejoués après une correction, `vision`, `glossaire` et
  `decoupage` **mettent à jour leur artefact en place** : ils préservent le
  validé, retirent les marqueurs résolus, signalent les nouveaux, sans duplication
  ni écrasement silencieux.
- **Capter ET invalider.** Un retour peut **remettre en cause un acquis**
  (`[REMIS EN CAUSE]`), pas seulement l'enrichir. Sinon la cadrage accumule des
  couches contradictoires au lieu de converger.

## Trois décisions humaines structurantes, jamais automatisées

- **Direction produit** — la boucle démonstrateur. Le client valide la
  maquette (`demonstrateur.client_validated`, geste humain), ce qui, avec aucun
  point bloquant ouvert, allume `demonstrateur_converged`.
- **Revue de couplage** — entre `decoupage` et `briefs`. L'humain arbitre la
  proposition **en session** ; les décisions sont écrites **en place** dans la
  carte de couplage, puis `arbitrated` passe à vrai. Un réjeu de découpage qui
  change matériellement la proposition **réinitialise** cet arbitrage.
- **Cadrage terminé** — `cadrage_complete`, calculée par `completude` : c'est la
  dernière étape avant l'architecte, qui lit ensuite directement `cadrage-out/`.

Ces conditions sont vérifiées **en silence**, jamais affichées comme des « portes ».
`cadrage-briefs` requiert `decoupage_arbitrated` **et** `demonstrateur_converged` —
un brief dérive d'une vision stable.

## Règles invariantes

- **Proposer, ne pas décider.** Le découpage est un arbitrage humain.
  `cadrage-decoupage` ne passe jamais `arbitrated` à vrai de lui-même.
- **Deux découpages.** La captation produit un découpage **fonctionnel** (use cases
  par valeur, vision PO, **sans MVP**) + une carte de couplage = **hypothèse**. La
  liste de features **numérotée et séquencée** (et le walking skeleton) se fige **en
  sortie d'architecture**. Les arbitrages de la revue de couplage sont écrits **en
  place** dans `coupling-map.md` (pas de journal séparé).
- **Contenu, pas provenance.** Les artefacts contiennent le **contenu décidé** : ni
  horodatage, ni interlocuteur, ni `(src:)`.
- **Découverte cadrée.** `cadrage-extraction` couvre 13 questions de cadrage
  (`skills/cadrage-extraction/references/discovery-questions.md`) : extraites du
  transcript, les manquantes posées **une par une**, stockées dans le
  `project-frame.md` et le bloc `discovery` du manifeste. Garde-fou déterministe :
  `scripts/check_discovery.py` échoue tant qu'une question n'a pas de statut. Les
  questions de charge/disponibilité/performance sont des *seeds qualité* pour
  l'architecte.
- **Ne pas inventer, ne rien persister d'ouvert.** Un élément non soutenu par la
  matière est **omis** (pas de placeholder écrit) ; ce qui reste à trancher se
  **résout en session** en posant la question. Seul `[REMIS EN CAUSE]` subsiste
  dans un artefact (acquis contredit par un retour).
- **Deux altitudes de validation.** La direction produit se valide une fois, par
  le prototype, hors plugin. La spécification se valide par feature, plus tard dans
  la chaîne (architecte → assembleur → SpecKit).
- **Frontière des artefacts.** Tous les documents du cadrage (vision, glossaire,
  découpage, briefs) sont dans `cadrage-out/`, et le **manifeste committé** (`manifest.json`)
  est **à la racine** du projet ; seuls les **gabarits** vivent dans `.factory/` (git-ignoré). L'architecte puis l'assembleur lisent directement
  ces fichiers ; la constitution finale convergée est produite par l'assembleur.
- **Skills indépendants.** Pas d'orchestrateur monolithique. La cohérence vient
  du manifeste.

## Structure

```
cadrage/
├── .claude-plugin/plugin.json     # manifeste du plugin
├── skills/                        # un dossier SKILL.md par skill (dont cadrage-init)
├── references/                    # conventions partagées (boucle interactive, UX)
├── scripts/                       # check_discovery.py (garde-fou déterministe)
├── templates/                     # gabarits EN des artefacts (project-frame, product-brief,
│                                  #   feature-brief ← contrat central, spec-index, coupling-map,
│                                  #   glossaire)
└── README.md
```

Le **contrat central** est `templates/feature-brief.md` : l'artefact
dont tout le pipeline dépend. `cadrage-briefs` le produit, `cadrage-completude`
le valide, l'architecte puis l'assembleur le reprennent. Il doit être auto-portant.
**Templates en anglais** (lus par le LLM) ; **interaction en français**.

## Workspace du projet client (créé par `cadrage-init`)

```
.factory/                          # caché, git-ignoré — gabarits seulement
└── cadrage/                       # gabarits FR du cadrage (copies projet)
manifest.json                      # contrat machine — COMMITTÉ à la racine, voyage avec le repo
cadrage-out/                       # documents générés, COMMITTÉ (à la racine)
├── source-contexte/               # matière brute déposée par l'utilisateur (facultatif)
├── capture-brute, project-frame, product-brief, glossaire,
│   spec-index, coupling-map, completude-report
└── features-fonctionnels-brief/   # un brief par feature (<feature>.md)
cadrage-out/prompts/               # prompts générés, en <NNN>-<JJ-MM>-<nom>.md (fichiers plats)
```
`cadrage-init` **ne demande aucun nom** ; c'est `cadrage-extraction` qui demande le **nom du projet** (le nom du client n'est jamais collecté).
Le plugin est l'outil ; `.factory/`, `cadrage-out/` et `cadrage-out/prompts/` portent l'état
et les livrables d'UN projet client. La **constitution finale** convergée est produite
plus tard par l'assembleur, pas ici.
