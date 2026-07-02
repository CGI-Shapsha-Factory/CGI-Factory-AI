# Guidelines de design — handoff pour l'Assembleur

> Les **règles à graver dans le projet** pour rendre le contrat de design **opposable en fabrication**.
> Consommées par l'Assembleur (constitution + `claude.md` + CI). Le design system vit dans Claude Design
> **ou** dans un export committé au repo, et est matérialisé en code par **`/design-sync`** (depuis l'export
> committé s'il est présent, sinon la réf. Claude Design) ; ces guidelines l'encadrent.

## Source du design system
- Design system **validé** : <réf. Claude Design **ou** export committé au repo (zip/dossier, ex. `tokens.css`)>
  — pont vers le code : **`/design-sync`** (depuis l'export committé s'il est présent, sinon la réf. Claude Design).
- Nature de la source : `<claude_design_ref | committed_export>` — un export committé rend la fabrication auto-portable.
- Stack front cible : … `(src: design-impact §1)`

## Règles d'états (par écran)
Chaque écran couvre ses **états canoniques** : **chargement, vide, erreur, succès** (1re utilisation ≠
aucun résultat). État vide = message clair + une action. *(NN/g)*

## Patterns d'erreur
- Validation **à la sortie du champ** (pas pendant la frappe), message **explicite et actionnable**.
- **Format d'erreur de l'API → messages par champ** `(src: design-impact §3)`.
- Erreur serveur et perte de connexion traitées ; focus porté sur le **1er champ en erreur**.

## Socle d'accessibilité
- **WCAG <niveau visé, ex. 2.2 AA>** : contraste AA, **focus visible**, cibles tactiles suffisantes,
  **navigation clavier**, erreurs identifiées **en texte** (pas par la couleur seule). `(src: design-impact §4)`

## Discipline d'implémentation (à forcer en fabrication)
- **Tout écran dérive du design system synchronisé** ; **aucune valeur de style en dur** → tokens et
  composants uniquement.
- `/design-sync` exécuté **au démarrage** ; on ne construit qu'à partir des tokens/composants synchronisés.

---
*Sans objet sur ce projet : <lister les items marqués sans objet>.*
