# Guidelines — review & développement (3 faces)

<!-- Public visé : équipe + Claude Code. Une PR se relit sous les 3 faces. -->

## Review fonctionnelle (src: cadrage)
- La PR couvre-t-elle les critères d'acceptation (Given/When/Then) de la feature ?
- Respecte-t-elle le périmètre IN/OUT et le langage du glossaire ?

## Review technique (src: architecte)
- Respect des ADR, de la stack et des conventions (`conventions/`) ?
- Cibles de qualité (perf / sécurité / fiabilité) tenues ? *Constitution Check* passée ?

## Review design (src: designer — §6, opposable)
- L'écran dérive-t-il du **design system synchronisé** (`/design-sync`) ? **Aucune valeur de style en
  dur** (tokens/composants uniquement) ?
- **États couverts** (vide / chargement / erreur / succès) ?
- **Patterns d'erreur** respectés (validation à la sortie du champ ; format d'erreur API → messages par
  champ) ?
- Accessibilité au niveau visé (ex. WCAG 2.2 AA) : contraste, focus visible, clavier, cibles ≥ 24×24 px ?

## Guidelines dev
- Une PR par feature (ou tranche) ; tests avant merge ; **CI verte** (`factory-checks`).
- Walking skeleton (`001`) en premier ; pas de feature hors séquence sans arbitrage.
