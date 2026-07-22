# Conventions UX : sortie utilisateur (validation)

## Typographie : écrire comme un humain (artefacts, commentaires Linear ET sortie chat)
S'applique à **tout ce que la Factory écrit** : le plan de test, la mission Cowork, les
résultats d'exécution, le rapport de recette, les scénarios rejouables, les commentaires
Linear, et le texte affiché. Ne jamais employer ces caractères ; toujours l'équivalent
clavier naturel :
- tiret cadratin (em dash, U+2014) -> ponctuation adaptée au contexte : deux-points dans un titre, virgule ou parenthèses dans une phrase, tiret simple " - " dans une liste.
- points de suspension unicode (U+2026) -> trois points ASCII "..."
- flèches unicode (U+2192 / U+2194) -> "->" / "<->" (ou un mot : "vers", "puis").
- guillemets à chevrons (U+00AB / U+00BB) -> guillemets droits "...".
- coche / croix (U+2713 / U+2717) -> les mots Oui / Non (dans un rapport de test : OK / KO).
- espaces insécables (U+00A0 / U+202F) et caractères invisibles -> une espace normale.
Objectif : le texte doit ressembler à de la frappe clavier humaine, pas à une sortie de modèle.

Règles transverses pour tout ce que les skills affichent à l'utilisateur. Mêmes principes
que les autres plugins de la Factory.

## 1. Jamais de nom d'attribut / clé JSON en sortie
Le manifeste garde ses clés (contrat machine) ; le **texte affiché** et les **refus** sont
en **langage naturel français**. Correspondance :

| Interne (manifeste / fichiers) | Langage utilisateur |
|---|---|
| `validation.environnement_recette` | "l'adresse de l'environnement de recette" |
| `validation.outil_prefere` | "l'outil d'exécution habituel" |
| `chrome-extension` / `playwright-mcp` | "l'extension Chrome" / "Playwright" |
| verdict `OK` / `KO` / `NON TESTABLE` | ces trois mots, tels quels (vocabulaire du rapport) |
| `parentId` | "le rattachement au ticket de la feature" |
| `architecture.feature_sequence` | "le registre des features" |

Ne jamais afficher de **tableau de booléens** bruts. **Règle absolue, même dans une
justification** : on n'écrit **jamais** un nom de variable / clé manifeste dans le texte vu
par l'utilisateur. On reformule **toujours** en clair.

## 1bis. Identifiants : cas de test et Linear oui, codes internes non
Deux familles d'identifiants sont **publiques** et peuvent être montrées et demandées :
- l'**identifiant d'un cas de test** (ex. `TC-001-003`) : c'est le repère de traçabilité du
  rapport, partagé entre le plan, les résultats et les scénarios rejouables ;
- l'**identifiant natif Linear** (ex. `ENG-123`) : le nom public d'un ticket.
Les **codes internes** restent bannis en sortie : pas de clé de manifeste, pas d'UUID interne,
pas de `parentId`. **Exception features (comme au cadrage)** : une feature se nomme par son
**intitulé complet en langage naturel** suivi de sa référence entre parenthèses, ex. "la
recherche en langage naturel (001)" - jamais un numéro nu.

## 1ter. Mise à jour du manifeste = silencieuse
Le manifeste se met à jour **sans le narrer**. **Interdit** à l'écran : toute ligne de bilan
"Manifeste à jour : ..." ou liste `champ: valeur` / `true`/`false`. **L'utilisateur ne
s'intéresse pas à l'état du manifeste.** À l'utilisateur, on dit **ce qui a été produit**
(en clair : le plan dérivé, les cas exécutés, le rapport écrit) et **la prochaine étape** -
rien de la mécanique sous le capot.

## 2. Refus en langage naturel
Quand un skill ne peut pas tourner, expliquer **en clair** pourquoi et quoi faire. Ex. :
"Je ne peux pas dériver de plan de test : la spécification de cette feature n'existe pas
encore (aucun dossier pour elle sous `specs/`) - fabrique d'abord la feature via SpecKit."
Jamais un refus technique avec un nom de champ ou un code d'erreur brut.

## 3. Aucun placeholder persisté (trois constats de test exceptés)
On **n'écrit pas** de point non tranché dans un fichier : un point sans réponse est **omis**
(cf. `interactive-loop.md`), jamais marqué `[À VALIDER]`. **Trois exceptions**, qui sont des
**constats de test**, pas des points ouverts : le statut `A CLARIFIER` d'un critère non
testable dans le plan (avec sa raison), le verdict `NON TESTABLE` dans les résultats et le
rapport, et la cellule "Décision sur l'écart" laissée **vide** dans la matrice pour un écart
pas encore trié (un écart est un fait, sa ligne ne peut pas être omise ; la porte de recette
reste infranchissable tant qu'une cellule de décision est vide). À l'oral on dit "à
confirmer" - jamais de variantes anglaises (`[TBD]`...).

## 4. Restitutions en prose
Les bilans (état d'une exécution, tri d'un écart, synthèse de recette) se restituent en
**prose claire** (ce qui est établi, ce qui reste, la prochaine étape). Un tableau n'est
utilisé que pour des listes courtes et énumérables (ex. la matrice critère -> cas -> verdict
du rapport, ou le récapitulatif de la porte de recette).

## 5. Une ligne "étape suivante" à la fin de chaque skill
Terminer chaque exécution par exactement une phrase, **toujours affichée** (elle n'est jamais
omise, même quand le skill s'arrête tôt ou refuse) :
> "Étape suivante : `/validation:<skill>` (ou `/maintenance:<skill>`) - <pourquoi en quelques mots>."

La recette est la phase la plus ramifiée de la factory : la suite dépend de l'outil
d'exécution choisi, de la nature des écarts et du verdict. Quand plusieurs suites sont
réellement possibles, **les nommer toutes dans cette même phrase**, chacune avec sa condition,
dans cet ordre : le **chemin normal en premier**, puis les branches (`Ou <skill> si <condition>`).
L'utilisateur doit voir d'un coup d'oeil "c'est ça, ou ça, selon". Ne jamais citer un skill qui
n'existe pas : les suites sont des skills réels de `/validation:*` ou `/maintenance:*`.

## 6. Langue
**Tout en français** (interaction + artefacts + commentaires Linear). Seuls les
identifiants/valeurs machine du manifeste et les noms d'outils/formats (Linear, SpecKit,
`spec.md`, Playwright, Chrome) restent tels quels.
