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
  projet ; chaque cas y est numéroté TC-[feature]-NNN avec ses préconditions, ses étapes et
  son résultat attendu)
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
   numérotées, en langage naturel (elles serviront de scénarios de non-régression).
7. **Aucune action destructive ni donnée réelle** : ne jamais supprimer, payer, ou envoyer
   quoi que ce soit vers l'extérieur sans que le plan le prévoie explicitement avec des
   données de test. Dans le doute, marquer le cas NON TESTABLE et passer au suivant.
8. Sur un écran de connexion ou un captcha que les comptes de test ne passent pas : s'arrêter,
   le signaler dans les résultats, et laisser la main au testeur.

## Format de résultats imposé

Écrire un fichier `validation-out/[feature]/resultats/execution-<JJ-MM>.md` (jour-mois du jour
de l'exécution ; si un fichier de ce nom existe déjà, suffixer `-2`, `-3`...) :

- En tête : l'adresse testée et l'outil utilisé ("Claude Cowork + extension Chrome").
- Puis **un bloc par cas de test**, dans l'ordre du plan :

```
## TC-[feature]-NNN - [intitulé du cas]
- Verdict : OK / KO / NON TESTABLE (raison)
- Déroulé effectif :
  1. ...
  2. ...
- Preuves : resultats/preuves/TC-[feature]-NNN-1.png
- Constaté vs attendu (sur KO seulement) : ...
```

- En fin de fichier : une ligne de synthèse (nombre de cas OK, KO, NON TESTABLE).

## Après la mission

Signaler au testeur que les résultats sont écrits. La suite (rapport de recette, tri des
écarts, verdict) se fait dans Claude Code avec `/validation:bilan-validation` - ce n'est pas
ton rôle.
