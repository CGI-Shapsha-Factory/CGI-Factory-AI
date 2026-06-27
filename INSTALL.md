# Installer la Factory IA

Un **installeur interactif** (façon BMAD) : une commande → un menu → tu **coches les modules** que tu
veux → seuls ceux-là s'installent (avec leurs templates). Choix **libre** : aucun rôle n'est imposé.

## Prérequis
- **Claude Code** installé (le CLI `claude` doit être dans le PATH).
- **Accès au dépôt de la marketplace** (repo privé `CGI-Shapsha-Factory/CGI-Factory-AI`) — sois
  authentifié à GitHub (`gh auth login` ou identifiants git configurés).
- **Python 3** (l'installeur est un script Python sans dépendance).

## Lancer l'installeur

**Via `npx` (Node ≥ 18, façon BMAD — aucune installation préalable) :**

```shell
npx github:CGI-Shapsha-Factory/CGI-Factory-AI            # menu interactif
npx github:CGI-Shapsha-Factory/CGI-Factory-AI --all --yes
npx github:CGI-Shapsha-Factory/CGI-Factory-AI --modules cadrage,designer
```

**Ou via Python (si tu as cloné le dépôt) :**

```shell
python install.py
```

Les deux donnent le même menu à cases à cocher (flèches + espace, entrée pour valider) :

```
Factory IA — coche les modules a installer
  (fleches haut/bas, ESPACE = cocher, ENTREE = valider)

 > [ ] cadrage     Contrat fonctionnel : captation -> vision, glossaire, decoupage, briefs.  (ex. chef de projet / PO)
   [ ] architecte  Contrat technique : drivers & qualite, composants, stack, ADR...           (ex. architecte)
   [ ] designer    Contrat de design : design system executable (tokens DTCG, WCAG 2.2)...    (ex. dev front / UX)
   [ ] assembleur  Convergence des 3 contrats -> repo SpecKit + init Linear + hook.           (ex. lead)
```

L'installeur ajoute la marketplace si besoin, installe les modules cochés, puis affiche les étapes
suivantes (`/reload-plugins` + le skill d'entrée de chaque module).

## Sans interaction (CI / rapide)

```shell
python install.py --modules cadrage,designer      # une sélection précise
python install.py --all --yes                     # toute la Factory, sans prompt
python install.py --modules cadrage --scope project   # portée projet (partagée équipe)
python install.py --list                          # juste lister les modules
python install.py --modules cadrage --dry-run     # voir les commandes sans rien installer
```

Options : `--scope user|project|local` (défaut `user`), `--yes`, `--no-add-marketplace`, `--dry-run`.

## Les modules (choix libre — l'indication de rôle est juste un repère)

| Module | Contrat | Repère de rôle |
|--------|---------|----------------|
| `cadrage` | Fonctionnel (captation → pack SpecKit) | chef de projet / PO |
| `architecte` | Technique (drivers, stack, ADR, walking skeleton) | architecte |
| `designer` | Design (design system exécutable, WCAG 2.2) | dev front / UX |
| `assembleur` | Convergence des 3 contrats → SpecKit + Linear | lead / convergence |

> Tu n'es **pas** obligé de suivre ces rôles : installe exactement les modules dont tu as besoin.

## Installation manuelle (équivalent, sans l'installeur)

```shell
/plugin marketplace add CGI-Shapsha-Factory/CGI-Factory-AI
/plugin install cadrage@Shapsha-Factory        # puis architecte/designer/assembleur au besoin
```

Dans l'app, `/plugin` → onglet **Discover** montre les modules **groupés par rôle** (catégories).

## Après l'installation
Dans un projet, démarre la phase voulue : `/cadrage:cadrage-init`, `/architecte:architecte-init`,
`/designer:designer-init`, `/assembleur:assembleur-init`.
