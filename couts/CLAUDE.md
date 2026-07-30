# CLAUDE.md : plugin `couts`

This file provides guidance to Claude Code (claude.ai/code) when working **on the `couts` plugin**
(this directory). Factory-wide overview: `../CLAUDE.md`.

## Ce qu'est le plugin
`couts` = **mesure du coût de la fabrication** (pas une phase), en **deux natures qui ne se
mélangent jamais** :
- **Coût estimé (simulation)** - les tokens des sessions Claude valorisés au **tarif API**
  ("combien ça coûterait en API"), jamais un montant facturé.
- **Coût réel (facturé)** - les appels **API Gemini** de `revue-gemini`, seuls appels payants de
  la Factory. Mesurés par `assembleur/scripts/gemini_review.py` (qui lit `usage_metadata` du SDK
  `google-genai`), tarifés ici.

**Autonome** et installé dans le **dossier courant**. Skills Markdown + scripts Python ; pas de
build/test. **Aucun chiffre saisi à la main, pas de fichier de config.** (Seule saisie du plugin :
prénom + nom de projet à l'init, une identité qui n'entre dans aucun calcul.)

**Piège de facturation Gemini (vérifié sur un vrai appel).** Le prix de sortie est annoncé
"including thinking tokens", et `thoughts_token_count` **n'est pas compté dans**
`candidates_token_count` : la sortie facturée vaut **candidates + thoughts**. Sur un simple ping
de validation, la mesure réelle donne 4 tokens de sortie visible pour 19 de raisonnement - ne
retenir que `candidates` sous-compterait la facture d'un facteur 5. `cost_report.jours_reels()`
additionne les deux ; ne jamais "simplifier" ce calcul.

## Langue & invocation
- **Tout en français** ; identifiants machine et noms d'outils/formats restent tels quels.
- **Skills uniquement, pas de `commands/`**. Invocation : `/couts:<skill>` + auto par le modèle.

## Les 4 skills
- `couts-init` - pose le compteur **dans le dossier courant** (à lancer tôt, autonome - pas de
  pré-requis). **Une seule question, à la première installation** : prénom du développeur et nom du
  projet, écrits dans `.factory/couts/identite.json` - ils identifieront sa ligne dans le tableau
  d'équipe (`couts-equipe`). Si le fichier existe, rien n'est redemandé ni réécrit
  (idempotence). `references/install_cost_hook.py` copie `turn_cost.py` en
  `.claude/hooks/` **et fusionne** le hook `SessionEnd` dans `.claude/settings.json` (sans écraser
  les hooks existants ; commande ancrée sur `${CLAUDE_PROJECT_DIR}`, lanceur Python détecté à
  l'installation), installe la table de prix datée dans `.factory/couts/`, crée `.factory/couts/` +
  **`.gitignore`** (ligne `.factory/` - tout `.factory/` est git-ignoré). Interaction **en français,
  sans exposer la mécanique**.
- `couts-rapport` - restitue **deux tableaux** et écrit un rapport **versionné** dans
  `.factory/couts/` (`rapport-couts.md`, puis `-2`, `-3`... - **jamais d'écrasement**) :
  **coût estimé**, une ligne **par session** (modèle, tokens input/output, cache, coût) ; puis
  **coût réel**, une ligne **par jour** et par modèle (`Période`, `Modèle`, `Input`, `Output`,
  `Coût`). Aucun appel externe mesuré -> une phrase, jamais un tableau vide.
- `couts-total` - agrège **toutes les sessions locales** en un seul fichier de bilan partageable
  (`.factory/couts/bilan-couts.md` : dev, période, nombre de sessions, total tokens en 5 catégories,
  **coût estimé ET coût réel**, distincts) - le fichier à remettre au chef d'équipe ; **écrasé à
  chaque run** (reflète toujours l'état courant du journal local).
- `couts-equipe` - **consolidation multi-développeurs** (`references/cost_equipe.py <collecte>`) :
  chacun envoie son répertoire de coûts, on les dépose en sous-dossiers côte à côte, et le script
  produit **une ligne par développeur** (`Développeur`, `Projet`, `Sessions`, `Input`, `Output`,
  `Cache lu`, `Cache écrit`, `Estimé`, `Réel`) + un Total, dans `rapport-equipe.md` **versionné**.
  Voir la section Consolidation d'équipe ci-dessous.

## Le compteur (`references/turn_cost.py`) : hook `SessionEnd` (écriture en fin de session)
Best-effort (ne bloque jamais, exit 0). **Un seul comportement**, déclenché par `SessionEnd` : lit
`transcript_path` (stdin), valide le chemin, lit le **transcript complet** -> **dédup streaming
`(message.id, requestId)` en gardant la DERNIÈRE valeur** (le streaming réécrit le même message ; garder la
1ʳᵉ sous-compte, bug ccusage #888) -> **un enregistrement par message assistant** (= une requête/réponse
API) avec 5 catégories (`input`, `output`, `cache_read`, `cache_write_5m`, `cache_write_1h`) -> tarif
**par tier** (**1h = 2× input**, non porté par LiteLLM) -> **RÉÉCRIT** (overwrite) le fichier de la
session `.factory/couts/<aaaa-mm>/<session-id>.jsonl`. Chaque enregistrement porte sa clé
**`key:"<message.id>:<requestId>"`** (dédup globale au rapport). Le champ `attribution` reste écrit
(exigé par le garde-fou) mais **le rapport ne l'utilise plus** (rapport par session, pas par phase).

**Ancrage (dossier courant).** La racine est **ancrée sur `__file__`** : la copie installée vit à
`<racine>/.claude/hooks/turn_cost.py` -> le hook écrit **toujours** dans le `.factory/couts/` de ce
dossier et **ne mesure que les sessions lancées là** (il ne remonte jamais vers un `.factory/` parent).

**Pourquoi à la fin de session, pas par tour** : les hooks sont **bloquants** - un hook par tour rallonge
chaque interaction (+13-16 s rapportés sur des stacks réels). `SessionEnd` tire **une fois, à la fin** ->
**zéro latence pendant les tours**, tout en gardant la **granularité par message** (relue du transcript).

## Suivi org (`references/OTEL.md`) : OpenTelemetry, sans hook par machine
Doc (pas de code) : activer `CLAUDE_CODE_ENABLE_TELEMETRY=1` + OTLP (métriques natives
`claude_code.token.usage` / `cost.usage`, par user/modèle) vers un collecteur, via un `settings.json` géré -
pour le rollup au niveau organisation. Alternative au journal-repo. **Deux voies pour le cross-dev,
pas une** : `couts-equipe` (dépôt de répertoires, aucune infra, à la demande) et OTel (temps réel,
dashboards, mais collecteur et `settings.json` géré à mettre en place). OTel reste la voie du suivi
continu à l'échelle organisation.

## Rendu PDF (`scripts/build_couts_pdf.py` + `templates/rapport-couts.html`)
`couts-rapport` et `couts-equipe` écrivent **un PDF à côté du Markdown**, même nom et même numéro
de version (`rapport-couts-2.md` / `rapport-couts-2.pdf`) : la paire est évidente et la règle de
non-écrasement reste unique. Page 1 = synthèse (chiffres clés + **barre de répartition du coût**),
pages suivantes = les tableaux, paginés.
- **Identité visuelle propre, à ne pas aligner sur la validation.** Là où un rapport de recette code
  un **verdict** (vert/ambre/rouge, badges, bloc de signature), un rapport de coûts code la
  distinction **estimé / réel** - l'invariant central du plugin. Teal pétrole pour l'estimé, ambre
  brun pour le réel. Aucun badge, aucune signature : il n'y a rien à prononcer dans un coût.
- **La barre de répartition** est l'élément propre à ce plugin : par **catégorie de tokens** sur le
  rapport individuel (elle rend visible que le cache lu domine, ce qu'un total unique masque), par
  **développeur** sur le rapport d'équipe (qui consomme quoi). La rampe de teintes est **calculée**
  pour n parts, pas figée : une liste fixe donnerait la même couleur à tous les développeurs
  au-delà du quatrième.
- **La ventilation par catégorie ne redit pas la tarification** : elle passe par
  `turn_cost.cost_par_categorie`, seule source de vérité des prix. Sans table de prix, pas de barre
  plutôt qu'une barre inventée.
- **Mécanique copiée de `validation/scripts/build_rapport_pdf.py`** (découpe du gabarit,
  substitution de jetons, pagination équilibrée, découverte de Chrome, comptage des pages) : les
  plugins sont distribués séparément, un import inter-plugins casserait à l'installation.
- **Jamais bloquant** : sans navigateur ou sans gabarit, le Markdown reste le livrable et le script
  affiche un message actionnable, sortie 0.
- Le PDF étant binaire, `check_costs.py` ne le balaie pas : sa typographie est garantie par
  `sanitize_typo`, passé au rendu et appliqué à chaque chaîne d'origine humaine (nom de projet,
  prénom).

## Consolidation d'équipe (`references/cost_equipe.py`)
Le journal étant git-ignoré donc individuel, la consolidation se fait par **dépôt de répertoires** :
un sous-dossier par développeur dans un dossier de collecte, et un tableau à **une ligne par
développeur**. Décisions structurantes :
- **L'identité vit au niveau du dossier** (`identite.json`), pas dans l'enregistrement. Raison : les
  enregistrements Gemini (`kind:"reel"`) n'ont **pas** de champ `dev` - une identité par
  enregistrement ne couvrirait pas la colonne de coût réel sans modifier `assembleur`. Bonus : un
  développeur sur deux projets a naturellement deux `.factory/couts/`, chacun avec son nom de projet.
- **Repli d'identité signalé** : `identite.json` -> champ `dev` (email git) -> nom du dossier. La
  ligne apparaît toujours, mais le repli est écrit dans une section **À vérifier**.
- **Dédup locale à chaque dossier, jamais entre développeurs.** Une dédup globale par `key` (celle du
  rapport individuel) ferait disparaître en silence les messages d'un développeur au profit d'un
  autre en cas de recouvrement. Le recouvrement est donc **détecté et signalé**, jamais fusionné.
- **Rien n'est retarifé côté simulation** (`sim_cost_usd` vient du compteur de chacun) ; le réel est
  tarifé avec **une seule table pour toute l'équipe**, sinon les lignes ne seraient pas comparables.
- **Tolérance de forme** : contenu de `.factory/couts/`, `.factory/` entier ou racine projet.
- **Hors portée de `check_costs.py`** : le rapport d'équipe vit en dehors d'un projet, le garde-fou
  ne le balaie pas. `sanitize_typo()` sur le document entier reste la seule garantie typographique.

## Stockage (individuel, git-ignoré)
**Un fichier par session** `.factory/couts/<aaaa-mm>/<session-id>.jsonl`, **réécrit à chaque `SessionEnd`**
depuis le transcript complet. **Pas d'état/curseur** (on réécrit tout à chaque fois). Tout `.factory/couts/`
est **git-ignoré** (données individuelles, jamais poussées au repo). Table de prix dans
`.factory/couts/`, identité du développeur dans `.factory/couts/identite.json`. **Partage au chef
d'équipe** : remettre un `rapport-couts.md` (fichier versionné), envoyer **tout le répertoire** pour
une consolidation via `couts-equipe`, ou rollup org via OTel.

**Reprise de session** : (1) **même id** -> réécriture idempotente du fichier depuis le transcript complet
(pas de doublon) ; (2) **nouvel id qui rejoue** l'historique -> chaque enregistrement porte sa `key`
`(message.id, requestId)` -> `cost_report.py` **déduplique GLOBALEMENT** (chaque requête comptée une fois).

## Journal du coût réel (Gemini)
Écrit par `assembleur/scripts/gemini_review.py` (fonction `journaliser_usage`), **pas** par ce
plugin : l'assembleur **mesure**, `couts` **tarife** - aucun import croisé entre plugins.
**Un enregistrement par appel API** dans
`.factory/couts/<aaaa-mm>/gemini-<aaaa-mm-jj>-<dimension>-<pid>.jsonl` :
`{kind:"reel", provider, model, ts, jour, dimension, key, tokens:{input, output, thoughts, cached}}`.
**Un fichier par processus** : `revue-gemini` lance six sous-agents en parallèle, un fichier
distinct évite tout verrou et tout entrelacement. La journalisation est **best-effort absolu** :
toute erreur est avalée, mesurer le coût ne doit jamais faire échouer une revue. La granularité
**par appel** est nécessaire : le palier long contexte se déclenche sur la taille du prompt, donc
agréger avant de tarifer perdrait le seuil.

## Table de prix (`references/price-table.json`, datée)
Structurée par **tier** : `{ tiers:{haiku,sonnet,opus,fable}, overrides:{<model-id>}, cache_write_1h_multiplier }`.
Résolveur `model-id -> tier` dans `turn_cost.py` (sous-chaîne + `overrides` pour les versions au prix
différent, ex. Opus 4.1 = 3×). Externe et **datée** (jamais en dur).
**Tarifs d'introduction : override borné par `until`** (`AAAA-MM-JJ`). Un modèle lancé à prix réduit
pour quelques mois (Sonnet 5 : 2/10 au lieu de 3/15 jusqu'au 2026-08-31) prendrait, en override
simple, ce tarif **pour toujours** - et surestimerait à l'inverse si on ne le met pas. Le résolveur
compare donc `until` à la **date du message** : la remise ne s'applique qu'aux messages antérieurs,
après quoi le tier reprend **sans édition**. Un même journal peut ainsi porter les deux tarifs, chaque
message au prix qui avait cours ce jour-là. **Message non daté = pas de remise** (on facture au tarif
catalogue, jamais moins - même prudence que le match par préfixe contre la sous-facturation).

## Table de prix Gemini (`references/gemini-price-table.json`, datée)
Prix **par modèle** (pas par tier), relevés sur la page officielle
`ai.google.dev/gemini-api/docs/pricing` - **les blogs agrégateurs sont périmés** (ils donnaient
0.15/1.25 pour 2.5 Flash contre 0.30/2.50 en réalité). Les modèles Pro portent un bloc
`long_context {seuil, input, output}` appliqué quand le **prompt** dépasse le seuil (200 000
tokens). Résolveur `prix_gemini()` dans `cost_report.py` : correspondance exacte puis par préfixe
(tolère un suffixe de version, `gemini-2.5-flash-002`). Un modèle absent de la table est
**signalé dans le rapport, jamais tarifé à zéro en silence**. Les modèles 2.5 sont annoncés en
retrait au **16 octobre 2026** : revoir la table à cette échéance.

## Rapport (par session, versionné)
`cost_report.py` agrège le journal **par session** : début/fin (`ts` min/max, format `JJ-MM`), tokens
**input** (bruts, hors cache), tokens **output**, tokens **cache lu**, tokens **cache écrit** (5m + 1h
cumulés), et **coût complet** (5 catégories au tarif par tier) converti en euros via un **taux figé**
(`USD_EUR`/`RATE_DATE` en tête du script). Un tableau + une ligne Total. Aucune ventilation par phase/feature/tier. **Simulation seule.** **Versionnage** (`_next_report_path`) :
chaque run écrit un **nouveau fichier** (`rapport-couts.md`, puis `rapport-couts-2.md`, `-3.md`...) -
**jamais d'écrasement** ; le chemin écrit est renvoyé (stdout + champ `report_path` en `--json`).

## Manifeste (optionnel)
Si un `manifest.json` existe, `couts-init` y ajoute le bloc `costs` :
`{ installed, hook:"SessionEnd", price_table_date, gitignored:true }`. Sinon rien n'est créé (le
garde-fou n'ouvre pas le manifeste).

## Scripts
`references/turn_cost.py` (compteur, hook `SessionEnd`, racine ancrée `__file__`),
`references/cost_report.py` (rapport **par session** versionné + taux figé, dédup globale par `key`,
localise le journal `.factory/couts/` avec journal, pas le git root), `references/cost_total.py`
(bilan agrégé toutes-sessions -> `.factory/couts/bilan-couts.md`, écrasé à chaque run),
`references/install_cost_hook.py` (copie `turn_cost.py` en `.claude/hooks/` + fusion hook SessionEnd,
cible le dossier courant, lanceur Python détecté), `references/price-table.json`,
`references/OTEL.md` (rollup org). Garde-fou : `scripts/check_costs.py` (dispositif en place +
**typographie des rapports produits**). Nettoyage typographique partagé :
`cost_report.sanitize_typo()`, importé par `cost_total.py`.

## Vérifications (à la place des tests)
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json', encoding='utf-8'))"
grep -L "^name:" skills/*/SKILL.md          # doit ne rien retourner
python -m py_compile references/*.py scripts/*.py
python scripts/check_costs.py <projet>/manifest.json
python references/cost_equipe.py <dossier-de-collecte>   # total = somme des rapports individuels
```

## Invariants
**Deux natures de coût, jamais mélangées** : la **simulation** (sessions Claude, estimation au tarif
API, jamais un montant facturé) et le **réel facturé** (appels API Gemini). Chacune a sa table de
prix datée, sa ligne dans le bilan et son tableau dans le rapport ; on ne les additionne jamais en
un chiffre unique, et le rapport dit lequel est facturé. **Sortie Gemini = candidates + thoughts**
(le prix de sortie inclut le raisonnement) ; **l'assembleur mesure, `couts` tarife** (pas d'import
croisé) ; **journalisation best-effort** (jamais bloquante pour la revue) ; pas de config, pas de
saisie manuelle ; **dossier courant** (installation + mesure confinées au dossier de la session, hook ancré sur
`__file__`) ; **fin de session** (hook `SessionEnd`, réécriture idempotente du fichier de session ;
**zéro latence par tour**) ; **granularité par message** conservée (relue du transcript) ; **dédup
`(message.id, requestId)` last-wins** (streaming) **puis dédup globale par `key`** au rapport
(reprise/fork comptés une fois) ; **5 catégories** dont **cache 1h à 2×** ; **table de prix par tier,
externe et datée** ; **rapport par session** (pas de ventilation phase/feature/tier) ; installation
**fusionnante** (ne jamais écraser un hook existant) ; **interaction en français, sans mécanique
exposée** ; **manifeste silencieux** - ne jamais annoncer que le bloc `costs` est écrit, ni afficher un
`champ: valeur`/`true`/`false` (l'utilisateur ne s'intéresse pas à l'état du manifeste). **Typographie humaine, garantie par le code** : aucun glyphe de style IA dans les rapports (pas de tiret cadratin, de points de suspension unicode, de flèches unicode, de guillemets à chevrons, de coche/croix, de point médian ni d'espace insécable). Ce n'est pas qu'une consigne de rédaction : `cost_report.sanitize_typo()` nettoie le **document entier** juste avant écriture (appelé par les deux générateurs), et `check_costs.py` **échoue** si un rapport de `.factory/couts/` en porte encore un - en nommant le fichier, la ligne et le glyphe. Une chaîne ajoutée plus tard dans un générateur est donc couverte d'office ; ne jamais retirer l'appel au nettoyage. Cf. la section Typographie de `references/ux-conventions.md`.
