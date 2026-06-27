# Table de correspondance — questions de design → entrées (maquette, cadrage, architecte)

Lue par le skill `designer` (étape 0 de vérification). Pour chaque question de design,
indique **où la réponse se trouve déjà**. Le skill auto-remplit (avec `(src: …)`) et ne
**pose** (boucle 3-options) que les questions **non couvertes**. Une question bloquante non
répondue empêche de démarrer la génération.

| # | Question de design | Source | À demander ? |
|---|--------------------|--------|--------------|
| 1 | Maquette validée (réf.) | `manifest.demonstrateur` (`client_validated`, `external_ref`) | non |
| 2 | Vision / ton produit | `product-brief.md` §1-2 (+ vision) | non |
| 3 | Langage / vocabulaire d'UI | `glossaire.md` | non |
| 4 | Parcours candidats (use cases) | `spec-index.md` | non |
| 5 | Palette de couleurs | maquette validée (observée) | non — sauf si la maquette ne la fixe pas |
| 6 | Typographies | maquette validée | non — idem |
| 7 | Espacement / densité | maquette validée | non — idem |
| 8 | Composants visibles | maquette validée + `components.md` (architecte) | non |
| 9 | Framework front-end (livraison des tokens) | `tech-stack.md` (architecte) | non |
| 10 | Plateformes / tailles cibles | `project-frame.md` + maquette | non — sauf si absent |
| 11 | **Identité de marque (logo, couleurs de marque, polices imposées)** | **souvent absent** | **OUI si non fixé par la maquette** |
| 12 | Contraintes d'accessibilité spécifiques | `product-brief.md` §contraintes | non — défaut WCAG 2.2 AA |

**Méthode (résumé)** : la **maquette validée** est la source primaire (couleurs, typo,
espacement, composants) ; le reste vient de cadrage/architecte. Seule l'**identité de
marque** (#11) est posée si la maquette ne la fixe pas. On ne re-pose **jamais** ce que la
maquette ou les phases amont ont déjà tranché. Une réponse de cadrage restée `[À VALIDER]`
bloquante est re-soumise avant de générer quoi que ce soit.
