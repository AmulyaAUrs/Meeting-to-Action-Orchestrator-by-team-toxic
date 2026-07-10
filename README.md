# 📋 Meeting-to-Action Orchestrator

An AI-powered, multi-agent system that turns raw meeting notes or transcripts into
**tracked, assigned, prioritized action** — and then chases what's slipping. It
automates the single most-neglected corporate chore: **follow-through**. Built with
Cognizant's [neuro-san](https://github.com/cognizant-ai-lab/neuro-san) /
[neuro-san-studio](https://github.com/cognizant-ai-lab/neuro-san-studio) multi-agent
framework.

Paste a meeting transcript (or point it at a file / URL) and a team of specialized
agents will: extract decisions and commitments → assign owners and due dates →
prioritize and detect overcommitment → research external context → draft follow-up
emails and calendar invites → and flag **overdue** items with real date math.

> All data is synthetic or user-provided. No real, client, or PII data is used.

---

## Why it's different

Most meeting tools stop at _summarizing_. This one adds the **accountability layer**:
it persists commitments, computes what's actually overdue against today's date, and
drafts the nudges — closing the loop the way a great chief-of-staff would.

## Demonstrated agentic capabilities

| Capability                   | How this project shows it                                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Multi-agent coordination** | A `MeetingCoordinator` front-man delegates to 6 specialists via the AAOSA protocol                         |
| **Tool usage**               | 3 toolbox tools (`read_file`, `web_fetch`, `ddgs_search`) + 3 custom coded tools                           |
| **Task planning**            | `PriorityPlanner` assigns P0–P3 and produces a sequenced roadmap                                           |
| **Evaluation loop**          | `FollowUpTracker` uses a coded tool for **real** overdue detection (due date vs. today), not LLM guesswork |

---

## Prerequisites

- Python 3.11+ (developed on 3.13)
- One LLM provider API key (Anthropic Claude by default; OpenAI, Gemini, or Mistral
  also supported — see [`.env.example`](.env.example))

## Setup

```bash
# 1. Clone
git clone <your-repo-url>
cd <repo>

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key
copy .env.example .env          # Windows  (cp on macOS/Linux)
# then edit .env and set, e.g.:  ANTHROPIC_API_KEY=sk-ant-...
```

## Running the app

This project runs on the neuro-san-studio runtime, which serves the agent network
and provides the **nsflow** graph UI.

```bash
ns run
```

Then open the printed **nsflow** URL (usually `http://localhost:4173`) and select
**`meeting_to_action_orchestrator`** from the Agent Networks panel. Chat on the right;
watch the agent graph light up as each agent is called.

> Windows note: if you hit a long-path error, set a short thinking dir first:
> `set THINKING_DIR=C:\t\thinking_dir` (PowerShell: `$env:THINKING_DIR="C:\t\thinking_dir"`).

---

## Example prompts

| Goal                       | Prompt                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Full workflow**          | `Process our sprint planning notes: Priya will finish the API migration by 2026-07-05 (high priority). Raj will update docs by 2026-07-20. Priya will review the security patch by 2026-07-06 and lead the DB upgrade by 2026-07-07. Extract the action items, assign owners and due dates, store them, then tell me which are overdue and who is overcommitted.` |
| **Read a file (tool use)** | `Read the meeting notes at sample_data/sample_meeting.txt and build an executive action plan.`                                                                                                                                                                                                                                                                    |
| **Real overdue detection** | `Give me the current status of all stored action items — overdue, due soon, and missing a due date.`                                                                                                                                                                                                                                                              |
| **Workload analysis**      | `Analyze the workload across all owners and tell me exactly who is overcommitted and why.`                                                                                                                                                                                                                                                                        |
| **Comms drafting**         | `Draft follow-up emails and calendar invites for everyone based on their stored action items. Meeting title: Sprint Planning.`                                                                                                                                                                                                                                    |

---

## Project structure

```
.
├── registries/
│   ├── manifest.hocon                      # Active agent registry
│   ├── meeting_to_action_orchestrator.hocon # The 7-agent network definition
│   └── aaosa.hocon                         # Shared AAOSA delegation protocol values
├── config/
│   └── llm_config.hocon                    # Provider-agnostic LLM fallback chain
├── coded_tools/
│   └── meeting_to_action_orchestrator/
│       ├── action_item_store.py            # Persists items (sly_data) + real overdue detection
│       ├── workload_analyzer.py            # Deterministic overcommitment detection
│       └── followup_drafter.py             # Template-based emails + calendar invites
├── sample_data/
│   └── sample_meeting.txt                  # Synthetic meeting notes for the file-read demo
├── requirements.txt
├── architecture.md                         # System architecture
├── summary.md                              # Project summary + acknowledgement
├── LICENSE                                 # Apache-2.0
└── README.md                               # This file
```

---

## How it works

| Agent                | Role                                                          | Tools                    |
| -------------------- | ------------------------------------------------------------- | ------------------------ |
| `MeetingCoordinator` | Front-man orchestrator; synthesizes the executive action plan | (delegates)              |
| `IntakeAgent`        | Ingests + extracts decisions, action items, commitments       | `read_file`, `web_fetch` |
| `OwnerResolver`      | Assigns owners + due dates; persists each item                | `ActionItemStore`        |
| `PriorityPlanner`    | Ranks P0–P3; flags overcommitment                             | `WorkloadAnalyzer`       |
| `ResearchAgent`      | Enriches items with external context                          | `ddgs_search`            |
| `CalendarComms`      | Drafts follow-up emails + calendar invites                    | `FollowUpDrafter`        |
| `FollowUpTracker`    | **Real** overdue/stalled detection                            | `ActionItemStore`        |

See [architecture.md](architecture.md) and [summary.md](summary.md) for details.

---

## License

Apache-2.0. Built on [neuro-san](https://github.com/cognizant-ai-lab/neuro-san)
(Apache-2.0) by Cognizant AI Lab.
