# Table de correspondance — items de checklist → entrées (cadrage, architecte, humain)

Lue par le skill `designer` (étape 1, pré-remplissage). Pour chaque **item de la checklist de couverture**,
indique **d'où il se déduit**. Le skill auto-remplit (`status: deduced`, avec `(src: …)`) ce qui vient des
handoffs et ne **pose** (boucle 3-options) que les items **H** ou restés `open`. Un item bloquant non
statué empêche de juger la couverture suffisante. La **maquette** est une **direction** (inspiration), pas
une cible.

| item | Élément | Origine | Source de pré-remplissage | À demander ? |
|------|---------|---------|---------------------------|--------------|
| F1 | Tokens essentiels | H | maquette (palette/typo/espacement observés) + marque si présente | oui (valider/poser la direction) |
| F2 | Thématisation (clair/sombre, tenant) | A+H | `design-impact.md` §2 (multitenance/theming) | oui si choix de thème |
| F3 | Composants de base + états | H | maquette + `design-impact.md` (états techniques) | oui (états par composant) |
| F4 | Mouvement | H | — | oui (jeu minimal de durées/easing) |
| E1 | Parcours et variantes | C | `spec-index.md` (use cases/parcours) | non |
| E2 | États de chaque écran | C+H | `spec-index.md` (déclenche) | oui (tranche 1re util. vs aucun résultat) |
| E3 | États vides utiles | H | — | oui |
| E4 | Hiérarchie et densité | C+H | `product-brief.md` (objectifs) | oui |
| E5 | Feedback et confirmation | H+A | `design-impact.md` §3 (async) | oui (destructrices + annulation) |
| E6 | Microcopie | H | `glossaire.md` (vocabulaire) | oui (ton, libellés) |
| T1 | Affichage des erreurs | A | `design-impact.md` §3 (format erreur API) | non (sauf trous) |
| T2 | Chargement et asynchrone | A | `design-impact.md` §3 (async) | non |
| T3 | Listes, tableaux, pagination | A | `design-impact.md` §3 (pagination/listes) | non |
| T4 | Identité, rôles, autorisations | A | `design-impact.md` §2 (identité/rôles/SSO) | non |
| T5 | Navigation et routage | A | `design-impact.md` §2 (navigation/routage) | non |
| T6 | Accessibilité, socle | A | `design-impact.md` §4 (niveau visé) | non — défaut WCAG 2.2 AA |
| T7 | Responsive | A | `design-impact.md` §4 (breakpoints) | non |
| T8 | Internationalisation | A | `design-impact.md` §4 (i18n) — sinon **sans objet** | non |
| T9 | Budget de performance | A | `design-impact.md` §4 (perf) — sinon **sans objet** | non |

**Méthode (résumé)** : les items **A** (versant technique) se pré-remplissent depuis `design-impact.md`
(le contrat propre de l'architecte) ; les items **C** depuis le cadrage ; les items **H** (expérience +
fondation) se co-construisent. On ne re-pose **jamais** ce que les handoffs ont déjà tranché. Item sans
objet → **`sans_objet`** (marqué, pas forcé). Rien d'inventé : un item resté `open` est listé tel quel.
