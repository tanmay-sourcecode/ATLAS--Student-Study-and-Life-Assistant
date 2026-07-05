# Atlas — Your AI Student Chief of Staff

> A multi-agent study-and-life assistant that helps university students plan their week, understand course materials, and communicate with instructors — grounded in their own documents, private by design, and always under the student's control. Built on Google's Agent Development Kit (ADK), developed in Antigravity.

**Capstone track:** Agents for Good · **Demo video:** _[your YouTube link]_ · **Live demo (optional):** _[URL or "run locally — see below"]_

**Key concepts:** Multi-agent system (ADK) · Agent skills · Antigravity · MCP · *bonus:* RAG, Security/PII

---

## What's New in This Version

This section summarizes the changes added since the initial build, and why.

- **Real MCP tool integrations (Google Maps, Calendar, Gmail).** Added `google_tools.py` at the project root — six real-world tools the agents call **on their own** during a normal terminal chat (no manual switch). Maps answers "how do I get to campus and how long?"; Gmail can search mail and create drafts; Calendar can list/create events.
- **Autonomous tool use in the terminal.** The Scheduler agent now carries the Maps tools and the Comms agent carries the Gmail tools. Because each tool's docstring says *when* to use it, the model selects and calls the right one automatically inside `app.py` — the same terminal experience, now with more powers.
- **MCP server folder renamed `mcp/` → `mcp_server/`.** The old name clashed with the installed `mcp` pip package (Python imported the local folder instead of the library, so the server couldn't start). Renaming fixed it. Run it with `python -m mcp_server.server`.
- **MCP server now exposes 8 tools** (was 2): `document_search`, `tasks_list`, plus the four Google Maps/Calendar and two Gmail tools — all wired to the project's real functions (`rag.retrieve.retrieve`, `tools.get_tasks`).
- **One-command launcher: `run.sh`.** Always runs the project with the Python 3.11 virtual environment (never the system 3.9, which breaks `chromadb`/`mcp`). Use `./run.sh`.
- **OAuth helper: `google_oauth_setup.py`.** One-time script that authorizes Calendar + Gmail and saves a private `token.json` (git-ignored). No credentials ever live in code.

See [MCP Server](#mcp-server) and [MCP Tool Setup](#mcp-tool-setup-maps--calendar--gmail) for details.

---

## Table of Contents
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running Atlas](#running-atlas)
- [Agent Skills](#agent-skills)
- [MCP Server](#mcp-server)
- [MCP Tool Setup (Maps / Calendar / Gmail)](#mcp-tool-setup-maps--calendar--gmail)
- [RAG Pipeline](#rag-pipeline)
- [Security & Privacy](#security--privacy)
- [Testing](#testing)
- [Concept Mapping](#concept-mapping)
- [Roadmap](#roadmap)

---

## The Problem

A university student coordinates a huge, fragmented workload alone: lectures across many courses, deadlines scattered across portals, group projects, exams, readings, and often a job. Executives get a chief of staff for far less; students get a planner app they abandon by week three. The result — missed deadlines, all-nighters, and burnout — hits first-generation, working, and neurodivergent students hardest. Existing tools are passive: they store information but don't plan, act, or remember.

## The Solution

**Atlas** is an AI chief of staff for students — a multi-agent system that reads course materials, tracks deadlines, plans study time, drafts academic communication, and helps with everyday logistics (like getting to campus) — always with the student's approval before anything is sent. It turns fragmented academic work into one coordinated, private system.

---

## Architecture

Atlas is a hierarchical multi-agent system on Google ADK. A central Orchestrator classifies intent and routes to one specialist agent, then composes the reply. Sensitive actions pass through a human-in-the-loop approval gate. Real-world actions (Maps, Calendar, Gmail) are shared tools that the agents call autonomously and that are also exposed through a Model Context Protocol (MCP) server.

```
                 Student (terminal chat — ./run.sh)
                          │
                 ┌────────▼─────────┐
                 │  ORCHESTRATOR    │  classify intent → delegate
                 │  (Chief of Staff)│  approval gate on sensitive actions
                 └───┬───┬───┬───┬──┘
        ┌────────────┘   │   │   └────────────┐
        ▼                ▼   ▼                ▼
   Scheduler        Study(RAG)   Comms         Memory
   classes/         summarize/   email +       durable prefs
   deadlines/       study plans  Gmail         (PII-redacted)
   study blocks +   w/ citations (never sends)
   Maps tools
        └───────────────┬────────────────┘
                        │  (same functions also exposed via MCP)
                ┌───────▼────────┐
                │   MCP SERVER   │  document_search · tasks_list
                │ (mcp_server/)  │  maps · calendar · gmail
                └────────────────┘
             Security: approval gate · PII redaction · audit log
```

| Agent (file) | Responsibility |
|---|---|
| Orchestrator (`orchestrator/agent.py`) | Intent classification, routing, reply synthesis, approval gating |
| Scheduler (`agents/scheduler.py`) | Classes, deadlines, assignments (CRUD), exam dates, study blocks, conflict detection, revision-aware scheduling, proactive task reminders, **and getting around (Maps travel time / find nearby)** |
| Study (`agents/study.py`) | RAG summaries, key concepts, study plans, grounded answers w/ citations, spaced-repetition revision reminders |
| Comms (`agents/comms.py`) | Drafts academic emails/messages (never sends) **and can search the student's Gmail** |
| Memory (`agents/memory.py`) | Durable student prefs, PII-minimized, separate from session context |

> Replace this ASCII diagram with `docs/architecture.png` for the media gallery.

---

## Features

- **Weekly planning** with focus-block suggestions and conflict detection.
- **Deadline tracking** prioritized by urgency and workload.
- **Document summarization & RAG** over syllabi/slides/notes, with citations.
- **Study-plan generation** for exams and finals.
- **Academic email drafting** with an approval gate.
- **Long-term memory** for student preferences (PII-safe).
- **Multi-agent coordination** via clear tool interfaces + an MCP server.
- **Google Maps tools** *(new)*: travel/commute time between two places and finding nearby study spots (e.g. libraries) — auto-invoked when the student asks how to get somewhere.
- **Google Calendar tools** *(new)*: list upcoming events and create events (behind the approval gate).
- **Gmail tools** *(new)*: search recent mail and create drafts (never auto-sends).
- **Pomodoro Focus Timer**: Guides study focus blocks (25-min focus / 5-min breaks), logs completed cycles, and tracks focus statistics.
- **Active-Recall Q&A Generator**: Generates practice question-and-answer pairs from RAG documents and conducts interactive conversational quizzes.
- **Smart Revision Reminders**: Tracks studied topics with spaced-repetition scheduling (2 → 5 → 10 → 17 → 24 days), surfaces concise micro-summaries of overdue lessons, and merges new topic suggestions from course files to keep study sessions fresh and non-monotonous.
- **To-Do List & Task Reminders**: Provides proactive reminders at session start separating tasks into Overdue (🔴), Urgent (🟡), and Upcoming (🟢). Supports complete task modification controls (editing properties, deleting tasks) secured behind approval gates.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Agent framework | Google Agent Development Kit (ADK) |
| LLM | Claude (Anthropic API) or Gemini — selected at runtime by `get_model()` based on which key is set; developed in Google Antigravity |
| Skills | Anthropic-style `SKILL.md` folders w/ progressive disclosure |
| Tool protocol | Model Context Protocol — internal (`document_search`, `tasks_list`) + Google Maps, Calendar, Gmail |
| Retrieval | RAG — chunking, top-k, grounded answers with citations |
| Interface | CLI (ADK Runner), launched via `./run.sh` |
| Language | Python 3.11+ |

---

## Project Structure

```
ATLAS--Student-Study-and-Life-Assistant/
├─ README.md
├─ run.sh                     # one-command launcher (uses the 3.11 venv)
├─ .env                       # secrets (git-ignored) — you create this
├─ requirements.txt
├─ app.py                     # CLI entry point (ADK Runner)
├─ google_tools.py            # NEW: shared Google Maps/Calendar/Gmail tools
├─ google_oauth_setup.py      # NEW: one-time Calendar+Gmail authorization
├─ docs/                      # design docs, diagrams
├─ orchestrator/
│  ├─ agent.py                # root agent + routing
│  └─ prompts.py              # system prompts for orchestrator + specialists
├─ agents/
│  ├─ scheduler.py            # + Maps tools
│  ├─ study.py                # RAG-backed
│  ├─ comms.py                # + Gmail tools
│  └─ memory.py
├─ skills/                    # SKILL.md folders (progressive disclosure)
│  ├─ daily_brief/  study_plan/  assignment_breakdown/  email_draft/
│  ├─ document_summary/  deadline_checkin/  pomodoro/  qa_generator/
│  └─ revision_reminder/  task_reminder/
├─ skills_runtime.py          # loads a skill's SKILL.md on demand
├─ tools.py                   # calendar/tasks/email/pomodoro/study/RAG helpers
├─ mcp_server/                # RENAMED from mcp/ (avoids clash with pip 'mcp')
│  └─ server.py               # MCP server: 8 tools (internal + Maps/Calendar/Gmail)
├─ rag/
│  ├─ ingest.py               # ingest uploaded docs
│  └─ retrieve.py             # retrieve(query, top_k) grounded retrieval
├─ security/                  # approval gate, PII redaction, audit log
├─ demo_data/                 # sample syllabus / notes / assignments
└─ tests/                     # router, skills, rag, approval, pomodoro, qa, revision, tasks
```

---

## Getting Started

### Prerequisites
- **Python 3.11+** (the system Python 3.9 on macOS is NOT enough — `chromadb` and `mcp` require 3.10+)
- An Anthropic API key (or a Google/Gemini key)
- *(optional, for MCP tools)* a Google Maps API key and Google OAuth credentials

### Install
```bash
# create the venv with Python 3.11 (via pyenv, adjust if you use Homebrew)
~/.pyenv/versions/3.11.9/bin/python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## Configuration

**Never commit secrets.** Create a `.env` file in the project root:

```env
# Required — one of these (get_model picks the provider automatically)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# or: GOOGLE_API_KEY=your_gemini_api_key_here

# Optional — only for the MCP tools you use
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here   # Maps tools
GOOGLE_OAUTH_CREDENTIALS=credentials.json           # Calendar + Gmail (OAuth client file)
GOOGLE_TOKEN_PATH=token.json                         # where the OAuth token is saved
```

`.env`, `credentials.json`, and `token.json` are git-ignored. Confirm before your first push:
```bash
git ls-files | grep -E "\.env$|token.json|credentials.json"   # should print nothing
```

---

## Running Atlas

Atlas runs as a command-line chat loop. Use the launcher so it always runs on Python 3.11:

```bash
./run.sh
```

> Why `./run.sh` and not `python app.py`? On macOS `python3` points at the system Python 3.9, which breaks `chromadb`/`mcp`. `run.sh` always uses `.venv/bin/python` (3.11). If you prefer, `source .venv/bin/activate` then `python app.py` works too.

Try, right in the terminal:
- `What should I focus on this week?`
- `Summarize the CS201 syllabus for exam prep`
- `Build me a study plan for finals`
- `Draft an email to my professor asking for a two-day extension` *(shows the approval gate)*
- `I'm new here — how do I get to my university and how long will it take?` *(auto-calls the Maps tool)*
- `Did my professor reply about the extension?` *(auto-calls Gmail search)*

---

## Agent Skills

Skills are reusable procedures built the Anthropic way — each is a folder with a `SKILL.md` (YAML frontmatter: `name`, `description` + markdown instructions). Loading is three-level (**progressive disclosure**): metadata always in context, the SKILL.md body only when the skill triggers (loaded via `get_skill_instructions`), bundled scripts only when needed. This keeps behavior consistent **and** keeps token usage/cost low.

Skills: `daily_brief`, `study_plan`, `assignment_breakdown`, `email_draft`, `document_summary`, `deadline_checkin`, `pomodoro`, `qa_generator`, `revision_reminder`, `task_reminder`.

---

## MCP Server

`mcp_server/server.py` is a Model Context Protocol server that exposes Atlas's capabilities as standardized, inspectable tools any MCP-compatible client (including Atlas's own agents) can call. The Google tool *logic* lives in `google_tools.py`, so the exact same functions power both this server and the agents.

**Tools exposed (8):**

- **Internal:** `document_search` (RAG over uploaded docs → grounded, cited), `tasks_list` (open assignments).
- **Google Maps:** `maps_travel_time`, `maps_find_nearby`.
- **Google Calendar:** `google_calendar_list`, `google_calendar_create` *(write — behind approval)*.
- **Gmail:** `gmail_search`, `gmail_create_draft` *(draft only — never sends)*.

Run the server:
```bash
.venv/bin/python -m mcp_server.server
```
It runs over stdio and waits for a client (so the terminal appears to "hang" — that's normal; `Ctrl+C` to stop).

**Inspect/test it** with the MCP Inspector (a client UI to list and call tools):
```bash
npx @modelcontextprotocol/inspector .venv/bin/python -m mcp_server.server
```
Then Connect → Tools → List Tools to see all 8, and call any of them directly.

> Note: the folder is `mcp_server/` (not `mcp/`) on purpose — a local folder named `mcp` shadows the installed `mcp` pip package and prevents the server from importing `FastMCP`.

---

## MCP Tool Setup (Maps / Calendar / Gmail)

The internal tools work out of the box. The Google tools need credentials — set up only the ones you want.

**1. Install integration dependencies** (already in `requirements.txt`):
```bash
.venv/bin/python -m pip install requests google-api-python-client google-auth google-auth-oauthlib mcp
```

**2. Google Maps (quickest — API key only):**
1. In the [Google Cloud Console](https://console.cloud.google.com/), create/select a project.
2. Enable the **Distance Matrix API** and **Places API**.
3. Create an **API key** → add `GOOGLE_MAPS_API_KEY=...` to `.env`. Maps tools now work.

**3. Google Calendar + Gmail (OAuth — one-time):**
1. Enable the **Calendar API** and **Gmail API** in the Cloud Console.
2. Configure the **OAuth consent screen** (External; add your Google account as a test user).
3. Create **OAuth client credentials** → type **Desktop app** → download the JSON, save as `credentials.json` in the project root; set `GOOGLE_OAUTH_CREDENTIALS=credentials.json` in `.env`.
4. Authorize once (opens a browser):
   ```bash
   .venv/bin/python google_oauth_setup.py
   ```
   This creates `token.json`, which the tools read on every run.

> **Security:** `credentials.json` and `token.json` are git-ignored — never commit them. Calendar/Gmail write actions still pass through Atlas's human-in-the-loop approval, and Gmail only ever creates drafts.

---

## RAG Pipeline

Uploaded documents are ingested (`rag/ingest.py`) and retrieved (`rag/retrieve.py` → `retrieve(query, top_k)`), returning grounded answers with citations to the source. If the answer isn't in the documents, Atlas says so rather than guessing. The `document_search` MCP tool wraps this same retriever.

---

## Security & Privacy

- **Human-in-the-loop** on every send/change (nothing external happens without confirmation).
- **PII redaction** before storage; durable memory stored as short structured facts; session vs long-term memory separated; delete/export supported.
- **Untrusted uploads** — documents are treated as data, never instructions.
- **Secret hygiene** — API keys and OAuth files in `.env` / local files only (git-ignored); never in code, logs, or prompts.
- **Audit log** — every tool call and action recorded.

---

## Testing

```bash
.venv/bin/python -m pytest
```

- `test_router.py` — intent routing
- `test_skills.py` — each skill runs
- `test_rag.py` — grounded answer + citation
- `test_approval.py` — no external action without confirmation
- `test_pomodoro.py` — Pomodoro logging and focus history
- `test_qa_generator.py` — Q&A pair storage and retrieval
- `test_revision.py` — study log, spaced-repetition intervals, revision queue, new topic suggestions
- `test_task_reminder.py` — task deletion, edits, and urgency categorization

---

## Concept Mapping

Demonstrates **four** required concepts (only three needed) plus two bonuses.

| Concept | Where |
|---|---|
| Agent / Multi-agent (ADK) | `orchestrator/`, `agents/` |
| Agent skills | `skills/*/SKILL.md` + `skills_runtime.py` + `get_skill_instructions` |
| Antigravity | Built & verified in Antigravity (see video) |
| MCP server | `mcp_server/server.py` + `google_tools.py` (8 tools: internal + Maps/Calendar/Gmail) |
| Security/PII *(bonus)* | `security/` |
| RAG *(bonus)* | `rag/` |

---

## Roadmap
- Google Fit integration (activity/sleep-aware break reminders)
- NotebookLM-style deep document study (pending a public API)
- Voice input and proactive deadline notifications
- A simple web UI (chat, file upload, approval modal, citations panel)
- Shared "study group" mode

---

*Built for the AI Agents: Intensive Vibe Coding Capstone (Google × Kaggle) — Agents for Good.*
