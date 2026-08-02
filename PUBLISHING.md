# Publishing AREG — paths to a recognised open standard

AREG is designed to be published through several complementary channels, mirroring the path laid out for SC-006 AAIF and SC-014 ACPM. None are mutually exclusive; together they give the standard academic citability, standards-body legitimacy, and developer reach. This document is the roadmap from "a specification in a repository" to "a standard the field cites and implements" — written honestly for a standard that is, as of this writing, brand new.

## 0. Before submitting anywhere: prior-art status and submission readiness

**Submission status: CONTENT COMPLETE, IDNITS PENDING — not yet filed.** Unlike AAIF and ACPM, this draft has not yet had an idnits pass run against it. `draft-schemacommons-areg-00.xml`/`.txt` are xml2rfc-clean and the `.txt` rendering has no lines over 72 columns, but that is not a substitute for actually running `idnits` locally before filing. The `<date>` element in the XML also still reads 2026-06-25 and MUST be bumped to the actual day of submission before filing — the IETF datatracker will reject or flag a stale date.

Prior-art diligence itself **is** complete: [SPECIFICATION.md §L ("Related work")](SPECIFICATION.md) covers the Agent2Agent (A2A) Protocol's Agent Cards (runtime service discovery vs. AREG's catalog discovery — complementary, not competing), npm/crates.io registry semantics (the direct model for AREG's versioning and yanking), and the Model Context Protocol's still-forming "Server Cards" effort. Two things worth flagging before this draft is ever filed:

- **Re-check MCP Server Cards' status.** As of the cited roadmap snapshot (2026-03-05), it was still a forming effort with no concrete specification text. Re-check `modelcontextprotocol.io/development/roadmap` for actual published Server Card text before finalizing any normative claim about how AREG entries relate to it.
- **Re-check A2A's governance state** under the Linux Foundation for any developments since this diligence was done — drafts and roadmaps move between when this was written and when AREG is actually filed.

This matters because of how IETF submission actually works: the instant a draft is filed with the IETF Datatracker, it is public and permanently archived. There is no private, embargoed, or draft-review submission step — "submitting" and "publishing to the world, forever, in a citable index" are the same action. Run idnits, bump the date, and re-confirm the two prior-art checks above before filing — same discipline as was applied to AAIF (submission #164929) and ACPM (submission #164930).

## 1. Archival + DOI (citable today)

**Goal:** a permanent, versioned, citable artifact for academic and industrial reference.

- [`CITATION.cff`](CITATION.cff) makes the repository citable on GitHub and is consumed by Zenodo.
- The repository is already connected to **Zenodo**; a tagged release has minted a versioned **DOI: 10.5281/zenodo.20845322**.
- The DOI is what papers, vendor docs, and the IETF draft reference. Each release gets its own DOI; a concept DOI always points at the latest.

## 2. Academic publication (the "PhD" track)

**Goal:** peer-reviewed grounding and a citable paper.

- AREG's core contribution can be framed three ways: (a) the **agent discoverability gap** — no standard, queryable answer to "where do I find agent X, and can I trust it?" — as a measured problem; (b) AREG as a **formal registry model** (an immutable-versioned, soft-deletable entry record plus a conformance lattice over server behaviors, §I); (c) an **evaluation** — coverage analysis mapping existing ad hoc agent-catalog patterns (internal service directories, MCP server lists) onto AREG's entry fields (§D).
- Strong venues: arXiv (cs.AI / cs.MA / cs.SE) for immediate availability, then a workshop/conference on agent infrastructure, package-registry design, or interoperability.
- Reproducibility: the schema and two examples in this repository are the seed artifact appendix.

## 3. IETF Internet-Draft (standards-track legitimacy)

**Goal:** review in an open standards body and a stable, referenceable document series.

- The specification already uses RFC 2119/8174 normative keywords (Conventions & terminology), has a **Security Considerations** section (§J, mirrored in [SECURITY.md](SECURITY.md)), an **IANA Considerations** section (§K, registering `application/areg+json`), and a **References** section (§O).
- [`draft-schemacommons-areg-00.xml`](draft-schemacommons-areg-00.xml) is the xml2rfc v3 reformatting of `SPECIFICATION.md`. Run idnits, bump the draft date, then submit to the IETF datatracker; seek a home in an AI/agents or applications-area discussion, or an Independent Submission via the ISE (Independent Submissions Editor) — same path as SC-006 and SC-014.

## 4. W3C Community Group (web + semantic-web reach)

**Goal:** multi-stakeholder governance and Linked-Data alignment.

- [`context.jsonld`](context.jsonld) maps AREG terms to URIs. A **W3C Community Group** is a low-barrier home for cross-vendor participation — AREG could plausibly share a CG with SC-006's "Portable AI Agents CG" given the overlapping audience, rather than spinning up a separate group immediately.

## 5. Reference runtime + adopters (running code)

**Goal:** "rough consensus and running code" — the credibility that matters most, and the area where AREG is furthest behind AAIF and ACPM.

- AREG currently has **no reference tooling beyond the schema validator** (`tools/validate.py`, which validates registry entry documents — there is no reference REST server implementing §E to run or fork). The honest next steps, in priority order: (1) a minimal reference registry server (even an in-memory/SQLite implementation) demonstrating all four REST endpoints and the Discover conformance level; (2) a small client library that resolves an `agent_id` against a registry and verifies `signature` per §F; (3) the conformance report schema and test corpus described in [CONFORMANCE.md](CONFORMANCE.md).
- The **first independently operated registry** is recorded as a founding adopter in [ADOPTERS.md](ADOPTERS.md).

## Canonical URIs (to reserve)

| Purpose | URI |
|---------|-----|
| Standard landing page | `https://github.com/Observalytics-SL/areg` |
| Registry entry schema `$id` | `https://schemacommons.org/SC-013/registry-entry.schema.json` |
| JSON-LD context | `https://raw.githubusercontent.com/Observalytics-SL/areg/main/context.jsonld` |
| Conformance report well-known *(planned)* | `/.well-known/areg-conformance.json` |
| Media type | `application/areg+json` (registered §K) |

Schema `$id`s already resolve under `schemacommons.org/SC-013/`, matching the canonical-URI convention shared across all Schema Commons standards (SC-006, SC-013, SC-014).

## Status

AREG v0.1.0 is a **proposed** standard. DOI minted (10.5281/zenodo.20845322). IETF Internet-Draft (`draft-schemacommons-areg-00`) is content-complete but **not yet submitted** — idnits and a draft-date bump are outstanding, see §0 above. No external adopters yet; see [ADOPTERS.md](ADOPTERS.md). arXiv submission, a reference registry server, and the conformance report schema all remain pending.
