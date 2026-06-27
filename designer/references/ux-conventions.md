# Conventions UX — sortie utilisateur (designer)

Règles transverses pour tout ce que les skills affichent à l'utilisateur. Mêmes principes
que les plugins cadrage et architecte.

## 1. Jamais de nom d'attribut / clé JSON en sortie
Le manifeste garde ses clés (contrat machine) ; le **texte affiché** et les **refus** sont
en **langage naturel français**. Correspondance :

| Interne (manifeste) | Langage utilisateur |
|---|---|
| `design.checklist` | « la checklist de couverture » |
| `design.checklist.foundation` | « la fondation (tokens, composants, mouvement) » |
| `design.checklist.experience` | « le versant expérience » |
| `design.checklist.technical` | « le versant technique qui se voit » |
| item `status: sans_objet` | « sans objet sur ce projet » |
| item `status: open` | « pas encore couvert » |
| `design.coverage_sufficient` | « la couverture est jugée suffisante » |
| `design.design_system_ref` | « le design system (Claude Design) » |
| `design.design_validated` | « le système de design est validé » |

Ne jamais afficher de tableau de booléens bruts ni `design_validated == false`.

## 2. Refus en langage naturel
Quand un skill ne peut pas tourner, expliquer **en clair** pourquoi et quoi faire. Ex. :
« Cette étape ne peut pas démarrer : il faut une maquette validée et un contrat technique
validé — termine d'abord le cadrage et l'architecture. » Jamais « ⛔ design_validated ==
false ».

## 3. Marqueurs internes hors texte utilisateur
Les marqueurs (`[À VALIDER]`, `[À CHIFFRER]`) vivent dans les **artefacts**. À l'oral on
dit « à valider », « à chiffrer ».

## 4. Langage non technique pour les restitutions
Composants, tokens, parcours restitués en valeur/usage compréhensibles ; pas de jargon
inutile ni d'identifiants techniques dans les tableaux affichés.

## 5. Une ligne « étape suivante » à la fin de chaque skill
Terminer chaque exécution par exactement une phrase :
> « Étape suivante : `/designer:<skill>` — <pourquoi en quelques mots>. »

## 6. Langue
**Tout en français** (interaction + artefacts). Seuls les identifiants/valeurs machine du
manifeste et les noms d'outils/formats (`/design-sync`, Claude Design, DTCG, Style Dictionary,
WCAG, ARIA) restent tels quels.
