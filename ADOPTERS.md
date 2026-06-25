# SC-014 ACPM — Adopter Registry

This file lists organisations and projects that have declared conformance with or use of the Agent Capability and Profile Model (ACPM, SC-014).

Listing is **self-service and free**. Add your entry via pull request. No approval required — the list is informational, not a certification.

**Honest note:** as of this writing, ACPM has **no adopters**. It is a brand-new proposed standard. The table below is intentionally empty except for the template row.

---

## How to register

Add a row to the table below and open a pull request. The only requirement is that you are genuinely using ACPM in some capacity (production, staging, tools, or active evaluation).

**Conformance levels** (see [SPECIFICATION.md](SPECIFICATION.md) §I):
- `Basic` — validates against the schema; `subject` present
- `Tooled` — Basic + `capabilities[]` non-empty
- `Trusted` — Tooled + `trust.level` ∈ {verified, attested, enterprise}
- `Priced` — Trusted + `cost_profile` present
- `Enterprise` — Priced + `sla` + `compliance` + `provenance.signature`

---

## Adopters

| Organisation / Project | Type | Conformance level | ACPM version | Use case | Since | Link |
|------------------------|------|------------------|-------------|---------|-------|------|
| *(your entry here)* | | | | | | |

---

## Template

Copy and fill in:

```
| Acme Corp | Enterprise | Trusted | 1.0.0 | Capability profiles for 6 internal agent platforms | 2026-07 | https://acme.example.com |
```

**Type options:** `Enterprise`, `Startup`, `Open source`, `Research`, `Individual`

---

## Reference implementations and tooling

If you have built a tool that reads or writes ACPM documents (validator, capability matcher, registry integration), list it here:

| Tool / Library | Language | ACPM version | Description | Link |
|----------------|----------|-------------|-------------|------|
| `schema-commons/validate.py` | Python | 1.0.0 | Reference schema validator (shared across all Schema Commons standards) | [tools/validate.py](../tools/validate.py) |
| *(your tool here)* | | | | |

---

## Wanted: first adopters

We are actively seeking the **first three independent adopters** of ACPM — whether you're publishing a profile for your own agent/platform/tool/model, or building a registry/orchestrator that consumes profiles for capability matching or trust gating. If interested, please open an issue titled `[Adoption] <Project name>`. We will:

- Help map your existing capability/trust/cost documentation to ACPM fields
- Co-author the conformance report schema with you if you need it before it ships generally (see [CONFORMANCE.md](CONFORMANCE.md))
- Credit your project as a founding adopter

Especially interested in: registries and marketplaces that already list agents/platforms/tools (a natural place for ACPM profiles to plug in), and any SC-006 AAIF or SC-013 ARP adopter looking to add comparable capability/trust/cost data to their existing listings.
