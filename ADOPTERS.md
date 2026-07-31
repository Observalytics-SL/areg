# SC-013 AREG — Adopter Registry

This file lists organisations and projects that have declared conformance with or use of the Agent Registry (AREG, SC-013).

Listing is **self-service and free**. Add your entry via pull request. No approval required — the list is informational, not a certification.

**Honest note:** as of this writing, AREG has **no adopters**. It is a proposed standard. The table below is intentionally empty except for the template row.

---

## How to register

Add a row to the table below and open a pull request. The only requirement is that you are genuinely using AREG in some capacity (production, staging, tools, or active evaluation).

**Conformance levels** (see [SPECIFICATION.md](SPECIFICATION.md) §J):
- `Discover` — GET endpoints; entry schema validation
- `Publish` — Discover + POST/PATCH/DELETE; auth enforced
- `Signed` — Publish + signature verification on POST
- `Full` — Signed + full query parameter support and pagination

---

## Adopters

| Organisation / Project | Type | Conformance level | AREG version | Use case | Since | Link |
|------------------------|------|------------------|-------------|---------|-------|------|
| *(your entry here)* | | | | | | |

---

## Template

Copy and fill in:

```
| Acme Corp | Enterprise | Publish | 0.1.0 | Internal agent catalogue | 2026-07 | https://acme.example.com |
```

**Type options:** `Enterprise`, `Startup`, `Open source`, `Research`, `Individual`

---

## Reference implementations and tooling

If you have built a tool that implements the AREG REST API (registry server, client library, CLI), list it here:

| Tool / Library | Language | AREG version | Description | Link |
|----------------|----------|-------------|-------------|------|
| `schema-commons/validate.py` | Python | 0.1.0 | Reference schema validator | [tools/validate.py](../tools/validate.py) |
| *(your tool here)* | | | | |
