# Conventions UX : sortie utilisateur (recette)

## Typographie : écrire comme un humain (tickets, commentaires ET sortie chat)
S'applique à **tout ce que la Factory écrit** : les tickets et commentaires Linear, les
mises à jour de spécification, et le texte affiché. Ne jamais employer ces caractères ;
toujours l'équivalent clavier naturel :
- tiret cadratin (em dash, U+2014) -> ponctuation adaptée au contexte : deux-points dans un titre, virgule ou parenthèses dans une phrase, tiret simple " - " dans une liste.
- points de suspension unicode (U+2026) -> trois points ASCII "..."
- flèches unicode (U+2192 / U+2194) -> "->" / "<->" (ou un mot : "vers", "puis").
- guillemets à chevrons (U+00AB / U+00BB) -> guillemets droits "...".
- coche / croix (U+2713 / U+2717) -> les mots Oui / Non.
- espaces insécables (U+00A0 / U+202F) et caractères invisibles -> une espace normale.
Objectif : le texte doit ressembler à de la frappe clavier humaine, pas à une sortie de modèle.

Règles transverses pour tout ce que les skills affichent à l'utilisateur. Mêmes principes
que les autres plugins de la Factory.

## 1. Jamais de nom d'attribut / clé JSON en sortie
Le manifeste garde ses clés (contrat machine) ; le **texte affiché** et les **refus** sont
en **langage naturel français**. Correspondance :

| Interne (manifeste / Linear) | Langage utilisateur |
|---|---|
| `recette.labels.anomalie` / `.evolution` | "les étiquettes de recette dans Linear" |
| `recette.statut_requalification` | "le statut de requalification dans Linear" |
| `statut_requalification.present: false` | "le statut de requalification n'existe pas encore dans l'équipe Linear" |
| `parentId` | "le rattachement au ticket de la feature" |
| `state: started` / `completed` | "le ticket passe en cours / est terminé" |
| `architecture.feature_sequence` | "le registre des features" |

Ne jamais afficher de **tableau de booléens** bruts ni écrire `present == false`. **Règle
absolue, même dans une justification** : on n'écrit **jamais** un nom de variable / clé
manifeste dans le texte vu par l'utilisateur. On reformule **toujours** en clair.

## 1bis. Identifiants : Linear oui, codes internes non
L'**identifiant natif Linear** (ex. `ENG-123`) est le nom public d'un ticket : on **peut** le
montrer et le demander (c'est comme ça que le PO et le développeur désignent une anomalie ou une
évolution). En revanche les **codes internes** restent bannis en sortie : pas de clé de manifeste,
pas d'UUID interne (`issue_id`), pas de `parentId`. **Exception features (comme au cadrage)** :
une feature se nomme par son **intitulé complet en langage naturel** suivi de sa référence entre
parenthèses, ex. "la recherche en langage naturel (001)" - jamais un numéro nu.

## 1ter. Mise à jour du manifeste = silencieuse
Le manifeste se met à jour **sans le narrer**. **Interdit** à l'écran : toute ligne de bilan
"Manifeste à jour : ..." ou liste `champ: valeur` / `true`/`false`. **L'utilisateur ne
s'intéresse pas à l'état du manifeste.** À l'utilisateur, on dit **ce qui a été produit**
(en clair : le ticket créé, la correction faite, la spécification mise à jour) et **la
prochaine étape** - rien de la mécanique sous le capot.

## 2. Refus en langage naturel
Quand un skill ne peut pas tourner, expliquer **en clair** pourquoi et quoi faire. Ex. :
"Je ne peux pas créer d'anomalie : je ne trouve pas le ticket de la feature dans Linear -
lance d'abord la première alimentation de Linear côté assembleur." Jamais un refus
technique avec un nom de champ ou un code d'erreur brut.

## 3. Aucun placeholder persisté
On **n'écrit pas** de point non tranché dans un ticket ou une spécification : un point sans
réponse est **omis** (cf. `interactive-loop.md`), jamais marqué `[À VALIDER]`. À l'oral on dit
"à confirmer" - jamais de variantes anglaises (`[TBD]`, `[TO CONFIRM]`...).

## 4. Restitutions en prose
Les bilans (impact, cause racine, périmètre d'une évolution) se restituent en **prose claire**
(ce qui est établi, ce qui reste, la prochaine étape), pas en tableau de contrôles. Un tableau
n'est utilisé que pour des listes courtes et énumérables (ex. la liste des features impactées).

## 5. Une ligne "étape suivante" à la fin de chaque skill
Terminer chaque exécution par exactement une phrase :
> "Étape suivante : `/recette:<skill>` - <pourquoi en quelques mots>."

## 6. Langue
**Tout en français** (interaction + tickets + commentaires). Seuls les identifiants/valeurs
machine du manifeste et les noms d'outils/formats (Linear, SpecKit, `spec.md`, `tasks.md`)
restent tels quels.
