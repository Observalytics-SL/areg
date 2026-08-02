# AREG Conformance & Self-Certification

> **How a registry server (or a consumer relying on one) proves it "speaks AREG."** Conformance is per-level and self-certified — the same model SC-006 AAIF and SC-014 ACPM use. There is no gatekeeper; credibility comes from the claim being checkable against this document and the schema. Normative level definitions are in [SPECIFICATION §I](SPECIFICATION.md).

Unlike AAIF and ACPM, AREG conformance levels apply to **registry server implementations**, not to the JSON documents they serve. A registry entry is either schema-valid or it isn't; a *registry* claims a conformance level based on which endpoints and behaviors it implements.

## 1. Pick a level

**Levels** (cumulative — see [§I](SPECIFICATION.md)): `Discover` → `Publish` → `Signed` → `Full`.

| Level | A conforming registry MUST satisfy… |
|-------|-------------------------------------|
| Discover | Implements `GET /v1/entries`, `GET /v1/entries/{id}`, `GET /v1/resolve/{agent_id}`, `GET /v1/resolve/{agent_id}/{version}`. Validates entries against `registry-entry.schema.json`. Returns correct `Content-Type: application/areg+json`. |
| Publish | Discover + implements `POST /v1/entries`, `PATCH /v1/entries/{id}`, `DELETE /v1/entries/{id}`. Enforces authentication on mutating endpoints. Assigns `registry_id` and `published_at` server-side. |
| Signed | Publish + verifies `signature` on POST when non-null; rejects entries whose signature does not verify against the key at `publisher.public_key_url`. |
| Full | Signed + supports every `GET /v1/entries` query parameter (`tag`, `capability`, `conformance_level`, `publisher_url`, `include_yanked`, `page`, `per_page`) with correct pagination metadata. |

Most first implementations should target **Discover** or **Publish**. **Signed** and **Full** require committing to the signature-verification and search-surface requirements in full — don't claim them speculatively.

## 2. Validate the entries you serve today

The schema-level check that exists today, regardless of which server-conformance level you claim:

```bash
python3 tools/validate.py
```

This validates every example in `examples/` against `registry-entry.schema.json`. To check your own entries, point the schema at them with any JSON Schema 2020-12 validator (e.g. `ajv-cli --spec=draft2020`) — every entry a conforming registry stores or returns MUST validate, independent of the server's own conformance level.

## 3. What's planned but not yet shipped

Being honest about the current state, not a hidden roadmap:

- **No reference registry-server implementation.** Unlike AAIF, which ships a Python reference toolchain, AREG currently ships only a document validator (`tools/validate.py`) — there is no reference REST server implementing §E to run against or fork.
- **Planned:** a conformance self-certification report schema and a `/.well-known` publication convention (candidate: `/.well-known/areg-conformance.json`), comparable to AAIF's `conformance-report.schema.json`.
- **Not planned (by design):** any AREG-defined mechanism for verifying publisher *identity* beyond what `signature` cryptographically attests (see [SECURITY.md](SECURITY.md) and SPECIFICATION §J) — a registry's authentication scheme for who may publish is registry-defined and out of scope.

If you need the report format or a reference server implementation now, open an issue — these are the most-requested next increments for this standard.

## 4. List yourself

Add a row to [ADOPTERS.md](ADOPTERS.md) describing which level your registry implementation claims. Listing is self-service and free; until the report format ships, the claim is verified by anyone re-reading your registry's behavior against §I and §E.

## What self-certification is and isn't

- **Is:** a public, reproducible statement that can be checked against SPECIFICATION §I and §E by hand or by script today, and against a machine-readable report once that tooling ships.
- **Isn't:** a guarantee that entries stored in the registry are trustworthy. Conformance to AREG means the *registry* correctly implements the endpoints and semantics this specification defines — it says nothing about whether any given entry's `aaif_url` content, `publisher` identity, or `signature` should be trusted. See SPECIFICATION §J (Security considerations) for what AREG does and does not verify.

## Conformance changes between versions

A registry entry's `sc_version` names the AREG schema version it targets. Every change is SemVer; a MINOR bump never invalidates an existing conformant entry or a registry's existing conformance-level claim.
