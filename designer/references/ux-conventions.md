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
| item `status: deduced` / `decided` | « validé » |
| item `status: open` | « à traiter » |
| item `status: sans_objet` | « sans objet » |
| `design.coverage_sufficient` | « la couverture est jugée suffisante » |
| `design.design_system_ref` | « le design system (Claude Design) » |
| `design.design_validated` | « le système de design est validé » |

Ne jamais afficher de **tableau de booléens** bruts ni de **tableau de contrôles / synthèse**,
ni écrire `design_validated == false`. **Règle absolue, même dans une justification** : on
n'écrit **jamais** un nom de variable / clé manifeste dans le texte vu par l'utilisateur — pas
`coverage_sufficient`, pas `design_validated`, pas `design.phase = "valide"`. On reformule
**toujours** en clair.

## 1bis. Jamais d'identifiant codé en sortie
L'utilisateur ne retient pas les codes. **Interdit** en sortie : les identifiants d'items de
checklist `F1`, `E6`, `T3`…, comme les codes de cadrage/archi `UC1`, `C2`, `ADR A6`. Chaque
item de la checklist se désigne par sa **phrase complète** (« la palette de couleurs, l'échelle
typographique et les espacements de base », « le ton des textes de l'interface »…), **jamais**
par son code. Les ids restent des **clés internes** du manifeste, jamais affichées ni utilisées
pour désigner une chose à l'écran ; **aucune colonne d'identifiants** dans un tableau montré.

## 1ter. Mise à jour du manifeste = silencieuse
Le manifeste se met à jour **sans le narrer**. **Interdit** à l'écran : « MAJ
`design.checklist` », « `design.phase = "atelier"` », « je passe `design_validated = true` »,
« `coverage_sufficient = true` », **toute ligne de bilan** « Manifeste à jour : phase: X, … » ou liste
`champ: valeur` / `true`/`false`. **L'utilisateur ne s'intéresse pas à l'état du manifeste.** À
l'utilisateur, on dit **ce qui a été produit** (en clair) et **la prochaine étape** — rien de la
mécanique sous le capot.

## 2. Refus en langage naturel
Quand un skill ne peut pas tourner, expliquer **en clair** pourquoi et quoi faire. Ex. :
« Cette étape ne peut pas démarrer : il faut une maquette validée et un contrat technique
validé — termine d'abord le cadrage et l'architecture. » Jamais « ⛔ design_validated ==
false ».

## 3. Marqueurs internes hors texte utilisateur
Les marqueurs (`[À VALIDER]`, `[À CHIFFRER]`) vivent dans la mécanique interne. À l'oral on
dit « à traiter », « à valider », « à chiffrer ». **Le prompt Claude Design sauvegardé ne
contient aucun `[À VALIDER]`** : tout point est résolu en session avant la génération
(cf. `skills/designer-prompt`).

## 3bis. Fichiers prompt sauvegardés = corps seul, prêt à coller
Tout prompt écrit sous `designer-out/prompts/….md` contient **uniquement le prompt prêt à coller**
dans Claude Design. **Interdit** dans le fichier : titre (`# Prompt Claude Design — …`), note
en blockquote, ligne de métadonnée (`Date : … | Version : …`), `---` d'en-tête, ou tout pied
de page. La métadonnée (sujet, date, version) vit dans l'entrée `prompts[]` du manifeste,
**jamais** dans le fichier. Objectif : l'utilisateur ouvre le fichier et copie tout, sans rien
nettoyer. Le gabarit `templates/claude-design-prompt.md` garde son en-tête explicatif ; seul le
**corps du bloc de code** rempli est sauvegardé.

Le prompt lui-même est du **plein texte prêt à coller** : **aucun Markdown dans le corps** — pas de
titre `#`, pas de `**gras**`, pas de tableau, pas de `---`, pas de blocs ``` ``` — seulement des
**libellés de section en clair** (« Direction visuelle », « Contexte produit », « Fondation »…) et des
tirets `-`. Ainsi le texte collé dans Claude Design reste propre, sans artefact de mise en forme.

## 4. Langage non technique, pas de tableau imposé
Composants, tokens, parcours et items de couverture restitués en **valeur / usage**
compréhensibles (prose claire). Pas de jargon inutile, pas d'identifiant technique, et **pas de
tableau de synthèse / cohérence** imposé à l'utilisateur : un **bilan en prose** (ce qui est
validé, ce qui reste, la prochaine étape) plutôt qu'un tableau de contrôles.

## 5. Une ligne « étape suivante » à la fin de chaque skill
Terminer chaque exécution par exactement une phrase :
> « Étape suivante : `/designer:<skill>` — <pourquoi en quelques mots>. »

## 6. Langue
**Tout en français** (interaction + artefacts). Seuls les identifiants/valeurs machine du
manifeste et les noms d'outils/formats (Claude Design, DTCG, Style Dictionary,
WCAG, ARIA) restent tels quels.
