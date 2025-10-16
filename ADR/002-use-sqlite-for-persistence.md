# 2. Use SQLite for Application Persistence

Date: 2024-01-15

## Status

Accepted

## Context

ADR-Master needs to persist metadata about ADRs, compilation jobs, integrations, and action logs. The application must work offline and be easily deployable without complex infrastructure.

## Problem Statement

Choose a database solution that:
- Works completely offline
- Requires no external services
- Is easy to backup and restore
- Supports the application's persistence needs
- Is FOSS licensed

## Decision Drivers

* Offline capability (critical requirement)
* Zero configuration required
* Easy deployment
* ACID compliance
* Good Python support
* File-based for easy backup

## Considered Options

* SQLite
* PostgreSQL with local instance
* Embedded key-value store (leveldb, rocksdb)
* JSON files

## Decision Outcome

Chosen option: "SQLite", because it provides ACID compliance, requires zero configuration, works completely offline, and is perfect for our single-user, file-based use case.

### Consequences

* Good: Zero configuration, works offline, easy backup (single file), ACID compliant, excellent Python support via SQLAlchemy
* Bad: Not suitable for high-concurrency (not a concern for our use case), limited advanced features compared to PostgreSQL
* Neutral: Single file database, limited to one writer at a time

## Pros and Cons of the Options

### SQLite

* Good: Zero configuration, offline, single file, ACID compliant, excellent tooling
* Bad: Limited concurrency (not needed), fewer advanced features
* Neutral: File-based

### PostgreSQL

* Good: Full-featured, excellent performance, advanced features
* Bad: Requires server process, complex setup, not truly offline
* Neutral: Network-based

### Embedded key-value store

* Good: Very fast, simple
* Bad: No SQL queries, no relational features, less ecosystem support
* Neutral: Different paradigm

### JSON files

* Good: Simple, human-readable
* Bad: No transactions, no queries, poor performance, data integrity risks
* Neutral: Requires custom implementation

## More Information

SQLite is used by SQLAlchemy ORM, which provides a clean abstraction and allows switching to PostgreSQL later if multi-user deployment becomes a requirement.

## References

* [SQLite Documentation](https://sqlite.org/docs.html)
* [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
* [When to use SQLite](https://sqlite.org/whentouse.html)
