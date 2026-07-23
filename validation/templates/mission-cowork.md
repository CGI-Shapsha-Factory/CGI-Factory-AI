# Mission de recette : [intitulé de la feature] ([numéro de registre])

<!-- Généré par `execution-validation` (voie Cowork) dans
     `validation-out/<feature>/mission-cowork.md`. Document AUTO-PORTANT que le testeur donne à
     Claude Cowork (qui pilote le navigateur via l'extension "Claude in Chrome") : Cowork n'a
     pas l'historique de la session Claude Code, tout ce dont il a besoin est ici ou dans le
     plan de test référencé. Aucune provenance, aucun horodatage. -->

> Tu es l'exécuteur de la recette fonctionnelle de cette feature. Ta mission : jouer le plan
> de test dans le navigateur contre l'environnement de recette, constater, prouver, et écrire
> les résultats au format imposé ci-dessous. **Tu exécutes et tu rapportes ; tu ne juges pas
> la livraison et tu ne corriges rien.**

## Cible

- **Environnement de recette** : [URL de l'application déployée]
- **Plan de test à jouer** : `validation-out/[feature]/plan-de-test.md` (dans ce dossier de
  projet). Le plan est un **tableau** : sous "Déroulé des cas", une **ligne par cas** numéroté
  TC-[feature]-NNN, avec ses colonnes Préconditions, Étapes, Résultat attendu et Source. Les
  étapes d'une cellule sont séparées par `<br>` et se jouent **dans l'ordre**. Les cas listés
  sous "Critères à clarifier" ne se jouent pas : ils sortent NON TESTABLE.
- **Comptes et données de test** : ceux de la section "Pré-requis et données de test" du plan,
  et uniquement ceux-là

## Règles d'exécution (non négociables)

1. **Un cas à la fois**, dans l'ordre du plan. Jouer les étapes telles qu'écrites.
2. **Ne jamais interpréter un critère ambigu** : si une étape ou un résultat attendu n'est pas
   clair ou pas observable, le cas sort en NON TESTABLE avec la raison - on ne devine pas.
3. **Constater, pas juger** : le verdict d'un cas est OK (le résultat attendu est observé),
   KO (le comportement observé le contredit) ou NON TESTABLE. Rien d'autre.
4. **Sur un échec, une seule relance** : si l'échec ressemble à de la lenteur ou à un élément
   pas encore affiché, attendre puis rejouer l'étape une fois ; au deuxième échec, verdict KO.
5. **Prouver chaque verdict** : une capture d'écran au point de vérification, enregistrée dans
   `validation-out/[feature]/resultats/preuves/` (nommée `TC-[feature]-NNN-<n>.png`). Sur KO,
   noter en plus, factuellement, ce qui est constaté par rapport à l'attendu.
6. **Capturer le déroulé effectif** : pour chaque cas, noter les étapes réellement jouées,
   numérotées, en langage naturel - ce qui s'est vraiment passé (relances, contournements,
   ordre effectif), pas la recopie des étapes prévues au plan.
7. **Aucune action destructive ni donnée réelle** : ne jamais supprimer, payer, ou envoyer
   quoi que ce soit vers l'extérieur sans que le plan le prévoie explicitement avec des
   données de test. Dans le doute, marquer le cas NON TESTABLE et passer au suivant.
8. Sur un écran de connexion ou un captcha que les comptes de test ne passent pas : s'arrêter,
   le signaler dans les résultats, et laisser la main au testeur.

## Format de résultats imposé

Écrire un fichier `validation-out/[feature]/resultats/execution-<JJ-MM>.md` (jour-mois du jour
de l'exécution ; si un fichier de ce nom existe déjà, suffixer `-2`, `-3`...).

**Tout est en tables** - c'est un format imposé, il sera relu par un autre outil. Règles de
forme, dans toutes les tables ci-dessous :
- une **ligne de séparation** `|---|---|...|` (autant de colonnes que l'en-tête) **entre chaque
  ligne de données** ; jamais après la dernière ligne, jamais juste après l'en-tête ;
- les **étapes dans une cellule** sont numérotées et séparées par `<br>` (`1. ...<br>2. ...`),
  jamais un pavé de texte ;
- une **cellule sans valeur** porte un tiret `-`, jamais du blanc.

Quatre sections, dans cet ordre :

```
# Résultats d'exécution : [feature] ([numéro]) - [JJ-MM]

## Contexte d'exécution

| Adresse testée | Outil | Plan joué | Cas joués |
|---|---|---|---|
| [URL] | Claude Cowork + extension Chrome | `validation-out/[feature]/plan-de-test.md` | [n] |

## Synthèse

| Verdict | Nombre | Cas concernés |
|---|---|---|
| OK | [n] | [identifiants, ou -] |
|---|---|---|
| KO | [n] | [identifiants, ou -] |
|---|---|---|
| NON TESTABLE | [n] | [identifiants, ou -] |

## Résultats par cas

| Cas | Intitulé | Verdict | Déroulé effectif | Constaté | Preuve |
|---|---|---|---|---|---|
| TC-[feature]-001 | [intitulé du plan] | OK | 1. ...<br>2. ... | [ce qui a été observé] | `preuves/TC-[feature]-001-1.png` |
|---|---|---|---|---|---|
| TC-[feature]-002 | [...] | KO | 1. ...<br>2. ... | [ce qui a été observé] | `preuves/TC-[feature]-002-1.png` |

## Écarts (KO et NON TESTABLE)

| Cas | Attendu | Constaté | Console et réseau |
|---|---|---|---|
| TC-[feature]-002 | [le résultat attendu, repris du plan] | [ce qui se produit vraiment] | [erreurs, requêtes en échec ; - si rien] |
```

- **Une ligne par cas du plan**, dans l'ordre, **aucun cas omis** - y compris les NON TESTABLE.
- Le **déroulé effectif est requis même pour un cas OK** : il dit ce qui a vraiment été joué, ce
  que le plan (étapes prévues) ne dit pas.
- La colonne **Constaté** de la table par cas reste **une phrase** ; le détail d'un échec va dans
  la table **Écarts**.
- **Si tous les cas sont OK** : supprimer la table Écarts et écrire "Aucun - tous les cas sont OK."

## Après la mission

Signaler au testeur que les résultats sont écrits. La suite (rapport de recette, tri des
écarts, verdict) se fait dans Claude Code avec `/validation:rapport-de-validation` - ce n'est pas
ton rôle.
