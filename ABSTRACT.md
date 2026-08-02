# SC-013 AREG — Abstract

**Standard:** SC-013 · **Full name:** Agent Registry
**Acronym:** AREG · **Version:** 0.1.0 · **Status:** Proposed
**License:** CC BY 4.0 · **Date:** June 2026
**Repository:** https://github.com/Observalytics-SL/areg
**Schema:** https://raw.githubusercontent.com/Observalytics-SL/areg/main/schema/registry-entry.schema.json
**Namespace:** https://github.com/Observalytics-SL/areg/vocab#

---

## One-paragraph abstract (for directories, registries, and citations)

The Agent Registry (AREG, SC-013) is an open, vendor-neutral specification for publishing, discovering, and resolving artificial intelligence agent definitions. An AREG registry entry is a lightweight metadata document that records where a specific version of an agent definition can be fetched, who published it, what version it is, and how consumers can verify its authenticity — without re-hosting the definition itself. AREG also defines a REST API that conforming registry servers implement to expose search, resolution, and publication endpoints. It composes with the Autonomous Agent Interchange Format (AAIF, SC-006), which defines the content a registry entry points to, and the Agent Capability and Profile Model (ACPM, SC-014), which a registry entry may optionally reference for richer capability, trust, cost, and SLA information. AREG is part of Schema Commons, a family of open, CC BY 4.0 licensed data standards.

---

## Extended abstract (for conference submission, IETF I-D, or W3C Note)

### Problem

The AI agent ecosystem has standards emerging for how to *run* a portable agent definition (SC-006 AAIF) and, separately, for describing what an agent, platform, tool, or model *offers* (SC-014 ACPM). Neither addresses a third problem: how to *find* an agent in the first place. Today, agent discovery is either hard-coded (a URL baked into client configuration) or built as a proprietary internal catalogue with no shared vocabulary for what is published, by whom, at what version, or whether a given version has been retracted. There is no standard, queryable answer to "where do I find agent X, and can I trust it?"

### Contribution

AREG defines a registry entry document as a JSON Schema (draft 2020-12) object, plus a REST API that registry servers implement:

1. **Entry, not copy** — a registry entry is a pointer-and-metadata record (`agent_id`, `agent_version`, `aaif_url`, `publisher`); the authoritative agent definition remains hosted at `aaif_url`, not re-hosted by the registry.
2. **Immutability and soft deletes** — once published, an entry's `aaif_url`, `signature`, and `published_at` never change; retraction is modeled as yanking (`yanked: true` + `yank_reason`), which preserves the record for audit rather than deleting it — the same model npm and crates.io use for packages, applied to agent definitions.
3. **Optional but fully specified signing** — a publisher may attach a detached JWS (RFC 7515) over the RFC 8785 canonical JSON of the AAIF document at `aaif_url`, verifiable against a JWK Set published at `publisher.public_key_url`. Signing is not required, but when present it is precisely specified enough for any consumer to verify it.
4. **A REST API** (§E) covering list/search, single-entry fetch, "resolve latest," publish, metadata update, and yank — with a minimal, interoperable filter surface (tag, capability, conformance level) so richer search remains a registry extension rather than a conformance requirement.
5. **Registry-level, not document-level, conformance** — four cumulative levels (Discover → Publish → Signed → Full, §I) describe what a *registry implementation* supports, distinct from whether an individual entry is schema-valid.

The minimum conformant registry entry requires `sc_standard: "SC-013"`, `agent_id`, `agent_version`, `publisher`, and `aaif_url`.

### Design rationale

AREG deliberately does not re-host or validate the content it points to: the registry's job is discovery and authenticity, not execution or capability description, both of which are explicitly out of scope and delegated to AAIF and ACPM respectively. This keeps AREG small and lets any party run a conforming registry without needing to also implement an agent runtime. Versioning and yanking follow package-registry precedent (npm, crates.io) rather than inventing new semantics, on the reasoning that agent definitions are, from a registry's point of view, versioned publishable artifacts much like software packages.

### Relationship to adjacent standards

AREG does not replace SC-006 (AAIF) or SC-014 (ACPM) and depends on neither. AAIF defines what an agent *is*; ACPM defines what it *offers*; AREG defines where to *find* it. A registry entry links all three: `agent_id` matches the AAIF document, `aaif_url` resolves to it, and an optional `acpm_profile_url` points to a capability profile. AREG is also deliberately scoped narrower than the Agent2Agent (A2A) Protocol's Agent Card, which is a runtime service-discovery document served by an agent itself rather than a searchable catalog record — the two are complementary, and an AREG entry's `aaif_url` target may itself reference an A2A Agent Card endpoint. See SPECIFICATION.md §L and §H for the full comparison, including the Model Context Protocol's still-forming "Server Cards" discovery effort.

### Validation

The schema is implemented as JSON Schema 2020-12. Both included examples (registry entries for the AAIF Invoice Chaser and Research Summarizer reference agents) validate against the schema using the Schema Commons reference validator (`tools/validate.py`).

### Status and next steps

AREG 0.1.0 is a **Proposed** standard: the registry entry schema, REST API specification, and signing model are complete, but there is no reference registry-server implementation, no deployed public registry, and no external adopters yet. Priority gaps before a stable release: (1) a reference server implementation of §E, comparable to how AAIF ships reference tooling; (2) the conformance self-certification report schema and `/.well-known` publication convention (currently only specified in prose, see CONFORMANCE.md); (3) at least one independently operated registry deployed and tested against this schema. Community contributions are invited.

---

## Keywords

AI agents · agent registry · agent discovery · agent portability · digital signatures · JWS · versioning and yanking · JSON Schema · Schema Commons · service discovery

---

## Citation

```bibtex
@techreport{areg-sc013-v0,
  title     = {Agent Registry (AREG) — SC-013 v0.1.0},
  author    = {van Bussel, Bob},
  year      = {2026},
  month     = {June},
  type      = {Proposed Standard},
  institution = {Schema Commons},
  url       = {https://github.com/Observalytics-SL/areg},
  note      = {CC BY 4.0. Schema: registry-entry.schema.json (sc_version 0.1.0)}
}
```

---

## Contact

- **Issues and proposals:** https://github.com/Observalytics-SL/areg/issues
- **Working group:** See CONTRIBUTING.md in the repository
- **General enquiries:** hello@observalytics.com *(forthcoming)*
