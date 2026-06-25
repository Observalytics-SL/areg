# SC-013 · AREG — Agent Registry

[![Schema Commons Standard](assets/schema-commons-badge.svg)](https://github.com/Observalytics-SL) ![Status: Proposed](https://img.shields.io/badge/status-proposed-lightgrey) [![Cite](https://img.shields.io/badge/cite-CITATION.cff-blue)](CITATION.cff)

> **Publish, discover, and resolve AAIF agents.** [SC-006 AAIF](https://github.com/Observalytics-SL/aaif) defines how to *run* a portable agent. [SC-014 ACPM](https://github.com/Observalytics-SL/acpm) defines what it *offers*. AREG defines where to *find* it — the registry and discovery layer for the AAIF ecosystem.

## The problem

An AAIF agent definition is a portable document, but there is no standard way to publish it so that orchestrators, platforms, and teams can find, verify, and fetch it. Every deployment either hard-codes an agent URL or builds a proprietary catalogue. There is no shared vocabulary for expressing what an agent is, who published it, what version it is, whether it has been yanked, or how to verify its authenticity.

## The solution

A registry entry is a lightweight metadata document that records a published AAIF agent:

```json
{
  "sc_standard": "SC-013",
  "sc_version": "0.1.0",
  "registry_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "agent_version": "1.0.0",
  "published_at": "2026-06-25T00:00:00Z",
  "publisher": {
    "name": "Acme Corp",
    "url": "https://agents.acme.example",
    "public_key_url": "https://agents.acme.example/.well-known/jwks.json"
  },
  "aaif_url": "https://agents.acme.example/agents/invoice-chaser/1.0.0/definition.json",
  "tags": ["finance", "invoicing"],
  "conformance_level": "Enterprise",
  "required_capabilities": ["tool.mcp", "memory.redis"],
  "acpm_profile_url": "https://agents.acme.example/agents/invoice-chaser/profile.json",
  "yanked": false,
  "yank_reason": null
}
```

AREG defines the **registry entry schema** and the **REST API** for publishing, discovering, and resolving agents. A registry entry points to a full AAIF definition and optionally to an ACPM capability profile, allowing consumers to filter and verify agents without fetching the full definition document for every candidate.

## Status

AREG is a **Proposed standard** — v0.1.0. The `registry-entry.schema.json` is defined and validated. The REST API is specified in [SPECIFICATION.md](SPECIFICATION.md). Before advancing to Draft, at least one public registry must be deployed and tested against this schema.

This is an early-stage standard with no external adopters yet. If you implement it, you are a founding adopter — open a PR to [ADOPTERS.md](ADOPTERS.md).

## Files

| File | Description |
|------|-------------|
| [SPECIFICATION.md](SPECIFICATION.md) | Full specification: registry entry schema, REST API, signing model, discovery, versioning |
| [schema/registry-entry.schema.json](schema/registry-entry.schema.json) | JSON Schema 2020-12 for a registry entry document |
| [context.jsonld](context.jsonld) | JSON-LD context mapping AREG terms to semantic URIs |
| [examples/invoice-chaser-entry.json](examples/invoice-chaser-entry.json) | Registry entry for the SC-006 Invoice Chaser reference agent |
| [examples/research-summarizer-entry.json](examples/research-summarizer-entry.json) | Registry entry for the SC-006 Research Summarizer reference agent |
| [CITATION.cff](CITATION.cff) | Citation metadata |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [ADOPTERS.md](ADOPTERS.md) | Self-service adopter registry |
| [NOTICE](NOTICE) | Copyright and implementation disclaimer |

## Validate

```bash
python3 tools/validate.py
```

## Relationship to the Schema Commons stack

| Standard | Layer | Question answered |
|----------|-------|-------------------|
| [AAIF — SC-006](https://github.com/Observalytics-SL/aaif) | Definition | What *is* this agent? |
| **AREG — SC-013** | **Registry** | **Where do I *find* it?** |
| [ACPM — SC-014](https://github.com/Observalytics-SL/acpm) | Profile | What does it *offer*? |

An AREG registry entry carries the agent_id (from AAIF), an optional acpm_profile_url (to ACPM), and the required_capabilities[] copied from the AAIF document — enabling capability-based search without fetching the full definition for every result.

## 📣 Ready-to-post LinkedIn announcement

> AI agents are becoming portable — but there's no standard place to publish them.
>
> We just proposed **AREG (SC-013)** — the Agent Registry standard for the AAIF ecosystem. A lightweight JSON document that records where an agent lives, who published it, what version it is, and how to verify its authenticity.
>
> Together with **AAIF (SC-006)** (what an agent *is*) and **ACPM (SC-014)** (what it *offers*), the Schema Commons agent stack now covers the full portability lifecycle: define → profile → discover.
>
> Early-stage, zero adopters, fully open. Help shape it.
>
> Part of **Schema Commons** — the Creative Commons for data schemas.
>
> #AIagents #OpenStandards #SchemaCommons #MultiAgent #AgentRegistry

*Licensed CC BY 4.0 — part of [Schema Commons](https://github.com/Observalytics-SL).*
