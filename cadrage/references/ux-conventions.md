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

**Interdiction stricte de surfacer toute mécanique interne.** Ne **jamais** parler de
« porte » / « porte d'entrée » / gate / drapeau, ni afficher un statut de pré-requis
(« vision_complete = false »), ni exposer le raisonnement de vérification d'étape. Si une
étape ne peut pas démarrer, soit **on pose une question en clair** à l'utilisateur, soit
**on avance** quand la direction produit est explicite — jamais un avertissement type
« ⚠️ Porte d'entrée : … ».

## 2. Quand une étape manque d'un pré-requis
Ne pas afficher de refus technique. Poser **une question en clair** sur ce qui manque, ou
avancer si la direction est claire. Exemple cible :
> « Avant de découper, j'ai besoin de la vision produit — on la fait maintenant ? »
Jamais : « ⛔ REFUSES: decoupage_arbitrated == false », ni « Porte d'entrée : … ».

## 2bis. Jamais de conformité / RGPD côté utilisateur
L'utilisateur du cadrage (Product Owner) **n'est pas concerné** par la conformité, le RGPD,
ou les contraintes transverses (droits, audit, journalisation). **Ne jamais les afficher ni
en faire des points d'arbitrage visibles.** Ces préoccupations sont captées **en silence**
comme contraintes transverses transmises à l'architecte, hors du regard de l'utilisateur.

## 3. Aucun placeholder persisté
On **n'écrit pas** de point non tranché dans un artefact : un point sans réponse est **omis**
(cf. `interactive-loop.md`), jamais marqué `[À VALIDER]`. Seul marqueur encore admis dans un
artefact : `[REMIS EN CAUSE]` (un acquis contredit par un retour, conservé pour relecture
humaine). À l'oral on dit « à confirmer », « remis en cause », etc. — jamais de variantes
anglaises (`[TBD]`, `[TO CONFIRM]`…).

## 3bis. Fichiers prompt sauvegardés = corps seul, prêt à coller
Tout prompt écrit sous `factory-prompts/…/prompt.md` contient **uniquement le prompt
prêt à coller** dans Claude Design. **Interdit** dans le fichier : titre (`# Prompt
Claude Design — …`), ligne `Date : … | Mode : … | Version : …`, `---` d'en-tête, ou
toute autre métadonnée. La métadonnée (mode, version, date, sujet) vit dans l'entrée
`prompts[]` du manifeste, **jamais** dans le fichier. Objectif : l'utilisateur ouvre
le fichier et copie tout, sans rien nettoyer.

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
