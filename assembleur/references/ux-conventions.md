# Conventions UX — sortie utilisateur (assembleur)

Règles transverses pour tout ce que les skills affichent à l'utilisateur. Mêmes principes
que cadrage / architecte / designer.

## 1. Jamais de nom d'attribut / clé JSON en sortie
Le manifeste garde ses clés (contrat machine) ; le **texte affiché** et les **refus** sont en
**langage naturel français**. Correspondance :

| Interne (manifeste) | Langage utilisateur |
|---|---|
| `assembly.target_repo` | « le repo SpecKit cible » |
| `assembly.feature_faces` | « les 3 faces de chaque feature » |
| `assembly.coherence_report` | « le rapport de cohérence » |
| `assembly.coherence_validated` | « la cohérence est validée » |
| `assembly.team_validated` | « l'équipe a validé le découpage » |
| `assembly.linear_initialized` | « Linear est initialisé » |

Ne jamais afficher de tableau de booléens bruts ni `coherence_validated == false`.

## 2. Refus en langage naturel
Quand un skill ne peut pas tourner, expliquer **en clair** pourquoi et quoi faire. Ex. :
« La convergence ne peut pas démarrer : il manque un contrat validé — termine d'abord la
phase concernée. » Jamais « ⛔ design.coverage_validated == false ».

## 3. Marqueurs internes hors texte utilisateur
Les marqueurs (`[À VALIDER]`, `NEEDS CLARIFICATION`) vivent dans les **artefacts**. À l'oral
on dit « à valider », « à clarifier ».

## 4. Langage non technique pour les restitutions
Features, faces, cohérence restituées en valeur/usage compréhensibles ; pas de jargon inutile.

## 5. Une ligne « étape suivante » à la fin de chaque skill
Terminer chaque exécution par exactement une phrase :
> « Étape suivante : `/assembleur:<skill>` — <pourquoi en quelques mots>. »

## 6. Langue
**Tout en français** (interaction + artefacts). Seuls les identifiants/valeurs machine et les
noms d'outils/formats (`spec.md`, `constitution.md`, SpecKit, Linear) restent tels quels.
