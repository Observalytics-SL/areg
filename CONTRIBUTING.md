# Contributing to AREG

*Published by [Observalytics SL](https://github.com/Observalytics-SL) — Schema Commons initiative.*

Thank you for your interest in the Agent Registry standard. AREG is at **Proposed** status — early-stage and actively shaped by real implementation experience. Contributions from anyone deploying or experimenting with agent registries are especially valuable.

## Ways to contribute

- **Fix or clarify** the spec, schema descriptions, or examples.
- **Report a schema or API issue** — if a valid registry entry fails validation, or the REST API spec is ambiguous, that is a bug.
- **Propose a new field** or enum value (backwards-compatible additions welcomed).
- **Report an implementation** — deploy a registry against this spec and tell us what broke or was missing.
- **Register as an adopter** — add yourself to [ADOPTERS.md](ADOPTERS.md) via PR. Founding adopters help advance AREG from Proposed to Draft.

## Repo layout

```
schema/
  registry-entry.schema.json   # JSON Schema 2020-12 — the source of truth
examples/                      # valid registry entry instances
context.jsonld                 # JSON-LD context
SPECIFICATION.md               # full normative spec: schema, REST API, signing, discovery
draft-schemacommons-areg-00.xml  # IETF Internet-Draft source
tools/validate.py              # validation helper
```

## Local setup

```bash
python -m pip install jsonschema referencing
python tools/validate.py
```

## Quality bar

1. **Schema validates** — run `python tools/validate.py` before opening a PR.
2. **Examples are realistic** — use plausible agent names and registry URLs.
3. **Fields are documented** — every added property needs a `description` in the schema.
4. **No breaking changes** without a major version bump.
5. **CHANGELOG updated** — add your change to the `[Unreleased]` section of [CHANGELOG.md](CHANGELOG.md).

## REST API contributions

AREG includes a REST API specification (in SPECIFICATION.md). If your change modifies endpoint behaviour, request/response shape, or error codes, update both the schema and the API spec sections together in the same PR.

## Advancing AREG from Proposed to Draft

AREG advances when at least one public registry is deployed and tested. If you build a registry implementation against this spec, opening a PR to ADOPTERS.md and a brief issue describing your experience is the single most impactful contribution you can make.

## IETF Internet-Draft

The IETF draft (`draft-schemacommons-areg-00.xml`) is maintained by the Schema Commons Steering Council. If your schema or API change is significant enough to warrant an IETF revision, note it in your PR and it will be queued for the next draft revision. You do not need to edit the XML directly.

## Commit & PR style

- One logical change per PR.
- Title format: `areg: <short description>` — e.g. `areg: add registry_url field to publisher object`.
- Reference the relevant section of SPECIFICATION.md if applicable.

## Licence

By contributing you agree your contribution is licensed under **CC BY 4.0** (documentation and schemas) or **Apache 2.0** (tooling), matching the existing licence.
