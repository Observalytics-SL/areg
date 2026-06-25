# AREG Changelog

## v0.1.0 — 2026-06-25 (Proposed)

Initial proposed release of the Agent Registry (AREG) standard, Schema Commons SC-013.

### What is defined

- `registry-entry.schema.json` — JSON Schema 2020-12 document format for a published AAIF agent registry entry. Fields: `sc_standard`, `sc_version`, `registry_id`, `agent_id`, `agent_version`, `published_at`, `updated_at`, `publisher` (name, url, public_key_url, contact), `aaif_url`, `signature` (JWS), `tags`, `conformance_level`, `required_capabilities`, `acpm_profile_url`, `yanked`, `yank_reason`, `license`.
- `context.jsonld` — JSON-LD context mapping AREG terms to `schema.org` and the `areg:` vocab namespace at `schemacommons.org/SC-013/vocab#`.
- Two validated examples: `invoice-chaser-entry.json`, `research-summarizer-entry.json`.
- `tools/validate.py` — Python 3 validator for examples against the schema.
- REST API outline in SPECIFICATION.md.

### Known gaps (to be resolved before Draft)

- Signing model not yet normative (JWS structure TBD).
- REST API endpoints specified at outline level only; authentication model (API key / OAuth / signed request) TBD.
- No reference registry implementation.
- Search/filter query language not yet specified beyond URL parameters.
- Pagination and cursor model for `/v1/agents` not yet specified.
