# Phase 11.8A — Internal Release Candidate (RC2)

**Product:** Leyra Wealth — Personal Wealth Intelligence System (PWIS)  
**Version:** 1.0.0-rc.2  
**Schema:** 035  
**Status:** Internal Release Candidate — production build validation  
**Precedes:** Phase 11.9 — Production Packaging, Installer Creation & Version 1.0 Release

---

## Purpose

Phase 11.8A proves that Leyra behaves exactly like a production application when built in production mode. This is **not** a feature phase. No new modules, schema, AI capabilities, UI surfaces, reports, or platform services were introduced.

The deliverable is **Internal RC2** — suitable for Home User Acceptance Testing and installer creation, pending Go/No-Go approval.

---

## Validation Checklist

### Part 1 — Production Build

| Check | Method | Expected |
|-------|--------|----------|
| Production mode enabled | `validateProductionBuild()` | `import.meta.env.DEV === false` |
| No development configuration | Vite `build.minify` without `TAURI_DEBUG` | Minified bundle |
| Environment variables validated | `VITE_BUILD_NUMBER`, `VITE_GIT_COMMIT` injected in `vite.config.ts` | Present at build time |
| Version embedded | `RELEASE_METADATA.version` | `1.0.0-rc.2` |
| Schema version embedded | `EXPECTED_SCHEMA_VERSION` | `035` |
| Build identifier generated | `getBuildInfo().buildNumber` | `YYYYMMDD.rc2` or CI override |

### Part 2 — Development Surfaces Removed

The following are **not** in `PRODUCTION_ROUTE_MANIFEST` and are gated behind `isReleaseReadinessVisible()` (dev builds only):

| Surface | Production status |
|---------|-------------------|
| Developer Sandbox | Hidden (`isDeveloperFeaturesVisible`) |
| Design Showcase | Hidden |
| Accessibility Verification pages | Dev-only module |
| Platform Diagnostics (Settings → Reliability) | Dev-only route |
| Developer Settings | Dev-only route |
| Developer banners / schema badge / module counters | `IS_DEV_MODE` gated in `App.tsx` |
| Pilot & UAT / Home UAT / Gold Master settings | Removed from production manifest |
| Debug panels / verbose traces | Production empty states |

Validated by `validateProductionSurfaces()`.

### Part 3 — First Run Validation

| Check | Validator |
|-------|-----------|
| Application launches | Manual + DB ping |
| Database created automatically | `core_app_meta` probe |
| Personal Workspace created | Workspace registry |
| Demo Workspace available | Registry `demo` workspace |
| Workspace switching | ≥2 workspaces |
| Theme / settings / window persistence | localStorage infrastructure |

### Part 4 — Full Workflow Validation (Demo Workspace)

`validateDemoWorkspaceWorkflows()` probes module tables and routes for:

Expenses, Assets, Property, Vehicles, Investments, Banking, Insurance, Estate, Business, Retirement, Goals, Philanthropy, Family Office, Executive Workspace, Ask Leyra, Digital Twin, Multimodal, Search, Command Palette, Reports, Documents, Relationships, Reminders, Notifications, Backups, Restore, Gold Master readiness.

### Part 5 — Stability Test

`runStabilityValidation()` simulates:

- 5× repeated startup (DB ping)
- 10× workspace switch (metadata queries)
- 3× export (large table reads)
- 8× search queries

### Part 6 — Performance Validation

`runRc2PerformanceSummary()` uses `runPerformanceProfile('micro')`:

| Metric | Threshold |
|--------|-----------|
| Database ping (cold proxy) | ≤ 5000 ms |
| Expense count query | ≤ 2000 ms |
| Document search | ≤ 2000 ms |
| Dashboard net worth cache | ≤ 3000 ms |
| Family Office aggregation | ≤ 5000 ms |
| AI context preparation | ≤ 4000 ms |
| JS heap memory | ≤ 512 MB |

### Part 7 — Automated Validations (RC2 Report)

`generateInternalRc2Report()` aggregates:

- Navigation validation (`validateProductionNavigation`)
- Integrity audit (`runIntegrityAudit`)
- Privacy certification (`generatePrivacyCertification`)
- Accessibility smoke + certification record
- Gold Master readiness (`runFinalReadinessReview`)

Export: **Settings → About → Export Internal_RC2_Report.json** (dev builds) or programmatic API.

### Part 8 — Go / No-Go

Single recommendation in report:

- **READY FOR INSTALLER CREATION** — all pass/fail gates green
- **FURTHER STABILISATION REQUIRED** — blockers listed in `recommendationReasons`

---

## Architecture

```
platform/internal-rc2/
├── internal-rc2.types.ts          # RC2 version, surface lists, report types
├── production-build.validation.ts # Build metadata checks
├── production-surface-guard.ts    # Dev surface accessibility audit
├── first-run.validation.ts        # Startup and workspace checks
├── workflow-validation.ts         # Demo workspace module probes
├── internal-rc2.service.ts        # Stability, performance, report orchestration
├── internal-rc2.test.ts           # Automated RC2 tests
└── index.ts
```

**Key decisions:**

1. **Internal routes removed from manifest** — production navigation and command palette cannot reach Pilot, Home UAT, Reliability, or Gold Master settings.
2. **`isReleaseReadinessVisible()` restricted to dev builds** — stale `homeUatEnabled` localStorage cannot expose internal tools in production.
3. **RC2 version constant** (`INTERNAL_RC2_VERSION = 1.0.0-rc.2`) separate from Gold Master target (`1.0.0`) to preserve certification semantics.
4. **Build metadata at compile time** — `vite.config.ts` injects build number and git commit for reproducible RC2 reports.

**Trade-offs:**

- Workflow validation uses **table probes** rather than full UI automation — faster, deterministic in CI, but does not replace manual Home UAT.
- Performance metrics use **micro profile** proxies — representative, not full cold-start UI measurement on device.
- RC2 export button visible only in dev builds to avoid confusing production users.

---

## Known Issues

- RC2 report generated in **development mode** will warn that production build validation cannot pass until `vite build` / `tauri build` is executed.
- Accessibility certification record must be present for full a11y gate pass (same as Gold Master).
- Open UAT issues appear in `knownIssues` when triage queue is non-empty.

---

## Verification Commands

```bash
pnpm typecheck
pnpm --filter @leyra/desktop test
pnpm --filter @leyra/desktop build
```

---

## Go / No-Go Recommendation

**Awaiting production build execution and manual sign-off.**

After running `pnpm --filter @leyra/desktop build` and exporting `Internal_RC2_Report.json` from a production build:

- If `recommendation` is **READY FOR INSTALLER CREATION** → approve Phase 11.9.
- If **FURTHER STABILISATION REQUIRED** → resolve blockers before installer work.

---

## Related Documents

- [`69_Gold_Master_Certification.md`](./69_Gold_Master_Certification.md)
- [`68_Gold_Master_Stabilisation.md`](./68_Gold_Master_Stabilisation.md)
- [`67_Home_User_Acceptance_Testing.md`](./67_Home_User_Acceptance_Testing.md)
- [`00_Project_Constitution.md`](./00_Project_Constitution.md)
