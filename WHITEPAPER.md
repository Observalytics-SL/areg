# Agent Registry (AREG): A Vendor-Neutral Standard for Publishing, Discovering, and Verifying AI Agent Definitions

**Bob van Bussel**
Observalytics SL · bob@observalytics.com
Schema Commons Working Group
June 2026

---

## Abstract

> A portable AI agent definition is only useful if it can be found. The Autonomous Agent Interchange Format (AAIF, SC-006) standardises how to describe an agent so it can run on any conforming platform, but defines nothing about how a consumer locates that definition, verifies who published it, or learns whether the published version has since been withdrawn. Today this gap is filled by hard-coded URLs and proprietary internal catalogues, each with its own vocabulary for publisher identity, versioning, and retraction. This paper describes the Agent Registry (AREG, SC-013), a JSON Schema 2020-12 standard defining a **registry entry** document — a lightweight, pointer-and-metadata record naming where a specific version of an agent definition can be fetched, who published it, and how to verify it — together with a REST API that conforming registry servers implement to expose search, resolution, and publication endpoints. AREG entries are immutable once published; retraction is modelled as yanking (a soft delete preserving the record for audit), directly following the versioning semantics established by the npm and crates.io package registries. Authenticity is addressed through an optional but fully specified signing model: a detached JSON Web Signature over the RFC 8785 canonical form of the referenced AAIF document, verifiable against a publisher's published JSON Web Key Set. AREG defines four cumulative conformance levels (Discover through Full) describing registry *implementations* rather than individual documents. AREG is part of Schema Commons (CC BY 4.0), positioned as the discovery layer complementing SC-006 AAIF (agent definition portability) and SC-014 ACPM (capability, trust, and cost description). No existing effort — including A2A Agent Cards or MCP's still-forming Server Cards — combines catalog-style search, immutable versioning, soft-delete retraction, and optional cryptographic authenticity verification for AI agent definitions in a single, vendor-neutral specification.

---

**Keywords:** AI agents, agent registry, agent discovery, digital signatures, JSON Web Signature, versioning, package registry semantics, JSON Schema, Schema Commons, interoperability, service discovery

---

## 1. Introduction

A portable agent definition solves only half of a deployment problem. Once an agent's identity, model routing, tools, memory, and compliance posture can be expressed in a vendor-neutral document — the problem SC-006 AAIF addresses — a second, distinct question remains: how does a consumer, an orchestrator, or a fellow team member actually locate that document? How do they know it came from the publisher it claims to, that it has not been silently altered since publication, and that the version they are about to deploy has not since been withdrawn for a security or correctness reason?

Today, none of these questions has a standard answer. Agent definitions are located through hard-coded URLs baked into client configuration, through proprietary internal service directories with no shared schema, or simply by asking a colleague where the latest version lives. There is no common vocabulary for what "the latest published version of agent X" means, no standard way to prove that a fetched definition has not been tampered with since a publisher signed off on it, and no standard signal that a previously published version should no longer be trusted.

This is not a novel category of problem. Software package ecosystems solved an analogous discovery problem decades ago: npm, crates.io, PyPI, and similar registries each define a catalog record — name, version, publisher, download location, integrity hash — and a small set of operations (publish, resolve latest, yank) that together make "where do I get version X of package Y, and can I trust it" a solved, boring question. AI agent definitions are, from a registry's point of view, structurally similar publishable, versioned artifacts. AREG applies the same pattern to them.

AREG is deliberately narrow. It does not re-host or validate the content of the agent definitions it points to — that is AAIF's domain. It does not describe what an agent's capabilities, trust posture, or cost are — that is SC-014 ACPM's domain. AREG answers exactly one question precisely: given an agent identity, where do I find a specific published version, who published it, and how do I verify it hasn't been altered? The remainder of this paper describes the motivation in detail (Section 2), the design principles that shaped the standard (Section 3), the full data model (Section 4), the conformance levels (Section 5), the relationship to related work (Section 6), the validation approach (Section 7), a discussion of adoption path and known limitations (Section 8), and a conclusion (Section 9).

---

## 2. Background and Problem Statement

### 2.1 What "Discovery" Means Today

Agent discovery in current practice takes one of three forms, none of which generalises. The first is a hard-coded URL: a client is configured with the direct location of an agent definition file, which works until the file moves, the publisher rotates infrastructure, or the client needs to discover an agent it does not already know the address of. The second is a proprietary internal catalogue — a database table or admin UI specific to one platform, with no shared schema that a second platform's tooling can query. The third is informal: asking a colleague, reading a wiki page, or searching a chat history for the last time someone shared a link.

None of these three approaches answers the questions that automated tooling needs answered before deploying an agent definition it did not author: is this the latest version? Has this specific version been withdrawn? Does the content at this URL still match what the publisher originally signed off on? A CI pipeline, an orchestrator selecting among candidate agents, or a security review process each needs a machine-readable, standard answer to these questions, and today must build bespoke integration for every source it consumes from.

### 2.2 What Is Missing

Three specific gaps are architecturally significant for automated agent deployment pipelines:

**Stable resolution.** There is no standard way to ask "give me the current published version of agent X" and receive a consistent answer independent of which publishing platform originally hosted it. Each catalogue defines its own "latest" semantics, if it defines them at all.

**Retraction signalling.** When a published agent version is found to have a defect or a security issue, there is no standard way to mark it as withdrawn while preserving the historical record for audit — most ad hoc catalogues either silently remove the entry (breaking anything that cached a reference to it) or have no retraction mechanism at all, leaving compromised versions indefinitely discoverable.

**Authenticity verification.** Because an agent definition frequently lives at a URL the registry does not control, nothing prevents the content at that URL from silently changing after a consumer last fetched it. Without a standard, optional signing mechanism, a consumer has no way to detect that a definition has been altered since a publisher last attested to its content.

### 2.3 Failure Scenarios

Three specific failure modes in current practice motivate the standard directly.

First, **broken hard-coded references**: a client is configured with a direct URL to an agent definition; the publisher restructures their hosting and the URL 404s with no forwarding address and no standard way for the client to discover the new location. An AREG `GET /v1/resolve/{agent_id}` call, by contrast, resolves through the registry rather than through a URL the consumer must independently keep current.

Second, **silent tampering**: a consumer fetches an agent definition from a URL it does not control. The definition is subsequently altered — maliciously or by accident — and the consumer has no way to detect the change on a later fetch, since nothing about the URL itself signals content integrity. An AREG entry with a non-null `signature` makes this detectable: a consumer that re-verifies the JWS against the current content at `aaif_url` will find the signature no longer validates if the content has changed.

Third, **using a withdrawn version**: a security vulnerability is discovered in a published agent version. Without a standard retraction mechanism, there is no way to signal "do not deploy this version" beyond out-of-band communication (an email, a Slack message) that new consumers will never see. AREG's yanking mechanism (§G) makes this a queryable, standard fact: `GET /v1/resolve/{agent_id}/{version}` returns `410 Gone` with a `yank_reason` for any yanked version, and `GET /v1/resolve/{agent_id}` never returns a yanked version as "latest."

---

## 3. Design Principles

Six design principles shaped the standard and are worth making explicit, as they explain several non-obvious choices in the data model.

**Entry, not copy.** A registry entry is a pointer-and-metadata record; the authoritative agent definition remains hosted at `aaif_url` rather than being re-hosted by the registry. This is a deliberate scope boundary: a registry that re-hosted full agent definitions would need to solve storage, replication, and content-serving problems orthogonal to discovery, and would create a second copy of the definition that could drift from the original. Keeping the registry a thin index over externally hosted content keeps AREG small and lets any party run a conforming registry without operating a content distribution system.

**Immutable versions.** Once a `(agent_id, agent_version)` entry is published, its `aaif_url`, `signature`, and `published_at` never change. This mirrors the immutability guarantee that makes package registries auditable and cacheable: a consumer that has resolved and cached a specific version can trust that the cached metadata will not silently change underneath it. Corrections require publishing a new version, not mutating history.

**Soft deletes only.** Retraction is modelled as yanking — `yanked: true` plus a `yank_reason` — rather than deletion. A registry MUST preserve yanked entries. This design choice reflects the same reasoning npm and crates.io apply to their own yank mechanisms: a hard delete breaks any consumer that cached a reference to the version, and destroys the audit trail of what was published and why it was later withdrawn. A yanked entry remains a fact of record; it simply carries a standard signal that new deployments must not use it.

**Signature is optional but described.** Not every publisher will sign their entries, and AREG does not require signing. But for the publishers who do, the standard specifies the signing and verification procedure (§F) precisely enough that any conforming consumer can verify a signature without publisher-specific integration — detached JWS over RFC 8785 canonical JSON, verified against a JWK Set at a stable, publisher-controlled URL. Making signing optional but fully specified, rather than mandatory, keeps the barrier to a first, unsigned registry deployment low while giving publishers who need stronger authenticity guarantees a standard mechanism to reach for.

**Public reads, gated writes.** Discovery is treated as a public good: all GET endpoints MUST be accessible without authentication, so that any consumer can search and resolve entries without first obtaining credentials. Mutating endpoints (POST, PATCH, DELETE) require authentication, whose specific scheme is registry-defined and out of scope — AREG standardises the shape of the data and the operations, not the access-control policy for who may publish to a given registry.

**Minimal search surface.** The REST API mandates a small, interoperable set of filter parameters — tag, capability, conformance level, publisher — deliberately leaving richer full-text or semantic search as a registry-specific extension rather than a conformance requirement. This keeps the bar for a conforming Discover-level implementation low while not precluding registries from offering more.

---

## 4. The AREG Data Model

An AREG document — a **registry entry** — is a JSON object conforming to `registry-entry.schema.json` (JSON Schema 2020-12). The object model is:

```
RegistryEntry (root)
├── sc_standard        "SC-013"                          [required]
├── sc_version         semver string                     [required]
├── registry_id        UUID — assigned by registry
├── agent_id           UUID — from the AAIF document     [required]
├── agent_version      semver — from the AAIF document   [required]
├── published_at       date-time — set by registry
├── updated_at         date-time — set by registry
├── publisher                                            [required]
│   ├── name / url                                       [required]
│   ├── public_key_url — REQUIRED when signature is set
│   └── contact
├── aaif_url           URI — where to fetch the AAIF definition  [required]
├── signature          compact JWS, or null
├── tags[]
├── conformance_level  copied from the AAIF document
├── required_capabilities[]  copied from the AAIF document
├── acpm_profile_url   URI to an SC-014 profile, or null
├── yanked             boolean, default false
├── yank_reason        string or null
└── license            SPDX identifier
```

### 4.1 Identity and Resolution Fields

`agent_id` and `agent_version` are carried directly from the referenced AAIF document and MUST match it — the registry entry's identity is derived from, not independent of, the definition it points to. `registry_id` is the registry's own stable key for one specific entry, assigned at publish time and unchanged by any subsequent PATCH. This distinction matters operationally: `agent_id` lets a consumer ask "what is the latest version of this agent, across whichever registry I query," while `registry_id` lets a consumer or an audit log reference one specific, immutable published record precisely.

`aaif_url` is the resolvable location of the actual AAIF agent definition. The registry validates, at publish time, that the content at `aaif_url` carries a matching `agent_id` and `agent_version` (§E, POST /v1/entries), but does not continuously monitor the URL thereafter — this is why the optional signature mechanism (§4.3) matters for consumers who need an ongoing integrity guarantee rather than a point-in-time check.

### 4.2 Publisher Identity

The `publisher` block carries `name` and `url` (both required), an optional `contact` for abuse and security reports, and `public_key_url` — required whenever `signature` is non-null. AREG does not itself verify that a publisher is who they claim to be beyond what the registry's own write-authentication provides (§J); `publisher` is a claim, similar in spirit to ACPM's self-declared trust model. What AREG does provide is a stable place for that claim to live, and, when a signature is present, cryptographic proof that the referenced content has not changed since the key at `public_key_url` was used to sign it.

### 4.3 Signing Model

The signing model (§F) is AREG's mechanism for authenticity, and its most structurally significant optional feature. Signing proceeds in five steps: fetch the AAIF document at `aaif_url`; produce its RFC 8785 canonical JSON form; produce a detached JSON Web Signature (RFC 7515) over those canonical bytes, using the compact serialisation with an empty payload field; publish the resulting string as `signature`; and publish the corresponding public key as a JWK Set (RFC 7517) at the stable `publisher.public_key_url`. `ES256` is RECOMMENDED for new implementations; `RS256` SHOULD also be supported for backwards compatibility with existing PKI infrastructure.

Verification is the mirror operation: fetch the entry, fetch the AAIF document, re-derive the canonical JSON, fetch the current JWK Set, and verify the JWS against the canonical bytes using the published key. A consumer that requires signed entries MUST reject any entry where `signature` is null, and MUST treat a failed verification as grounds to distrust the referenced document regardless of any other metadata in the entry.

The choice of a *detached* signature over the AAIF document's canonical form — rather than, say, signing the registry entry itself — is deliberate: it is specifically the referenced content's integrity that matters to a consumer, and canonicalisation (RFC 8785) ensures that semantically identical JSON with different formatting still verifies, so a signature does not spuriously break if the AAIF document is re-serialised without a meaningful content change.

### 4.4 Versioning and Yanking

Each registry entry identifies exactly one `(agent_id, agent_version)` pair. Updating an agent requires publishing a new entry with the new `agent_version`; the previous entry remains unchanged in the registry, and `GET /v1/resolve/{agent_id}` returns the SemVer-highest non-yanked version as "latest." This is the same model npm and crates.io apply to software packages, applied here to agent definitions: published versions are immutable historical records, and "what is current" is a derived query over that history rather than a mutable pointer that erases what came before.

Yanking is the standard's only retraction mechanism, and it is deliberately one-directional: `yanked` MUST NOT be un-set once true. If a version is yanked in error, the correct remedy is publishing a new, corrected `agent_version`, not reversing the yank — preserving the historical fact that the version was, for some period, marked unfit for new deployments. A registry MUST preserve yanked entries indefinitely and continue to serve them from `GET /v1/entries/{registry_id}` for audit purposes, while excluding them from default search results and from "latest" resolution.

### 4.5 Discovery Metadata

`tags[]`, `conformance_level`, and `required_capabilities[]` are copied from the referenced AAIF document into the registry entry itself, specifically so that a consumer can filter candidates without fetching every full definition. This is a deliberate, bounded denormalisation: the registry entry duplicates a small amount of AAIF metadata for search efficiency, while `aaif_url` remains the single source of truth for the full definition. `acpm_profile_url` is the entry's bridge to SC-014: an optional pointer to a capability profile giving a consumer richer trust, cost, and SLA data than the registry entry itself carries.

### 4.6 Illustrative Example

The following is the complete registry entry for the AAIF Invoice Chaser reference agent (`examples/invoice-chaser-entry.json`):

```json
{
  "sc_standard": "SC-013",
  "sc_version": "0.1.0",
  "registry_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "agent_id": "550e8400-e29b-41d4-a716-446655440001",
  "agent_version": "1.0.0",
  "published_at": "2026-06-25T00:00:00Z",
  "publisher": {
    "name": "Schema Commons",
    "url": "https://schemacommons.org",
    "public_key_url": "https://schemacommons.org/.well-known/jwks.json",
    "contact": "bob@observalytics.com"
  },
  "aaif_url": "https://raw.githubusercontent.com/Observalytics-SL/aaif/main/examples/invoice-chaser.json",
  "signature": null,
  "tags": ["finance", "invoicing", "accounts-receivable", "mcp", "enterprise"],
  "conformance_level": "Enterprise",
  "required_capabilities": ["tool.mcp", "memory.redis", "memory.postgres"],
  "acpm_profile_url": "https://raw.githubusercontent.com/Observalytics-SL/acpm/main/examples/invoice-chaser-profile.json",
  "yanked": false,
  "yank_reason": null,
  "license": "CC-BY-4.0"
}
```

This entry is immediately machine-readable by a consumer: it can be found by searching for the `finance` or `mcp` tag, or by filtering on `required_capabilities` containing `tool.mcp`; a capability-matching orchestrator can follow `acpm_profile_url` for richer trust and cost data before dispatch; and because `signature` is `null` here, a consumer with a policy requiring cryptographic authenticity would correctly reject this particular entry, illustrating that AREG's Signed conformance level is meaningfully stricter than Discover or Publish.

---

## 5. Conformance Model

AREG defines four cumulative conformance levels. Unlike AAIF and ACPM, these levels describe **registry server implementations**, not individual documents — a registry entry is simply schema-valid or it is not; what varies is which endpoints and behaviours the *server* implements.

| Level | Requirements |
|-------|-------------|
| **Discover** | Implements all four GET endpoints (`/v1/entries`, `/v1/entries/{id}`, `/v1/resolve/{agent_id}`, `/v1/resolve/{agent_id}/{version}`); validates entries against the schema; returns correct `Content-Type`. |
| **Publish** | Discover + implements POST, PATCH, DELETE with authentication enforced on all three; assigns `registry_id` and `published_at` server-side. |
| **Signed** | Publish + verifies `signature` on POST when present; rejects entries whose signature does not verify. |
| **Full** | Signed + supports every `GET /v1/entries` query parameter with correct pagination metadata. |

The progression reflects real deployment requirements. A **Discover**-level registry is immediately useful as a read-only catalogue — sufficient for a consumer that only needs to resolve existing entries. A **Publish**-level registry supports the full entry lifecycle. A **Signed**-level registry actively enforces the authenticity guarantee described in Section 4.3 rather than merely storing an unverified signature field. A **Full**-level registry supports the complete interoperable search surface a consumer might reasonably expect. Conformance is self-certified, in keeping with the model used by AAIF and ACPM: there is no central authority issuing conformance certificates, and the value of the standard comes from broad, low-friction adoption rather than gatekeeping.

---

## 6. Related Work

### 6.1 A2A Agent Cards

The Agent2Agent (A2A) Protocol, now under Linux Foundation governance, defines an Agent Card: a small JSON structure an agent server exposes at a well-known URL to advertise its capabilities to a directly connecting client. Agent Cards address *runtime service discovery* — connect to this URL right now and learn what the agent can do — a fundamentally different problem from AREG's *catalog discovery*: search a registry, independent of any single agent's uptime, to find candidates by tag, capability, or publisher before ever connecting to one. The two are complementary rather than competing: an AREG entry's `aaif_url` may point to an AAIF document that itself references an A2A Agent Card endpoint for the runtime-connection step that follows discovery.

### 6.2 npm and crates.io Registry Semantics

AREG's versioning and yanking model is not a novel design; it is a direct application of the model npm and crates.io have used for software packages for over a decade: published versions are immutable, retraction is a soft "yank" that preserves the historical record rather than a hard delete, and a "latest" resolution endpoint returns the newest non-yanked version. The rationale for adapting rather than reinventing this model is that agent definitions are, from a registry's point of view, structurally the same kind of artifact package registries already solve for — versioned, publishable, and consumed by tooling that needs stable, cacheable resolution. Where AREG differs is content: a package registry entry points to a downloadable archive, while an AREG entry points to a JSON document and optionally carries a cryptographic signature over that document's canonical form rather than a package registry's typical content hash — a difference driven by AAIF documents being mutable-at-the-source-URL in a way package tarballs conventionally are not.

### 6.3 MCP Server Cards

The Model Context Protocol's development roadmap (dated 2026-03-05) lists a planned "Server Cards" effort for MCP server discovery via `.well-known` URLs — conceptually adjacent to both A2A Agent Cards and, more distantly, to AREG. Like Agent Cards, this is a per-server, connect-to-discover mechanism rather than a searchable catalog, and it is scoped specifically to MCP servers rather than AI agents generally. An AREG entry for an MCP-based agent SHOULD carry an `acpm_profile_url` pointing to an ACPM profile whose `tools[]` section captures the server's MCP-specific capabilities, so that AREG's catalog-discovery layer can coexist with, rather than compete against, any future MCP Server Card standard. Because this effort was still forming at the time of this writing, this mapping should be re-checked before AREG makes any firm interoperability claim.

### 6.4 SC-006 AAIF and SC-014 ACPM

Within Schema Commons, AREG occupies the discovery layer of a three-standard stack. AAIF (SC-006) defines what an agent *is* and how to run it. ACPM (SC-014) defines what an agent, platform, tool, or model *offers* — capability fidelity, trust, cost, SLA. AREG defines where to *find* a specific published version of an agent and how to verify it. The three compose without coupling: a registry entry's `agent_id` matches an AAIF document, and its optional `acpm_profile_url` points to an ACPM profile, but AREG has no schema dependency on either standard and functions correctly (per §H) even when `aaif_url` points to a resource AREG does not otherwise validate.

---

## 7. Validation and Implementation

The normative schema artefact is `schema/registry-entry.schema.json`, implemented as JSON Schema draft 2020-12, with `additionalProperties: false` and `agent_id`/`agent_version`/`publisher`/`aaif_url` required alongside `sc_standard` and `sc_version`. Two example entries are included and validate cleanly against the schema using the Schema Commons reference validator (`tools/validate.py`): a registry entry for the AAIF Invoice Chaser reference agent (Section 4.6, Enterprise conformance level, unsigned) and one for the AAIF Research Summarizer reference agent.

What schema validation proves is structural correctness — an entry contains the required fields and satisfies the type and format constraints. It does not prove that a signed entry's signature actually verifies against live content at `aaif_url`, nor that a registry server correctly implements the REST API and conformance behaviour described in Sections 4 and 5; those require, respectively, live signature verification (§F) and testing an actual server implementation against §E, neither of which the document-level schema validator addresses. This is the same scope boundary AAIF and ACPM draw between document validation and conformance-level verification, and AREG's own known gap here — no reference registry-server implementation yet exists to test against — is discussed in Section 8.2.

---

## 8. Discussion

### 8.1 Adoption Path

AREG is most valuable once at least one independently operated registry exists for consumers to query, since the standard's value is in enabling cross-publisher, cross-platform discovery rather than in any single deployment. A registry implementing Discover-level conformance is a low-effort starting point — a read API over a stored set of validated entries is sufficient. Publish-level conformance requires authenticated write endpoints; Signed-level conformance requires the registry to actually perform JWS verification rather than merely storing an opaque signature string; Full-level conformance requires the complete filter surface described in §E.

No such deployment exists today. AREG v0.1.0 is a **Proposed** standard with no external adopters and no reference registry-server implementation — a precondition for agent discovery to become a standard, queryable operation rather than a description of current, ad hoc practice. The first independently operated registry deployed against this schema is recorded as a founding adopter in ADOPTERS.md.

### 8.2 Known Limitations

**No reference server implementation.** Unlike AAIF, which ships a Python reference toolchain, AREG currently ships only a document-level validator. There is no reference implementation of the REST API in §E to run, fork, or test a conforming client against — a priority gap noted in CONFORMANCE.md.

**Federation is unaddressed.** AREG defines no mechanism for querying multiple registries as if they were one, or for a registry to mirror or federate entries from another. §N (FAQ) notes this explicitly: "Future versions of this specification may define a cross-registry federation protocol." Until then, a consumer that wants comprehensive coverage must know which registries to query and merge results itself.

**Point-in-time signature verification.** A consumer that verifies a signature once and caches the result has no standard signal to know when to re-verify. Because `aaif_url` content can, in principle, be replaced by anyone who later gains control of that URL even after a legitimate initial signing, a consumer relying on long-lived cached verification results should re-verify at an interval appropriate to its own security posture (§F, Normative constraints) — the standard specifies the mechanism but not a mandated refresh cadence.

**Publisher identity is unverified.** As with ACPM's trust model, AREG does not itself verify that a `publisher.name`/`publisher.url` claim is accurate beyond whatever authentication a specific registry's write API enforces. A compromised publisher account can publish entries under a legitimate-looking identity. §J (Security considerations) recommends registries implement rate limiting, review workflows, and abuse reporting, but does not mandate a specific identity-verification mechanism.

### 8.3 The Three-Standard Stack

AREG is the discovery layer of a three-standard stack that together answers the full "define it, find it, know what it offers" workflow for an AI agent:

- **AAIF (SC-006)** — defines what an agent *is* and how to run it.
- **AREG (SC-013)** — defines where to *find* a specific published version and how to verify it.
- **ACPM (SC-014)** — defines what it *offers* and under what trust, cost, and SLA terms.

None of the three requires the others — each is independently useful — but together they close the gap between "I have written a portable agent definition" and "a stranger can find my agent, confirm it has not been tampered with, know it has not been withdrawn, and decide whether it meets their capability, trust, and cost requirements before ever executing it."

---

## 9. Conclusion

Portable agent definitions solve the problem of *how* to describe an agent so it runs anywhere; they do not solve the separate problem of *finding* that description, verifying who published it, or learning that a previously published version has since been withdrawn. Today this gap is filled by hard-coded URLs and proprietary catalogues, each reinventing publisher identity, versioning, and retraction semantics from scratch, with no way for a consumer to detect tampering in a definition it did not author.

AREG (SC-013) defines a JSON Schema 2020-12 registry entry document and a REST API that conforming registry servers implement, directly adapting the immutable-version, soft-delete-yank model that npm and crates.io have used successfully for software packages, and adding an optional but fully specified digital-signature mechanism for authenticity that package registries typically address only through content hashing. Four cumulative conformance levels — Discover through Full — let a registry implementation be immediately useful at the read-only level while providing a clear path to full authenticity enforcement and search capability.

AREG v0.1.0 is a Proposed Standard in Schema Commons, licensed CC BY 4.0. The registry entry schema and REST API specification are complete; no reference server implementation and no external adopters exist as of the publication date. The standard is a necessary precondition for open, cross-publisher agent discovery — a layer the ecosystem does not yet have. Adoption by an independently operated registry would validate the schema and API design against real-world traffic and surface the open questions around signature refresh cadence, publisher identity verification, and cross-registry federation noted as priority items for future work.

---

## References

[1] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels," BCP 14, RFC 2119, IETF, March 1997. https://www.rfc-editor.org/rfc/rfc2119

[2] Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words," BCP 14, RFC 8174, IETF, May 2017. https://www.rfc-editor.org/rfc/rfc8174

[3] Jones, M., Bradley, J., and N. Sakimura, "JSON Web Signature (JWS)," RFC 7515, IETF, May 2015. https://www.rfc-editor.org/rfc/rfc7515

[4] Jones, M., "JSON Web Key (JWK)," RFC 7517, IETF, May 2015. https://www.rfc-editor.org/rfc/rfc7517

[5] Jones, M., "JSON Web Algorithms (JWA)," RFC 7518, IETF, May 2015. https://www.rfc-editor.org/rfc/rfc7518

[6] Rundgren, A., Jordan, B., and S. Erdtman, "JSON Canonicalization Scheme (JCS)," RFC 8785, IETF, June 2020. https://www.rfc-editor.org/rfc/rfc8785

[7] Davis, K., Peabody, B., and P. Leach, "Universally Unique IDentifiers (UUIDs)," RFC 9562, IETF, May 2024. https://www.rfc-editor.org/rfc/rfc9562

[8] Wright, A., Andrews, H., Hutton, B., and G. Dennis, "JSON Schema: A Media Type for Describing JSON Documents," Internet-Draft draft-bhutton-json-schema-01, IETF, December 2020. https://json-schema.org/draft/2020-12

[9] van Bussel, B., "Autonomous Agent Interchange Format (AAIF)," Schema Commons SC-006, Observalytics SL, June 2026. https://github.com/Observalytics-SL/aaif

[10] van Bussel, B., "Agent Capability and Profile Model (ACPM)," Schema Commons SC-014, Observalytics SL, June 2026. https://github.com/Observalytics-SL/acpm

[11] Google LLC / Linux Foundation (Agent2Agent Project), "Agent2Agent (A2A) Protocol," 2025–2026. https://github.com/a2aproject/A2A

[12] Anthropic / Model Context Protocol Contributors, "Model Context Protocol Development Roadmap," modelcontextprotocol.io/development/roadmap, March 5, 2026.

[13] npm, Inc., "npm Registry API," and Rust Foundation, "crates.io," package registry documentation (design precedent for versioning and yanking semantics).

---

*Licensed CC BY 4.0. Part of [Schema Commons](https://github.com/Observalytics-SL). To cite this paper, see `CITATION.cff` in the repository.*
