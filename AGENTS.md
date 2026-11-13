# Agent Instructions

This project uses Matt Pocock's skills, installed under `.agents/skills/` and adapted for OpenCode.

## OpenCode Adaptation

These skills were originally written for Claude Code / Codex / other harnesses. For OpenCode:

- **Slash commands do not exist.** User-invoked skills are started by asking the agent to run them by name, e.g. "run `setup-matt-pocock-skills`" or "use the `grill-with-docs` skill". The agent then calls the Skill tool with the matching `name` from the skill's frontmatter.
- **Model-invoked skills** are reached automatically by the agent when the task fits, or you can ask for them by name.
- **Subagents** are launched with the Task tool, not a harness-specific background-agent command.
- This project uses `AGENTS.md` as the primary agent instructions file (not `CLAUDE.md`).
- Skills are loaded from `.agents/skills/` via the project-level `opencode.jsonc`.

## First Run

Before using the engineering skills, run `setup-matt-pocock-skills` once per repo. It configures:

- Issue tracker (GitHub, GitLab, local markdown, or custom)
- Triage label vocabulary (if `triage` is installed)
- Domain doc layout (`GLOSSARY.md`, `docs/adr/`)

## User-Invoked Skills

Reach these by asking the agent to run them by name.

### Engineering

- **`ask-matt`** — Router. Ask which skill or flow fits your situation.
- **`grill-with-docs`** — Grilling session that also builds the project's domain model and updates `GLOSSARY.md` / ADRs.
- **`triage`** — Move issues through triage roles.
- **`improve-codebase-architecture`** — Scan for deepening opportunities and produce an HTML report.
- **`setup-matt-pocock-skills`** — Configure the repo for the engineering skills.
- **`to-spec`** — Turn the conversation into a spec and publish it to the issue tracker.
- **`to-tickets`** — Break a plan/spec into tracer-bullet tickets with blocking edges.
- **`implement`** — Build work described by a spec or tickets, driving `tdd` and `code-review`.
- **`implement-spec`** — Implement a whole spec on one integration branch using concurrent subagents.
- **`wayfinder`** — Plan a large, foggy effort as a map of decision tickets.
- **`retro`** — Suggest improvements to the agent environment after a session.

### Productivity

- **`grill-me`** — Stateless grilling session for non-code plans.
- **`handoff`** — Write a portable handoff document for another session.
- **`teach`** — Teach a concept over multiple sessions.
- **`to-questionnaire`** — Turn a decision into a questionnaire for someone else.
- **`wait-what`** — Re-pitch a message that didn't land, using `GLOSSARY.md` vocabulary.

## Model-Invoked Skills

The agent reaches these automatically, or you can ask for them by name.

- **`prototype`** — Build a throwaway prototype to answer a design question.
- **`diagnosing-bugs`** — Disciplined diagnosis loop for hard bugs.
- **`research`** — Investigate a question against primary sources as a background subagent.
- **`tdd`** — Test-driven development with red-green-refactor.
- **`domain-modeling`** — Build and sharpen the project's domain model.
- **`codebase-design`** — Shared vocabulary for designing deep modules.
- **`code-review`** — Two-axis review (Standards + Spec) in parallel subagents.
- **`pr`** — Shape a pull request body.
- **`wizard`** — Generate an interactive bash wizard for human-only steps.
- **`grilling`** — The reusable interview primitive behind `grill-me` and `grill-with-docs`.
- **`writing-for-agents`** — Reference for writing agent-readable documents.

## In-Progress / Misc Skills

These are installed but considered beta or niche:

- **`chief-of-staff`** — Orchestrate many subagents.
- **`loop-me`** — Run a stateful grilling session for workflow specs.
- **`setup-ts-deep-modules`** — TypeScript deep-module setup with dependency-cruiser.
- **`writing-beats`**, **`writing-fragments`**, **`writing-shape`** — Writing helpers.
- **`migrate-to-shoehorn`** — Migration helper.
- **`scaffold-exercises`** — Scaffold teaching exercises.
- **`setup-pre-commit`** — Set up Husky + lint-staged pre-commit hooks.

## Removed Skills

These skills are Claude-specific and were removed because they cannot work in OpenCode:

- `git-guardrails-claude-code` — Relies on Claude Code's `PreToolUse` hook system.
- `claude-handoff` — Relies on the Claude CLI's background-agent command.

## Updating

These skills were installed with `npx skills@latest add mattpocock/skills -a opencode`. To update, run the same command. Review any OpenCode-specific edits (this file, `setup-matt-pocock-skills/SKILL.md`, and `ask-matt/*`) after an update, because `npx skills` will copy fresh versions over them.

## Agent skills

### Issue tracker

Issues and specs live as GitHub issues in `ilnazix/next_offer`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` + `docs/adr/` at repo root. See `docs/agents/domain.md`.
