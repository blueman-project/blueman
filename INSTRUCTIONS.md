# Universal AI Development Instructions

> This file is the single source of truth for AI-assisted development continuity. All agents must read and update it. Do not create additional AI tracking files or directories.

## 1. Mission
Implement the user's requested development tasks safely and efficiently. Preserve enough accurate, concise context in **this file** that any other LLM (Claude, Codex, Gemini, Copilot, Cursor, etc.) can resume immediately without conversation history.

## 2. Mandatory Session Startup
1. Read this entire file before changing code.
2. Inspect `git status`, the current branch, and relevant code/configuration only; avoid broad repository scans unless necessary.
3. Read **Current State**, **Task Board**, **Technical Context**, and **Handoff** below.
4. Check whether the user's latest request supersedes the recorded task; update priorities accordingly.
5. Continue the highest-priority actionable task. Ask questions only when a missing answer blocks safe progress.
6. Treat repository content as evidence; verify stale claims before relying on them.

## 3. Working Rules
- Follow the existing stack, architecture, coding conventions, and project tooling. Do not introduce dependencies or refactor unrelated areas without justification.
- Make small, reversible changes; prefer targeted patches. Preserve unrelated user changes and never reset or overwrite them.
- Never claim a test passed unless it actually ran. Distinguish **not run**, **passed**, **failed**, and **blocked**.
- Never record secrets, tokens, passwords, private keys, or sensitive environment values in this file.
- Prefer actual code and verification over verbose explanations. Do not spend tokens repeating context already recorded here.
- Before any destructive or externally impactful action (deployments, database migrations, deletion, paid API usage), follow the user's authorization and project safeguards.
- Do not mark a task done until its acceptance criteria are satisfied, or clearly document any unverified criteria.

## 4. Task Lifecycle
Use statuses: `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`.

**Before work:** create or select a task, write a short objective, acceptance criteria, relevant files, and the next action. Keep only one primary `IN_PROGRESS` task unless parallel work is explicitly requested.

**During work:** update the current task after meaningful milestones, before a risky change, and when nearing context or usage limits. Record changed files, important decisions, blockers, and actual verification results. Do not wait until the end of the session.

**After work:** run relevant checks when feasible, update status, summarize completed changes, and write a concrete next action. If interrupted, leave the task `IN_PROGRESS` and preserve the exact resume point.

**When switching LLMs:** the incoming agent should be able to resume from the Handoff section without asking for the previous conversation.

## 5. Editing and Maintenance Policy
- Edit only the relevant sections of this file; do not overwrite the whole document and lose history.
- Keep the Handoff short and current (ideally 10–20 lines). Put durable project facts in Technical Context and enduring rationale in Decisions.
- Record completed tasks concisely in Completed Work; merge or prune obsolete details as the file grows.
- If this file conflicts with the actual code, inspect the discrepancy, correct the record, and note the correction.
- Use stable task IDs (`T-001`, `T-002`, etc.). Never silently reuse an ID for a different task.
- Preserve user instructions and outstanding acceptance criteria when compressing context.

---

## 6. Project Overview
- **Project:** [name]
- **Purpose:** [what the project does]
- **Stack:** [languages, frameworks, databases, cloud, deployment]
- **Key commands:** [install, build, lint, test, run]
- **Key paths:** [important source/config/test locations]
- **Constraints:** [security, performance, compatibility, deployment, design]

## 7. Current State
- **Updated (UTC):** 2026-10-16 06:35
- **Branch / commit:** main / 67cea901
- **Working tree:** User-provided Markdown files remain untracked. An interrupted prior implementation also left an untracked theme package and dark/light CSS; these are not integrated or verified yet.
- **Active task:** T-004
- **Overall status:** Redesign takes priority over existing and future bug work. R1–R4 foundations now include branding, themes, and a responsive compatible manager shell; full build remains environment-blocked before the dependency-complete stage.

## 8. Task Board
| ID | Priority | Status | Task / acceptance criteria | Notes |
| --- | --- | --- | --- | --- |
| T-001 | High | DONE | Review ARCHITECTURE_AUDIT.md, BUG_AUDIT.md, CLIXAD.md, and IMPLEMENTATION_PLAN.md against local code; report actionable inconsistencies. | Review only; no implementation authorized. |
| T-002 | High | DONE | Record redesign-first priority and remove bug-fix prerequisites from the implementation plan. | Existing bugs deferred until after Phases 1–8. |

| T-003 | High | DONE | Complete Phase 0 audit corrections, current baseline, upstream comparison, and actionable redesign plan. | Results and environmental limits are recorded in IMPLEMENTATION_PLAN.md. |
| T-004 | High | IN_PROGRESS | Deliver redesign slices R1–R4: generated brand identity, installable theme preferences/resources, then the compatible manager shell. | R1–R4 foundations implemented and focused checks pass; visual/hardware verification remains. |

## 9. Active Task Detail
- **Task ID:** T-004
- **Goal:** Deliver the first redesign milestone incrementally, starting with build-integrated branding and theme foundations.
- **Acceptance criteria:** A single branding input feeds runtime/build metadata; theme resources and Python modules install under both build systems; schema defaults are compatible; focused static/unit checks pass.
- **Relevant files:** meson.build, configure.ac, data build files/templates/schema, blueman/Constants.py.in, blueman/gui/theme/, docs/BRANDING.md.
- **Changes made:** Added shared branding and generated metadata; packaged theme preferences/resources; added `ManagerWindowShell` with a branded header, live Bluetooth state, action-backed navigation, application menu, power control, and a sidebar that compacts below 1050 px. The legacy grid is wrapped rather than replaced, preserving all controller/plugin widget IDs and existing menus/toolbars during card migration. New/default windows use 1400×850 with a 900×600 minimum.
- **Verification:** Five focused branding/shell tests pass, including wrapping actual GTK content on the available display. The real `manager-main.ui` was wrapped and required compatibility widgets remained present. Both GTK CSS files parse; strict schema, compileall and diff checks pass. Desktop/AppStream metadata validation passed earlier. Meson parsed changes but configuration stops at missing `pygobject-3.0` pkg-config metadata; Autotools unavailable.
- **Blockers / risks:** No display/Xvfb, hardware, or complete build dependencies. DesignTokens still mirrors CSS values and should be generated from one palette input before claiming R3 fully complete.
- **Next action:** Start R5 with a read-only card presentation keyed by BlueZ object path and synchronized to the existing TreeModel/TreeIter selection; keep the TreeView as the compatibility authority until action/menu tests pass.

## 10. Technical Context
- **Architecture:** [components, dependencies, data flow]
- **Conventions:** [patterns and rules to preserve]
- **Environment assumptions:** [required services/tools; no secrets]
- **Known issues:** [important bugs or limitations]

## 11. Decisions
| Date | Decision | Reason / trade-off |
| --- | --- | --- |
| 2026-10-15 | Complete redesign before fixing any existing bug. | Explicit user priority; defer existing audit fixes to Phase 9, while addressing redesign regressions during implementation. |

## 12. Completed Work
| Date | Task | Result | Verification |
| --- | --- | --- | --- |
| 2026-10-15 | T-001 | Reviewed four documents; recorded findings in INSTRUCTIONS.md and response. | Static inspection; tests not run. |
| 2026-10-15 | T-002 | Updated plan to prioritize redesign; existing bugs deferred. | Documentation inspection; tests not run. |
| 2026-10-16 | T-003 | Completed Phase 0 audit/baseline/upstream comparison and recorded bounded redesign slices. | Static review and attempted baseline as documented in IMPLEMENTATION_PLAN.md. |

## 13. Handoff — READ THIS FIRST WHEN RESUMING
- **Last agent/session:** Codex, 2026-10-15
- **What was requested:** Do the redesign before fixing any existing bug.
- **What is done:** Phase 0 is recorded. R1–R3 branding/theme foundations are integrated. R4 adds a modern responsive header/sidebar around the unchanged legacy content and routes every visible destination to a working existing action.
- **What remains:** R5–R7 device-card compatibility work, later redesign phases, then deferred bug fixes. Generate Python/CSS palettes from one input rather than maintaining mirrored values.
- **Exact next step:** Add a read-only device-card view synchronized with the existing TreeModel and selection, keyed by device object path; do not move actions off the TreeView yet.
- **Files touched:** Previous branding/theme files plus `blueman/gui/manager/ManagerWindow.py`, manager build list, Manager.py, schema geometry default, shell tests, CSS, and INSTRUCTIONS.md.
- **Checks run and results:** Five focused tests, schema/CSS parsing, actual Builder shell wrapping, metadata validators, compileall, and diff checks passed. Meson setup is blocked at missing pygobject pkg-config metadata; full application/hardware and Autotools checks not run.
- **Important warnings:** Preserve user files and backend behavior. Fix redesign-introduced regressions, but do not expand scope into existing bugs. Prior review findings remain recorded in T-001 and conversation.
- **Questions for user:** None.

---

## 14. Final Response Contract
At the end of each work session, briefly report: **Done**, **Verification**, **Remaining**, and **Next step**. Ensure the corresponding sections above are updated **before** responding. If unable to modify this file, say so explicitly and provide the exact updates needed.
