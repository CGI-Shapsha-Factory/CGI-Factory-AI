# Feature 00X : <Nom>
Statut : draft | complete   <!-- complete = brief complet ; draft = il reste un point à trancher en session. -->

## 1. Narratif (quoi et pourquoi)
2 à 4 phrases héritées de la vision. Problème résolu et valeur. Aucune technologie.

## 2. Utilisateurs concernés
Personas de la feature. Acteur principal, acteurs secondaires.

## 3. User stories
En tant que <rôle>, je veux <action>, afin de <bénéfice>. Plusieurs par feature,
chacune testable isolément.

## 4. Critères d'acceptation
Par story, au moins un scénario : Étant donné <contexte>, quand <action>, alors
<résultat>. Cas nominal et cas limites connus. Énoncés non ambigus (pas de
"rapide", "simple", "convivial").

## 5. Critères de succès mesurables
Résultats traduits en métriques avec une cible chiffrée, indépendants de la technologie.
Si une cible n'est pas captée, l'écrire en clair "cible à préciser à l'architecture".

## 6. Périmètre
IN : ce que la feature fait. OUT : ce qu'elle ne fait pas, explicitement.

## 7. Dépendances
Features dont celle-ci dépend, et l'ordre qui en résulte. Repris du spec index.

## 8. Contraintes héritées
Contraintes de la pré-constitution / vision applicables à la feature.

## 9. Glossaire pertinent
Liste des termes utilisés par la feature (noms seulement). Les définitions vivent
dans le glossaire global (`glossaire.md`), la **source de vérité** - ne pas
les copier ici, pour prévenir la dérive.

## 10. Trous
Section conservée par contrat ; rien d'ouvert n'y est laissé (les points se
tranchent en session). Vide quand le brief est complet.

<!--
RÈGLE DE VALIDATION DU BRIEF (cadrage-briefs) :
sections 1 à 9 présentes, chaque story avec au moins un critère d'acceptation,
critères de succès chiffrés ou "à préciser à l'architecture", périmètre OUT non vide.

Ce gabarit EST le contrat central. Ne pas changer sa structure : le skill
cadrage-completude valide à partir de lui et SpecKit le consomme via
/speckit.specify. Ne pas inventer : un élément absent des sources se tranche EN
SESSION (on pose la question), jamais comblé ni marqué. Aucune provenance écrite
(pas de `(src:)`), aucune notion de MVP.

AUTO-CONTRÔLE QUALITÉ (INVEST / QUS), §3 et §4 :
- Chaque story : Indépendante, Négociable, Valorisable, Estimable, Petite, Testable.
- Chaque critère : non ambigu (aucun mot vague), atomique, testable.
-->
