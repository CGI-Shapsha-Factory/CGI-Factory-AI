---
name: create-cowork-md
description: Génère init-cowork.md à la racine - le contexte unique du PO qui supervise depuis Quark : liens vers le dépôt GitHub et le projet Linear + le contexte issu des 3 contrats, sans rien du workflow SpecKit à venir.
---

# create-cowork-md

**Document de supervision pour Quark.** À lancer **pendant la phase assembleur** (après la
convergence ; idéalement après `premier-alimente-linear` pour que les tickets soient déjà liés). Ce
skill **détecte** le dépôt GitHub et le projet Linear, rassemble le **contexte figé par les 3
contrats** (cadrage / architecte / designer), et **génère `init-cowork.md` à la racine** du projet
- le document unique que le PO donne à **Quark** pour superviser sans setup supplémentaire.

## Objectif
Produire, **à la racine**, un `init-cowork.md` qui porte **tout le contexte utile** pour que le PO
**initialise un projet dans Quark/Cowork** et supervise sans setup supplémentaire. Il centralise :
- le **routage vers l'état vivant** - "où chercher quoi" : tâches / issues / avancement -> **Linear** ;
  fichiers / specs / features implémentées / technique -> **dépôt GitHub** ;
- le **contexte produit complet** figé par les 3 contrats : **problème** (le pourquoi), **objectif**,
  **utilisateurs & rôles**, **proposition de valeur**, **critères de succès**, **périmètre** (inclus /
  hors-périmètre / **contraintes clés**), la **liste des features** (description + dépendances + walking
  skeleton), la **synthèse technique** (stack, intégrations, hébergement, cibles qualité) et la
  **référence design** ;
- les deux **liens vivants** (GitHub, Linear).

Idempotent : régénère le fichier proprement. **Synthèse, pas copie ; rien d'inventé ; rien d'aval.**

## Frontière (exception assumée)
L'assembleur ne produit que son paquet (`assembleur-out/`) et **n'écrit jamais un fichier que
SpecKit génère**. Écrire `init-cowork.md` **à la racine** est une **exception explicitement
bornée** (au même titre que les tickets Linear et `specify init`) : c'est un **fichier de contexte
de supervision** destiné au PO/Quark, pas un artefact SpecKit ni le repo cible SpecKit. La seule
autre écriture propre à la Factory est le bloc `cowork` du manifeste.

## Contrainte de périmètre (phase assembleur)
On est **en convergence** : **rien en aval n'existe encore** (pas de `specify init`, pas de
fabrication feature-par-feature, pas d'avancement d'implémentation, pas de PR). `init-cowork.md`
ne contient donc **que** ce qui sort des **3 contrats** + les **liens** GitHub/Linear.
**Ne jamais** y écrire de section sur le workflow SpecKit, les étapes `/speckit.*`, ou un "comment
on construit" à venir - le PO lira l'état vivant lui-même via les liens.

## Pré-requis (vérification silencieuse)
Lire `manifest.json` **sans l'annoncer** :
- la convergence a tourné et le paquet est présent (`assembleur-out/feature-map.md` + au moins une
  graine `assembleur-out/features/*.md`) ;
- sinon -> le dire en clair et orienter vers `/assembleur:assembleur-convergence` :
  > "Le contexte de supervision ne peut pas être produit : il faut d'abord la convergence (le
  > paquet de features approuvées)."

Le bloc `linear` (s'il existe) fournit `team`/`project` ; les tickets déjà créés se relèvent
**dans Linear** (`list_issues({team, label Feature})`) ; le registre des features est
`architecture.feature_sequence`.
**Ne rien inventer** : uniquement du contenu réellement présent en amont.

## Étape 1 : Détecter le dépôt GitHub
Best-effort, sans bloquer :
1. `git remote get-url origin` (le repo cible est souvent un dépôt git).
2. **Normaliser** en URL web `https://github.com/<org>/<repo>` : convertir `git@github.com:<org>/<repo>.git`
   -> `https://github.com/<org>/<repo>` ; retirer le suffixe `.git` ; retirer d'éventuels identifiants
   dans l'URL (`https://<token>@github.com/...` -> `https://github.com/...`).
3. Repli si `origin` manque ou n'est pas GitHub : `gh repo view --json url -q .url`.
4. **Aucun remote / pas GitHub** -> **ne pas bloquer** : mettre `<à renseigner>` dans la section
   GitHub + une note ("le dépôt n'a pas encore de remote GitHub ; renseigner l'URL dès sa création").

## Étape 2 : Détecter le projet Linear (MCP linear-prism)
Sonder `mcp__plugin_linear-prism_linear__list_teams` (cf. `references/linear-guide.md`).
- **Disponible** :
  - lire le bloc `linear` du manifeste (`team`, `project`) ;
  - **URL du projet** : `get_project({id})` (ou retrouver via `list_projects({team})`) -> champ `url` ;
  - **repli d'URL** : si le projet n'est pas résolu, relever un ticket `Feature` via
    `list_issues({team, label Feature})` et dériver l'URL du **workspace** depuis son `url`
    (`https://linear.app/<workspace>/...`), avec une note.
- **Indisponible** -> **ne pas bloquer** : mettre `<à renseigner>` dans la section Linear + embarquer
  les **instructions d'installation** (section "Installation du plugin linear-prism" de
  `references/linear-guide.md`). Si **aucun ticket** n'existe encore, ajouter la note "tickets à
  créer via `/assembleur:premier-alimente-linear`".

## Étape 3 : Rassembler le contexte des 3 contrats (silencieux, best-effort)
Sources = **sorties amont uniquement**, en **synthèse** (pas de copie ; source absente -> omettre ou
`<à renseigner>`, **jamais inventer**) :
- **Projet** (contexte riche, <- `cadrage-out/product-brief.md` + `manifest.project`) :
  - **Problème** (le *pourquoi*, §Problème), **Objectif** (§Objectif métier), **Utilisateurs & rôles**
    (§Parties prenantes + `cadrage-out/project-frame.md` §Utilisateurs & rôles), **Proposition de valeur**
    (une phrase), **Critères de succès** (§Critères de succès, à haut niveau).
- **Périmètre** (<- product-brief + `cadrage-out/project-frame.md`) :
  - **Inclus** (§Périmètre IN), **Hors périmètre** (§Hors périmètre OUT), **Contraintes clés**
    (§Contraintes + project-frame : légal/RGPD, sécurité, sensibilité des données, hébergement,
    disponibilité, performance).
- **Périmètre & features** : `architecture.feature_sequence` (`{id, name}`) + `assembleur-out/feature-map.md`
  -> tableau feature avec **description courte** + **dépendances** + **walking skeleton** ; colonne
  **Ticket Linear** = `identifier` + `url` relevés dans Linear (`list_issues({team, label Feature})`,
  jointure par titre) **si créés**, sinon "à créer via
  premier-alimente-linear". (Glossaire `cadrage-out/glossaire.md` / use cases `cadrage-out/spec-index.md`
  pour nommer juste.)
- **Contexte technique** : synthèse de la stack (`architecte-out/stack-technique.md`) + **intégrations**
  (project-frame §Intégrations) + **hébergement** (project-frame §Hébergement) + **cibles de qualité**
  (`architecte-out/facteurs-et-qualite.md`), en bref.
- **Contexte design** : référence du design system (`designer-out/design-guidelines.md` / système
  synchronisé Claude Design).

## Étape 4 : Générer `init-cowork.md` (racine) + confirmer
1. Partir du gabarit `.factory/assembleur/init-cowork.md` (installé par `assembleur-init`) et le
   **remplir intégralement** avec les infos détectées (Étapes 1-3) : la section **"Où chercher quoi"**
   (routage GitHub/Linear), le **contexte projet** (problème, objectif, utilisateurs, valeur, critères
   de succès), le **périmètre** (inclus / hors-périmètre / contraintes clés), le **tableau des features**
   (description + dépendances + walking skeleton), la **synthèse technique** et la **référence design**,
   plus la section **"Accès Linear pour Quark"** (setup MCP + clé API - cf. `references/linear-guide.md`,
   sous-section "Accès par clé API"). Toute section sans matière amont -> `<à renseigner>`, jamais inventée.
2. **Confirmer les deux liens vivants - une question par lien, posées SÉPARÉMENT (jamais les deux à
   la fois).** Chaque question est **un appel `AskUserQuestion` distinct**, portant **une seule
   URL**, avec deux options : l'URL détectée (recommandé) et "aucune de ces adresses" ; la saisie
   libre reçoit l'URL exacte.
   1. **D'abord GitHub** : poser **un seul appel** sur l'**URL GitHub** - proposer l'URL détectée
      (Étape 1) en option recommandée, ou `<à renseigner>` si aucune. **Attendre la réponse** avant
      de passer à la suivante.
   2. **Ensuite Linear** : poser **un second appel, distinct**, sur l'**URL Linear** - proposer
      l'URL détectée (Étape 2 : projet existant / dérivée) en option recommandée, ou
      `<à renseigner>`.
   **Ne rien écrire à la racine tant que les deux liens ne sont pas tranchés.**
3. **Écrire** `init-cowork.md` à la **racine** du projet (read-modify-write si déjà présent).
4. **Consigner en silence** le bloc `cowork` du manifeste, en y **reportant les deux URL tranchées
   en 4.2** (jamais `null` quand l'humain a confirmé une adresse ; `null` uniquement pour un lien
   resté `<à renseigner>`) :
```json
"cowork": {
  "phase": "init", "path": "init-cowork.md",
  "github_url": "<URL GitHub confirmée>", "linear_project_url": "<URL Linear confirmée>",
  "generated": true
}
```
(read-modify-write + revalidation JSON). Ces deux valeurs sont ce qui évite de **redemander les
liens à chaque relance** : à la relance, les proposer en option recommandée.

## Vérification avant de conclure
- `init-cowork.md` existe à la racine, expose une **section GitHub**, une **section Linear**, une
  section **"Périmètre"** et un **contexte projet** (problème / objectif / périmètre / contraintes),
  et **ne contient aucune** section SpecKit / fabrication / avancement (contrainte de périmètre).
- Lancer le garde-fou. La variable de plugin **ne s'expanse pas pareil selon le shell** - prendre
  la forme du shell utilisé (utiliser `python` ; `python3` sur macOS/Linux) :
  - Bash : `python "${CLAUDE_PLUGIN_ROOT}/scripts/check_cowork.py" <racine>/manifest.json`
  - PowerShell : `python "$env:CLAUDE_PLUGIN_ROOT/scripts/check_cowork.py" <racine>/manifest.json`
    (en PowerShell, `${CLAUDE_PLUGIN_ROOT}` désigne une variable de session, **pas**
    l'environnement : le chemin serait vide et la commande échouerait)
- Le bloc `cowork` porte bien les **deux URL confirmées** (pas `null` là où l'humain a tranché).
- Le bloc `cowork` du manifeste **reparse sans erreur** ; restitution **en prose** ("j'ai généré
  le contexte de supervision `init-cowork.md` - GitHub + Linear"), manifeste mis à jour **en silence**.

## Règles invariantes
- **Exception racine bornée.** On n'écrit que `init-cowork.md` (racine) + le bloc `cowork` du
  manifeste ; jamais un fichier que SpecKit génère.
- **Contexte complet.** Le document porte tout le contexte utile à la supervision (problème, objectif,
  utilisateurs, périmètre inclus/hors, contraintes, features, technique, design) + le routage
  "où chercher quoi" - pas seulement les deux liens.
- **Rien d'aval.** Aucun contenu sur SpecKit / la fabrication / l'avancement - ils n'existent pas
  encore ; seuls les **liens** GitHub/Linear renvoient à l'état vivant.
- **Confirmer avant d'écrire.** Les deux liens sont validés par l'humain **une question par lien,
  posées séparément** (GitHub d'abord, Linear ensuite - jamais les deux à la fois) avant l'écriture racine.
- **Ne pas bloquer.** Source manquante -> `<à renseigner>` + note ; jamais d'arrêt.
- **Rien d'inventé.** Uniquement du contenu réellement présent dans les 3 contrats / le manifeste.
- **Manifeste en silence.** Aucun nom de clé à l'écran ; restitution en prose.

Étape suivante : `/assembleur:install-speckit` - poser SpecKit dans le repo, puis fabriquer feature par feature (chaque ticket Linear pilote un cycle SpecKit).
