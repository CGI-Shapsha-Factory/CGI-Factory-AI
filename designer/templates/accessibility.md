# Contrat d'accessibilité (WCAG 2.2 AA)

<!-- Public visé : designers + Claude Code. Cible : WCAG 2.2, niveau AA. -->
<!-- Remplir chaque [placeholder]. Marqueurs [À VALIDER]/[À CHIFFRER]. (src: …). -->

> Standard : **WCAG 2.2**, niveau **AA**. Les critères ci-dessous sont opposables.

## Contraste
- Texte normal ≥ **4,5:1** ; grand texte (≥ 24 px, ou 19 px gras) & composants/icônes ≥ **3:1**.
- Paires de couleurs sémantiques vérifiées dans `foundations.md`. [À CHIFFRER]

## Clavier & focus
- Toute fonctionnalité est **opérable au clavier** (pas de piège).
- **Focus visible** et **non masqué** (critères 2.4.11 / 2.4.13, nouveaux en 2.2).
- Ordre de focus logique ; modèle clavier par composant (voir `components.md`).

## Cibles & pointeur
- **Taille de cible ≥ 24×24 px** (critère 2.5.8, nouveau en 2.2), ou espacement suffisant.
- Alternatives au **glisser** (critère 2.5.7).

## Mouvement & préférences
- Respecter `prefers-reduced-motion` ; pas de contenu clignotant > 3 fois/s.

## Structure & sémantique
- Titres hiérarchisés, points de repère (landmarks), libellés de formulaire associés.
- Messages d'état via rôles `status` / `alert`.

## Contenu
- Alternatives textuelles aux images porteuses de sens ; langue de la page déclarée.

<!-- Tout critère non vérifié reste [À VALIDER]. -->
