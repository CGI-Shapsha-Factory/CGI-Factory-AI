# Table de correspondance : questions d'architecture -> artefacts de cadrage

Lue par le skill `architecte` (étape de vérification). Pour chaque question
structurante d'architecture, indique **où la réponse se trouve déjà** dans les
artefacts de cadrage (`cadrage-out/`). Le skill auto-remplit depuis ces
champs (avec `(src: ...)`) et ne **pose** (boucle 3-options) que les questions
**non couvertes**. Une question bloquante non répondue empêche de démarrer la
génération des fichiers d'architecture.

| # | Question d'architecture | Source dans le cadrage | À demander ? |
|---|--------------------------|------------------------|--------------|
| 1 | Domaine métier (à quoi sert le système ?) | `product-brief.md` §1-2 (Problème, Objectif métier) | non |
| 2 | Types d'utilisateurs | `project-frame.md` §1 (Q1) | non |
| 3 | Rôles d'utilisateurs | `project-frame.md` §1 (Q3) | non |
| 4 | Volume d'utilisateurs (total / simultanés) | `project-frame.md` (Q2, *seed qualité*) | non |
| 5 | Données stockées (nature) | `project-frame.md` §2 (Q4) | non |
| 6 | Volume de données | `project-frame.md` §2 (Q4) | non |
| 7 | Sensibilité des données (PII, santé, etc.) | `project-frame.md` §2 (Q4) + `glossaire.md` | non |
| 8 | Systèmes externes à intégrer | `project-frame.md` §3 (Q5) | non |
| 9 | Disponibilité / SLA | `project-frame.md` §4 (Q6, *seed qualité*) | non |
| 10 | Contraintes de performance | `project-frame.md` §4 (Q7, *seed qualité*) | non |
| 11 | Légal / conformité (RGPD...) | `project-frame.md` §5 (Q8) + `product-brief.md` §6 | non |
| 12 | Type de projet (ponctuel / long terme / périmètre visé) | `project-frame.md` §6 (Q9) | non |
| 13 | **Profil d'équipe (taille, expertise langage/framework)** | **absent du cadrage** | **OUI - à demander** |
| 14 | Exploitation de la production (client / nous / tiers) | `project-frame.md` §7 (Q10) | non |
| 15 | Infrastructure (existante / nouvelle, cloud) | `project-frame.md` §8 (Q11) | non |
| 16 | Budget infrastructure | `project-frame.md` §9 (Q12) | non |
| 17 | Authentification / autorisation | `project-frame.md` §10 (Q13) | non |

**Méthode (résumé)** : 16/17 réponses viennent du cadrage ; seule la **#13 profil
d'équipe** est posée à l'utilisateur (boucle 3-options). Si une réponse de cadrage
est restée `[À VALIDER]`/`deferred` (bloquante), elle est re-soumise ici avant de
générer quoi que ce soit. On ne re-pose **jamais** ce que le cadrage a déjà tranché.
