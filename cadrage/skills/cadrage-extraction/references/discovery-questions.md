# Questions de découverte (cadrage du projet client)

Liste **figée** des 19 questions de cadrage à couvrir pour tout projet. Lue par
`cadrage-extraction` (passe de découverte). Chaque question est : cherchée dans les
sources (transcript / docs), puis si absente, **posée à l'utilisateur une par
une**. Réponses -> `project-frame.md` + le bloc `discovery` du manifeste.

Catégories fondées sur l'ISO/IEC/IEEE 29148 (utilisateurs, données, interface, non-fonctionnel,
légal, opérationnel), complétées d'une catégorie **produit** (cadrage produit : problème,
différenciation, succès, supports, hypothèses). Les questions marquées **seed qualité** captent
un attribut qualité brut que le plugin **architecte** transformera en driver/scénario (QAW).

| id | question | catégorie | cible (project-frame) | seed qualité |
|----|----------|----------|------------------------|--------------|
| Q1 | Qui utilise l'application ? | utilisateurs | Utilisateurs & rôles | - |
| Q2 | Combien d'utilisateurs différents ? combien en même temps ? | NFR / charge | Utilisateurs & rôles (charge) | **oui** |
| Q3 | Quels rôles utilisateurs ? | utilisateurs / auth | Utilisateurs & rôles | - |
| Q4 | Quelles données sont stockées ? quantité, contenu, sensibilité ? | données | Données | - |
| Q5 | Quels systèmes externes à intégrer ? | interface | Intégrations | - |
| Q6 | Quelle disponibilité du système est requise ? | NFR | Disponibilité & performance | **oui** |
| Q7 | Contraintes de performance ? | NFR | Disponibilité & performance | **oui** |
| Q8 | Contraintes légales ? | légal/réglementaire | Légal/réglementaire | - |
| Q9 | Type de projet ? (ponctuel, long terme, périmètre visé) | opérationnel | Type de projet | - |
| Q10 | Qui gère la production ? le client ? nous ? | opérationnel | Exploitation/production | - |
| Q11 | Où l'application est-elle déployée ? infra existante ou nouvelle ? cloud ? | opérationnel | Hébergement & déploiement | - |
| Q12 | Budget pour l'infrastructure ? | opérationnel | Budget infra | - |
| Q13 | Besoins spécifiques d'authentification / autorisation ? | sécurité/auth | Auth & autorisation | - |
| Q14 | Quel problème principal l'application résout-elle ? que coûte la situation actuelle ? | produit | Problème & enjeu | - |
| Q15 | Pourquoi ce projet maintenant ? qu'est-ce qui déclenche le besoin ? | produit | Problème & enjeu | - |
| Q16 | Qu'est-ce qui distinguera l'application des alternatives utilisées aujourd'hui ? | produit | Différenciation | - |
| Q17 | À quoi verra-t-on que l'application est un succès ? | produit | Signaux de succès | - |
| Q18 | Sur quels supports l'application sera-t-elle utilisée ? (web, mobile, desktop, plusieurs) | produit | Supports & accès | - |
| Q19 | Quelles sont les principales incertitudes ou hypothèses à vérifier ? | produit | Risques & hypothèses | - |

**Note - Q8 (contraintes légales / conformité / RGPD) : OPTIONNELLE, jamais poussée.** La conformité
(RGPD, hébergement UE, secret professionnel, non-entraînement des modèles, etc.) est **gérée
manuellement par l'équipe**, **hors cadrage** - ce n'est **pas** à l'IA de la porter ni d'insister.
La **proposer au plus une fois**, en clair, comme un simple choix (lister l'option à l'utilisateur).
Si l'utilisateur **décline ou la laisse** ("on gère nous-mêmes, plus tard"), c'est une réponse
**terminale et non bloquante** : marquer Q8 **`na`** (traitée hors cadrage par l'équipe), **jamais
`deferred`** - **ne plus jamais la re-soulever** ni en faire un point bloquant pour la Definition of
Ready. **Ne jamais pousser la conformité.**

**Note de suggestion - Q11 (hébergement / cloud).** Quand la réponse n'est pas dans les sources et
qu'on **propose** une suggestion de fournisseur cloud, mettre **GCP (Google Cloud Platform) en première
option** - **jamais Azure par défaut**, même si le contexte mentionne Microsoft 365 / Azure. C'est une
**suggestion de départ, pas une décision** : **toujours attendre la réponse et la confirmation de
l'utilisateur**, ne **rien supposer**, et n'écrire dans `project-frame.md` / le manifeste que la valeur
**tranchée** (cf. invariant "proposer, pas décider").

**Note - questions produit (Q14-Q19) : réutilisées en aval.** Les réponses Q14 (problème),
Q15 (pourquoi maintenant) et Q17 (signaux de succès) sont **reprises par `cadrage-vision`**
comme suggestions pré-remplies du product-brief (même mécanisme que Q1/Q3/Q9 - on ne repose
pas la question, on fait confirmer). Q16 (différenciation) nourrit la section "Alternatives
réellement utilisées" de la capture et le product-brief. Q18 (supports) informe le designer
en aval via le project-frame. Q19 (incertitudes / hypothèses) alimente l'"Hypothèse produit
initiale" du product-brief et sert de candidat aux points de validation du démonstrateur.

**Statuts possibles par question** (le bloc `discovery` du manifeste) :
- `answered` - réponse tranchée par l'utilisateur (aucune provenance écrite dans l'artefact).
- `pending` - pas encore posée (à poser interactivement).
- `deferred` - laissée de côté par l'utilisateur ; **rien n'est écrit** dans l'artefact pour ce champ.
- `na` - non applicable pour ce projet **ou traitée hors cadrage** (ex. Q8 conformité/RGPD gérée
  manuellement par l'équipe) ; **terminale et non bloquante**, jamais re-soulevée.

La porte `discovery_complete` est à vrai quand **aucune** question n'est `pending`/`deferred` (un `na`
- dont un Q8 légal laissé à l'équipe - **n'empêche pas** la complétude).
