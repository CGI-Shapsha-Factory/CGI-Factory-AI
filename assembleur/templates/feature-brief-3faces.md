# Feature NNN — <nom> (brief 3-faces)

Walking skeleton : [oui/non] · Dépendances : [NNN, …]

## Face fonctionnelle (src: cadrage)
- **Valeur / objectif :** [...]
- **Périmètre IN / OUT :** [...]
- **Critères d'acceptation :** Given/When/Then [...]

## Face technique (src: architecte)
- **Composants touchés :** [...]
- **Stack / frameworks :** [...]
- **ADR applicables :** [ADR-00X]
- **Cibles de qualité (QS) :** [mesurables] [À CHIFFRER]

## Face design (src: designer)
- **Parcours :** [...]
- **Composants & états :** [...] (vide / chargement / erreur traités)
- **Tokens mobilisés :** [color.*, space.* — pas de valeur brute]
- **Accessibilité :** WCAG 2.2 AA [points spécifiques]

## Checklist de cohérence (3 faces) — porte humaine
- [ ] chaque parcours design a une FR fonctionnelle correspondante
- [ ] chaque composant design est supporté par la face technique
- [ ] aucune FR sans parcours ni critère d'acceptation
- [ ] cibles de qualité mesurables (ou [À CHIFFRER] assumé)
- [ ] aucun trou bloquant `[À VALIDER]`
