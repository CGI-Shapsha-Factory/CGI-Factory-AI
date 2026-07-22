# CLAUDE.md : plugin `validation`

This file provides guidance to Claude Code (claude.ai/code) when working **on the
`validation` plugin** (this directory). For the factory-wide overview see `../CLAUDE.md`.

## Ce qu'est le plugin
`validation` industrialise la **recette fonctionnelle d'une feature livrée** : dériver un
**plan de test** depuis les critères d'acceptation de la spécification
(`specs/<feature>/spec.md` - un cas par critère, tracé, critère non testable marqué
`A CLARIFIER`, jamais interprété), **exécuter** ce plan dans le navigateur contre
l'environnement de recette (extension Chrome "Claude in Chrome" en priorité, MCP Playwright
en repli, ou mission différée pour Claude Cowork), **capturer** le déroulé en scénarios
rejouables (capital de non-régression), et produire un **rapport de recette tracé exigence
par exigence** dont le **verdict reste humain** (porte de recette : le testeur est juge et
valideur). Ce n'est **pas un projet applicatif** : des **skills Markdown** + un
`plugin.json`. Pas de build, pas de lint, pas de tests unitaires.

**La validation détecte et trace ; la maintenance traite.** Le tri d'un écart distingue le
**bug** (critère non respecté -> renvoi vers `/maintenance:creation-anomalie`, contenu
pré-rempli) de la **spécification en cause** (critère faux ou incomplet -> renvoi vers
`/maintenance:creation-evolution`, geste PO) et du **critère flou** (clarification ou suivi
Linear). **Aucune anomalie ni évolution n'est créée ici en direct** : la porte de création
unique et ses portes de complétude restent côté maintenance. Seule exception bornée : le **ticket
de suivi** d'un critère flou (sur accord explicite du testeur) - un sous-ticket du ticket
`Feature`, **sans label de recette** (jamais `Anomalie`/`Evolution`, ni `Feature`/`Task`).
Le déclenchement est **toujours manuel** (jamais de hook de déploiement).

## Langue & invocation
Frontmatter `name:` + `description:` ; corps, artefacts et interaction **en français**.
Invocation directe `/validation:<skill>` + auto-invocation par la description. Pas de
`commands/` (un command homonyme d'un skill boucle à l'infini).

## Les 4 skills
| # | skill | rôle | porte |
|---|-------|------|-------|
| 0 | `validation-init` | gabarits dans `.factory/validation/` + bloc manifeste `validation` (adresse de recette, outil habituel - config statique seule) + `.gitignore` complété + état de l'amont signalé (specs/, Linear, maintenance) | jamais bloquant |
| 1 | `plan-de-validation` | `specs/<feature>/spec.md` -> `validation-out/<feature>/plan-de-test.md` : plan **entièrement en tableaux** (vue d'ensemble + déroulé par thème + critères à clarifier), **une ligne = un scénario** `TC-<feature>-NNN` (Given/When/Then traduit en préconditions / étapes séparées par `<br>` / résultat observable), critère **jamais recopié verbatim** (colonne `Source` compacte pour la traçabilité, colonne `Ce qui est vérifié` en phrase française), critère flou = `à clarifier` avec raison dans sa seule table, données de test collectées en boucle interactive, porte de régénération à la relance | **plan validé par le testeur** (humain) |
| 2 | `execution-validation` | **préflight de disponibilité** des outils avant le choix (l'état "disponible / à installer" est porté dans les options, et "(recommandé)" ne va qu'à un outil qui répond), puis choix à chaque lancement : extension Chrome (non installable par le skill - marche à suivre `/chrome`, `claude --chrome`, Web Store ; impasses nommées : clé API / `setup-token`, WSL, fournisseur tiers) / Playwright en repli (**installé directement** par le skill : `claude mcp add playwright --scope <user\|project> -- npx -y @playwright/mcp@latest`, après confirmation et choix de portée, Node 18+ requis, **redémarrage de session obligatoire** avant usage) / mission Cowork différée via `mission-cowork.md` auto-portant, toujours disponible -> `resultats/execution-<JJ-MM>.md` au **contrat commun** (un bloc par cas : verdict OK/KO/NON TESTABLE, déroulé effectif, preuves, constaté vs attendu sur KO) + captures dans `resultats/preuves/` | le testeur choisit l'outil ; l'IA constate, ne juge pas |
| 3 | `rapport-de-recette` | matrice de traçabilité (critère -> cas -> verdict -> preuve -> décision) + tri des écarts un par un avec le testeur (anomalie / évolution / flou -> renvois `/maintenance:*`) + scénarios rejouables `scenarios/TC-*.md` (cas OK) + **porte de recette** : verdict humain inscrit dans le rapport et commenté sur le ticket `Feature` Linear | **verdict de recette** (humain) |

Flux : `validation-init` -> (par feature livrée) `plan-de-validation` -> `execution-validation`
-> `rapport-de-recette` -> écarts traités côté maintenance (`correction-anomalie`,
`realisation-evolution`) -> nouvelle exécution pour lever les réserves si besoin.

## Workspace & manifeste
```
.factory/validation/               # gabarits (git-ignoré, reposé par validation-init)
validation-out/<feature>/          # committé - le handoff de la validation
├── plan-de-test.md
├── mission-cowork.md              # seulement si la voie Cowork est choisie
├── resultats/execution-<JJ-MM>.md # une exécution = un fichier, jamais écrasé
├── resultats/preuves/*.png
├── scenarios/TC-*.md              # non-régression (cas OK, déroulé effectif)
├── rapport-de-recette.md          # matrice + écarts + Verdict de recette
└── _archives/                     # versions archivées par la porte de régénération
```
Bloc manifeste `validation` : `{ phase, environnement_recette, outil_prefere }` -
**configuration statique seulement**. Les verdicts, l'avancement et les écarts vivent dans le
rapport committé et **dans Linear** (jamais dans le manifeste : concurrence multi-dev).

## Frontière SpecKit (lecture seule)
La spécification est **lue, jamais écrite** : clarifier un critère se fait **dans le plan de
test** (sa lecture observable) ; changer le critère lui-même passe par une évolution de
maintenance (geste PO, via les commandes SpecKit). Jamais d'écriture dans `specs/` ni `.specify/`.

## Conventions partagées
`references/interactive-loop.md`, `references/ux-conventions.md` (typographie humaine
incluse), `references/regles-validation.md` (place dans la chaîne, un cas par critère,
tri des écarts, humain/automatisé, fiabilité d'exécution, scénarios rejouables),
`references/execution-navigateur.md` (les trois voies : extension Chrome / Playwright /
mission Cowork, contrat de sortie commun). Porte de régénération : même principe que
l'assembleur (jamais d'écrasement sans choix explicite, question posée **avant** de
regénérer) avec un **écart assumé** : les archives vivent **par feature** sous
`validation-out/<feature>/_archives/` (nommées `<nom>-v<N>.md`, `N` = index croissant -
pas de front-matter `version:` dans les gabarits), car tout le livrable de la validation est
rangé par feature. Les résultats d'exécution, eux, ne passent jamais par la porte : un
fichier par exécution, jamais écrasé.
Garde-fou déterministe : `scripts/check_validation.py` (bloc `validation` + gabarits en
place ; par feature : plan présent et tracé, et si le rapport existe, **verdict rempli**
- la présence du titre de section ne suffit pas, le gabarit le contient toujours).
Gabarits : `templates/{plan-de-test,mission-cowork,rapport-de-recette,scenario-rejouable}.md`.
Identifiant d'un cas de test : `TC-<numéro>-NNN` où `<numéro>` est le **numéro de registre à
3 chiffres** de la feature (ex. `TC-001-003`), jamais le nom complet du dossier `specs/`.
Linear : mêmes patrons que la maintenance (`maintenance/references/linear-maintenance.md`, référence de
ce dépôt ; les skills restent auto-portants et affichent eux-mêmes l'installation du MCP) -
détection
`list_teams`, ticket `Feature` résolu par le numéro en tête de titre, états par **nom**
résolu via `list_issue_statuses` avec vérification de l'état retourné, `save_comment` pour la
trace ; MCP absent = signaler, jamais d'écriture silencieuse ratée.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python -m py_compile scripts/check_validation.py
python scripts/check_validation.py <projet>/manifest.json [<feature>]
```

## Invariants
**L'IA exécute et rapporte, l'humain valide** : le plan est validé par le testeur avant
exécution ; le tri de chaque écart et le verdict de recette sont humains ; le skill ne
prononce jamais le verdict. **Un critère = un cas, cité** (traçabilité totale, aucun critère
écarté en silence). **Jamais interpréter un critère flou** (A CLARIFIER au plan,
NON TESTABLE à l'exécution). **Détection ici, traitement côté maintenance** (jamais de ticket
d'anomalie/évolution créé en direct). **Contrat de sortie commun** aux trois voies
d'exécution. **Fiabilité** : relance unique triée avant KO, budget d'étapes borné, preuve à
chaque verdict, jamais d'action destructive sans confirmation, données de test uniquement.
**Aucun état d'avancement dans le manifeste** (rapport committé + Linear). Restitutions en
prose, manifeste mis à jour en silence ; **typographie humaine** : aucun glyphe de style IA
dans les artefacts/commentaires/sorties (pas de tiret cadratin, de points de suspension
unicode, de flèches unicode, de guillemets à chevrons, ni de coche/croix ; équivalents
clavier, cf. la section Typographie de `references/ux-conventions.md`).
