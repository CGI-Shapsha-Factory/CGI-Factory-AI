# Design — système, états, accessibilité

<!-- Fichier mémoire (assembleur-out/memory/design.md), chargé à la demande. Digest du handoff
     design pour la fabrication. Contenu seul. -->

## Design system (opposable)
- **Source** : le design system **synchronisé via `/design-sync`** — depuis un **export committé** au repo
  s'il est présent (auto-portable), sinon la **réf. Claude Design**.
- **Règle non négociable** : tout écran dérive du design system synchronisé ; **aucune valeur de
  style en dur** — on utilise les **tokens et composants**.

## États par écran
[La checklist des états à couvrir : chargement, vide (message + action), erreur, succès, et tout
état spécifique aux parcours.]

## Patterns d'erreur
[Comment les erreurs s'affichent : validation à la sortie du champ ; le format d'erreur de l'API se
projette en messages par champ ; erreur serveur ; perte de connexion.]

## Accessibilité
[Le niveau visé (ex. WCAG 2.2 AA) et le socle : contraste, focus visible, navigation clavier,
erreurs pas par la couleur seule.]
