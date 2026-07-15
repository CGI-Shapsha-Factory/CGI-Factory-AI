# Guide de la porte de cohérence — grille canonique (architecte)

Référence lue par le skill `architecte-coherence`. C'est la **grille de vérification** que la
porte déroule sur le contrat technique **avant de passer au designer**. Elle est **ancrée dans
des méthodes reconnues** d'évaluation d'architecture (pas une checklist maison) et s'applique en
**grille pragmatique**, pas en atelier formel.

**Principe directeur — challenger, pas cocher.** On ne vérifie pas la *présence* d'un fichier :
on cherche ce qui **manque**, ce qui se **contredit**, ce qui pourrait **casser**. La présence
est déjà couverte par le garde-fou déterministe `check_architecture.py` ; cette grille est le
travail de **jugement** que le script ne peut pas faire.

**Principe de résolution — toujours une décision, jamais un simple constat.** Chaque point
relevé (manque, contradiction, anomalie) n'est **jamais** seulement affiché « bloquant ». Il est
transformé en **décision en session** via la boucle 3-options (`interactive-loop.md`) : énoncer
en clair ce qui est là / ce qui manque, demander « que veux-tu faire ? », proposer **deux actions
adaptées + saisie libre**, puis **appliquer le choix en place**. L'utilisateur ne relit jamais
les artefacts : tout se règle dans la décision. Voir `interactive-loop.md` (règle d'or).

---

## Lentille A — Cohérence (rien ne se contredit)

**A1. Points de sensibilité et de compromis classés risque / non-risque.** Un *point de
sensibilité* = un élément qui affecte un attribut de qualité ; un *point de compromis* = un
élément qui est sensible pour **deux attributs en compétition** (ex. cache = performance ↔
fraîcheur). Vérifier qu'aucun n'est laissé **non classé** : chacun est soit un **risque** soit un
**non-risque**, et les risques sont regroupés en **thèmes** rattachés à un driver métier.
*(Ancrage : ATAM — Architecture Tradeoff Analysis Method, étapes 6 et 9, SEI/Kazman-Klein-Clements.)*

**A2. ADR non contradictoires et supersession propre.** Deux ADR **acceptés** ne se contredisent
jamais (croiser le journal de décisions). Un ADR remplacé est **marqué `Statut: superseded` et
lié** à son successeur — jamais réécrit ni supprimé en silence ; l'ADR successeur référence le
précédent. Chaque ADR porte : contexte (faits neutres), décision, **rationale (le pourquoi)**,
options réellement considérées avec leurs compromis, conséquences (positives **et** négatives),
statut courant. Un ADR sans rationale ni alternatives n'a pas de valeur d'architecture.
*(Ancrage : Michael Nygard ; adr.github.io ; arc42 §9.)*

**A3. Contradictions inter-artefacts.** Confronter **drivers ⨉ stack ⨉ ADR ⨉ déploiement**. Ex. :
un driver « hébergement UE / pas de fuite de données » contredit-il un service externe hors UE ?
la cible de disponibilité/performance est-elle réellement tenue par le déploiement décrit ? un ADR
en contredit-il un autre ? une techno de la stack contredit-elle une contrainte d'un driver ?

**A4. Cohérence de nommage (langage ubiquitaire).** Un même concept est nommé pareil partout —
alignement avec le `glossaire.md` du cadrage. Pas deux noms pour une même chose, pas deux choses
sous le même nom (artefacts, composants, diagrammes, ADR).

**A5. Diagrammes C4 ↔ inventaire réel.** Les conteneurs/composants montrés dans les diagrammes
**existent** dans `composants.md` ; les frontières sont **cohérentes** entre les niveaux
Contexte → Conteneurs → Composants ; noms réels partout (aucun placeholder) ; les images PNG sont
présentes dans `architecte-out/diagrammes/`. *(Ancrage : modèle C4 + traçabilité.)*

---

## Lentille B — Consistance (traçabilité bidirectionnelle, aucun orphelin)

Principe : **ni parent sans enfant, ni orphelin.** Aucune exigence sans élément qui la réalise,
aucun élément qui ne remonte pas à une exigence. La plupart des défauts de traçabilité sont des
**liens manquants** ou **non mis à jour** quand une exigence a changé.

**B1. Sens avant (couverture).** Chaque **driver**, chaque **attribut de qualité**, chaque
**contrainte de brief** et chaque **entité du glossaire** est **adressé** par ≥1 composant et/ou
ADR. Une entité de l'ERD sans composant qui la gère = **trou**. Un besoin de sécurité/droits/audit
est reflété par un composant **et** un ADR (journal d'audit présent si exigé).

**B2. Sens arrière (pas d'orphelin).** Chaque **composant** remonte à un besoin/driver ; un
composant qui ne sert aucune exigence = **orphelin** à justifier ou retirer.

**B3. Use cases ↔ features.** Couverture **1:1** : chaque use case du `spec-index.md` a une feature
dans `architecture.feature_sequence` ; aucune feature ne référence un use case inexistant.

**B4. Composant ↔ stack (deux sens, versions concordantes).** Chaque composant a une techno
**définie** dans la matrice (pas « à définir ») ; aucune ligne de matrice sans composant. La stack
inline d'un composant (`composants.md`) **correspond** à `stack-technique.md` — mêmes technos,
**mêmes versions exactes**. Échec si un composant décrit une stack que `stack-technique.md` ne
retient pas, ou une version divergente/vague. **Un composant Frontend/UI existe si le produit a
des écrans.**

**B5. Conventions ↔ stack.** Chaque langage retenu a son fichier de conventions installé dans
`conventions/`.

---

## Lentille C — Complétude (chaque exigence bien formée et couverte)

**C1. Scénarios qualité bien formés et testables.** Chaque attribut de qualité est exprimé en
**scénario à 6 parties** : **source** du stimulus · **stimulus** · **artefact** stimulé ·
**environnement** (nominal / pointe / dégradé) · **réponse** observable · **mesure de réponse
chiffrée**. La mesure est la partie critique : sans elle, l'exigence n'est pas testable. **Rejeter**
tout « scalable / robuste / performant / user-friendly » sans source/stimulus/mesure. Chaque
attribut significatif a ≥1 scénario, tracé à un driver. *(Ancrage : Bass/Clements/Kazman, *Software
Architecture in Practice* ; arc42 §10.)*

**C2. Drivers ≠ attributs de qualité.** Distincts, non redondants, dérivés : un **driver** =
objectif métier / contrainte / risque (concret, adressé par composant/ADR/attribut) ; un **attribut
de qualité** = une -ilité avec **cible mesurable + scénario**. Aucun doublon (un driver et un
attribut ne désignent jamais le même concept) ; chaque -ilité **découle** d'un driver (sinon :
driver manquant, ou -ilité injustifiée).

**C3. Walking skeleton valide.** La tranche est **réellement de bout en bout** (fonction réelle,
pas une démo mockée), **traverse les vrais composants** (pas une seule couche), est **automatiquement
build/deploy/test**, et **frappe l'intégration la plus risquée sans stub** (dépendance externe /
tierce / inter-équipe la plus incertaine) — pas juste la première feature. *(Ancrage : Cockburn ;
Freeman & Pryce ; « tracer bullet », Hunt & Thomas.)*

**C4. Registre de risques non vide et fermé.** Chaque risque porte **impact + mitigation
proportionnée + déclencheur de revue**, priorisé (proba × impact). L'effort de conception est
**proportionné** au risque (pas de sur-conception sur un petit risque, ni de sous-conception sur un
risque majeur), et il y a une **évidence de réduction** (la mitigation agit vraiment). Les **items à
haut risque (sécurité / fiabilité)** sont traités **avant le handoff**. Les spikes/POC bloquants
sont identifiés **avant la 1re feature**. Un registre de risques **vide** est un signal d'alerte.
*(Ancrage : Fairbanks, *Just Enough Software Architecture* ; arc42 §11 ; AWS Well-Architected —
fermer les high-risk items avant go-live.)*

**C5. Impact-design complet (contrat consommé par le designer).** `impact-design.md` couvre la
tranche **qui se voit** : (1) stack front + approche de style ; (2) contrats transverses visibles
(multitenance/theming, identité/rôles/autorisations avec variantes par rôle + non-autorisé +
session expirée, navigation/routage) ; (3) conventions d'API qui décident des états d'UI (format
d'erreur → messages par champ, asynchrone, pagination/listes, cas vides) ; (4) NFR qui touchent
l'UX (niveau d'accessibilité visé, breakpoints responsive, i18n, budget de performance). **C'est ce
que le designer va consommer** — donc vérifié **en priorité** ici.

**C6. Aucun marqueur résiduel & front-matter valide.** Aucun `[À VALIDER]` / `[À CHIFFRER]` /
`[À DÉFINIR]` ne subsiste dans un fichier `architecte-out/` ; chaque fichier porte son front-matter
`version:` (entier) / `date:` (ISO). *(Couvert aussi par le garde-fou déterministe.)*

**C7. Passe finale « ce qui manque / ce qui peut casser ».** Une lecture critique de bout en bout,
pas une checklist de présence. C'est le filet qui rattrape ce que les contrôles ciblés ont laissé
passer.

---

## Sources (vérification)

- ATAM — SEI, *ATAM: Method for Architecture Evaluation* (Kazman, Klein, Clements) :
  https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/
- Scénarios qualité 6-parties — Bass, Clements, Kazman, *Software Architecture in Practice* ;
  arc42 §10 : https://docs.arc42.org/section-10/
- ADR — Michael Nygard (martinfowler.com/bliki/ArchitectureDecisionRecord.html) ;
  https://adr.github.io/ ; arc42 §9.
- Traçabilité bidirectionnelle (ni parent sans enfant, ni orphelin) — pratique standard
  d'ingénierie des exigences (matrice de traçabilité).
- Walking skeleton — Alistair Cockburn ; Freeman & Pryce, *GOOS* ; « tracer bullet », Hunt &
  Thomas, *The Pragmatic Programmer*.
- Risque-driven — George Fairbanks, *Just Enough Software Architecture* ; arc42 §11
  (https://docs.arc42.org/section-11/) ; AWS Well-Architected Framework (6 piliers, revue avant
  go-live).
