# Project Summary — Meeting-to-Action Orchestrator

**Team:** Toxic | **Track:** Track 2 — Vibing + Grounding
**Framework:** Cognizant neuro-san / neuro-san-studio (Apache-2.0)
**LLM:** Anthropic Claude (`claude-sonnet-4-5`), provider-agnostic config

---

## 1. Problem

Corporate meetings are where decisions are made — and where accountability quietly
dies. A large share of action items agreed in meetings are never tracked, never
assigned a clear owner, or silently miss their deadline. Teams now have plenty of
tools that _transcribe_ and _summarize_ meetings, but almost none that close the loop
on **follow-through**: who owns what, by when, what is now overdue, and who is
overloaded. That last mile — the chasing, the nudging, the status-keeping — still
lands on a human chief-of-staff or manager and is the single most-neglected chore in
corporate life.

This is a universal, high-value pain, and it maps naturally onto what multi-agent AI
does well: parallel extraction, specialized reasoning, planning, and coordination.

## 2. Solution overview

The **Meeting-to-Action Orchestrator** is a team of AI agents, built on neuro-san,
that runs the entire meeting-to-accountability pipeline. A user provides meeting
content — pasted text, a local file path, or a URL — and a front-man agent
(`MeetingCoordinator`) coordinates six specialists via the AAOSA delegation protocol
to turn that raw content into a tracked, prioritized, owner-assigned action plan, and
then to flag exactly what is slipping.

The pipeline:

1. **Ingest & extract** — `IntakeAgent` uses the `read_file` / `web_fetch` tools to
   read the meeting content (including PDFs) and extracts decisions, action items, and
   verbal commitments.
2. **Assign & persist** — `OwnerResolver` determines an owner and due date for each
   item and stores it via the `ActionItemStore` coded tool.
3. **Prioritize & balance** — `PriorityPlanner` ranks tasks P0–P3 and calls the
   `WorkloadAnalyzer` tool to deterministically flag overcommitted people.
4. **Enrich** — `ResearchAgent` uses `ddgs_search` to add external context such as
   typical timelines, standards, or compliance considerations.
5. **Communicate** — `CalendarComms` calls the `FollowUpDrafter` tool to produce
   per-owner follow-up emails and calendar invites from the tracked tasks.
6. **Hold accountable** — `FollowUpTracker` calls `ActionItemStore` (status mode),
   which compares each item's due date to today and returns real overdue, due-soon,
   and missing-due-date buckets with exact day counts.

The `MeetingCoordinator` then synthesizes an executive-ready action plan: executive
summary, prioritized actions, research insights, communication plan, and risk flags.

## 3. Why it is novel

- **Accountability, not just summaries.** Most tools stop at "here's what was said."
  This system persists commitments and actively surfaces what's slipping — the rare,
  genuinely useful part of the workflow.
- **A real evaluation loop.** Overdue and overcommitment findings are computed in
  Python by comparing due dates to today's date — accurate and reproducible, not
  hallucinated. In testing, the system returned exact day counts (e.g. 908, 906, 905
  days overdue) and per-owner cumulative overdue totals.
- **A true multi-agent org chart.** Seven agents with a front-man delegating via
  AAOSA, each with a scoped role and its own tools — not one agent with a pile of
  prompts.

## 4. How it uses neuro-san (framework features)

| Feature                   | Usage in this project                                                                      |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| AAOSA adaptive delegation | Run-time, agent-decided routing across 7 agents                                            |
| Toolbox tools             | `read_file`, `web_fetch`, `ddgs_search` ground agents in real files, web pages, and search |
| Custom coded tools        | `ActionItemStore`, `WorkloadAnalyzer`, `FollowUpDrafter` add deterministic logic           |
| `sly_data` state          | Action items persist out-of-band and are shared across agents within a session             |
| LLM fallback config       | One network runs on Anthropic, OpenAI, Gemini, or Mistral via the shared config            |

## 5. Fulfilment of required agentic capabilities

| Capability                   | Where it is demonstrated                                              |
| ---------------------------- | --------------------------------------------------------------------- |
| **Multi-agent coordination** | AAOSA front-man delegation across 7 agents                            |
| **Tool usage**               | 3 toolbox tools + 3 custom coded tools                                |
| **Task planning**            | `PriorityPlanner` P0–P3 ranking + sequenced roadmap                   |
| **Evaluation loops**         | `FollowUpTracker` + `ActionItemStore` status — real overdue detection |

## 6. Architecture at a glance

```
User (notes / file / URL)
        │
        ▼
MeetingCoordinator ──► IntakeAgent ──► read_file / web_fetch
        │           ──► OwnerResolver ──► ActionItemStore ──┐
        │           ──► PriorityPlanner ──► WorkloadAnalyzer │  sly_data
        │           ──► ResearchAgent ──► ddgs_search        │ (action_items)
        │           ──► CalendarComms ──► FollowUpDrafter ───┤
        │           ──► FollowUpTracker ──► ActionItemStore ─┘
        ▼
Executive action plan (owners, priorities, overdue, risks)
```

Agents are LLM-driven; the tools are deterministic Python (custom) or studio-provided
(toolbox). Action items live in `sly_data`, giving every agent one shared source of
truth. See `architecture.md` for full sequence and topology diagrams.

## 7. Impact and scalability

The design is production-shaped: every synthetic or local tool is a drop-in seam for a
real enterprise integration.

| Tool                      | Production equivalent                                |
| ------------------------- | ---------------------------------------------------- |
| `read_file` / `web_fetch` | Otter/Zoom transcript export, Confluence, SharePoint |
| `ActionItemStore`         | Jira / Asana / a task database                       |
| `WorkloadAnalyzer`        | Capacity data from the task system                   |
| `FollowUpDrafter`         | Outlook / Google Calendar + email APIs               |
| `ddgs_search`             | Enterprise search / internal knowledge base          |

Because orchestration is declarative HOCON, the pattern scales to any team and extends
easily with new specialists (e.g. a `RiskAssessor` or `BudgetChecker`). The realistic
business impact is turning the post-meeting scramble — often days of manual chasing —
into seconds of automated, auditable follow-through, directly improving delivery
predictability and reducing dropped commitments.

## 8. Running the project

```bash
pip install -r requirements.txt
copy .env.example .env        # set ANTHROPIC_API_KEY
ns run                        # open the nsflow UI (http://localhost:4173)
```

Select `meeting_to_action_orchestrator`, then try:
_"Read the meeting notes at sample_data/sample_meeting.txt, extract the action items,
assign owners and due dates, store them, then tell me which are overdue and who is
overcommitted."_

## 9. Data and compliance

All content used is **synthetic or user-provided**. The project contains no real,
client, or personally identifiable data, no credentials, and no restricted material,
in line with the hackathon rules and Cognizant policy.

## 10. Tech stack

Python 3.13 · neuro-san / neuro-san-studio (multi-agent orchestration + nsflow UI) ·
Anthropic Claude / OpenAI / Gemini / Mistral (LLM providers, via fallback config).

---

## Terms and Conditions / Participant Acknowledgement

By submitting this project, I confirm and agree that:

1. My submission follows the hackathon rules and uses neuro-san as required.
2. My project does not include any client data, confidential information, restricted
   material, credentials, access keys, or policy-sensitive content.
3. I have used only open-source, public, or synthetic data/materials, and I am
   responsible for complying with applicable licenses and corporate policies.
4. My submission has been developed ethically and does not promote harmful, unsafe,
   unlawful, discriminatory, or policy-violating use cases.
5. I am responsible for ensuring that my GitHub repository, ZIP file, documentation,
   and demo video are complete, accessible, and submitted in the required format
   before the deadline.
6. Submissions that are incomplete, inaccessible, incorrectly formatted, or do not
   follow the rules may not be evaluated.
7. The organizers' and judges' decisions on evaluation, ranking, prizes, and
   recognition will be final and binding.
8. The organizers reserve the right to modify rules, timelines, evaluation criteria,
   or prizes if required, with reasonable notice where practical.
9. The organizers are not responsible for any policy, data, licensing, intellectual
   property, or compliance violations arising from my submission.
