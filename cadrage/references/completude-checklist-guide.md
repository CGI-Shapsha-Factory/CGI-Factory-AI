# Guide de la porte de complétude — grille canonique (cadrage)

Référence lue par le skill `cadrage-completude`. C'est la **grille de vérification** que la porte
déroule sur le **pack fonctionnel** (contrat de cadrage) **avant de passer à l'architecte**. Elle
est **ancrée dans des méthodes reconnues** d'ingénierie des exigences (pas une checklist maison)
et s'applique en **grille pragmatique adaptée au cadrage** — un contrat *fonctionnel* (le quoi et
le pourquoi), **jamais technique**.

**Principe directeur — challenger, pas cocher.** On ne vérifie pas la seule *présence* d'un
fichier : on cherche ce qui **manque**, ce qui se **contredit**, ce qui est **mal formé**, ce qui
n'a **pas de valeur**. Le garde-fou déterministe `check_discovery.py` couvre la découverte ; cette
grille est le travail de **jugement** que le script ne peut pas faire.

**Principe de résolution — toujours une décision, jamais un simple constat.** Chaque point relevé
(trou, contradiction, exigence mal formée) n'est **jamais** seulement affiché « il manque X ». Il
devient une **décision en session** (`interactive-loop.md`) : énoncer en clair ce qui est là / ce
qui manque, demander « que veux-tu faire ? », proposer une **réponse recommandée + une alternative
plausible + « ta réponse »** (en prose, **pas de menu numéroté**), puis **appliquer en place**. Si
l'utilisateur ne tranche pas, **on n'écrit rien** (le point est omis) et le **verdict reste au
rouge**. L'utilisateur ne relit jamais les artefacts : tout se règle dans la décision.

**Contraintes de cadrage (rappel).** Sortie **sans tableau**, **sans nom de champ ni code**
(seule exception : les use cases, nommés « intitulé complet (UCn) »). **Rien d'ouvert persisté** :
un point non tranché est omis, jamais marqué (seul `[REMIS EN CAUSE]` survit, le temps d'être
retranché). Contrat *fonctionnel* : aucune technologie. Aucune notion de MVP.

---

## Les 6 critères Definition of Ready (le socle, conservé)

Calculés depuis l'état réel des artefacts + manifeste (ET strict — un seul non atteint = verdict
rouge) : **vision complète** (product-brief : OUT non vide, critères de succès présents) ·
**glossaire validé** (en bloc) · **découpage arbitré** (revue de couplage tranchée) · **tous les
briefs complets** · **aucun trou de découverte bloquant** (13 questions — Q8 légal/RGPD optionnelle
si laissée à l'équipe) · **démonstrateur convergé** (client a validé la maquette). *(Ancrage :
Definition of Ready — Scrum ; Atlassian.)* Ces six restent la **condition nécessaire** ; les
lentilles ci-dessous sont la **condition de qualité** qui les rend honnêtes.

---

## Lentille A — Complétude (rien d'essentiel manquant)

**A1. Couverture use case → brief.** Chaque use case du découpage (`spec-index.md`) a **son brief**
dans `features-fonctionnels-brief/` ; aucun use case laissé sans brief.

**A2. Brief complet section par section.** Chaque brief porte ses **sections 1 à 9** remplies
(narratif, utilisateurs, user stories, critères d'acceptation, critères de succès, périmètre,
dépendances, contraintes héritées, glossaire pertinent) ; **section 10 (Trous) vide** ; **périmètre
OUT non vide** ; critères de succès **chiffrés** ou explicitement « à préciser à l'architecture ».

**A3. Glossaire couvrant.** Chaque terme employé dans un brief (section 9) et dans le product-brief
a une **définition dans le glossaire global** (`glossaire.md`, source de vérité). Une entité citée
sans définition = trou.

**A4. Seeds qualité pour l'architecte.** Les questions de découverte **charge (Q2)**,
**disponibilité (Q6)**, **performance (Q7)** sont captées ou explicitement différées — l'architecte
en dérive les attributs de qualité ; un trou ici pénalise la phase suivante. *(Ancrage : DoR — les
critères non-fonctionnels doivent être définis avant le pull.)*

**A5. Périmètre IN couvert.** Chaque capacité annoncée dans le périmètre IN (project-frame /
product-brief) est couverte par ≥1 use case / brief. Une capacité IN sans feature = trou à trancher.

---

## Lentille B — Cohérence (rien ne se contredit)

**B1. Langage ubiquitaire cohérent.** **Un terme = un sens** partout (pas de terme employé dans
deux sens) ; **un concept = un terme** (pas de synonymes pour un même acteur/objet : « client » vs
« utilisateur » vs « usager »). Le pack « parle » le glossaire. *(Ancrage : Ubiquitous Language —
Evans ; Fowler.)*

**B2. Vision ↔ use cases.** Chaque use case sert un **objectif** de la vision (product-brief) ;
aucun use case orphelin d'objectif. Rien qui contredit le narratif produit.

**B3. Périmètre respecté (pas de fuite OUT→IN).** Rien de ce qui est déclaré **hors périmètre**
(OUT) n'a **fuité** dans un brief comme fonctionnalité IN. Les souhaits hors périmètre repérés sont
**confirmés une fois** (rester OUT, ou basculer IN par décision explicite) — **jamais poussés**.
*(Ancrage : MoSCoW / Won't-Have ; détection de scope creep.)*

**B4. Retour démonstrateur résolu.** Aucun acquis `[REMIS EN CAUSE]` ne survit : chacun est
**retranché** en session (corrigé ou retiré, en place). Un projet sans boucle démonstrateur n'est
convergé que lorsque le client a validé la maquette.

**B5. Dépendances cohérentes.** Les features citées en « Dépendances » **existent** ; pas de cycle ;
l'ordre est cohérent avec la `coupling-map`. Nommage aligné entre product-brief, spec-index, briefs
et glossaire.

---

## Lentille C — Qualité des exigences (bien formées)

**C1. User stories INVEST.** Chaque story est **Indépendante · Négociable · Valorisable ·
Estimable · Petite · Testable**. Une story qui échoue à une lettre est **reformulée, scindée ou
retirée** (pas laissée telle quelle). *(Ancrage : INVEST — Bill Wake ; Agile Alliance.)*

**C2. Critères d'acceptation testables.** Chaque critère suit **Étant donné / Quand / Alors**
(Given-When-Then), avec un **pass/fail clair et observable**, **atomique** et autonome. **Mots
vagues bannis** (« rapide », « simple », « convivial », « robuste ») → remplacés par une **valeur
mesurable**. Discipline de nombre : **~1 à 3 critères** par story ; **4+ = signal** que la story est
trop grosse, à scinder. *(Ancrage : acceptance criteria / Gherkin — AltexSoft, TestQuality.)*

**C3. Critères de succès mesurables.** Résultats traduits en **métriques chiffrées** (indépendantes
de la techno) ou explicitement « à préciser à l'architecture ». Pas d'objectif de succès invérifiable.

**C4. Chaque exigence bien écrite.** **Nécessaire** (rien de superflu), **non ambiguë** (une seule
lecture), **singulière** (pas de « et » cachant deux exigences), **vérifiable** (un test/inspection
existe), au **bon niveau** (fonctionnel, aucune solution technique prématurée). *(Ancrage :
ISO/IEC/IEEE 29148 ; BABOK §7.2 — Verify Requirements.)*

---

## Lentille D — Validation & prêt pour l'architecte (valeur + handoff)

**D1. Chaque feature délivre de la valeur (validation).** Chaque feature **trace vers un objectif
métier** et apporte une **valeur** à un besoin de partie prenante ; une feature bien écrite **mais
sans valeur** est candidate au retrait. *(Ancrage : BABOK §7.3 — Validate Requirements ; distinct de
« bien écrite ».)*

**D2. Traçabilité bidirectionnelle objectifs ↔ features.** **Sens avant** : chaque feature remonte à
un objectif (aucune **orpheline** / scope creep). **Sens couverture** : chaque objectif de la vision
est couvert par ≥1 feature (aucun objectif **sans enfant**). Construire mentalement la matrice
objectifs × features et chasser les **lignes vides** (objectif non couvert) et **colonnes vides**
(feature injustifiée). *(Ancrage : matrice de traçabilité des exigences.)*

**D3. Prêt pour l'architecte (handoff direct).** L'architecte lit **directement** `cadrage-out/`
(pas d'intermédiaire) : vérifier que **project-frame**, **product-brief**, **glossaire**,
**spec-index** (use cases + walking skeleton candidat + hypothèse de couplage) et les **briefs** sont
présents et **mutuellement cohérents**. C'est ce que la phase 2 va consommer — donc vérifié **en
priorité**.

---

## Sources (vérification)

- Definition of Ready — Scrum PLoP (scrumbook.org) ; Atlassian
  (https://www.atlassian.com/agile/project-management/definition-of-ready) ; Scrum.org.
- INVEST — Bill Wake ; Agile Alliance (https://agilealliance.org/glossary/invest/).
- Qualité des exigences — ISO/IEC/IEEE 29148:2018 ; tradition IEEE 830 ;
  BABOK v3 §7.2 (Verify) / §7.3 (Validate) — IIBA.
- Critères d'acceptation / Given-When-Then — AltexSoft ; TestQuality ; ParallelHQ.
- Langage ubiquitaire — Eric Evans, *Domain-Driven Design* ; Martin Fowler
  (https://martinfowler.com/bliki/UbiquitousLanguage.html).
- Périmètre / MoSCoW — Agile Business Consortium (DSDM)
  (https://www.agilebusiness.org/dsdm-project-framework/moscow-prioritisation.html).
- Traçabilité — matrice de traçabilité des exigences (Perforce ; Jama Software).
