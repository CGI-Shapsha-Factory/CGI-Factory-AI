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
| `ready_for_speckit` | « le cadrage est prêt » |

Ne jamais afficher de tableau de booléens bruts ni `coherence_validated == false`.

## 2. Refus en langage naturel
Quand un skill ne peut pas tourner, expliquer **en clair** pourquoi et quoi faire.
Ex. : « Cette étape ne peut pas démarrer : le cadrage n'est pas encore prêt — lance
d'abord la phase de cadrage. » Jamais « ⛔ ready_for_speckit == false ».

## 3. Marqueurs internes hors texte utilisateur
Les marqueurs (`[À VALIDER]`, `[À CHIFFRER]`) vivent dans les **artefacts**. À l'oral
on dit « à valider », « à chiffrer ».

## 4. Langage non technique pour les restitutions
Composants, drivers, stack restitués en valeur/usage compréhensibles ; pas de jargon
inutile ni d'identifiants techniques dans les tableaux affichés.

## 5. Une ligne « étape suivante » à la fin de chaque skill
Terminer chaque exécution par exactement une phrase :
> « Étape suivante : `/architecte:<skill>` — <pourquoi en quelques mots>. »

## 6. Langue
**Tout en français** (interaction + artefacts). Seuls les identifiants/valeurs
machine du manifeste et les noms d'outils/formats (`ruff.toml`, `biome.json`…)
restent tels quels.
