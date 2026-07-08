# Conventions UX — sortie utilisateur (assembleur)

Règles transverses pour tout ce que les skills affichent à l'utilisateur. Mêmes principes
que cadrage / architecte / designer.

## 1. Jamais de nom d'attribut / clé JSON en sortie
Le manifeste garde ses clés (contrat machine) ; le **texte affiché** est en **langage naturel
français**. **Règle absolue, même dans une justification** : on n'écrit **jamais** un nom de
variable / clé manifeste (`assembly.coherence_validated`, `feature_seeds`…) ni un statut brut
(`coherence_validated == false`) dans le texte vu par l'utilisateur. On reformule toujours en
clair (« la cohérence est validée », « le paquet est complet »).

## 1bis. Mise à jour du manifeste = silencieuse
Le manifeste se met à jour **sans le narrer**. Interdit à l'écran : « MAJ `assembly.*` »,
« je passe `coherence_validated = true` », « `phase = "converge"` », **toute ligne de bilan**
« Manifeste à jour : phase: X, … » ou liste `champ: valeur` / `true`/`false`. **L'utilisateur ne
s'intéresse pas à l'état du manifeste.** On dit **ce qui a été produit** (en prose) et **la prochaine
étape** — rien de la mécanique.

## 2. Refus / pré-requis en langage naturel
Quand un skill ne peut pas tourner, expliquer **en clair** pourquoi et quoi faire. Ex. :
« La convergence ne peut pas démarrer : il manque un contrat validé — termine d'abord la
phase concernée. » Jamais « ⛔ design_validated == false ».

## 3. Aucun marqueur laissé, aucun identifiant codé
- Les marqueurs `[À VALIDER]` / `[À CHIFFRER]` / `NEEDS CLARIFICATION` ne **restent jamais**
  dans le paquet : ils se **résolvent en session** (cf. `interactive-loop.md`), la réponse est
  écrite **en place**. On ne dit pas « il reste X points » sans **poser la question**.
- Pas d'identifiant codé en sortie utilisateur ; on nomme chaque chose en clair.
- **Contenu seul** dans les artefacts : aucune `(src:)`, aucun horodatage, aucun nom de personne.

## 4. Pas de tableau, restitution en prose
Restituer la cohérence et l'avancement **en prose** ; pas de tableau de booléens, pas de jargon.

## 5. Une ligne « étape suivante » à la fin de chaque skill
Terminer chaque exécution par exactement une phrase en clair sur la suite.

## 6. Langue
**Tout en français** (interaction + artefacts). Seuls les identifiants/valeurs machine et les
noms d'outils/formats (`spec.md`, `constitution.md`, SpecKit) restent tels quels.
