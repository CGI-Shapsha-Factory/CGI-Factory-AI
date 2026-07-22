# Guide de la porte de cohérence : grille canonique (designer)

Référence lue par le skill `designer-coherence`. C'est la **grille de vérification** que la porte
déroule sur le **design system généré par Claude Design** (l'export committé dans
`designer-out/maquette-de-claude-design/`) **avant le handoff vers l'assembleur**.

> **Ne pas confondre avec `coverage-checklist-guide.md`** : celui-là définit la checklist de
> **l'atelier** (les 19 items fondation / expérience / technique statués dans le manifeste, avant
> Claude Design). Le présent guide est la **porte de sortie**, déroulée **après** que l'export a
> été déposé.

**Principe directeur - challenger, pas cocher.** On ne vérifie pas la *présence* d'un fichier :
on confronte l'export aux **trois contrats amont** (cadrage, architecte, couverture de l'atelier)
et on cherche ce qui **manque**, ce qui se **contredit**, ce qui a été **perdu en route**. La
présence est couverte par le garde-fou déterministe `check_design.py` ; cette grille est le
travail de **jugement** que le script ne peut pas faire.

**Principe de résolution - toujours une décision, jamais un simple constat.** Chaque point relevé
devient une **décision en session** via la boucle interactive (`interactive-loop.md`) :
`AskUserQuestion`, recommandation adaptée au projet + alternative (la saisie libre est ajoutée par
l'outil), puis application. L'utilisateur ne
relit jamais les artefacts : tout se règle dans la décision.

---

## Comment se déroule cette checklist

Chaque item est une **question de qualité** posée à l'export, jamais un test de présence. On
n'écrit pas "les tokens existent", on écrit "les tokens permettent-ils réellement de tenir le
contraste visé ?".

Format d'un item :

```
- [ ] CHK### Question de qualité ? [Dimension, source de traçabilité]
```

Règles de déroulé :
- **Un item à la fois, dans l'ordre.** On ne saute pas, on ne groupe pas.
- **Coché = la question a reçu une réponse satisfaisante** sur l'export réel. Un item dont la
  réponse est "non" ou "je ne sais pas" **reste décoché** et devient une décision en session.
- **Sans objet** : cocher en annotant `[SANS OBJET : raison]`. Jamais de case cochée sans raison
  lisible.
- **IDs stables.** `CHK###` ne se renumérote jamais.
- **Traçabilité.** Chaque item nomme le contrat à confronter.
- L'état coché vit le temps de la session de porte ; les corrections partent dans
  `designer-out/design-guidelines.md` ou `designer-out/coverage-report.md`.

### Deux routes de résolution (propre à cette porte)

- **Point de guidelines ou de couverture** (règle d'état, pattern d'erreur, note a11y, microcopie,
  incohérence de nommage) -> **corrigé en place**. Aucun fichier annexe.
- **Trou structurel dans l'export** (parcours sans écran, entité non affichable, état absent,
  thème manquant, contraste cassé, stack incohérente) -> **ne se corrige pas ici** : le plugin ne
  régénère pas le design system. Renvoyer vers `/designer:designer-atelier` puis
  `/designer:designer-prompt`, ou faire redéposer un export corrigé. **Ne pas sceller** tant qu'il
  subsiste.

---

## Le socle déterministe (couvert par `check_design.py`)

Lancé **en dernier**, à l'étape 4, parce qu'il vérifie aussi le handoff (`guidelines_path`) qui
n'existe pas avant. Il **bloque** en `exit 1` ; ces points ne se cochent jamais à la main.

- [ ] SOC1 Bloc `design` présent avec sa checklist, les trois blocs non vides
- [ ] SOC2 Aucun item au statut `open`, aucun statut invalide
- [ ] SOC3 Prompt, rapport de couverture et guidelines existent réellement sur disque
- [ ] SOC4 `designer-out/maquette-de-claude-design/` non vide

**Jamais sceller sur un exit 1.**

---

## Lentille A : Intégrité de l'export (rien d'incomplet, rien d'injustifié)

- [ ] CHK001 Ne subsiste-t-il aucun marqueur `[À VALIDER]` dans `coverage-report.md`, et les
      guidelines sont-elles réellement produites ? [Complétude, coverage-report.md +
      design-guidelines.md]
- [ ] CHK002 Chaque item de la checklist montré comme validé (`deduced` / `decided`) est-il
      **réellement matérialisé** dans l'export - "états d'erreur couverts" implique un pattern
      d'erreur qui existe, "thématisation clair/sombre" implique des tokens de thème présents ?
      [Consistance, `design.checklist` -> maquette-de-claude-design/]
- [ ] CHK003 Sens inverse : l'export contient-il un écran, un composant ou un token **injustifié**
      par un item de checklist ou un document amont (invention, scope creep) ? [Périmètre,
      maquette-de-claude-design/]

---

## Lentille B : Couverture inverse (rien du cadrage n'est perdu)

C'est le coeur de la porte : on part du **cadrage** et on vérifie qu'il est arrivé jusqu'à
l'écran, pas l'inverse.

- [ ] CHK004 Chaque parcours et chaque use case du `spec-index.md` a-t-il les **écrans et
      transitions** qu'il exige représentés dans l'export ? Un parcours sans écran est un trou
      structurel. [Couverture, cadrage-out/spec-index.md -> maquette-de-claude-design/]
- [ ] CHK005 Chaque entité ou donnée que le glossaire dit **affichée** a-t-elle un composant ou un
      pattern pour l'afficher ? Une entité affichable sans rien dans le design est orpheline.
      [Couverture, cadrage-out/glossaire.md -> maquette-de-claude-design/]
- [ ] CHK006 La microcopie et les libellés de l'export emploient-ils le vocabulaire du glossaire -
      pas deux noms pour un concept, pas un concept sous deux noms ? [Cohérence,
      cadrage-out/glossaire.md]

---

## Lentille C : États et complétude d'écran (pas seulement le happy path)

- [ ] CHK007 Chaque écran data-driven traite-t-il les **cinq états** - initial/vide, chargement,
      partiel, **erreur**, succès ? [Complétude, states-catalog.md ->
      maquette-de-claude-design/]
- [ ] CHK008 Chaque composant interactif porte-t-il ses états - **focus visible non masqué**,
      `disabled`, `error`, `loading` ? [Complétude, states-catalog.md]
- [ ] CHK009 Les états vides sont-ils utiles (message + action) plutôt que de simples écrans
      blancs ? [Substance, maquette-de-claude-design/]

*(Ancrage : états canoniques d'écran - Nielsen Norman Group.)*

---

## Lentille D : Contrat technique honoré (la tranche qui se voit)

- [ ] CHK010 Le format d'erreur d'API décrit par l'architecte se traduit-il par des **messages par
      champ** présents dans le design ? [Consistance, architecte-out/impact-design.md §3]
- [ ] CHK011 L'asynchrone est-il traité - états de chargement, mise à jour optimiste ?
      [Consistance, impact-design.md §3]
- [ ] CHK012 L'identité et les rôles produisent-ils des **variantes d'UI par rôle**, avec les cas
      non-autorisé et session expirée ? [Consistance, impact-design.md §2]
- [ ] CHK013 La navigation et le routage de l'export sont-ils cohérents avec ceux décidés par
      l'architecte ? [Consistance, impact-design.md §2]
- [ ] CHK014 La **stack front et l'approche de style** de l'export correspondent-elles à celles
      retenues par l'architecture ? **Échec** si l'export suppose une stack que l'architecture n'a
      pas retenue. [Consistance, impact-design.md §1 + architecte-out/stack-technique.md]

---

## Lentille E : Accessibilité et direction (le socle tenu, pas déclaré)

- [ ] CHK015 Le niveau d'accessibilité visé (défaut **WCAG 2.2 AA**) est-il **atteignable par les
      tokens** de l'export - contraste texte/fond suffisant ? Un token de couleur qui casse le
      contraste est un point à corriger. [Accessibilité, impact-design.md §4 -> tokens]
- [ ] CHK016 L'anneau de focus est-il visible et non masqué (WCAG 2.4.11 / 2.4.13), et les tailles
      de cible suffisantes ? [Accessibilité, tokens + composants]
- [ ] CHK017 L'export contredit-il la direction stylistique validée du démonstrateur sans
      justification ? [Cohérence, manifeste `demonstrateur` + cadrage-out/product-brief.md]
- [ ] CHK018 Anti-slop : constate-t-on un retour aux défauts génériques que l'atelier avait bannis
      - violet/indigo par défaut, polices type Inter/Roboto/Poppins ? [Anti-théâtre,
      maquette-de-claude-design/]
- [ ] CHK019 Passe finale : une lecture critique "ce qui manque / ce qui peut casser" a-t-elle été
      faite de bout en bout, plutôt qu'une checklist de présence ? [Jugement,
      maquette-de-claude-design/]

---

## Sources (vérification)

- Checklists comme "tests unitaires de l'exigence" - GitHub Spec Kit, `/speckit.checklist`
  (https://github.com/github/spec-kit/blob/main/templates/commands/checklist.md).
- États canoniques d'écran et règles d'erreur - Nielsen Norman Group
  (https://www.nngroup.com/articles/error-message-guidelines/).
- Accessibilité - WCAG 2.2 (https://www.w3.org/TR/WCAG22/), critères 2.4.11 / 2.4.13 (focus
  visible non masqué), 1.4.3 (contraste).
- Modèle de porte et boucle interactive (`AskUserQuestion`, deux options) - `interactive-loop.md`,
  `ux-conventions.md`.
