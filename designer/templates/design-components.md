# Contrats de composants (design system)

<!-- Public visé : designers + Claude Code (référencé à chaque implémentation d'UI).
     Une entrée par composant. Le composant fige le SYSTÈME, pas un écran. -->
<!-- Remplir chaque [placeholder]. Marqueurs [À VALIDER]. (src: maquette | …). -->

---

## [NomDuComposant]

- **Objet :** [rôle du composant en une phrase] (src: maquette)
- **Anatomie :** [parties : conteneur, libellé, icône, …]
- **Variantes :** [primaire / secondaire / … ; tailles ; tons]
- **États :** <!-- définir le rendu de chacun ; ne garder que ceux qui s'appliquent -->
  - default · hover · focus (visible, non masqué) · active/pressed · disabled
  - loading · empty · error · selected — [le cas échéant]
- **Props / API :** [propriétés publiques : nom, type, défaut]
- **Accessibilité :**
  - Rôle / sémantique : [rôle ARIA ou élément HTML natif]
  - Clavier (WAI-ARIA APG) : [touches : Tab, Entrée/Espace, flèches, Échap…]
  - Focus : [ordre, piège de focus si modale, restitution]
  - Contraste : [respecte les tokens sémantiques AA]
- **Responsive :** [comportement par point de rupture]
- **Tokens utilisés :** [color.*, typography.*, dimension.space.*, radius.*, elevation.*]

---

<!-- Répéter par composant. RÈGLE : aucune valeur brute (couleur/taille) — toujours un
     token sémantique. Chaque composant interactif liste ses états ; pas d'écran figé ici. -->
