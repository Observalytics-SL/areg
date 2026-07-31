# Security Policy — ACPM (SC-014)

ACPM is a data-format standard for describing capability, trust, cost, and SLA claims about AI agents, platforms, tools, and models. It carries no executable content itself, but the claims it carries are used by other systems (orchestrators, registries, marketplaces) to make trust and dispatch decisions. Security is therefore in scope for the **specification's claim model**, even though there is no reference tooling yet to attack directly.

## Reporting a vulnerability

- **Specification weaknesses** (a construct that invites a false sense of assurance, an under-specified MUST, a missing guardrail): open a public issue titled `[security] SC-014: <summary>` so it can be discussed and corrected in the open.
- **Future reference tooling**, once it exists: report privately to **security@observalytics.com**. (As of this writing there is no ACPM-specific tooling beyond the shared schema validator, so this path is forward-looking.)

Please include: affected field/section or version, a minimal reproducing ACPM document or scenario, and the impact you observed.

## Threat model (normative references in SPECIFICATION §F, §G)

ACPM's central security property is also its central limitation: **it is a claims format, not a verification protocol.** Consumers MUST treat every field in a profile as a self-reported claim by the subject (or whoever published the profile on the subject's behalf) unless they independently verify it.

| Threat | Mitigation required of the *consumer* (ACPM itself does not enforce this) |
|--------|------------------------------------------------------------------------|
| **Overstated trust level** | A profile can claim `trust.level: "enterprise"` with no backing evidence. Consumers gating on trust level MUST check `trust.attestation.evidence_url` and SHOULD require a verifiable attestation (third_party or formal_audit) before relying on `attested`/`enterprise` claims for consequential decisions. |
| **Overstated or fabricated capability support** | `capabilities[].support: "native"` is asserted, not tested. Consumers performing capability matching for safety-relevant features SHOULD independently probe the subject (e.g. a smoke test) before trusting a `native` claim at face value. |
| **Stale or falsified cost/SLA claims** | `cost_profile` and `sla` are point-in-time, unverified claims (§G). A subject can publish an attractive `sla.uptime_pct` it does not actually meet. ACPM has no field distinguishing "committed" from "observed" figures (a known gap, see CHANGELOG.md) — consumers making procurement or routing decisions SHOULD corroborate SLA claims against independent monitoring where the decision is consequential. |
| **Unverified or absent signature** | `provenance.signature` is advisory: ACPM does not mandate a signature scheme, key distribution, or verification step. A profile without a verifiable signature SHOULD be treated as `trust.level: "untrusted"` regardless of what `trust.level` it self-declares, by any consumer that requires provenance assurance. |
| **Delegation rule bypass via unsupported Condition `lang`** | A `delegation_rules[].condition` naming a `lang` the consumer does not implement MUST be treated as unsatisfiable-unknown (apply the conservative default — deny outbound, reject inbound) rather than silently treated as `allow`. Silent fallback to `allow` is a conformance violation. |
| **Stale `attestation.expires_at`** | Consumers MUST check expiry before relying on an attestation; ACPM does not auto-invalidate expired attestations — the profile's `trust.level` field is not automatically downgraded when `expires_at` passes. |
| **Profile/subject mismatch** | Nothing in ACPM cryptographically binds a profile to the real-world subject it claims to describe (beyond the advisory `sc_refs[]` cross-reference). A malicious actor could publish a profile claiming to describe a well-known agent/platform. Consumers SHOULD only trust profiles obtained from a channel they already trust (the subject's own domain, a registry they trust) rather than an arbitrary URL. |

## Scope

In scope: the schema, the normative specification, and this repository's examples. Out of scope: any third-party tooling that produces or consumes ACPM profiles (report issues to their own maintainers), and the actual trustworthiness of any specific subject described by a profile (ACPM describes the claim format, not the subject).

## Disclosure

We follow coordinated disclosure. Reporters acting in good faith will be credited in the advisory unless they request otherwise.
