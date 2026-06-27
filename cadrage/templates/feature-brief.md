# Feature 00X — <Nom>
MVP : oui | non   <!-- hérité du spec-index (source unique), copié à la génération, non re-décidé ici -->
Statut : draft | complete   <!-- complete = AUCUN trou BLOQUANT ; des [À CHIFFRER] non-bloquants peuvent rester (déférés à l'architecture). draft = il reste un trou bloquant. -->

## 1. Narratif (quoi et pourquoi)
2 à 4 phrases héritées de la vision. Problème résolu et valeur. Aucune technologie.

## 2. Utilisateurs concernés
Personas de la feature. Acteur principal, acteurs secondaires.

## 3. User stories
En tant que <rôle>, je veux <action>, afin de <bénéfice>. Plusieurs par feature,
chacune testable isolément. Chaque story porte sa source `(src: <ref>)`.

## 4. Critères d'acceptation
Par story, au moins un scénario : Étant donné <contexte>, quand <action>, alors
<résultat>. Cas nominal et cas limites connus. Énoncés non ambigus (pas de
« rapide », « simple », « convivial »), chacun avec sa source `(src: <ref>)`.

## 5. Critères de succès mesurables
Résultats traduits en métriques avec une cible chiffrée, indépendants de la technologie.
Marquer `[À CHIFFRER]` si non capté. Source `(src: <ref>)` par critère.

## 6. Périmètre
IN : ce que la feature fait. OUT : ce qu'elle ne fait pas, explicitement.

## 7. Dépendances
Features dont celle-ci dépend, et l'ordre qui en résulte. Repris du spec index.

## 8. Contraintes héritées
Contraintes de la pré-constitution / vision applicables à la feature.

## 9. Glossaire pertinent
Liste des termes utilisés par la feature (noms seulement). Les définitions vivent
dans le glossaire global (`glossaire.md`), la **source de vérité** — ne pas
les copier ici, pour prévenir la dérive.

## 10. Trous
Liste des éléments `[À VALIDER]`. Vide quand le brief est complet.

<!--
RÈGLE DE VALIDATION DU BRIEF (porte de sortie de cadrage-briefs) :
sections 1 à 9 présentes, chaque story avec au moins un critère d'acceptation,
critères de succès chiffrés ou marqués `[À CHIFFRER]`, périmètre OUT non vide.
Si la section 10 contient un trou bloquant, le brief reste `draft`.

Ce gabarit EST le contrat central. Ne pas changer sa structure : le skill
cadrage-completude valide à partir de lui et SpecKit le consomme via
/speckit.specify. Marquer, ne pas inventer : tout élément absent des sources
est laissé `[À VALIDER]` et listé en section 10, jamais comblé.

AUTO-CONTRÔLE QUALITÉ (INVEST / QUS), §3 et §4 :
- Chaque story : Indépendante, Négociable, Valorisable, Estimable, Petite, Testable.
- Chaque critère : non ambigu (aucun mot vague), atomique, testable, sourcé.
- Chaque énoncé en §3/§4/§5 porte sa source `(src:)` ; sinon `[À VALIDER]`.
-->
