# Conventions UX — sortie utilisateur (architecte)

Règles transverses pour tout ce que les skills affichent à l'utilisateur. Mêmes
principes que le plugin cadrage.

## 1. Jamais de nom d'attribut / clé JSON en sortie
Le manifeste garde ses clés (contrat machine) ; le **texte affiché** et les **refus**
sont en **langage naturel français**. Correspondance :

| Interne (manifeste) | Langage utilisateur |
|---|---|
| `architecture.drivers` | « les drivers d'architecture » |
| `architecture.components` | « les composants » |
| `architecture.stack` | « la stack technique » |
| `architecture.adrs` | « les décisions d'architecture (ADR) » |
| `architecture.walking_skeleton` | « le walking skeleton » |
| `architecture.coherence_validated` | « la validation de cohérence est faite » |
| `definition_of_ready.cadrage_complete` | « le cadrage est prêt » |

Ne jamais afficher de tableau de booléens bruts ni `coherence_validated == false`.
**Règle absolue, même dans une justification** : on n'écrit **jamais** un nom de
variable / clé manifeste dans le texte vu par l'utilisateur.

## 1bis. Jamais d'identifiant codé en sortie
Le PO/l'architecte lecteur ne retient pas les codes. **Interdit** en sortie : `C1`,
`C2`, `UC1`, `UC2`, `P1`, `ADR A6`, `Q2`/`Q6`/`Q7`… On nomme **toujours en clair**
(« le composant de recherche RAG », « le service de droits », « la question sur la
performance »). Les ids internes restent dans l'artefact/le manifeste, **jamais
affichés** ni utilisés pour désigner une chose à l'écran.

## 1ter. Mise à jour du manifeste = silencieuse
Le manifeste se met à jour **sans le narrer**. **Interdit** à l'écran : « MAJ
`architecture.components` », « `architecture.phase = "contrat"` », « je passe
`coherence_validated = true` », **toute ligne de bilan** « Manifeste à jour : phase: X, … » ou liste
`champ: valeur` / `true`/`false`. **L'utilisateur ne s'intéresse pas à l'état du manifeste.** À
l'utilisateur, on dit **ce qui a été produit** (en clair) et **la prochaine étape** — rien de la
mécanique sous le capot.

## 2. Refus en langage naturel
Quand un skill ne peut pas tourner, expliquer **en clair** pourquoi et quoi faire.
Ex. : « Cette étape ne peut pas démarrer : le cadrage n'est pas encore prêt — lance
d'abord la phase de cadrage. » Jamais « ⛔ cadrage_complete == false ».

## 3. Aucun marqueur laissé, aucun horodatage, aucune provenance
- Les marqueurs `[À VALIDER]` / `[À CHIFFRER]` / `[À DÉFINIR]` ne **restent jamais**
  dans un artefact terminé : ils se **résolvent en session** (cf.
  `interactive-loop.md`), la réponse est écrite **en place**. On ne dit pas « il
  reste X points » sans **poser la question**.
- **Aucune provenance écrite** dans les artefacts : pas de `(src: …)`, **pas
  d'horodatage** (`[00:07:47]`), **pas de nom de personne** issu du transcript
  (« Priorité Sophie », « validé bâtonnier »…). On écrit le **contenu**, le cœur
  technique — jamais qui l'a dit ni quand.

## 4. Langage non technique, pas de tableau imposé
Composants, drivers, stack, vérifications restitués en **prose claire** (valeur /
usage). **Pas de tableau** de vérification, de synthèse ou de cohérence ; pas
d'identifiant technique. Désigner chaque chose par son **nom métier**.

## 5. Une ligne « étape suivante » à la fin de chaque skill
Terminer chaque exécution par exactement une phrase :
> « Étape suivante : `/architecte:<skill>` — <pourquoi en quelques mots>. »

## 6. Langue
**Tout en français** (interaction + artefacts). Seuls les identifiants/valeurs
machine du manifeste et les noms d'outils/formats (`ruff.toml`, `biome.json`…)
restent tels quels.
