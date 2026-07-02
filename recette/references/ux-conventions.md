# Conventions UX — sortie utilisateur (recette)

Règles transverses pour tout ce que les skills affichent à l'utilisateur. Mêmes principes
que cadrage / architecte / designer / assembleur.

## 1. Jamais de nom d'attribut / clé JSON en sortie
Le manifeste garde ses clés (contrat machine) ; le **texte affiché** est en **langage naturel
français**. **Règle absolue, même dans une justification** : on n'écrit **jamais** un nom de
variable / clé manifeste (`recette.anomalies`, `trace.non_regression_passed`, `workflow_state`…) ni
un statut brut (`state == "done"`) dans le texte vu par l'utilisateur. On reformule toujours en clair
(« l'anomalie est refermée », « la non-régression est prouvée »).

## 1bis. Mise à jour du manifeste = silencieuse
Le bloc `recette` se met à jour **sans le narrer**. Interdit à l'écran : « je passe l'état à
`done` », « j'écris `trace.linear_synced = true` ». On dit **ce qui a été fait** (en prose) et **la
prochaine étape** — rien de la mécanique.

## 2. Refus / pré-requis en langage naturel
Quand un skill ne peut pas tourner ou refuse de conclure, expliquer **en clair** pourquoi et quoi
faire. Ex. : « Je ne peux pas refermer cette anomalie : la spécification et les tâches ne reflètent
pas encore la correction. » Jamais « ⛔ trace.tasks_updated == false ».

## 3. Anomalie ou évolution : toujours nommer la nature en clair
On parle d'**anomalie** (le code ne respecte pas la spec) ou d'**évolution** (la spec doit changer),
jamais d'un code interne. Un objet mal qualifié se **requalifie** en clair, avec sa raison.

## 4. Pas de tableau, restitution en prose
Restituer l'analyse d'impact, la cause racine, l'avancement **en prose** ; pas de tableau de
booléens, pas de jargon. (Seule exception éventuelle : une revue de features candidates à créer.)

## 5. Une ligne « étape suivante » à la fin de chaque skill
Terminer chaque exécution par exactement une phrase en clair sur la suite (souvent : la commande
`/speckit.*` exacte à taper, ou « le PO peut ouvrir l'évolution »).

## 6. Langue
**Tout en français** (interaction + artefacts propres à la recette). Seuls les identifiants/valeurs
machine et les noms d'outils/formats (`spec.md`, `constitution.md`, SpecKit, `/speckit.*`,
`feature:<id>`) restent tels quels.
