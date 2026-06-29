# Gabarit — Prompt Claude Design du design system

> Gabarit statique lu par `/designer:designer-atelier` une fois la **couverture jugée
> suffisante**. **Cet en-tête reste dans le plugin** ; le fichier sauvegardé sous
> `prompts/designer/<NNN>-<JJ-MM>-claude-design.md` ne contient **que le corps du prompt**
> (le bloc de code ci-dessous, rempli), **sans titre, sans note, sans métadonnée, sans pied
> de page** — cf. `references/ux-conventions.md` §3bis.
>
> Le modèle **remplace tous les `<…>`** par le contenu réel tiré du `product-brief.md`
> (vision, ton), du `spec-index.md` (parcours), du `glossaire.md` (entités/microcopie) et de
> `design-impact.md` (stack cible §1, thématisation/identité §2, erreurs/async §3,
> accessibilité/responsive/i18n/perf §4). Le prompt doit être **auto-portant** : Claude
> Design n'a aucun contexte projet, tout doit être dans le prompt. **Aucune `(src:)` dans le
> prompt sauvegardé.** Les items « sans objet » sont **omis** ; **aucun `[À VALIDER]`** ne
> figure dans le prompt (tout point est résolu en session avant la génération).

```
Conçois et produis le design system de <produit en 1 phrase>, puis applique-le à tous les
écrans. Objectif : un système cohérent, accessible et exécutable, prêt à être synchronisé en
code. Ne copie pas la maquette existante : elle est une inspiration, pas une cible. Marque ce
qui manque plutôt que de l'inventer.

Contexte produit
- Produit / vision : <1–2 phrases>.
- Direction stylistique : <maquette de cadrage comme inspiration (réf. …) ; marque si
  présente — palette / typo / ton — sinon direction à poser, feuille blanche assumée>.
- Stack cible (rend le système exécutable et synchronisable) : <framework front, lib de
  composants, stratégie CSS / tokens>.

Fondation à produire (commencer petit, ne pas sur-tokeniser)
- Tokens essentiels : couleurs sémantiques (primaire, texte, fond, succès, erreur, alerte),
  échelle typographique (tailles + graisses), échelle d'espacement (4–8 valeurs), rayons,
  élévation.
- Thématisation : <clair / sombre si requis ; branding par tenant si multitenance>.
- Composants de base avec TOUS leurs états (défaut, survol, focus, actif, désactivé,
  chargement, erreur) : bouton, champ, select, case / radio, bascule, modale, notification,
  liste / tableau, navigation.
- Mouvement : petit jeu de durées + easing, minimal, appliqué partout.

Couverture exigée (consignes de discipline)
- Tous les états par composant — ne livre pas un composant sans ses états.
- Tous les parcours clés couverts de bout en bout : <lister les parcours>.
- États d'écran : chargement, vide (message + action), contenu, succès ; distinguer 1re
  utilisation et aucun résultat.
- Erreurs : validation à la sortie du champ (message explicite et actionnable), erreur
  serveur, perte de connexion ; le format d'erreur de l'API se projette en messages par
  champ.
- Identité / rôles : <variantes par rôle, non autorisé, écran de connexion, session
  expirée>.
- Accessibilité : contraste AA, focus visible, cibles suffisantes, navigation clavier,
  erreurs jamais signalées par la couleur seule, focus porté sur le 1er champ en erreur.
- Responsive : <breakpoints cibles + comportement mobile> ; internationalisation si requise ;
  budget de performance (éviter les animations lourdes si contrainte).

Hors périmètre
Le back, la persistance, le modèle de données interne et le déploiement ne sont pas demandés.
```
