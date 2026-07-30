# Conventions UX : sortie utilisateur (couts)

Règles transverses pour tout ce que les skills `couts` affichent ou écrivent (rapports `rapport-couts.md` / `bilan-couts.md`, tableaux en session).

## Typographie : écrire comme un humain (artefacts, prompts ET sortie chat)
S'applique à **tout ce que la Factory écrit** : les rapports, les tableaux, et le texte affiché. Ne jamais employer ces caractères ; toujours l'équivalent clavier naturel :
- tiret cadratin (em dash, U+2014) -> ponctuation adaptée au contexte : deux-points dans un titre, virgule ou parenthèses dans une phrase, tiret simple " - " dans une liste.
- points de suspension unicode (U+2026) -> trois points ASCII "..."
- flèches unicode (U+2192 / U+2194) -> "->" / "<->" (ou un mot : "vers", "puis").
- guillemets à chevrons (U+00AB / U+00BB) -> guillemets droits "...".
- coche / croix (U+2713 / U+2717) -> les mots Oui / Non.
- espaces insécables (U+00A0 / U+202F) et caractères invisibles -> une espace normale.
- point médian (U+00B7) en séparateur -> une virgule, ou " - ".
Objectif : le texte doit ressembler à de la frappe clavier humaine, pas à une sortie de modèle.

**Pour les rapports, ce n'est plus une consigne mais une garantie.** `rapport-couts.md` et
`bilan-couts.md` sont des documents qu'on transmet tels quels : les générateurs
(`cost_report.py`, `cost_total.py`) passent le document entier dans `sanitize_typo()` **juste
avant de l'écrire**, et `check_costs.py` **échoue** si un rapport présent dans `.factory/couts/`
porte encore un de ces caractères. Une chaîne ajoutée plus tard dans un générateur est donc
couverte sans qu'on ait à y penser. Ne jamais contourner l'appel au nettoyage pour "gagner un
appel" : c'est lui qui tient la promesse.
