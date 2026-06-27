# Prompt Claude Design — <projet>

> Généré par `/designer:designer` une fois la **couverture jugée suffisante**. Sert à faire **naître le
> design system dans Claude Design** (nativement). Le design system produit est ensuite **validé par
> l'humain** puis synchronisé en code par **`/design-sync`**. Ce prompt ne copie pas la maquette : elle
> est une **inspiration/direction**, pas une cible. **Marquer ce qui manque plutôt que l'inventer.**

## 1. Contexte produit
- Produit / vision (1–2 phrases) : … `(src: product-brief)`
- Direction stylistique : maquette de cadrage comme **inspiration** (réf. …) ; **marque** si présente
  (palette/typo/ton) sinon **direction à poser** (feuille blanche stylistique assumée). `(src: maquette / marque)`
- Stack cible (rend le système exécutable/synchronisable) : framework front, lib de composants, stratégie
  CSS/tokens. `(src: design-impact §1)`

## 2. Fondation à produire (commencer petit)
- **Tokens essentiels** : couleurs sémantiques (primaire, texte, fond, succès, erreur, alerte), échelle
  typo (tailles + graisses), échelle d'espacement (4–8 valeurs), rayons, élévation.
- **Thématisation** : clair / sombre si requis ; branding par tenant si multitenance. `(src: design-impact §2)`
- **Composants de base** + **tous leurs états** (défaut, survol, focus, actif, désactivé, chargement,
  erreur) : bouton, champ, select, case/radio, bascule, modale, notification, liste/tableau, navigation.
- **Mouvement** : petit jeu de durées + easing, minimal, appliqué partout.

## 3. Couverture exigée (consignes de discipline)
- **Tous les états par composant** — ne pas livrer un composant sans ses états.
- **Tous les parcours** clés couverts de bout en bout `(src: cadrage parcours)`.
- **États d'écran** : chargement, vide (avec message + action), contenu, succès ; 1re utilisation ≠ aucun résultat.
- **Erreurs** : validation à la sortie du champ (message explicite et actionnable), erreur serveur, perte
  de connexion ; le **format d'erreur API** se projette en **messages par champ** `(src: design-impact §3)`.
- **Identité/rôles** : variantes par rôle, non autorisé, connexion, session expirée `(src: design-impact §2)`.
- **Accessibilité** : contraste AA, focus visible, cibles suffisantes, navigation clavier, erreurs pas par
  la couleur seule, focus sur le 1er champ en erreur `(src: design-impact §4)`.
- **Responsive** : breakpoints cibles + comportement mobile ; **i18n** si requis ; **budget perf**
  (éviter animations lourdes si contrainte). `(src: design-impact §4)`
- **Marquer ce qui manque** (ne pas inventer) ; ne pas sur-tokeniser ni créer de composant inutile.

## 4. Ce qui est hors périmètre du prompt
Le back, la persistance, le modèle de données interne, le déploiement (cf. exclusions du handoff architecte).

---
*Items « sans objet » de la checklist : omis du prompt. Items « ouverts » restants : listés comme
`[À VALIDER]` à clarifier, jamais comblés.*
