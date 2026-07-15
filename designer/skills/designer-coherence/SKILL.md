---
name: designer-coherence
description: Valide le design system généré par Claude Design, vérifie la couverture, et produit le handoff design (réf. du système synchronisé + guidelines) pour l'assembleur.
---

# designer-coherence

Dernière étape de la phase design : la **porte de validation de cohérence du système généré** (def :
« après Claude Design, la validation du système généré ; le designer valide l'export committé avant de le
transmettre à la fabrication »). On ne **coche pas une présence** : on **challenge** l'export produit
contre les trois contrats amont (cadrage, architecte, couverture de l'atelier) — ce qui **manque**, ce qui
se **contredit**, ce qui a été **oublié du cadrage** — avant de préparer le **handoff** pour l'assembleur.

## Porte d'entrée
Le skill `designer-prompt` a produit le prompt + le rapport de couverture (`design.phase = "atelier"`,
`design.coverage_sufficient = true`). Sinon, orienter en clair vers `/designer:designer-prompt`.
*(Entre les deux : l'humain a lancé **Claude Design** avec le prompt, obtenu un design system, et **déposé son
export dans `designer-out/maquette-de-claude-design/`**.)*

## Entrées (relues, jamais supposées de mémoire)
- La **source du design system validé** = l'**export committé** dans
  `designer-out/maquette-de-claude-design/` (dossier ou ZIP avec tokens, écrans, composants, ex.
  `tokens.css`), déposé par l'humain. *(Source unique : plus de référence Claude Design externe — l'équipe
  travaille à plusieurs et ne partage pas l'accès aux comptes ; tout vit dans le repo committé.)*
- `designer-out/coverage-report.md` + le bloc `design` du manifeste (checklist).
- **Cadrage** : `cadrage-out/spec-index.md` (parcours / use cases), `cadrage-out/glossaire.md`
  (entités / données affichées), `cadrage-out/product-brief.md` (ton / vision), le **démonstrateur validé**
  (`demonstrateur`, `client_validated`) comme **direction**.
- **Architecte** : `architecte-out/impact-design.md` (§2 identité/rôles/navigation/theming, §3
  erreurs/async/listes, §4 a11y/responsive/i18n/perf).
- Conventions : `references/states-catalog.md`, `references/coverage-checklist-guide.md`,
  `references/question-map.md`, `references/interactive-loop.md`, `references/ux-conventions.md`.
> **Lecture seule du cadrage.** `spec-index.md`, `glossaire.md`, `product-brief.md` sont des **artefacts du
> cadrage** : on les **lit** pour vérifier la couverture, on ne les **crée ni ne les modifie jamais**.

## Étape 1 — Relecture parallèle (fan-out) de l'export + de l'amont
**Toujours (re)lire depuis les fichiers committés**, même si tu crois les avoir déjà lus dans cette
session — **ne jamais** t'appuyer sur la mémoire du chat (exécution reproductible par n'importe qui).
Dispatcher des sous-agents lecteurs (`agentType: "designer-reader"`), **un par lot**, chacun avec un
**schéma de sortie structuré**, en **un seul message** (appels parallèles), puis synthétiser :
1. **Export** — `designer-out/maquette-de-claude-design/` : tokens (couleurs + rôles, typo, espacement,
   rayons, thèmes), écrans et composants présents, **états matérialisés par écran/composant**.
2. **Cadrage** — `spec-index.md` (parcours / use cases + états d'écran impliqués), `glossaire.md`
   (entités / données affichées), `product-brief.md` (ton, objectifs).
3. **Architecte** — `impact-design.md` (§2/§3/§4) : stack front + style, contrats visibles, conventions
   d'API → états d'UI, NFR qui se voient.
4. **Interne** — `designer-out/coverage-report.md` + `design.checklist` du manifeste.

*(Garde simple : export minuscule → un seul lecteur ; sinon fan-out.)* **Passe de complétude** : vérifier
qu'aucun écran, entité, parcours ou décision d'un contrat n'a été manqué avant de challenger.

## Étape 2 — Contrôles de cohérence stricts et adversariaux
Ne **pas** se contenter de vérifier la présence. **Challenger** l'export contre chaque contrat amont : ce
qui manque, ce qui se contredit, ce qui a été perdu en route. Au minimum :

1. **Aucun marqueur résiduel & artefacts présents** : aucun `[À VALIDER]` dans `coverage-report.md` ;
   `designer-out/maquette-de-claude-design/` **non vide** (dossier ou ZIP avec des tokens) ; guidelines
   produites. Chaque manque est un point à **résoudre en session**.
2. **Checklist ↔ export (deux sens)** : chaque item montré **validé** (`deduced`/`decided`) est **réellement
   matérialisé** dans l'export — ex. « états d'erreur couverts » ⇒ un pattern d'erreur existe bien ;
   « thématisation clair/sombre » ⇒ les tokens de thème sont présents. **Inversement**, l'export ne contient
   **aucun écran/token injustifié** par un item ou un doc amont (invention / scope creep).
3. **Parcours du cadrage (couverture inverse — cœur du « rien du cadrage n'est perdu »)** : **chaque**
   parcours / use case du `spec-index.md` a les **écrans et transitions** qu'il exige représentés dans
   l'export. Un parcours sans écran = **trou** (voir Étape 3, route « renvoi Claude Design »).
4. **Entités / données affichées (glossaire)** : chaque **entité ou donnée que le glossaire dit affichée** a
   un composant / pattern pour l'afficher. Une entité affichable sans rien dans le design = **orpheline**.
5. **États d'écran & composant complets (`states-catalog.md`)** : chaque écran data-driven traite les **cinq
   états** (initial/vide · chargement · partiel · **erreur** · succès) ; chaque composant interactif porte
   ses états (**focus visible non masqué**, `disabled`, `error`, `loading`…). Pas seulement le *happy path*.
6. **Impact-design honoré (la tranche technique qui se voit)** : format d'erreur API → **messages par
   champ** présents ; async → chargement / optimiste ; identité & rôles → variantes d'UI par rôle ;
   navigation / routage cohérents. **La stack front + le style de l'export CORRESPONDENT à
   `impact-design.md`** — **échec** si l'export suppose une stack ou une approche que l'architecture n'a pas
   retenue.
7. **Socle d'accessibilité réellement tenu** : le niveau visé (défaut **WCAG 2.2 AA**) est **atteignable par
   les tokens** de l'export — **contraste** texte/fond suffisant, **anneau de focus visible** (2.4.11/2.4.13),
   tailles de cible. Un token de couleur qui casse le contraste = point à corriger.
8. **Direction stylistique vs démonstrateur & anti-slop** : l'export ne **contredit pas** la direction
   validée du démonstrateur sans justification ; **aucun retour aux défauts génériques** que l'atelier avait
   bannis (violet/indigo par défaut, polices par défaut type Inter/Roboto/Poppins).
9. **Cohérence de nommage (langage ubiquitaire)** : la microcopie et les libellés de l'export emploient le
   **vocabulaire du `glossaire.md`** — pas deux noms pour un même concept, pas un concept sous deux noms.
10. **Passe « ce qui manque / ce qui peut casser »** : une **lecture critique finale**, pas une checklist de
    présence.

Garde-fou déterministe (**obligatoire, jamais sauté**) :
`python "${CLAUDE_PLUGIN_ROOT}/scripts/check_design.py" <racine>/manifest.json` — il échoue notamment s'il
reste un item `open`, un statut invalide, ou si prompt / rapport / handoff manquent. S'il est **introuvable**
(chemin plugin non résolu) ou renvoie **exit 1**, **s'arrêter** et **dire en clair** ce qui manque —
**jamais** de vérification « à la main » silencieuse. *(Le script valide la couverture ; les contrôles 2–10
ci-dessus sont le travail adversarial que le script ne peut pas faire.)*

## Étape 3 — Résolution interactive de chaque point (obligatoire avant d'avancer)
Tout point relevé — **bloquant ou non** — n'est **pas seulement affiché**. **Énumérer TOUT ce qui a été
trouvé**, puis les traiter **un par un**, jamais un seul ni une liste en bloc : pour chaque point, la boucle
3-options (`references/interactive-loop.md`) — **recommandation adaptée au projet** + **alternative** +
**saisie**. Selon la nature du point, deux routes de résolution :
- **Point de guidelines / couverture** (règle d'état, pattern d'erreur, note a11y, microcopie, incohérence de
  nommage) → **corrigé en place** dans `designer-out/design-guidelines.md` ou
  `designer-out/coverage-report.md`. **Aucun fichier annexe.**
- **Trou structurel dans l'export** (parcours sans écran, entité non affichable, état/écran absent, thème
  manquant, contraste cassé, stack incohérente) → il **ne se corrige pas ici** (le plugin **ne régénère pas**
  le système) : le **renvoyer vers Claude Design** — rouvrir la **couverture** via `/designer:designer-atelier`
  si elle-même était fausse **puis regénérer le prompt via `/designer:designer-prompt`**, ou faire
  **redéposer un export corrigé** dans
  `designer-out/maquette-de-claude-design/`. **Ne pas sceller** tant qu'il subsiste.

**On ne passe pas à la validation humaine ni à l'assembleur tant qu'un point ou un marqueur n'est pas résolu.**

## Étape 4 — Porte humaine & handoff
1. **Porte humaine : validation du système généré** (porte 2, jamais automatisée). Une fois les points
   résolus, le designer **valide** le design system (cohérent avec la couverture, la direction stylistique et
   la stack). Capter la **source** dans `design.design_system_ref` = chemin
   `designer-out/maquette-de-claude-design/`. Le skill ne passe **jamais** `design.design_validated` à vrai
   de lui-même ; il le **propose**, l'humain confirme.
2. **Finaliser le handoff design** → `designer-out/design-guidelines.md` (gabarit
   `.factory/designer/design-guidelines.md`) : **source du design system validé** = l'export committé,
   **règles d'états** (par écran), **patterns d'erreur** (validation à la sortie du champ, format API →
   messages par champ), **socle d'accessibilité** (niveau visé), et la règle **tout écran dérive de l'export
   committé, aucune valeur de style en dur**. MAJ `design.guidelines_path`.

## Sortie
- **Rapport de couverture** à jour (statut par item, dans l'artefact) + points corrigés en place.
- En chat : **pas de tableau de synthèse** ni de nom de variable/clé — un **bilan en prose** qui énumère en
  clair ce qui a été **vérifié**, ce qui a été **corrigé**, ce qui reste éventuellement **à traiter ou à
  renvoyer vers Claude Design**, puis **la prochaine étape**. Rien de plus.
- **Handoff design** (`design-guidelines.md`) prêt pour l'assembleur ; `design.design_system_ref` posée.
- **Porte humaine** : `design.design_validated = true` **par l'humain uniquement** ; `design.phase = "valide"`
  une fois acté — **mise à jour du manifeste en silence** (jamais narrée). Verdict honnête : rien n'est
  annoncé validé tant qu'un point reste **à traiter**.

## Handoff (vers l'assembleur)
Le contrat de design prêt à transmettre = la **source du design system validé** — l'**export committé** dans
`designer-out/maquette-de-claude-design/` (repo auto-portable) — + les **guidelines** (règles d'états,
patterns d'erreur, socle a11y). La phase design est **auto-portable** : tout vit dans le repo committé, aucun
accès à un compte externe n'est requis. C'est ce que l'Assembleur grave dans la constitution / le `claude.md` : **tout écran dérive de l'export committé du design system**, interdire les valeurs de style en dur,
contrôler les états et patterns d'erreur.

## Règles invariantes
- **Challenger, pas cocher.** Cohérence stricte et adversariale : on cherche ce qui **manque** et ce qui se
  **contredit** contre les trois contrats amont, pas la simple présence.
- **Remonter tout, résoudre un par un.** Énumérer **chaque** point trouvé, puis les dérouler un à un (boucle
  3-options). Ne jamais s'arrêter au premier ; ne jamais poser une liste en bloc.
- **Rien laissé indéfini.** Chaque point se résout en session — corrigé en place (guidelines/couverture) ou
  renvoyé à Claude Design (trou structurel) — avant d'avancer. Aucun marqueur ne survit.
- **L'humain valide.** Le système généré n'est jamais auto-validé par l'IA.
- **Refléter l'état réel.** Aucun item maquillé ; un point « à traiter » reste un trou.
- **Lecture seule du cadrage** : `spec-index.md`, `glossaire.md`, `product-brief.md` sont lus pour vérifier la
  couverture, jamais créés ni modifiés (artefacts du cadrage).
- **Le design system vit dans l'export committé** (`designer-out/maquette-de-claude-design/`) ; le plugin ne
  le régénère pas. L'export committé rend la phase auto-portable.
- **Pas de fuite de champ** en sortie utilisateur ni de tableau de booléens ; **manifeste mis à jour en
  silence** (voir `references/ux-conventions.md`).

**Handoff (avant de passer la main).** Committer `manifest.json` (design **scellé**) **et**
`designer-out/` — **y compris l'export du design system déposé dans
`designer-out/maquette-de-claude-design/`**. La phase suivante lit le **repo committé**, pas ta session.

Étape suivante : `/assembleur:assembleur-init` — démarrer la convergence des 3 contrats (fonctionnel, technique, design) puis l'amorçage du repo SpecKit. Ou corriger d'abord la couverture via `/designer:designer-atelier` (puis regénérer le prompt via `/designer:designer-prompt`).
