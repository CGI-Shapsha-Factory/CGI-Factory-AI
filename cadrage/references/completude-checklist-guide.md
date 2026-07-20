# Guide de la porte de complétude : grille canonique (cadrage)

Référence lue par le skill `cadrage-completude`. C'est la **grille de vérification** que la porte
déroule sur le **pack fonctionnel** (contrat de cadrage) **avant de passer à l'architecte**. Elle
est **ancrée dans des méthodes reconnues** d'ingénierie des exigences (pas une checklist maison)
et s'applique en **grille pragmatique adaptée au cadrage** - un contrat *fonctionnel* (le quoi et
le pourquoi), **jamais technique**.

**Principe directeur - challenger, pas cocher.** On ne vérifie pas la seule *présence* d'un
fichier : on cherche ce qui **manque**, ce qui se **contredit**, ce qui est **mal formé**, ce qui
n'a **pas de valeur**. Le garde-fou déterministe `check_discovery.py` couvre la découverte ; cette
grille est le travail de **jugement** que le script ne peut pas faire.

**Principe de résolution - toujours une décision, jamais un simple constat.** Chaque point relevé
(trou, contradiction, exigence mal formée) n'est **jamais** seulement affiché "il manque X". Il
devient une **décision en session** (`interactive-loop.md`) : énoncer en clair ce qui est là / ce
qui manque, demander "que veux-tu faire ?", proposer une **réponse recommandée + une alternative
plausible + "ta réponse"** (en prose, **pas de menu numéroté**), puis **appliquer en place**. Si
l'utilisateur ne tranche pas, **on n'écrit rien** (le point est omis) et le **verdict reste au
rouge**. L'utilisateur ne relit jamais les artefacts : tout se règle dans la décision.

**Contraintes de cadrage (rappel).** Sortie **sans tableau**, **sans nom de champ ni code**
(seule exception : les use cases, nommés "intitulé complet (UCn)"). **Rien d'ouvert persisté** :
un point non tranché est omis, jamais marqué (seul `[REMIS EN CAUSE]` survit, le temps d'être
retranché). Contrat *fonctionnel* : aucune technologie. Aucune notion de MVP.

---

## Comment se déroule cette checklist

Chaque item est une **question de qualité**, jamais un test de présence - c'est la discipline des
"tests unitaires de l'exigence" : on n'écrit pas "le brief existe", on écrit "le brief dit-il
quelque chose de vérifiable ?". Les verbes d'action d'implémentation (vérifier que ça marche,
tester le comportement) n'ont pas leur place ici : c'est le **texte** qu'on met à l'épreuve.

Format d'un item :

```
- [ ] CHK### Question de qualité ? [Dimension, source de traçabilité]
```

Règles de déroulé :
- **Un item à la fois, dans l'ordre.** On ne saute pas, on ne groupe pas.
- **Coché = la question a reçu une réponse satisfaisante** sur l'artefact réel, pas "le fichier
  existe". Un item dont la réponse est "non" ou "je ne sais pas" **reste décoché** et devient une
  décision en session (boucle 3-options), puis se coche une fois la correction appliquée en place.
- **Sans objet** : cocher en annotant `[SANS OBJET : raison]` sur la ligne. Jamais de case cochée
  sans que la raison soit lisible.
- **IDs stables.** `CHK###` ne se renumérote jamais : on ajoute à la suite, on ne réordonne pas.
  Le code de lentille historique (`A1`, `B3`...) est conservé entre parenthèses comme ancre pour
  les renvois existants.
- **Traçabilité.** Chaque item nomme la source à confronter (fichier, section, question de
  découverte). C'est ce qui empêche de cocher de mémoire.
- Cette checklist est un **gabarit** : l'état coché vit le temps de la session de porte, et la
  synthèse de ce qui a été trouvé et corrigé part dans `cadrage-out/completude-report.md`.

---

## Les 6 critères Definition of Ready (le socle, conservé)

Calculés depuis l'état réel des artefacts + manifeste (ET strict - un seul non atteint = verdict
rouge). Ce ne sont **pas** des items de jugement : ce sont les **booléens de sortie de phase**,
alimentés par les lentilles ci-dessous.

- [ ] DOR1 **Vision complète** - le product-brief porte-t-il un périmètre OUT non vide et des
      critères de succès présents ? [Socle, product-brief.md]
- [ ] DOR2 **Glossaire validé** - la validation en bloc a-t-elle été prononcée par l'humain ?
      [Socle, glossaire.md]
- [ ] DOR3 **Découpage arbitré** - la revue de couplage a-t-elle été tranchée ? (le skill **ne
      relève jamais ce critère lui-même**, il le lit) [Socle, coupling-map.md]
- [ ] DOR4 **Tous les briefs complets** - chaque brief est-il sorti de l'état d'ébauche ?
      [Socle, features-fonctionnels-brief/]
- [ ] DOR5 **Aucun trou de découverte bloquant** - les 19 questions sont-elles couvertes (Q8
      légal/RGPD optionnelle si laissée à l'équipe) ? [Socle, check_discovery.py --strict]
- [ ] DOR6 **Démonstrateur convergé** - le client a-t-il validé la maquette ? [Socle,
      manifeste `demonstrateur`]

*(Ancrage : Definition of Ready - Scrum ; Atlassian.)* Ces six restent la **condition
nécessaire** ; les lentilles ci-dessous sont la **condition de qualité** qui les rend honnêtes.

---

## Lentille A : Complétude (rien d'essentiel manquant)

- [ ] CHK001 (A1) Chaque use case du découpage a-t-il son brief, sans exception ?
      [Complétude, spec-index.md -> features-fonctionnels-brief/]
- [ ] CHK002 (A2) Chaque brief a-t-il ses sections 1 à 9 réellement remplies - narratif,
      utilisateurs, user stories, critères d'acceptation, critères de succès, périmètre,
      dépendances, contraintes héritées, glossaire pertinent ? [Complétude, briefs §1-9]
- [ ] CHK003 (A2) La section 10 (Trous) est-elle vide dans chaque brief ?
      [Complétude, briefs §10]
- [ ] CHK004 (A2) Le périmètre OUT est-il non vide dans chaque brief, ou son absence est-elle
      justifiée ? [Complétude, briefs §6]
- [ ] CHK005 (A2) Les critères de succès sont-ils chiffrés, ou explicitement marqués "à préciser
      à l'architecture" ? [Mesurabilité, briefs §5]
- [ ] CHK006 (A3) Chaque terme employé dans un brief (§9) ou dans le product-brief a-t-il une
      définition dans le glossaire global ? [Cohérence, glossaire.md]
- [ ] CHK007 (A4) Les seeds qualité destinés à l'architecte sont-ils captés ou explicitement
      différés - charge (Q2), disponibilité (Q6), performance (Q7) ? [Complétude, découverte
      Q2/Q6/Q7]
- [ ] CHK008 (A5) Chaque capacité annoncée dans le périmètre IN est-elle couverte par au moins un
      use case ? [Couverture, project-frame.md + product-brief.md -> spec-index.md]

*(Ancrage : DoR - les critères non-fonctionnels doivent être définis avant le pull.)*

---

## Lentille B : Cohérence (rien ne se contredit)

- [ ] CHK009 (B1) Un terme porte-t-il partout un seul sens, et un concept est-il désigné partout
      par un seul terme (pas "client" vs "utilisateur" vs "usager") ? [Cohérence, glossaire.md]
- [ ] CHK010 (B2) Chaque use case sert-il un objectif explicite de la vision, sans use case
      orphelin ni contradiction avec le narratif produit ? [Cohérence, product-brief.md ->
      spec-index.md]
- [ ] CHK011 (B3) Est-on certain que rien de déclaré hors périmètre (OUT) n'a fuité dans un brief
      comme fonctionnalité IN ? [Périmètre, briefs §6]
- [ ] CHK012 (B3) Chaque souhait hors périmètre repéré a-t-il été confirmé une fois - rester OUT,
      ou basculer IN par décision explicite ? [Périmètre, briefs §6]
- [ ] CHK013 (B4) Ne subsiste-t-il aucun acquis marqué `[REMIS EN CAUSE]` non retranché ?
      [Complétude, tous artefacts cadrage-out/]
- [ ] CHK014 (B5) Les features citées en dépendances existent-elles, sans cycle, dans un ordre
      cohérent avec la carte de couplage ? [Cohérence, briefs §7 + coupling-map.md]
- [ ] CHK015 (B6) Le product-brief se lit-il comme une thèse (problème -> différenciation ->
      succès) plutôt que comme un catalogue de sections ? Signal d'alerte : une vision
      interchangeable avec n'importe quel autre projet. [Substance, product-brief.md]
- [ ] CHK016 (B6) Chaque rôle ou profil utilisateur cité pèse-t-il sur au moins une décision du
      pack (une story, un périmètre, un critère) ? Un profil qui ne pilote rien est du décor.
      [Substance, product-brief.md + briefs §2]

*(Ancrages : Ubiquitous Language - Evans, Fowler ; MoSCoW / Won't-Have ; anti "persona theater".)*

---

## Lentille C : Qualité des exigences (bien formées)

- [ ] CHK017 (C1) Chaque user story satisfait-elle INVEST - Indépendante, Négociable,
      Valorisable, Estimable, Petite, Testable ? Une story qui échoue à une lettre est reformulée,
      scindée ou retirée. [Clarté, briefs §3]
- [ ] CHK018 (C2) Chaque critère d'acceptation suit-il Étant donné / Quand / Alors, avec un
      pass/fail clair, observable et atomique ? [Testabilité, briefs §4]
- [ ] CHK019 (C2) Les mots vagues ("rapide", "simple", "convivial", "robuste") ont-ils été
      remplacés par une valeur mesurable ? [Clarté, briefs §4]
- [ ] CHK020 (C2) La discipline de nombre est-elle tenue - environ 1 à 3 critères par story, 4 et
      plus signalant une story à scinder ? [Granularité, briefs §3-4]
- [ ] CHK021 (C3) Les critères de succès sont-ils traduits en métriques chiffrées indépendantes
      de la techno, sans objectif invérifiable ? [Mesurabilité, briefs §5 + product-brief.md]
- [ ] CHK022 (C4) Chaque exigence est-elle nécessaire, non ambiguë, singulière (pas de "et"
      cachant deux exigences), vérifiable et au bon niveau fonctionnel - sans solution technique
      prématurée ? [Qualité, briefs §3-4]
- [ ] CHK023 (C5) Les attributs non-fonctionnels nus et génériques ("scalable", "sécurisé",
      "performant", "fiable") sont-ils raccordés à une réponse de découverte, chiffrés, ou
      retirés ? [Anti-théâtre, briefs + découverte]
- [ ] CHK024 (C5) Le "fini" flou a-t-il disparu des critères ("gère correctement", "de façon
      conviviale", "raisonnable") - un développeur peut-il dire objectivement quand c'est fait ?
      [Anti-théâtre, briefs §4]

*(Ancrages : INVEST - Bill Wake ; Given-When-Then ; ISO/IEC/IEEE 29148 ; BABOK §7.2.)*

---

## Lentille D : Validation & prêt pour l'architecte (valeur + handoff)

- [ ] CHK025 (D1) Chaque feature trace-t-elle vers un objectif métier et apporte-t-elle une
      valeur à un besoin de partie prenante ? Une feature bien écrite mais sans valeur est
      candidate au retrait. [Valeur, product-brief.md -> briefs]
- [ ] CHK026 (D2) Sens avant : chaque feature remonte-t-elle à un objectif, sans orpheline ni
      scope creep ? [Traçabilité, matrice objectifs x features]
- [ ] CHK027 (D2) Sens couverture : chaque objectif de la vision est-il couvert par au moins une
      feature, sans objectif sans enfant ? [Traçabilité, matrice objectifs x features]
- [ ] CHK028 (D3) Les cinq artefacts que l'architecte va lire directement sont-ils présents et
      mutuellement cohérents - project-frame, product-brief, glossaire, spec-index (use cases +
      walking skeleton candidat + hypothèse de couplage) et les briefs ? **Vérifié en priorité.**
      [Handoff, cadrage-out/]

*(Ancrages : BABOK §7.3 - Validate Requirements ; matrice de traçabilité des exigences.)*

---

## Sources (vérification)

- Definition of Ready - Scrum PLoP (scrumbook.org) ; Atlassian
  (https://www.atlassian.com/agile/project-management/definition-of-ready) ; Scrum.org.
- Checklists comme "tests unitaires de l'exigence" - GitHub Spec Kit, `/speckit.checklist`
  (https://github.com/github/spec-kit/blob/main/templates/commands/checklist.md).
- INVEST - Bill Wake ; Agile Alliance (https://agilealliance.org/glossary/invest/).
- Qualité des exigences - ISO/IEC/IEEE 29148:2018 ; tradition IEEE 830 ;
  BABOK v3 §7.2 (Verify) / §7.3 (Validate) - IIBA.
- Critères d'acceptation / Given-When-Then - AltexSoft ; TestQuality ; ParallelHQ.
- Langage ubiquitaire - Eric Evans, *Domain-Driven Design* ; Martin Fowler
  (https://martinfowler.com/bliki/UbiquitousLanguage.html).
- Périmètre / MoSCoW - Agile Business Consortium (DSDM)
  (https://www.agilebusiness.org/dsdm-project-framework/moscow-prioritisation.html).
- Traçabilité - matrice de traçabilité des exigences (Perforce ; Jama Software).
