# Gabarit — Prompt Claude Design du design system

> Gabarit statique lu par `/designer:designer-atelier` une fois la **couverture jugée
> suffisante**. **Cet en-tête reste dans le plugin** ; le fichier sauvegardé sous
> `designer-out/prompts/<NNN>-<JJ-MM>-claude-design.md` ne contient **que le corps du prompt**
> (le bloc de code ci-dessous, rempli), **sans titre, sans note, sans métadonnée, sans pied
> de page** — cf. `references/ux-conventions.md` §3bis.
>
> Le modèle **remplace tous les `<…>`** par le contenu réel tiré du `product-brief.md`
> (vision, ton), du `spec-index.md` (parcours), du `glossaire.md` (entités/microcopie) et de
> `impact-design.md` (stack cible §1, thématisation/identité §2, erreurs/async §3,
> accessibilité/responsive/i18n/perf §4). Le prompt doit être **auto-portant** : Claude
> Design n'a aucun contexte projet, tout doit être dans le prompt. **Aucune `(src:)` dans le
> prompt sauvegardé.** Les items « sans objet » sont **omis** ; **aucun `[À VALIDER]`** ne
> figure dans le prompt (tout point est résolu en session avant la génération).

```
Tu es directeur artistique et designer de systèmes de design senior dans un studio réputé,
spécialiste des interfaces <domaine>. Tu produis des systèmes que des équipes implémentent en
production : cohérents, distinctifs, avec un vrai parti pris — jamais l'aspect « template » ou
« généré par IA ».

Conçois et produis le design system de <produit en 1 phrase>, puis applique-le à tous les
écrans. Objectif : un système cohérent, accessible et exécutable, prêt à être exporté et
implémenté en code. Ne copie pas la maquette existante : elle est une inspiration, pas une cible. Marque ce
qui manque plutôt que de l'inventer.

Avant de concevoir (décider, puis appliquer)
- Décide d'abord la langue visuelle : un mood en 3 mots, la palette nommée ci-dessous, le duo de
  polices, et UN parti pris signature (un geste récurrent de mise en page, un traitement typographique
  ou une façon d'utiliser l'accent) — c'est ce qui distingue le système du template générique.
- Applique-la ensuite de façon cohérente à chaque token, composant et écran.
- Vise l'excellence, pas la moyenne : hiérarchie nette, espaces respirés, une décision assumée
  partout ; le système doit paraître conçu par un humain qui a fait des choix, pas la médiane d'une IA.

Direction visuelle — à suivre à la lettre (aucun choix laissé au défaut)
- Palette : 3 couleurs en hexadécimal avec rôle nommé — <--couleur-primaire: #RRGGBB (actions/CTA)>,
  <--fond: #RRGGBB (légèrement teinté, jamais #ffffff)>, <--texte: #RRGGBB (jamais #000000)>, plus
  <succès / erreur / alerte>. Répartition dominante ~60 % / neutre ~30 % / accent ~10 %, déclinée par
  nuances. Choisie pour ce domaine et ce public (ou la marque du client). JAMAIS violet / indigo /
  mauve « par défaut », JAMAIS de dégradé violet→bleu.
- Typographie : <police de titrage nommée> + <police de corps nommée> — jamais Inter, Roboto, Poppins,
  Space Grotesk, Geist, Arial, system-ui. Échelle ×1,25 ou ×1,333, corps ≥ 16 px, graisses 400/500/600.
- Espacement : unité de base <4 px> sur une grille de 8 pt. Rayons par composant (<boutons 4 px,
  cartes 8 px, panneaux 0 px>). Bordures 1 px uniquement, jamais 2 px et plus.
- N'introduis AUCUNE couleur, police, rayon ou traitement hors de ceux listés ici. Tout choix non
  spécifié retombe sur un défaut générique : suis cette direction à la lettre.

Contexte produit
- Produit / vision : <1–2 phrases>.
- Direction stylistique : <maquette de cadrage = inspiration (réf. …), jamais une cible ; marque du
  client si présente>. Appliquer la « Direction visuelle » ci-dessus (valeurs déjà fixées, concrètes).
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

À éviter absolument (marqueurs d'interface générée par IA)
- Violet / indigo / mauve « par défaut » et dégradés violet→bleu (sauf vraie couleur de marque) ;
  glassmorphism généralisé, orbes ou dégradés flottants, néon sur fond sombre.
- Fonds blanc pur #ffffff ou noir pur #000000 (préférer des fonds légèrement teintés) ; cartes à
  bordure grise 1 px partout ou à bande colorée à gauche (préférer : l'espace, puis un léger décalage
  de fond 3–5 %, puis une ombre douce).
- Polices par défaut (Inter, Roboto, Poppins, Space Grotesk, Geist, Arial, system-ui) ; icônes
  génériques géantes centrées ; emoji ; coins très arrondis sur *tout* ; padding de 50 px et plus
  partout ; layouts clichés : héro plein écran centré (titre + sous-titre + CTA), « exactement trois
  cartes » alignées, sections en grille d'icônes, carrousels de témoignages, rangées d'étapes 1·2·3,
  bannières de statistiques.
- Structure de palette : 3 teintes maximum (dominante ~60 %, neutre ~30 %, accent ~10 %), déclinées
  par nuances/teintes ; espacement sur une grille de 8 pt ; échelle typographique nette (×1,25 ou
  ×1,333), corps ≥ 16 px.

Hors périmètre
Le back, la persistance, le modèle de données interne et le déploiement ne sont pas demandés.
```
