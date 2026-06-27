# Questions de découverte (cadrage du projet client)

Liste **figée** des 13 questions de cadrage à couvrir pour tout projet. Lue par
`cadrage-extraction` (passe de découverte). Chaque question est : cherchée dans les
sources (transcript / docs), puis si absente, **posée à l'utilisateur une par
une**. Réponses → `project-frame.md` + le bloc `discovery` du manifeste.

Catégories fondées sur l'ISO/IEC/IEEE 29148 (utilisateurs, données, interface, non-fonctionnel,
légal, opérationnel). Les questions marquées **seed qualité** captent un attribut qualité
brut que le plugin **architecte** transformera en driver/scénario (QAW).

| id | question | catégorie | cible (project-frame) | seed qualité |
|----|----------|----------|------------------------|--------------|
| Q1 | Qui utilise l'application ? | utilisateurs | Utilisateurs & rôles | — |
| Q2 | Combien d'utilisateurs différents ? combien en même temps ? | NFR / charge | Utilisateurs & rôles (charge) | **oui** |
| Q3 | Quels rôles utilisateurs ? | utilisateurs / auth | Utilisateurs & rôles | — |
| Q4 | Quelles données sont stockées ? quantité, contenu, sensibilité ? | données | Données | — |
| Q5 | Quels systèmes externes à intégrer ? | interface | Intégrations | — |
| Q6 | Quelle disponibilité du système est requise ? | NFR | Disponibilité & performance | **oui** |
| Q7 | Contraintes de performance ? | NFR | Disponibilité & performance | **oui** |
| Q8 | Contraintes légales ? | légal/réglementaire | Légal/réglementaire | — |
| Q9 | Type de projet ? MVP ? projet long terme ? | opérationnel | Type de projet | — |
| Q10 | Qui gère la production ? le client ? nous ? | opérationnel | Exploitation/production | — |
| Q11 | Où l'application est-elle déployée ? infra existante ou nouvelle ? cloud ? | opérationnel | Hébergement & déploiement | — |
| Q12 | Budget pour l'infrastructure ? | opérationnel | Budget infra | — |
| Q13 | Besoins spécifiques d'authentification / autorisation ? | sécurité/auth | Auth & autorisation | — |

**Statuts possibles par question** (le bloc `discovery` du manifeste) :
- `answered` — réponse trouvée (source obligatoire : transcript/doc ou `workshop/user`).
- `pending` — pas encore répondue (à poser interactivement). **Trou bloquant.**
- `deferred` — `[À VALIDER]`, repoussée à un atelier ultérieur (justification requise). **Trou bloquant.**
- `na` — non applicable pour ce projet (justification requise).

La porte `discovery_complete` est à vrai quand **aucune** question n'est `pending`/`deferred`.
