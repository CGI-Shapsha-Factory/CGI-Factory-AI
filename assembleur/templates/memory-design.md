# Design : système, états, accessibilité

<!-- Fichier mémoire (.claude/memory/design.md), lu par Claude au besoin. Digest du handoff
     design pour la fabrication. Contenu seul. -->

## Design system (opposable)
- **Source** : le design system = l'**export committé** dans `designer-out/maquette-de-claude-design/`
  (dossier ou ZIP), auto-portable - tout vit dans le repo.
- **Règle non négociable** : tout écran dérive de l'export committé du design system ; **aucune valeur de
  style en dur** - on utilise les **tokens et composants**.

## États par écran
[La checklist des états à couvrir : chargement, vide (message + action), erreur, succès, et tout
état spécifique aux parcours.]

## Patterns d'erreur
[Comment les erreurs s'affichent : validation à la sortie du champ ; le format d'erreur de l'API se
projette en messages par champ ; erreur serveur ; perte de connexion.]

## Accessibilité
[Le niveau visé (ex. WCAG 2.2 AA) et le socle : contraste, focus visible, navigation clavier,
erreurs pas par la couleur seule.]
