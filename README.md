<div align="center">

# Factory IA

**Fabrique logicielle spec-driven pour Claude Code — l'IA propose et structure, l'humain décide.**

Quatre plugins qui transforment un atelier (transcripts, docs) en un **paquet prêt à fabriquer avec SpecKit** — sans jamais laisser l'IA franchir une décision structurante.

![Claude Code](https://img.shields.io/badge/Claude_Code-plugins-8A2BE2)
![Plugins](https://img.shields.io/badge/plugins-4-1f6feb)
![Spec-driven](https://img.shields.io/badge/spec--driven-SpecKit-2ea043)
![Marketplace](https://img.shields.io/badge/marketplace-Shapsha--Factory-f78c40)
![Langue](https://img.shields.io/badge/langue-fran%C3%A7ais-1f6feb)

<img src="docs/factory-ia.png" alt="Schéma complet de la Factory IA — cadrage → architecte → designer → assembleur" width="880">

📐 **[Schéma complet & interactif sur Excalidraw](https://app.excalidraw.com/l/7jNppvtCKM7/8hisUsmacFM)**

</div>

---

> **Le principe** — on **fige les contrats en amont**, **l'humain arbitre à chaque étape**, et des **garde-fous déterministes** (sans IA) refusent en aval ce qui n'est pas conforme. L'IA propose et structure ; elle ne décide jamais.

## 🚀 Démarrage rapide

**Prérequis** — Claude Code installé + un accès à l'organisation GitHub `CGI-Shapsha-Factory` (dépôt privé). S'authentifier avec son compte CGI :

```shell
gh auth login        # GitHub.com → HTTPS → compte CGI
```

### Installation (marketplace)

L'installation se fait **uniquement via la marketplace** Claude Code — il n'y a **pas** d'installeur `npx`/Python (l'ancien a été retiré). Chaque plugin est une collection de **skills Markdown** : pas de build, pas de dépendance à installer.

```shell
/plugin marketplace add CGI-Shapsha-Factory/CGI-Factory-AI
/plugin install cadrage@Shapsha-Factory        # puis architecte/designer/assembleur au besoin
```

Dans l'app, `/plugin` → onglet **Discover** montre les modules **groupés par rôle** (catégories).

### Démarrer un projet

```shell
/cadrage:help-factory     # carte des 4 plugins, l'ordre et les portes humaines
/cadrage:cadrage-init     # initialise le projet à cadrer
```

> **Mises à jour** : `/plugin marketplace update Shapsha-Factory`. Dépôt privé → Claude Code réutilise tes identifiants git (`gh auth login`) ; pour les mises à jour automatiques au démarrage, exporter `GITHUB_TOKEN` (ou `GH_TOKEN`) avec le scope `repo`.

## 🧩 Les quatre plugins

Exécutés dans l'ordre, pilotés par un **manifeste partagé** (`.factory/manifest.json`) — chacun produit un **contrat** validé par une porte humaine et écrit dans son propre dossier de sortie à la racine (`cadrage-out/`, `architecte-out/`, `designer-out/`, `assembleur-out/`). La mécanique interne (manifeste + gabarits) vit dans le dossier caché `.factory/` ; les prompts Claude Design dans `prompts/<plugin>/`.

| # | Plugin | Contrat | Ce qu'il produit |
|---|--------|---------|------------------|
| 1 | **`cadrage`** | Fonctionnel | Capte la matière brute (transcripts, docs) → vision produit, glossaire du projet, découpage en features de valeur + carte de couplage, un brief par feature. → `cadrage-out/` |
| 2 | **`architecte`** | Technique | Drivers & attributs de qualité (ISO/IEC 25010), composants, stack, ADR transverses, walking skeleton, conventions/linters, diagrammes C4 **rendus en images PNG**. → `architecte-out/` |
| 3 | **`designer`** | Design | **Atelier de couverture** : une checklist fondation / expérience / technique pré-remplie par les handoffs garantit que rien d'important n'est oublié, puis produit le **prompt Claude Design**, le rapport de couverture et le handoff design. Le design system naît dans **Claude Design** et passe au code via **`/design-sync`** — il n'est pas généré par le plugin. → `designer-out/` |
| 4 | **`assembleur`** | Convergence | Lit les 3 contrats **en parallèle** et produit un **paquet de handoff SpecKit** dans `assembleur-out/` : **pré-constitution** (format `constitution.md`), **graines spec** par feature (format `spec.md`), **carte des features** (séquence + couplage), **contexte technique**, `CLAUDE.md` projet et un dossier **mémoire**. Il n'écrit jamais dans le repo cible. |

## 🔁 Workflow

```text
cadrage  →  architecte  →  designer  →  assembleur  →  SpecKit
```

**cadrage** (fonctionnel) → **architecte** (technique) → **designer** (design) → **assembleur** (convergence → **paquet de handoff**) → fabrication **SpecKit** : l'équipe prend le paquet de `assembleur-out/` et lance `specify init` → `/speckit.constitution` (depuis la pré-constitution) → `/speckit.specify` par feature (ordre du `feature-map.md`, walking skeleton d'abord) → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`.

Chaque passage est une **porte humaine** : arbitrage du découpage et maquette validée (cadrage), arbitrage des ADR puis cohérence (architecte), arbitrage du designer puis couverture (designer), garant de cohérence (assembleur). Et chaque skill se termine par une ligne « Étape suivante » qui guide vers la suite.

## 🔥 Pourquoi Factory IA ?

| | Cadrage « ad hoc » assisté par IA | Avec **Factory IA** |
|---|---|---|
| Décisions structurantes | l'IA comble les blancs | **l'humain tranche** ; rien n'est laissé indéfini — tout point se **résout en session** |
| Sortie | prose non opposable | **contrats** (fonctionnel, technique, design) cousus par feature |
| Cohérence | au jugé | **garde-fous déterministes** qui refusent en aval |
| Lisibilité | jargon, variables, horodatages | **langage naturel** ; contenu seul (pas de provenance, pas de nom de variable affiché) |
| Handoff | manuel | **paquet SpecKit prêt** (pré-constitution + graines spec + carte des features + mémoire) |

## ✨ Principes

- **Contrats figés en amont** — chaque plugin produit un contrat arbitré par un humain ; un manque se **résout en session** (on pose la question, on écrit la réponse en place), jamais comblé d'office.
- **L'IA propose, l'humain tranche** — aucune porte structurante n'est franchie par l'IA.
- **Hygiène déterministe en aval** — des scripts sans IA valident les manifestes (réutilisables en hook git / CI).
- **Contenu, pas provenance** — les artefacts portent le fond décidé ; pas d'horodatage, pas de nom de personne, pas de nom de variable affiché à l'utilisateur.
- **Tout en français** — skills, artefacts, interaction ; seuls les identifiants machine et noms d'outils restent tels quels.

## 🗂️ Structure d'un plugin

```
<plugin>/
├── .claude-plugin/plugin.json     # manifeste du plugin
├── skills/<skill>/SKILL.md         # skills, invocables via /<plugin>:<skill>
├── templates/                      # gabarits des artefacts produits
├── references/                     # conventions partagées (boucle interactive, UX…)
├── agents/                         # sous-agents custom (ex. assembleur : contract-reader)
└── scripts/check_*.py              # garde-fous déterministes (sans IA)
```

## 🧭 Vue d'ensemble & aide

- **`/cadrage:help-factory`** — l'**aide unique** : la carte des 4 plugins (rôle de chaque skill, ordre, portes humaines).

## 👥 Déploiement d'équipe (optionnel)

Pour pré-déclarer le marketplace et les plugins à toute l'équipe, ajouter à `.claude/settings.json` (versionné) :

```json
{
  "extraKnownMarketplaces": {
    "Shapsha-Factory": {
      "source": { "source": "github", "repo": "CGI-Shapsha-Factory/CGI-Factory-AI" }
    }
  },
  "enabledPlugins": {
    "cadrage@Shapsha-Factory": true,
    "architecte@Shapsha-Factory": true,
    "designer@Shapsha-Factory": true,
    "assembleur@Shapsha-Factory": true
  }
}
```

## 🛠️ Garde-fous déterministes

Sans IA dans la boucle, réutilisables en hook git / CI : `check_discovery` · `check_ready` (cadrage) · `check_architecture` · `check_design` · `check_assembly`. Ils échouent tant qu'une réponse structurante manque ou qu'un point reste à trancher — c'est la « compilation » de la Factory. L'architecte rend aussi ses diagrammes en images PNG (`render_diagrams.py`, mermaid-cli).

## 🏗️ Construit avec / standards

Claude Code · [SpecKit](https://github.com/github/spec-kit) · **Claude Design** + `/design-sync` · **WCAG 2.2 AA** + WAI-ARIA APG · **ISO/IEC 25010** · diagrammes **C4** (mermaid-cli).

---

<div align="center">

**Construit avec Claude Code — Factory IA.**

Commence par `/cadrage:help-factory`.

</div>
