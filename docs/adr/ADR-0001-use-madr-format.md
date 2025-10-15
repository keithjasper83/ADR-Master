# 1. Use MADR format for Architecture Decision Records

Date: 2025-01-15

## Status

ACCEPTED

## Context

We need a standardized format for documenting architecture decisions in ADR-Workbench. The format should be:
- Easy to read and write
- Structured but flexible
- Version control friendly
- Widely adopted in the industry

Several ADR formats exist, including:
1. Michael Nygard's original ADR format
2. MADR (Markdown Any Decision Records)
3. Y-Statements format

## Decision

We will use MADR (Markdown Any Decision Records) as the default format for ADRs in ADR-Workbench.

MADR provides a structured template that includes:
- Context and problem statement
- Decision drivers
- Considered options
- Decision outcome
- Consequences (positive and negative)
- Pros and cons of options
- Links to related decisions

## Consequences

### Positive

- MADR is well-documented and actively maintained
- Provides good structure without being overly rigid
- Easy for developers to learn and use
- Supports documenting alternatives and trade-offs
- Works well with markdown tooling

### Negative

- Teams familiar with other formats may need to adapt
- May be more verbose than simpler formats
- Requires discipline to fill out all sections properly

## Links

- [MADR GitHub Repository](https://github.com/adr/madr)
- [ADR GitHub Organization](https://adr.github.io/)
