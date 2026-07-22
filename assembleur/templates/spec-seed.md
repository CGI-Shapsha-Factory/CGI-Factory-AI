# Feature Specification: <NOM DE LA FEATURE>

<!-- Graine produite par l'assembleur dans `assembleur-out/features/`, mappée sur le spec.md de
     SpecKit. L'équipe l'étend via /speckit.specify. Un trou = NEEDS CLARIFICATION (convention
     SpecKit) - mais l'assembleur RÉSOUT ces points EN SESSION avant de conclure, donc une graine
     livrée ne contient pas de marqueur. Contenu seul : aucune provenance. -->

**Feature**: `NNN-feature`
**Status**: Draft (graine factory)

## User Scenarios & Testing *(mandatory)*

### User Story 1 : [titre] (Priority: P1)
[Parcours en langage clair.]

**Independent Test**: [comment le tester seul, valeur livrée]

**Acceptance Scenarios**:
1. **Given** [état initial], **When** [action], **Then** [résultat attendu]

### Edge Cases
- [état vide / erreur / hors-ligne]

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: Le système DOIT [capacité]
- **FR-002**: [capacité]

### Key Entities
- **[Entité]**: [ce qu'elle représente]  <!-- voir memory/domain.md ; relations <- ERD architecte -->

## Success Criteria *(mandatory)*
<!-- Deux origines : (1) les critères de succès mesurables du brief cadrage (section 5) - les cibles
     chiffrées négociées avec le client, reprises TOUTES, aucune écartée ; (2) les cibles qualité de
     l'architecte et le niveau d'accessibilité visé. Une cible du brief laissée "à préciser à
     l'architecture" se tranche en session, jamais supprimée. -->
- **SC-001**: [mesurable, techno-agnostique]

## Hors périmètre *(cette feature)*
- [exclusion locale explicite : ce que CETTE feature ne fait pas]

## Assumptions
- [hypothèses / dépendances]

---

## Annexe : Face technique (pour `/speckit.plan` -> Technical Context)
Composants : [...] · Stack : [...] · ADR : [ADR-00X]  <!-- voir technical-context.md -->

## Annexe : Face design
Parcours : [...] · Composants & états : [...] · Accessibilité : [niveau visé]  <!-- voir memory/design.md -->
