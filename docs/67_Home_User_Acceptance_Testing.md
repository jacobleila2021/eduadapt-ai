# Phase 11.6 — Home User Acceptance Testing (UAT)

**Product:** Leyra Wealth Intelligence System (LWIS)  
**Phase:** 11.6  
**Status:** In progress — real household validation period  
**Constraint:** Validation and QA only — no new business modules or architectural redesign.

---

## 1. Objectives

Transform Leyra from a technically complete application into a trusted daily financial companion by validating genuine household workflows over an extended period.

Success criteria:

- Real household data can be entered safely
- Daily workflows complete without data loss
- Issues are captured, triaged, and resolved locally
- Gold Master readiness improves as UAT progresses
- All UAT artefacts remain on the user's device

---

## 2. Home UAT Mode (Part 1)

**Enable:** Settings → Pilot & UAT → Enable Home UAT  
**Safety gate:** Settings → Home UAT → Real data safety → acknowledge backup  
**Badge:** Header displays **Home User Acceptance Testing** when `homeUatEnabled` is true

When active:

| Capability | Location |
|------------|----------|
| Issue logging | Header **Log issue** + Home UAT → Issues |
| Usability feedback | Pilot & UAT feedback form |
| Workflow validation | Home UAT → Workflows |
| Daily checklist | Home UAT → Daily checklist |
| Session notes | Home UAT → Daily checklist |
| Screenshot placeholders | Issue form fields |
| Session duration tracking | Automatic on app launch |

All data stored in localStorage — no telemetry.

---

## 3. Home UAT Dashboard (Part 2)

**Navigation:** Settings → Home UAT

Displays:

- Testing progress %
- Completed / outstanding workflows
- Issues raised / resolved / open / known
- Crash count (from local diagnostics)
- Average session duration
- Daily usage streak
- Overall readiness score
- Feature request and journal counts

Export: **Export full report** (JSON)

---

## 4. Daily Workflow Validation (Part 3)

22 guided workflows across expenses, banking, assets, wealth intelligence, AI, exports, backup, and platform.

Each workflow outcome:

| Outcome | Meaning |
|---------|---------|
| Pass | Workflow completed successfully |
| Issue found | Blocker or defect discovered |
| Needs improvement | Works but UX or clarity issues |
| Not applicable | Not relevant to this household |
| Pending | Not yet tested |

---

## 5. Issue Tracker (Part 4)

Each issue records:

- Title, description, module
- Severity and priority
- Steps to reproduce
- Screenshot placeholder
- Status (open, investigating, resolved, known, won't fix)
- Resolution notes
- Date discovered / resolved

---

## 6. Feature Request Log (Part 5)

Captures ideas deferred from v1 unless critical:

- Idea, reason, frequency requested
- Priority, potential module, business value

Duplicate ideas increment frequency counter.

---

## 7. Usability Journal (Part 6)

Daily narrative notes with categories:

- Confusing workflow, unexpected behaviour, slow screen
- Missing information, layout issue, accessibility
- Positive feedback, suggestions

---

## 8. Real Data Safety (Part 7)

Before acknowledging real data entry, verify:

1. Workspace backup exists
2. Recovery / checksum verified
3. Integrity audit passes
4. Privacy certification passes

User must explicitly confirm: **I have verified backup — enable Home UAT Mode**

---

## 9. Gold Master Readiness (Part 8)

Gold Master dashboard tracks UAT-derived metrics:

- Critical / major / minor bugs from issue tracker
- Usability issues from journal
- Feature requests
- Performance and accessibility observations
- Production readiness % and Gold Master UAT %

---

## 10. Daily Testing Plan

### Week 1 — Foundation

| Day | Focus |
|-----|-------|
| 1 | Enable Home UAT, safety gate, backup verify |
| 2 | Expense entry, editing, search |
| 3 | Banking, recurring payments |
| 4 | Documents, receipts |
| 5 | Net worth review |
| 6 | Workspace switching, exports |
| 7 | Weekly review — export UAT report |

### Week 2 — Breadth

| Day | Focus |
|-----|-------|
| 8–10 | Properties, vehicles, insurance |
| 11–12 | Investments, goals |
| 13 | Family Office / Executive Workspace |
| 14 | Full workflow checklist completion |

### Ongoing

- Complete daily checklist each session
- Log issues immediately when found
- Add journal notes for UX observations
- Export weekly UAT report

---

## 11. Issue Categories

| Category | Severity guidance |
|----------|-------------------|
| Data loss / corruption | Critical |
| Privacy / workspace leakage | Critical |
| Cannot complete workflow | Major |
| Incorrect calculation | Major |
| Slow performance | Minor |
| Layout / clarity | Minor / usability journal |
| Feature idea | Feature request log |

---

## 12. Acceptance Criteria

Home UAT passes when:

- [ ] All required workflows marked Pass or N/A
- [ ] Zero open critical issues
- [ ] Zero open major issues (or documented as known)
- [ ] Real data safety acknowledged
- [ ] Platform reliability checks pass (Settings → Reliability)
- [ ] Backup verified within last 7 days
- [ ] Two weeks of daily checklist completion
- [ ] Gold Master UAT readiness ≥ 85%

---

## 13. Gold Master Exit Criteria

Proceed to Phase 11.7 (Bug Fix & Stabilisation Sprint) when:

1. Home UAT acceptance criteria met
2. Full UAT report exported and reviewed
3. Feature requests triaged (none blocking v1)
4. Performance acceptable on household hardware
5. Explicit approval to enter stabilisation sprint

**Do not begin Phase 11.7 until Home UAT period is complete.**

---

## 14. Key Files

```
apps/desktop/src/platform/pilot/
  home-uat.types.ts
  home-uat-workflows.ts
  home-uat.storage.ts
  home-uat.service.ts
  home-uat-gold-master.ts
  home-uat.test.ts

apps/desktop/src/presentation/
  pilot/HomeUatBadge.tsx
  settings/pages/HomeUatDashboardPage.tsx
```

---

## 15. Verification

```bash
pnpm typecheck
pnpm --filter @leyra/desktop test
```

Manual: Settings → Home UAT — complete one workflow, log one issue, add journal entry, export report.
