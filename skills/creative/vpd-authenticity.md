# VPD (Verifiable Proof Data) & The 5% Authenticity Injection Protocol

This skill guides OpenMontage agents in integrating **Verifiable Proof Data (VPD)** — empirical screenshots, teardown photos, telemetry graphs, patent drawings, and rights-cleared public domain evidence — into synthetic video pipelines.

## The 95/5 Authenticity Formula

AI-generated visuals (95%) provide the cinematic polish, engaging narrative, pacing, and visual entertainment.
VPD (5%) provides the undeniable empirical proof that builds absolute trust and conversion.

```
[95% Generative Polish & Storytelling] + [5% Verifiable Proof Data (VPD)] = Unassailable Authentic Authority
```

## When to Inject VPD in Pipeline Stages

### 1. Script & Scene Plan Stage (`scene_plan.json`)
- Identify **Key Evidence Beats** (e.g., turning point in an explainer, hardware teardown step, software configuration resolution, historic document reveal).
- Designate the cut type as a **Split-Screen Proof**, **Picture-in-Picture (PiP) Inset**, or **Macro Detail Cut**.
- Assign the proof asset reference using `vpd_vault`.

### 2. Asset Stage (`asset-director.md`)
- Call `vpd_vault` (`operation="search_vpd"` or `operation="harvest_public_domain"`).
- Retrieve verified, anonymized proof media with locked copyright provenance.

### 3. Composition & Editing (`edit_decisions.json`)
- Composite VPD assets with clean borders, micro-zoom motion (subtle Ken Burns), and timestamp/evidence callout badges (`[VERIFIED PROOF]`).
- Maintain strict narrative context: Present the proof as objective factual reference.

## Legal & Anonymity Safety Rules

1. **PII Elimination (Zero Identifiability)**: All personal faces, private email addresses, home IP addresses, or serial numbers MUST be redacted via `vpd_vault.redact_pii_region`.
2. **Explicit Copyright Provenance**: Every VPD item in `vpd_manifest.json` must be assigned to an approved tier (`work_for_hire_assigned`, `public_domain_cc0`, `gov_open_data`, or `internal_mining`).
3. **Third-Person Objective Stance**: Narrations referencing VPD must use objective guide framing:
   - *Prohibited*: "Look at the photo I took in my kitchen last week."
   - *Standard*: "As verified in the teardown schematic below, the pressure relief valve is seated directly behind the boiler."
