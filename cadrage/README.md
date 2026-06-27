# Cadrage Amont

Plugin Claude qui **industrialise la phase amont d'un projet spec-driven**. Il
transforme de la matière brute — transcripts Notion, fichiers texte — en un repo
SpecKit prêt à lancer : une pré-constitution, un brief par feature, un spec index.

Il couvre deux travaux distincts : **capter la vision produit**, puis la
**découper en features cohérentes et fabricables**.

> Le plugin n'est pas un outil de saisie. La matière existe déjà dans les
> transcripts. Les skills transforment, valident et structurent — ils ne
> ressaisissent rien.

## Principe : une ligne de production, un manifeste partagé

Chaque skill fait une chose et est **invocable seul**. La cohérence ne vient pas
d'un orchestrateur, elle vient d'un fichier d'état unique, le **manifeste**
(`factory-docs/manifest.json`), que tous les skills lisent et mettent à
jour en read-modify-write. Chaque skill vérifie sa **porte d'entrée** avant
d'agir et sa **porte de sortie** avant d'écrire le manifeste.

## Les onze skills, dans l'ordre du pipeline

| # | Skill | Rôle | Porte d'entrée |
|---|-------|------|----------------|
| 0 | `cadrage-init` | Amorce le workspace `factory-docs/` + `factory-prompts/`, installe les gabarits, crée le manifeste | aucune (projet vierge) |
| 1 | `cadrage-extraction` | Matière brute → `capture-brute.md` + **passe découverte** (13 questions, interactif) → `project-frame.md` | manifeste existe + une source déclarée |
| 2 | `cadrage-vision` | Capture → `product-brief.md` (le quoi, le pourquoi) | capture_brute existe |
| 3 | `cadrage-glossaire` | Construit le langage ubiquitaire sourcé | capture_brute existe |
| 4 | `cadrage-decoupage` | Vision → découpage **fonctionnel** (use cases par valeur) + couplage (**hypothèse**) | vision_complete |
| 5 | `cadrage-demonstrateur-brief` | Prompt Claude Design du démonstrateur (mode initial / adaptatif) | vision dispo. / retour dispo. |
| 6 | `cadrage-retour-demonstrateur` | Ingère le retour client, résout et **invalide** les points | retour disponible |
| 7 | `cadrage-clarification` | Agrège les points à valider → **liste de balayage client** | ≥1 point ouvert |
| 8 | `cadrage-briefs` | Un brief auto-portant par feature (contrat central) | **decoupage_arbitrated ET demonstrateur_converged** |
| 9 | `cadrage-completude` | Confronte le manifeste à la Definition of Ready | aucune |
| 10 | `cadrage-handoff` | Prépare la pré-constitution + dépose briefs + spec index dans le repo SpecKit | **ready_for_speckit** |
| — | `help-cadrage` | Affiche le rôle de chaque skill et l'ordre d'exécution (aide) | aucune |

Flux nominal : extraction → vision & glossaire → decoupage → **prompt
démonstrateur → maquette (Claude Design) → balayage client → atelier de
validation → retour → réjeu incrémental → prompt adaptatif → maquette**, en
boucle jusqu'à `demonstrateur_converged` → **revue de couplage humaine** → briefs
→ completude → handoff quand la porte maîtresse est verte.

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

## Trois portes structurantes, jamais automatisées

- **Porte 1, direction produit** — la boucle démonstrateur. Le client valide la
  maquette (`demonstrateur.client_validated`, geste humain), ce qui, avec aucun
  point bloquant ouvert, allume `demonstrateur_converged`.
- **Revue de couplage** — entre `decoupage` et `briefs`. L'humain arbitre la
  proposition et passe `arbitrated` à vrai. Un réjeu de découpage qui change
  matériellement la proposition **réinitialise** cet arbitrage.
- **Porte maîtresse, prêt pour SpecKit** — `ready_for_speckit`, calculée par
  `completude`. Sans elle, `handoff` ne tourne pas.

`cadrage-briefs` est gardé par une **double condition** : `decoupage_arbitrated`
**et** `demonstrateur_converged` — un brief dérive d'une vision stable.

## Règles invariantes

- **Proposer, ne pas décider.** Le découpage est un arbitrage humain.
  `cadrage-decoupage` ne passe jamais `arbitrated` à vrai de lui-même.
- **Deux découpages.** La captation produit un découpage **fonctionnel** (use cases
  par valeur, vision PO) + une carte de couplage = **hypothèse**. La liste de
  features **numérotée et séquencée** (et le walking skeleton) se fige **en sortie
  d'architecture**. Les arbitrages de la revue de couplage sont tracés dans
  `arbitrage-log.md` (append-only).
- **Traçabilité source.** Chaque énoncé des artefacts porte sa source `(src:)` ;
  sans trace → `[À VALIDER]`.
- **Découverte cadrée.** `cadrage-extraction` couvre 13 questions de cadrage
  (`skills/cadrage-extraction/references/discovery-questions.md`) : extraites du
  transcript, les manquantes posées **une par une**, stockées dans le
  `project-frame.md` et le bloc `discovery` du manifeste. Garde-fou déterministe :
  `scripts/check_discovery.py` échoue tant qu'une question n'a pas de statut. Les
  questions de charge/disponibilité/performance sont des *seeds qualité* pour
  l'architecte.
- **Marquer, ne pas inventer.** Tout élément sans trace dans la source est
  marqué `[À VALIDER]` ou `[NON COUVERT EN ATELIER]`. Jamais de comblement.
- **Deux altitudes de validation.** La direction produit se valide une fois, par
  le prototype, hors plugin. La spécification se valide par feature, au niveau du
  brief et de `/speckit.clarify`, après le handoff.
- **Frontière des artefacts.** Documents de travail (vision, glossaire,
  pré-constitution) → workspace `factory-docs/`. Artefacts de fabrication (briefs,
  spec index) → markdown dans le repo SpecKit ; la constitution finale est générée
  par SpecKit. Le skill `cadrage-handoff` matérialise la frontière.
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
│                                  #   glossaire, arbitrage-log, pre-constitution)
└── README.md
```

Le **contrat central** est `templates/feature-brief.md` : l'artefact
dont tout le pipeline dépend. `cadrage-briefs` le produit, `cadrage-completude`
le valide, SpecKit le consomme. Il doit être auto-portant. **Templates en anglais**
(lus par le LLM) ; **interaction en français** (questions, refus, résumés).

## Workspace du projet client (créé par `cadrage-init`)

Structure **plate** :
```
factory-docs/
├── manifest.json     # état machine du projet
├── templates/        # copies des gabarits installées dans le projet
└── work/             # TOUS les artefacts à plat (capture-brute, project-frame,
                      #   product-brief, glossaire, spec-index, coupling-map,
                      #   arbitrage-log, 00X-*.brief.md, pre-constitution, completude-report)
factory-prompts/      # prompts générés, en <NNN>-<JJ-MM>-<nom>/
```
`cadrage-init` **ne demande aucun nom** ; c'est `cadrage-extraction` qui demande le **nom du projet** (le nom du client n'est jamais collecté).
Le plugin est l'outil ; `factory-docs/` et `factory-prompts/` portent l'état et
les livrables d'UN projet client. La **constitution finale** n'est pas produite
ici : SpecKit la génère à partir de `factory-docs/work/pre-constitution.md`.
