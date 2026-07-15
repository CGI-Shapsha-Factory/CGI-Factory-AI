---
name: revue-gemini
description: Revue de code independante par l'API Gemini avant PR/merge — fan-out d'un reviewer par dimension (securite, correction, perf, architecture, qualite, tests) sur le diff de branche, agregation dedupliquee et classee par severite, restituee en un tableau en session. Contre l'exces de confiance de Claude par un relecteur externe non biaise.
---

# revue-gemini

**Relecteur independant avant PR/merge.** But : **contrer l'exces de confiance de Claude sur son propre
code** en confiant la revue a un moteur **externe et non biaise** — l'**API Gemini**. A lancer **avant de
creer une PR ou de merger** (le code ne doit pas partir en prod sans ce regard exterieur). Ce skill
**fan-out plusieurs sous-agents `gemini-reviewer` en parallele** (un par **dimension** de revue), chacun
lance le reviewer Gemini sur le **diff de branche**, puis **agrege** les findings en un **tableau unique
en session**. **Consultatif** : l'IA propose, l'humain tranche — aucun blocage, aucun fichier de sortie.

## Frontiere (exception assumee)
Comme les skills Linear/SpecKit, appeler l'API Gemini est une **exception bornee** a « pas d'API externe » :
Gemini est un **systeme externe** (pas le repo cible, pas un artefact SpecKit). Ce skill **n'ecrit aucun
fichier dans l'arbre versionne** : il ne pose qu'un **diff temporaire git-ignore** (`.factory/gemini-review/`)
et restitue **en session**. **La revue est faite par Gemini, jamais par Claude** (c'est tout l'interet).

## Etape 1 — Pre-requis : cle API Gemini
Verifier `GEMINI_API_KEY` (variable d'environnement **ou** `.env` a la racine). Sonder avec :
`python "${CLAUDE_PLUGIN_ROOT}/scripts/gemini_review.py" --check`.
- **`status:"ok"`** → continuer.
- **`reason:"no_key"`** (cle absente) → **ne pas bloquer sechement** : demander la cle a l'utilisateur en
  clair (« Il me faut une cle API Gemini pour la revue independante — colle-la ici, ou dis-moi de passer.
  Tu peux en creer une sur aistudio.google.com/apikey. »). Une fois fournie : **l'ajouter au `.env`**
  (ligne `GEMINI_API_KEY=<valeur>`, **creer `.env` s'il manque, git-ignore**) et poser un placeholder
  `GEMINI_API_KEY=` dans **`.env.example`** (committe) s'il existe — **convention architecte** (`.env`
  jamais committe). S'assurer que `.env` est bien dans `.gitignore` (l'ajouter sinon, sans reecrire le fichier).
- **`reason:"no_genai"`** (paquet `google-genai` absent, auto-install echouee) → le dire en clair et
  proposer `pip install --user google-genai`, puis relancer.
- **`reason:"auth"`** (cle invalide/expiree) → le dire en clair, demander une cle valide, mettre a jour `.env`.
- **`reason:"quota"` / `"network"` / `"model"`** → relayer le message actionnable (« quota atteint,
  reessaie plus tard », « reseau indisponible », « modele introuvable, definis `GEMINI_REVIEW_MODEL` »).

## Etape 2 — Calculer le diff de branche (portee de revue)
1. **Base** : par defaut `origin/main` (repli `main`) ; si la branche courante cible autre chose,
   **confirmer la base** avec l'utilisateur (une question, recommande + saisir). Pas de git / pas de
   base → le dire en clair et s'arreter.
2. Ecrire le diff dans un **fichier temporaire git-ignore** :
   `git diff --no-color <base>...HEAD > .factory/gemini-review/diff.patch` (creer le dossier ;
   `.factory/` est deja git-ignore). **Ne pas** afficher le diff en session (il reste hors contexte).
3. **Diff vide** (aucun changement vs base) → le dire en clair (« rien a revoir ») et **s'arreter** —
   ne pas lancer les reviewers.

## Etape 3 — Fan-out des reviewers (un sous-agent par dimension, en parallele)
Lancer, **en un seul message** (appels paralleles), **six sous-agents `gemini-reviewer`**
(`agentType: "gemini-reviewer"`), un par **dimension** :
`security`, `correctness`, `performance`, `architecture`, `quality`, `testing`.
Donner a **chaque** sous-agent : sa `dimension`, le chemin `diff_file` = `.factory/gemini-review/diff.patch`,
`plugin_root` = `${CLAUDE_PLUGIN_ROOT}`, `repo` = racine du projet. Chaque sous-agent lance le reviewer
Gemini pour SA dimension et renvoie **un objet JSON** (`status`, `findings`, ou `reason`/`error`). Le
fan-out **isole le contexte** (le diff et les findings ne saturent pas l'orchestrateur) et **parallelise**
les appels — c'est la partie « optimisation ».

> **Pourquoi une dimension par sous-agent (et non un chunk par sous-agent).** Chaque reviewer a un
> **mandat distinct** (securite ≠ perf ≠ tests…) → **pas de redondance** (deux reviewers ne refont pas
> la meme passe) et **plus de profondeur** par angle. Les gros diffs sont **chunkes a l'interieur** du
> script (par fichier), transparent pour l'orchestrateur.

## Etape 4 — Agregation (reduce) : dedup, conflits, classement
Collecter les six JSON, puis :
- **Ne garder que les `status:"ok"`/`"empty"`** ; noter a part les dimensions **`failed`** (avec leur
  `reason`) et **`partial`**/`truncated`.
- **Dedupliquer** les findings par `(file, line, titre proche)` : deux dimensions qui pointent le meme
  probleme au meme endroit → **une seule ligne**, en gardant la **severite la plus haute** et en
  fusionnant les recommandations.
- **Conflits entre reviewers** (memes fichier:ligne, diagnostics divergents) → **ne pas trancher a la
  place de Gemini** : garder les deux angles dans la meme ligne (« divergence : … »), l'humain arbitre.
- **Classer** par severite `critical > high > medium > low`, puis par dimension.

## Etape 5 — Restitution en session (tableau, aucun fichier)
Afficher **un seul tableau** bien presente (aucun fichier ecrit) :

| Severite | Dimension | Fichier:ligne | Probleme | Recommandation |
|----------|-----------|---------------|----------|----------------|
| critical | security | api/auth.py:42 | … | … |

Precede d'**une ligne de synthese** : total par severite (ex. « 2 critical, 3 high, 5 medium, 1 low »),
**dimensions couvertes** et **non couvertes** (avec la raison : quota/reseau/…). Si **aucun finding** :
le dire clairement (« Gemini n'a rien releve de bloquant sur le diff — revue independante passee »).
Terminer par **une** phrase de suite (« Etape suivante : … » — corriger les critical/high avant la PR,
ou relancer apres correction). **Consultatif** : ne jamais presenter ca comme un blocage automatique.

## Cas limites (tous geres, jamais bloquant)
- **Cle absente / invalide / expiree** → Etape 1 (demander + ecrire `.env`, convention architecte).
- **Quota / rate limit** → le script **retente avec backoff** puis rend `reason:"quota"` ; la dimension
  touchee est marquee **non couverte** dans la synthese, les autres s'affichent quand meme.
- **Echec reseau / erreur serveur Gemini (5xx)** → retry backoff, puis dimension **non couverte** + note.
- **Modele introuvable (404)** → le dire ; `GEMINI_REVIEW_MODEL` permet de changer de modele.
- **Gros codebase / diff > contexte** → le script **chunk par fichier** (borne `GEMINI_REVIEW_MAX_CHARS`
  / `MAX_CHUNKS`) ; si tronque, l'afficher (« diff tronque : N fichiers non couverts »).
- **Echecs partiels** (certaines dimensions echouent) → **rendre le tableau** avec les dimensions
  reussies + lister les **non couvertes** ; **ne jamais** abandonner toute la revue pour un echec partiel.
- **Conflits entre reviewers** → conserves cote a cote (Etape 4), l'humain tranche.
- **Diff vide / pas de git** → Etape 2, on s'arrete proprement.
- **Fichiers binaires / generes** dans le diff → Gemini les ignore de fait ; ne pas s'en inquieter.

## Regles invariantes
- **Revue par Gemini, pas par Claude.** Claude **orchestre et agrege** ; il n'emet **jamais** son propre
  avis de code a la place du reviewer independant (sinon le biais qu'on veut eviter revient).
- **Aucun fichier de sortie.** Restitution **en session** ; seul un diff temporaire **git-ignore** est pose.
- **Consultatif.** Findings classes par severite ; l'humain decide d'ouvrir/merger la PR. Aucun blocage auto.
- **Jamais bloquant sur une erreur externe.** Cle/quota/reseau → message actionnable, revue partielle
  affichee si possible.
- **Secrets : convention architecte.** La cle vit dans `.env` (git-ignore), jamais committee ;
  `.env.example` ne porte qu'un placeholder.

Etape suivante : corriger d'abord les findings **critical**/**high** signales par le reviewer independant,
puis relancer `/assembleur:revue-gemini` avant d'ouvrir ou de merger la PR.
