# SC-013 · AREG — Agent Registry — Specification

- **Standard:** SC-013 · **Acronym:** AREG · **Version:** 0.1.0 (Proposed) · **License:** CC BY 4.0

---

## Conventions & terminology

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [BCP 14](https://www.rfc-editor.org/info/bcp14) ([RFC 2119](https://www.rfc-editor.org/rfc/rfc2119), [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174)) when, and only when, they appear in all capitals, as shown here.

| Term | Definition |
|------|------------|
| **Registry entry** | A JSON instance conforming to `registry-entry.schema.json`. Describes one published version of one AAIF agent. |
| **Registry** | A server that stores and serves registry entries via the AREG REST API. |
| **Publisher** | The party that submits a registry entry to a registry. |
| **Consumer** | Software that queries a registry to discover, resolve, or verify agents. |
| **Agent ID** | The `agent_id` UUID carried in both the AAIF document and the registry entry. Stable across versions. |
| **Registry ID** | The `registry_id` UUID assigned by a registry to one specific `(agent_id, agent_version)` entry. |
| **Yanked** | An entry that has been retracted — it remains in the registry but MUST NOT be used for new deployments. |
| **Canonical JSON** | The deterministic byte representation produced by RFC 8785 (JCS) applied to a JSON value. |
| **Conformance level** | One of the cumulative levels in §J that a registry implementation claims. |

This document is normative. Examples and tables marked *informative* are not.

---

## A. Purpose & scope

AREG defines the **registry entry format** and the **REST API** for publishing, discovering, and resolving AAIF-format AI agent definitions. Together these two things answer the question "where do I find agent X?" across implementations without bespoke per-vendor integration.

**In scope:** the registry entry document format; the REST API for CRUD operations on entries; the signing model for verifying that a published AAIF document has not been tampered with; versioning and yanking semantics; conformance requirements for registry implementations; IANA media type registration.

**Out of scope:** the content of the AAIF definition pointed to by `aaif_url` (that is SC-006's domain); capability declaration of the agent or registry server (that is SC-014's domain); the execution of an agent once discovered; transport-layer security (TLS is REQUIRED but its configuration is out of scope); billing or access-control policies above and beyond what this specification mandates.

---

## B. Design principles

1. **Entry, not copy** — a registry entry is a pointer and metadata record; the authoritative AAIF document lives at `aaif_url`. The registry does not re-host agent definitions.
2. **Immutable versions** — once a `(agent_id, agent_version)` entry is published, the `aaif_url`, `signature`, and `published_at` MUST NOT change. Corrections require a new version. This makes entries auditable and cacheable.
3. **Soft deletes only** — yanking sets `yanked: true` but preserves the entry in the registry. Consumers can audit what was retracted and why; the record of a version's existence is never erased.
4. **Signature is optional but described** — not every publisher will sign. AREG defines the signing model precisely enough that a consumer can verify a signature when one is present, without requiring it.
5. **Public reads, gated writes** — discovery is a public good. All GET endpoints MUST be accessible without authentication. Mutating endpoints REQUIRE authentication whose exact scheme is registry-defined.
6. **Minimal search surface** — the REST API mandates a small, interoperable set of filter parameters (tag, capability, conformance level). Richer full-text or semantic search is a registry extension, not a conformance requirement.

---

## C. Object model

```
RegistryEntry (root)
├── sc_standard        "SC-013" (required)
├── sc_version         string (semver, required)
├── registry_id        UUID — assigned by registry, stable for this (agent_id, agent_version)
├── agent_id           UUID — from the AAIF document (required)
├── agent_version      string (semver) — from the AAIF document (required)
├── published_at       date-time — set by registry on POST
├── updated_at         date-time — set by registry on PATCH
├── publisher
│   ├── name           string (required)
│   ├── url            URI (required)
│   ├── public_key_url URI — JWK Set or PEM for signature verification
│   └── contact        string — abuse/security contact
├── aaif_url           URI — where to fetch the AAIF definition (required)
├── signature          string | null — compact JWS over canonical AAIF document
├── tags[]             string[] — free-form topic tags
├── conformance_level  enum — highest AAIF conformance level the agent claims
├── required_capabilities[] — copy of AAIF required_capabilities[]
├── acpm_profile_url   URI | null — optional ACPM profile for the agent
├── yanked             boolean (default false)
├── yank_reason        string | null
└── license            string — SPDX ID for the agent definition itself
```

---

## D. Field dictionary

### Root

| Field | Type | Req | Description |
|-------|------|-----|-------------|
| `sc_standard` | `"SC-013"` | ✓ | Literal. Identifies this document as an AREG registry entry. |
| `sc_version` | string (semver) | ✓ | AREG schema version. Current: `0.1.0`. |
| `registry_id` | string (uuid) | ✓ | Stable UUID assigned by the registry at publish time. Never changes. |
| `agent_id` | string (uuid) | ✓ | The `agent_id` from the AAIF document at `aaif_url`. MUST match. |
| `agent_version` | string (semver) | ✓ | The `agent.version` from the AAIF document. MUST match. |
| `published_at` | string (date-time) | ✓ | ISO 8601 UTC timestamp of first publication. Set by the registry; publishers MUST NOT supply this field on POST. |
| `updated_at` | string (date-time) | | ISO 8601 UTC timestamp of the most recent metadata update. Set by the registry on PATCH. |

### publisher

| Field | Type | Req | Description |
|-------|------|-----|-------------|
| `publisher.name` | string | ✓ | Human-readable publisher name. |
| `publisher.url` | string (uri) | ✓ | Publisher's canonical URL. |
| `publisher.public_key_url` | string (uri) | | URL resolving to a JWK Set (`application/json`) or PEM (`text/plain`) containing the public key(s) used to produce `signature`. REQUIRED when `signature` is non-null. |
| `publisher.contact` | string | | Contact email or URI for abuse and security reports. |

### Core resolution fields

| Field | Type | Req | Description |
|-------|------|-----|-------------|
| `aaif_url` | string (uri) | ✓ | Resolvable URL for the AAIF agent definition. MUST return a document with matching `agent_id` and `agent_version`. |
| `signature` | string or null | | Compact JWS serialization (RFC 7515) of a detached signature over the canonical JSON (RFC 8785) of the AAIF document at `aaif_url`. Null for unsigned entries. See §F. |

### Discovery metadata

| Field | Type | Req | Description |
|-------|------|-----|-------------|
| `tags[]` | array of string | | Free-form topic tags. Lowercase hyphenated RECOMMENDED. Used as an OR-filter in `GET /v1/entries?tag=`. |
| `conformance_level` | enum | | Highest AAIF conformance level the agent claims (`Core`, `Tooled`, `Portable`, `Multi-agent`, `Observable`, `Enterprise`, `Stateful`). Copied from the AAIF document. |
| `required_capabilities[]` | array of string | | Copy of `required_capabilities[]` from the AAIF document. Allows capability filtering without fetching the full definition. |
| `acpm_profile_url` | string (uri) or null | | URL to an ACPM (SC-014) profile that describes what this agent offers. Null if none published. |

### Lifecycle

| Field | Type | Req | Description |
|-------|------|-----|-------------|
| `yanked` | boolean | | If `true`, this entry has been retracted. Consumers MUST NOT use yanked entries for new deployments. Default: `false`. |
| `yank_reason` | string or null | | Human-readable reason for yanking. Null if not yanked. |
| `license` | string | | SPDX identifier for the AAIF agent definition document (not the registry entry). |

---

## E. REST API

### Base URL

A registry server MUST expose the following endpoints under a stable base URL. This specification uses `{server}` as a placeholder; a registry MUST document its base URL. All paths are relative to `{server}/v1`.

### Content type

All request and response bodies are JSON. Requests that include a body MUST send `Content-Type: application/areg+json` (see §K). Responses carry `Content-Type: application/areg+json`.

### Error format

All error responses use:

```json
{ "error": "short_code", "detail": "human-readable explanation" }
```

### Authentication

All GET endpoints MUST be accessible without authentication. Mutating endpoints (POST, PATCH, DELETE) REQUIRE authentication. The exact authentication mechanism (Bearer token, API key, OAuth 2.0) is registry-defined and out of scope of this specification. A registry MUST document its authentication requirement.

### GET /v1/entries — list and search

Returns a paginated list of registry entries. Yanked entries are excluded by default.

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `tag` | string (repeatable) | Include entries that carry **any** of the supplied tags (OR logic). |
| `capability` | string (repeatable) | Include only entries whose `required_capabilities[]` contains **all** supplied values (AND logic). |
| `conformance_level` | string | Exact match against `conformance_level`. |
| `publisher_url` | string | Exact match against `publisher.url`. |
| `include_yanked` | boolean | If `true`, include yanked entries. Default: `false`. |
| `page` | integer | 1-based page number. Default: `1`. |
| `per_page` | integer | Results per page. Default: `20`. Maximum: `100`. |

**Response 200:**

```json
{
  "entries": [ /* array of registry entry objects */ ],
  "total": 42,
  "page": 1,
  "per_page": 20
}
```

### GET /v1/entries/{registry_id} — fetch one entry

Returns a single registry entry by its `registry_id`.

**Response 200:** the registry entry object.
**Response 404:** `{ "error": "not_found", "detail": "..." }`

### GET /v1/resolve/{agent_id} — resolve latest version

Returns the latest non-yanked entry for the given `agent_id`, ordered by `agent_version` (SemVer descending).

**Response 200:** the registry entry object.
**Response 404:** no non-yanked entry exists for this `agent_id`.

### GET /v1/resolve/{agent_id}/{version} — resolve specific version

Returns the entry for a specific `(agent_id, agent_version)` pair.

**Response 200:** the registry entry object.
**Response 404:** no entry exists for this pair.
**Response 410 Gone:** the entry exists but is yanked. Body includes `yank_reason`.

### POST /v1/entries — publish a new entry

Publishes a new registry entry. The publisher MUST supply all required fields except `registry_id`, `published_at`, and `updated_at`, which the registry assigns and sets.

The registry MUST validate the submitted body against `registry-entry.schema.json` before accepting it.

The registry SHOULD verify that the `agent_id` and `agent_version` in the body match the AAIF document at `aaif_url` at publish time. If they do not match, the registry MUST reject the request with 422.

**Request body:** a registry entry object (omitting `registry_id`, `published_at`, `updated_at`).
**Response 201:** `{ "registry_id": "...", "published_at": "..." }`
**Response 400:** schema validation failure.
**Response 409:** an entry for this `(agent_id, agent_version)` already exists and is not yanked.
**Response 422:** `agent_id` or `agent_version` mismatch with the AAIF document at `aaif_url`.

### PATCH /v1/entries/{registry_id} — update metadata

Updates mutable metadata on an existing, non-yanked entry. The following fields MAY be updated: `tags`, `acpm_profile_url`, `publisher.contact`. The following fields MUST NOT be changed via PATCH: `agent_id`, `agent_version`, `aaif_url`, `signature`, `publisher.name`, `publisher.url`, `published_at`. The registry MUST reject a PATCH that attempts to modify an immutable field with 422.

**Response 200:** the updated registry entry object.
**Response 403:** the requester does not own this entry.
**Response 404:** entry not found.
**Response 409:** entry is yanked; update a yanked entry is not permitted.
**Response 422:** attempt to modify an immutable field.

### DELETE /v1/entries/{registry_id} — yank

Marks an entry as yanked. The entry is not removed; `yanked` is set to `true` and `yank_reason` is recorded.

**Request body:** `{ "yank_reason": "string" }` — REQUIRED.
**Response 200:** the updated registry entry object (with `yanked: true`).
**Response 403:** the requester does not own this entry.
**Response 404:** entry not found.
**Response 409:** entry is already yanked.

---

## F. Signing model

The signature in `signature` attests that the AAIF document at `aaif_url` has not been tampered with since the publisher signed it. Signature is OPTIONAL but fully specified.

### Signing (publisher)

1. Fetch the AAIF document from `aaif_url`.
2. Produce the canonical JSON representation using RFC 8785 (JSON Canonicalization Scheme).
3. Produce a JWS (RFC 7515) using detached payload mode (the canonical JSON bytes are the payload; they are NOT included in the JWS serialization).
4. Use the compact serialization (`header.payload.signature` with an empty payload field: `header..signature`).
5. Recommended algorithm: `ES256` (ECDSA with P-256 and SHA-256, RFC 7518). `RS256` (RSASSA-PKCS1-v1_5 with SHA-256) SHOULD also be supported by registry implementations for backwards compatibility.
6. Set `signature` in the registry entry to the compact JWS string.
7. Publish the public key at `publisher.public_key_url` as a JWK Set (RFC 7517) with `Content-Type: application/json`, or as a PEM file with `Content-Type: text/plain`. The URL MUST remain stable and resolvable for as long as the entry is in use.

### Verification (consumer)

1. Retrieve the registry entry. If `signature` is null, the entry is unsigned — proceed without cryptographic verification or enforce a policy based on the required trust level.
2. Fetch the AAIF document from `aaif_url`.
3. Produce canonical JSON using RFC 8785.
4. Fetch the JWK Set or PEM from `publisher.public_key_url`.
5. Verify the compact JWS against the canonical JSON bytes, using the public key.
6. If verification fails, the AAIF document MUST be treated as untrusted regardless of other metadata in the registry entry.

### Normative constraints

- A registry MUST NOT modify `aaif_url` or `signature` after an entry is published.
- A consumer that requires signed entries MUST reject entries where `signature` is null.
- A consumer MUST NOT cache the public key indefinitely; it SHOULD re-fetch from `publisher.public_key_url` at an interval appropriate to its security policy (e.g. once per day).

---

## G. Versioning and yanking semantics

### Versioning

A registry entry identifies one `(agent_id, agent_version)` pair. When an agent is updated:

- A new entry MUST be submitted with the new `agent_version` value.
- The new entry receives a new `registry_id` assigned by the registry.
- The previous entry (previous `agent_version`) remains in the registry unchanged.
- The `GET /v1/resolve/{agent_id}` endpoint returns the latest non-yanked version (SemVer descending).

The registry_id is the registry's own stable key for one specific entry — it does not change even if metadata is updated via PATCH.

### Yanking

Yanking retracts a specific `(agent_id, agent_version)` entry. It MUST be used when:

- A security vulnerability has been found in the agent definition.
- The AAIF document at `aaif_url` has been changed in a way that invalidates the registry entry.
- The publisher has withdrawn the version for any reason.

Yanking MUST NOT be reversed by un-setting `yanked`. If a version is inadvertently yanked, the publisher SHOULD re-publish the entry as a new `agent_version` with a corrective note, or contact the registry operator.

A registry MUST preserve yanked entries. Consumers who store a reference to a specific `registry_id` MUST be able to retrieve it (including its `yank_reason`) for audit purposes.

---

## H. Relationship to SC-006 and SC-014

AREG does not replace either standard and has no dependency on either:

- **SC-006 (AAIF)** defines the content of the agent definition document that `aaif_url` points to. An AREG registry entry carries the `agent_id` and `required_capabilities[]` from the AAIF document to enable search without fetching every definition. Using AREG without AAIF is possible but unusual — a registry entry is most useful when `aaif_url` returns a document that conforming runtimes can execute.
- **SC-014 (ACPM)** provides a capability profile that `acpm_profile_url` MAY point to. ACPM profiles give consumers richer capability, trust, cost, and SLA information than the minimal `conformance_level` and `required_capabilities[]` in the registry entry. Neither AREG nor ACPM requires the other.

```
AAIF (SC-006)         — definition   → What is this agent?
AREG (SC-013)         — registry     → Where do I find it?
ACPM (SC-014)         — profile      → What does it offer?

A registry entry links all three:
  registry_id  ──→  agent_id (matches AAIF)
  aaif_url     ──→  AAIF document (SC-006)
  acpm_profile_url  ──→  ACPM profile (SC-014) [optional]
```

---

## I. Conformance levels (registry implementations)

These levels apply to software that implements an AREG registry server, not to registry entries themselves.

| Level | Requirements |
|-------|-------------|
| **Discover** | Implements `GET /v1/entries`, `GET /v1/entries/{id}`, `GET /v1/resolve/{agent_id}`, and `GET /v1/resolve/{agent_id}/{version}`. Validates entries against the schema. Returns correct `Content-Type`. |
| **Publish** | Discover + implements `POST /v1/entries`, `PATCH /v1/entries/{id}`, `DELETE /v1/entries/{id}`. Enforces authentication on mutating endpoints. Assigns `registry_id` and `published_at` server-side. |
| **Signed** | Publish + verifies `signature` on POST when `signature` is non-null. Rejects entries whose signature does not verify against the key at `publisher.public_key_url`. |
| **Full** | Signed + supports all query parameters for `GET /v1/entries` (tag, capability, conformance_level, publisher_url, include_yanked, page, per_page). Returns correct pagination metadata. |

Levels are cumulative. A **Full** registry satisfies every requirement of **Discover** through **Signed**. Conformance is self-certified; there is no central certifying authority.

---

## J. Security considerations

### Unsigned entries

A registry entry without a `signature` provides no cryptographic assurance that the AAIF document at `aaif_url` is authentic. Consumers operating in high-trust environments MUST require `signature` to be non-null and verified before deploying or executing an agent. Unsigned entries are appropriate for development, experimentation, and low-trust contexts.

### Publisher impersonation

AREG does not define a mechanism for verifying the identity of a publisher beyond what the registry's own authentication provides. A compromised publisher account can publish malicious entries. Registries SHOULD implement rate limiting, review workflows, and abuse reporting to reduce this risk.

### URL redirection and AAIF document mutation

Because AREG entries point to `aaif_url` rather than embedding the AAIF document, a publisher who controls the server at `aaif_url` can silently substitute a different document after the entry is published. The `signature` field mitigates this: a consumer who verifies the signature detects any change to the canonical JSON. Registries that do not require signatures SHOULD document this risk prominently.

### Key revocation

AREG does not define a key revocation mechanism beyond the publisher updating the JWK Set at `public_key_url`. A consumer that caches public keys indefinitely is vulnerable to continued reliance on a compromised key. Consumers MUST re-fetch keys at an appropriate interval and MUST NOT trust a signature verified against a key that the publisher has subsequently removed from their JWK Set.

### Yanked entry misuse

A consumer that caches registry entries locally MUST periodically re-check the live entry to detect yanking. Using a yanked entry for a new deployment after the `yanked` flag has been set is a misuse. Consumers SHOULD treat a 410 Gone response from `GET /v1/resolve/{agent_id}/{version}` as an immediate signal to halt any pending deployment of that version.

### Transport security

All registry endpoints MUST be served over HTTPS (TLS 1.2 or higher). Registries MUST NOT serve entries over plain HTTP. Consumers MUST NOT fetch `aaif_url` or `publisher.public_key_url` over plain HTTP when performing signature verification.

---

## K. IANA considerations

### Media type registration: application/areg+json

This specification registers the following media type:

| Field | Value |
|-------|-------|
| Type name | application |
| Subtype name | areg+json |
| Required parameters | None |
| Optional parameters | None |
| Encoding considerations | Binary (UTF-8 JSON) |
| Security considerations | See §J |
| Interoperability considerations | Instances MUST validate against registry-entry.schema.json v0.1.0 or later |
| Published specification | This document |
| Applications that use this media type | AREG registry clients and servers |
| Fragment identifier considerations | None |
| Additional information | Magic number: none; file extension: `.areg.json`; Macintosh file type code: none |
| Intended usage | COMMON |
| Restrictions on usage | None |
| Author | Bob van Bussel, bob@observalytics.com |
| Change controller | Schema Commons (schemacommons.org) |

---

## L. Related work

### A2A Agent Cards

The Agent2Agent (A2A) Protocol, now under Linux Foundation governance, defines an Agent Card — a small JSON structure that an agent server exposes at a well-known URL to advertise its capabilities. Agent Cards are designed for runtime service discovery (connect to this URL and learn what the agent can do right now), whereas AREG registry entries are designed for catalog discovery (search a registry to find agents by capability, publisher, or tag before connecting). The two are complementary: an AREG entry MAY carry the `aaif_url` of an AAIF document that in turn references an A2A Agent Card endpoint.

### npm and crates.io registry semantics

AREG's versioning and yanking semantics are directly inspired by the npm and crates.io package registries. Both use the same model: published versions are immutable records; yanking marks a version as retracted without removing it; a "latest" resolution endpoint returns the latest non-yanked version. AREG adapts this model for AI agent definitions rather than software packages.

### MCP Server Cards

The Model Context Protocol roadmap (2026-03-05) lists a planned Server Cards effort for MCP server discovery via `.well-known` URLs. An AREG registry entry for an MCP-based agent SHOULD include an `acpm_profile_url` pointing to an ACPM profile whose `tools[]` section captures the server's MCP capabilities, enabling the AREG discovery layer to coexist with any future MCP Server Card standard rather than competing with it.

---

## M. Versioning & changelog

| Version | Date | Change |
|---------|------|--------|
| 0.1.0 | 2026-06-25 | Initial proposed standard. Registry entry schema, REST API, signing model (JWS/JCS/JWK), versioning and yanking semantics, conformance levels, IANA media type. |

---

## N. FAQ

**Does AREG require AAIF?**
No. `aaif_url` is a URI pointing to any resource the publisher declares. In practice, AREG is most useful when `aaif_url` points to an AAIF document, but AREG does not validate the content at `aaif_url` beyond checking that `agent_id` and `agent_version` match.

**Can there be multiple registries?**
Yes. AREG defines no central registry. Any party can run a conforming AREG registry. Consumers can query multiple registries and merge results. Future versions of this specification may define a cross-registry federation protocol.

**How do I update a published agent?**
Increment `agent_version` and submit a new POST. The previous version remains in the registry. The `GET /v1/resolve/{agent_id}` endpoint returns the new version as "latest".

**Can I delete an entry entirely?**
No. AREG defines only yanking (soft delete). A hard delete would break consumer caches and audit trails. Registries MAY implement administrative hard deletion as a non-conforming extension, but MUST NOT expose it as the standard DELETE endpoint.

**What algorithm should I use for signing?**
`ES256` (ECDSA with P-256) is RECOMMENDED. Keys are shorter, signing is faster, and the algorithm is widely supported. `RS256` is a valid alternative if your existing PKI infrastructure uses RSA.

---

## O. References

### Normative references

- **[RFC 2119]** Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, 1997.
- **[RFC 8174]** Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words", BCP 14, RFC 8174, 2017.
- **[RFC 7515]** Jones, M., Bradley, J., and N. Sakimura, "JSON Web Signature (JWS)", RFC 7515, 2015.
- **[RFC 7517]** Jones, M., "JSON Web Key (JWK)", RFC 7517, 2015.
- **[RFC 7518]** Jones, M., "JSON Web Algorithms (JWA)", RFC 7518, 2015.
- **[RFC 8259]** Bray, T., "The JavaScript Object Notation (JSON) Data Interchange Format", STD 90, RFC 8259, 2017.
- **[RFC 8785]** Rundgren, A., Jordan, B., and S. Erdtman, "JSON Canonicalization Scheme (JCS)", RFC 8785, 2020.
- **[RFC 9562]** Davis, K., Peabody, B., and P. Leach, "Universally Unique IDentifiers (UUIDs)", RFC 9562, 2024. (Obsoletes RFC 4122.)
- **[JSON-SCHEMA]** Wright, A., et al., "JSON Schema: A Media Type for Describing JSON Documents", Draft 2020-12.

### Informative references

- **[SC-006]** Schema Commons, "Autonomous Agent Interchange Format (AAIF)", https://github.com/Observalytics-SL/aaif.
- **[SC-014]** Schema Commons, "Agent Capability and Profile Model (ACPM)", https://github.com/Observalytics-SL/acpm.
- **[A2A]** Linux Foundation (Agent2Agent Project), "Agent2Agent Protocol", https://github.com/a2aproject/A2A.
- **[MCP-ROADMAP]** Model Context Protocol contributors, "Development Roadmap", 2026-03-05, https://modelcontextprotocol.io/development/roadmap.

### Author / editor

Edited under the Schema Commons governance model. Contributions are licensed CC BY 4.0 (specification) and Apache 2.0 (tooling, where applicable). To cite, see [CITATION.cff](CITATION.cff).

---
