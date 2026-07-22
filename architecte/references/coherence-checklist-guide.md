# Guide de la porte de cohérence : grille canonique (architecte)

Référence lue par le skill `architecte-coherence`. C'est la **grille de vérification** que la
porte déroule sur le contrat technique **avant de passer au designer**. Elle est **ancrée dans
des méthodes reconnues** d'évaluation d'architecture (pas une checklist maison) et s'applique en
**grille pragmatique**, pas en atelier formel.

**Principe directeur - challenger, pas cocher.** On ne vérifie pas la *présence* d'un fichier :
on cherche ce qui **manque**, ce qui se **contredit**, ce qui pourrait **casser**. La présence
est déjà couverte par le garde-fou déterministe `check_architecture.py` ; cette grille est le
travail de **jugement** que le script ne peut pas faire.

**Principe de résolution - toujours une décision, jamais un simple constat.** Chaque point
relevé (manque, contradiction, anomalie) n'est **jamais** seulement affiché "bloquant". Il est
transformé en **décision en session** via la boucle interactive (`interactive-loop.md`) : énoncer
en clair ce qui est là / ce qui manque, demander "que veux-tu faire ?" **avec `AskUserQuestion`**,
proposer **deux actions adaptées** (la saisie libre est ajoutée par l'outil), puis **appliquer le
choix en place**. L'utilisateur ne relit jamais
les artefacts : tout se règle dans la décision. Voir `interactive-loop.md` (règle d'or).

---

## Comment se déroule cette checklist

Chaque item est une **question de qualité** posée au contrat technique, jamais un test de
présence - la présence, c'est le travail du script. On n'écrit pas "les ADR existent", on écrit
"deux ADR acceptés se contredisent-ils ?".

Format d'un item :

```
- [ ] CHK### Question de qualité ? [Dimension, source de traçabilité]
```

Règles de déroulé :
- **Un item à la fois, dans l'ordre.** On ne saute pas, on ne groupe pas.
- **Coché = la question a reçu une réponse satisfaisante** sur l'artefact réel. Un item dont la
  réponse est "non" ou "je ne sais pas" **reste décoché** et devient une décision en session
  (boucle interactive, deux options avec `AskUserQuestion`), puis se coche une fois la correction
  appliquée en place.
- **Sans objet** : cocher en annotant `[SANS OBJET : raison]` sur la ligne. Jamais de case cochée
  sans raison lisible.
- **IDs stables.** `CHK###` ne se renumérote jamais : on ajoute à la suite, on ne réordonne pas.
  Le code de lentille historique (`A1`, `B4`...) est conservé entre parenthèses comme ancre.
- **Traçabilité.** Chaque item nomme l'artefact à confronter. C'est ce qui empêche de cocher de
  mémoire.
- Cette checklist est un **gabarit** : l'état coché vit le temps de la session de porte, et la
  synthèse part dans `architecte-out/coherence-report.md`.

---

## Le socle déterministe (couvert par `check_architecture.py`)

Ces points ne sont **pas** des items de jugement : le script les tranche seul et **bloque** en
`exit 1`. Ils sont listés ici pour mémoire, jamais cochés à la main.

- [ ] SOC1 Profil d'équipe renseigné, composants non vides, langages de stack définis
- [ ] SOC2 Conventions installées pour chaque langage retenu
- [ ] SOC3 Séquence de features non vide, chaque entrée portant `{id, ucs}`
- [ ] SOC4 Walking skeleton, impact-design et enforcement des tests déclarés
- [ ] SOC5 Aucun marqueur résiduel, versions figées (pas de "latest"), front-matter valide,
      fichiers d'environnement cohérents

**Si le script échoue, on s'arrête** : aucune des lentilles ci-dessous ne se déroule sur un
contrat que le socle refuse.

---

## Lentille A : Cohérence (rien ne se contredit)

- [ ] CHK001 (A1) Chaque point de sensibilité et chaque point de compromis est-il classé risque
      ou non-risque, sans aucun laissé non classé ? [Cohérence, facteurs-et-qualite.md]
- [ ] CHK002 (A1) Les risques sont-ils regroupés en thèmes rattachés à un driver métier ?
      [Cohérence, facteurs-et-qualite.md + risques.md]
- [ ] CHK003 (A2) Deux ADR acceptés se contredisent-ils quelque part dans le journal de
      décisions ? [Cohérence, decisions/ADR-*.md]
- [ ] CHK004 (A2) Chaque ADR remplacé porte-t-il `Statut: superseded` avec le lien vers son
      successeur, et le successeur référence-t-il le précédent ? [Traçabilité, decisions/]
- [ ] CHK005 (A2) Chaque ADR porte-t-il contexte, décision, **rationale**, options réellement
      considérées avec leurs compromis, conséquences positives **et** négatives, statut courant ?
      Un ADR sans rationale ni alternatives n'a pas de valeur d'architecture. [Substance,
      decisions/]
- [ ] CHK006 (A3) La confrontation drivers x stack x ADR x déploiement fait-elle apparaître une
      contradiction - par exemple un driver "hébergement UE" face à un service externe hors UE ?
      [Cohérence, facteurs-et-qualite.md + stack-technique.md + decisions/]
- [ ] CHK007 (A3) La cible de disponibilité et de performance est-elle réellement tenue par le
      déploiement décrit ? [Faisabilité, facteurs-et-qualite.md + diagrammes/]
- [ ] CHK008 (A4) Un même concept est-il nommé pareil partout, en alignement avec le glossaire du
      cadrage - pas deux noms pour une chose, pas deux choses sous un nom ? [Cohérence,
      cadrage-out/glossaire.md]
- [ ] CHK009 (A5) Les conteneurs et composants montrés dans les diagrammes existent-ils dans
      `composants.md`, avec des frontières cohérentes entre Contexte, Conteneurs et Composants et
      aucun placeholder ? [Traçabilité, diagrammes/ + composants.md]

*(Ancrages : ATAM étapes 6 et 9 - SEI/Kazman-Klein-Clements ; Nygard, adr.github.io, arc42 §9 ;
modèle C4.)*

---

## Lentille B : Consistance (traçabilité bidirectionnelle, aucun orphelin)

Principe : **ni parent sans enfant, ni orphelin.** La plupart des défauts de traçabilité sont des
liens **manquants** ou **non mis à jour** quand une exigence a changé.

- [ ] CHK010 (B1) Chaque driver, chaque attribut de qualité, chaque contrainte de brief et chaque
      entité du glossaire est-il adressé par au moins un composant ou un ADR ? [Couverture,
      facteurs-et-qualite.md -> composants.md]
- [ ] CHK011 (B1) Chaque entité de l'ERD a-t-elle un composant qui la gère ? [Couverture,
      composants.md]
- [ ] CHK012 (B1) Les besoins de sécurité, de droits et d'audit sont-ils reflétés par un composant
      **et** un ADR - journal d'audit présent s'il est exigé ? [Couverture, composants.md +
      decisions/]
- [ ] CHK013 (B2) Chaque composant remonte-t-il à un besoin ou un driver ? Un composant qui ne
      sert aucune exigence est un orphelin à justifier ou retirer. [Traçabilité, composants.md]
- [ ] CHK014 (B3) La couverture use cases vers features est-elle 1:1 - chaque use case du
      spec-index a sa feature, aucune feature ne référence un use case inexistant ? [Traçabilité,
      cadrage-out/spec-index.md -> `architecture.feature_sequence`]
- [ ] CHK015 (B4) Chaque composant a-t-il une techno définie dans la matrice, sans "à définir", et
      chaque ligne de matrice a-t-elle son composant ? [Consistance, composants.md +
      stack-technique.md]
- [ ] CHK016 (B4) La stack inline d'un composant correspond-elle exactement à `stack-technique.md`
      - mêmes technos, **mêmes versions exactes**, sans divergence ni version vague ?
      [Consistance, composants.md + stack-technique.md]
- [ ] CHK017 (B4) Un composant Frontend/UI existe-t-il, dès lors que le produit a des écrans ?
      [Complétude, composants.md]
- [ ] CHK018 (B5) Chaque langage retenu a-t-il son fichier de conventions installé dans
      `conventions/` ? [Consistance, stack-technique.md -> conventions/]

*(Ancrage : matrice de traçabilité, pratique standard d'ingénierie des exigences.)*

---

## Lentille C : Complétude (chaque exigence bien formée et couverte)

- [ ] CHK019 (C1) Chaque attribut de qualité est-il exprimé en scénario à 6 parties - source,
      stimulus, artefact, environnement (nominal / pointe / dégradé), réponse observable, mesure
      chiffrée ? [Testabilité, facteurs-et-qualite.md]
- [ ] CHK020 (C1) La mesure de réponse est-elle chiffrée dans chaque scénario ? Sans elle,
      l'exigence n'est pas testable. Rejeter tout "scalable / robuste / performant / user-friendly"
      sans source, stimulus ni mesure. [Anti-théâtre, facteurs-et-qualite.md]
- [ ] CHK021 (C1) Chaque attribut significatif a-t-il au moins un scénario, tracé à un driver ?
      [Traçabilité, facteurs-et-qualite.md]
- [ ] CHK022 (C2) Drivers et attributs de qualité sont-ils distincts et non redondants - aucun
      doublon désignant le même concept ? [Clarté, facteurs-et-qualite.md]
- [ ] CHK023 (C2) Chaque attribut de qualité découle-t-il d'un driver ? Sinon : driver manquant ou
      attribut injustifié. [Traçabilité, facteurs-et-qualite.md]
- [ ] CHK024 (C3) La tranche du walking skeleton est-elle réellement de bout en bout, avec une
      fonction réelle et non une démo mockée ? [Faisabilité, standards-ingenierie.md]
- [ ] CHK025 (C3) Traverse-t-elle les vrais composants plutôt qu'une seule couche, et est-elle
      automatiquement build, deploy et test ? [Faisabilité, standards-ingenierie.md]
- [ ] CHK026 (C3) Frappe-t-elle l'intégration la plus risquée **sans stub** - la dépendance
      externe, tierce ou inter-équipe la plus incertaine - plutôt que simplement la première
      feature ? [Risque, standards-ingenierie.md + risques.md]
- [ ] CHK027 (C4) Le registre de risques est-il non vide, chaque risque portant impact, mitigation
      proportionnée et déclencheur de revue, priorisé par probabilité x impact ? Un registre vide
      est un signal d'alerte. [Complétude, risques.md]
- [ ] CHK028 (C4) L'effort de conception est-il proportionné au risque, avec une évidence que la
      mitigation agit vraiment - ni sur-conception sur un petit risque, ni sous-conception sur un
      risque majeur ? [Proportion, risques.md]
- [ ] CHK029 (C4) Les items à haut risque de sécurité et de fiabilité sont-ils traités avant le
      handoff, et les spikes ou POC bloquants identifiés avant la première feature ? [Risque,
      risques.md]
- [ ] CHK030 (C5) `impact-design.md` couvre-t-il la stack front et l'approche de style ?
      [Handoff, impact-design.md §1]
- [ ] CHK031 (C5) Couvre-t-il les contrats transverses visibles - multitenance/theming, identité,
      rôles et autorisations avec variantes par rôle, cas non-autorisé, session expirée,
      navigation et routage ? [Handoff, impact-design.md §2]
- [ ] CHK032 (C5) Couvre-t-il les conventions d'API qui décident des états d'UI - format d'erreur
      vers messages par champ, asynchrone, pagination et listes, cas vides ? [Handoff,
      impact-design.md §3]
- [ ] CHK033 (C5) Couvre-t-il les NFR qui touchent l'UX - niveau d'accessibilité visé, breakpoints
      responsive, i18n, budget de performance ? **C'est ce que le designer va consommer, vérifié
      en priorité.** [Handoff, impact-design.md §4]
- [ ] CHK034 (C6) Ne subsiste-t-il aucun marqueur `[À VALIDER]`, `[À CHIFFRER]`, `[À DÉFINIR]`
      dans `architecte-out/`, et chaque fichier porte-t-il son front-matter `version` et `date` ?
      [Complétude, architecte-out/]
- [ ] CHK035 (C7) Passe finale : une lecture critique de bout en bout, "ce qui manque / ce qui
      peut casser", a-t-elle été faite ? C'est le filet qui rattrape ce que les contrôles ciblés
      ont laissé passer - jamais une checklist de présence. [Jugement, architecte-out/]

*(Ancrages : Bass/Clements/Kazman, arc42 §10 ; Cockburn, Freeman & Pryce, Hunt & Thomas ;
Fairbanks, arc42 §11, AWS Well-Architected.)*

---

## Sources (vérification)

- ATAM - SEI, *ATAM: Method for Architecture Evaluation* (Kazman, Klein, Clements) :
  https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/
- Checklists comme "tests unitaires de l'exigence" - GitHub Spec Kit, `/speckit.checklist`
  (https://github.com/github/spec-kit/blob/main/templates/commands/checklist.md).
- Scénarios qualité 6-parties - Bass, Clements, Kazman, *Software Architecture in Practice* ;
  arc42 §10 : https://docs.arc42.org/section-10/
- ADR - Michael Nygard (martinfowler.com/bliki/ArchitectureDecisionRecord.html) ;
  https://adr.github.io/ ; arc42 §9.
- Traçabilité bidirectionnelle (ni parent sans enfant, ni orphelin) - pratique standard
  d'ingénierie des exigences (matrice de traçabilité).
- Walking skeleton - Alistair Cockburn ; Freeman & Pryce, *GOOS* ; "tracer bullet", Hunt &
  Thomas, *The Pragmatic Programmer*.
- Risque-driven - George Fairbanks, *Just Enough Software Architecture* ; arc42 §11
  (https://docs.arc42.org/section-11/) ; AWS Well-Architected Framework (6 piliers, revue avant
  go-live).
