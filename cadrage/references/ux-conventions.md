# Conventions UX — sortie utilisateur

Règles transverses pour **tout** ce que les skills affichent à l'utilisateur.

## 1. Jamais de nom d'attribut / clé JSON en sortie
Le manifeste garde ses clés (contrat machine), mais le **texte affiché** et les
**messages de refus** sont en **langage naturel**. Table de correspondance :

| Interne (manifeste) | Langage utilisateur (FR) |
|---|---|
| `vision_complete` | « la vision produit est complète » |
| `glossary_validated` | « le glossaire est validé » |
| `decoupage_arbitrated` | « la revue de couplage est faite » |
| `all_briefs_complete` | « tous les briefs sont complets » |
| `no_blocking_gaps` | « aucun point bloquant ouvert » |
| `demonstrateur_converged` | « le prototype est validé par le client » |
| `ready_for_speckit` | « prêt pour SpecKit » |
| `discovery_complete` | « toutes les questions de cadrage sont répondues » |
| `validation_points[]` | « les points à clarifier » |
| `arbitrated: false` | « proposition — revue de couplage pas encore faite » |

Ne jamais afficher de tableau de booléens bruts (ex. `decoupage_arbitrated == true`).

**Ne jamais parler de « portes » ouvertes/fermées** ni de drapeaux : énoncer en clair
*ce qui* est validé. Ex. : au lieu de « les deux portes sont ouvertes », dire « le
découpage est arbitré et la maquette est validée par le client ».

## 2. Messages de refus en langage naturel
Quand un skill ne peut pas tourner (gate non franchie), expliquer **en clair**
pourquoi et quoi faire. Exemple cible :
> « Cette étape ne peut pas démarrer encore : la revue de couplage et la
> validation du prototype doivent d'abord être faites. »
Jamais : « ⛔ REFUSES: decoupage_arbitrated == false ».

## 3. Marqueurs internes hors texte utilisateur
**Marqueurs canoniques — n'utiliser QUE ceux-ci, toujours en français :** `[À VALIDER]`,
`[À CHIFFRER]`, `[À ÉPROUVER]`, `[REMIS EN CAUSE]`, `[NON COUVERT EN ATELIER]`. **Interdites** :
toutes les variantes anglaises — `[TO CONFIRM]`, `[TO QUANTIFY]`, `[TO PROVE]`, `[NOT COVERED]`,
`[TBD]`… (ne jamais les écrire dans un artefact). Ces marqueurs vivent dans les **artefacts** (lus
par le LLM), pas dans les phrases adressées à l'utilisateur. À l'oral on dit « à confirmer », etc.

## 4. Langage produit (non technique) pour le découpage
Dans les affichages de découpage/vision, parler **valeur et usage** (style Product
Owner). Pas d'identifiants techniques, pas de jargon d'archi.

## 5. Une ligne « étape suivante » à la fin de chaque skill
Terminer **chaque** exécution par exactement une phrase :
> « Étape suivante : `/cadrage:cadrage-<skill>` — <pourquoi en quelques mots>. »

## 6. Langue
**Tout en français** : interaction (questions, refus, résumés, tableaux affichés)
ET artefacts/templates. Seules les clés/valeurs machine du manifeste restent des
identifiants (`status`, `pending`, `ready_for_speckit`…).

## 7. Expliquer les termes du framework à leur première apparition
Tout terme propre à la factory — **walking skeleton, contrainte transverse, démonstrateur,
revue de couplage, handoff, pré-constitution** — reçoit, **à sa première apparition** dans la
conversation, une **explication d'une phrase en langage clair** (ex. « le walking skeleton = la
première tranche de bout en bout qui prouve que la techno tient »). Ne jamais lâcher un terme du
framework cru. (Les acronymes **métier** du client — GED, DSI, SSO… — relèvent du glossaire, pas
de cette règle.)
