# Rapport de recette : [intitulé de la feature] ([numéro de registre])

<!-- Généré par `rapport-de-recette` dans `validation-out/<feature>/rapport-de-recette.md`.
     Rapport TRACÉ exigence par exigence : une ligne par critère d'acceptation, reliée à son
     cas de test, son verdict, sa preuve et la décision prise sur l'écart. La section "Verdict
     de recette" n'est remplie QUE par le verdict humain du testeur (porte de recette) : la
     skill ne la remplit jamais de sa propre initiative, et ne l'écrit pas tant que des écarts
     restent sans décision. -->

## Exécution de référence

- **Environnement testé** : (l'URL)
- **Exécution** : (le fichier de résultats utilisé, ex. `resultats/execution-12-08.md`, et
  l'outil d'exécution)

## Matrice de traçabilité (exigence par exigence)

<!-- Une ligne par cas de test, dans l'ordre du plan. "Ce qui est vérifié" est une PHRASE en
     français (reprise du plan de test) : elle se lit sans rouvrir la spécification. La
     référence de spécification vit dans la colonne "Source", jamais seule en tête de ligne. -->

| Ce qui est vérifié | Cas de test | Verdict | Preuve | Source | Décision sur l'écart |
|---|---|---|---|---|---|
| (la phrase du plan, ex. "une note saisie apparait dans la liste") | TC-[feature]-001 | OK | (capture) | (référence compacte, ex. "US1 sc.1 / FR-003") | `-` |
|---|---|---|---|---|---|
| (la phrase du plan) | TC-[feature]-002 | KO / NON TESTABLE | (capture) | (référence compacte) | (anomalie [identifiant Linear] / évolution [identifiant Linear] / clarifié en session / suivi [identifiant Linear]) |

## Synthèse

(En prose courte : combien de critères couverts, combien OK, combien d'écarts et de quelle
nature, ce que ça dit de la livraison. Factuel.)

## Écarts et suites données

<!-- Une ligne par écart (verdict KO ou NON TESTABLE), remplie au fil du tri avec le testeur.
     La nature (anomalie / évolution / flou) est une décision HUMAINE : ne jamais la préremplir
     de sa propre initiative. Si un ticket Linear a été créé (via /maintenance:creation-anomalie
     ou /maintenance:creation-evolution), citer son identifiant natif et son lien.
     Si aucun écart : SUPPRIMER la table et écrire "Aucun - tous les cas sont OK." -->

| Cas | Constaté vs attendu | Nature retenue | Suite donnée |
|---|---|---|---|
| TC-[feature]-002 | (factuel, depuis les résultats d'exécution : ce qui était attendu, ce qui se produit) | (anomalie : le logiciel ne respecte pas sa spécification / évolution : la spécification est fausse ou incomplète / critère flou : à clarifier) | (le ticket Linear avec son identifiant et son lien, ou la clarification actée en session, ou la décision de ne pas donner suite) |
|---|---|---|---|
| TC-[feature]-007 | (...) | (...) | (...) |

## Scénarios de non-régression

(La liste des scénarios rejouables consolidés depuis les cas OK :
`scenarios/TC-[feature]-NNN.md`, un par ligne avec l'intitulé du cas.)

## Verdict de recette

<!-- Rempli UNIQUEMENT sur le verdict explicite du testeur, une fois tous les écarts triés.
     Trois verdicts possibles ; les réserves listent ce qui reste ouvert (tickets Linear). -->

- **Verdict** : (livraison validée / validée avec réserves / refusée)
- **Date de la recette** : (JJ-MM-AAAA)
- **Réserves** : (les tickets Linear restant ouverts, avec leur identifiant ; ou "aucune")
