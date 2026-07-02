# Atlas — Your AI Student Chief of Staff

> A multi-agent study-and-life assistant that helps university students plan their week, understand course materials, and communicate with instructors — grounded in their own documents, private by design, and always under the student's control. Built on Google's Agent Development Kit (ADK) with Claude, developed in Antigravity.

**Capstone track:** Agents for Good · **Demo video:** _[your YouTube link]_ · **Live demo (optional):** _[URL or "run locally — see below"]_

**Key concepts:** Multi-agent system (ADK) · Agent skills · Antigravity · MCP (small) · *bonus:* RAG, Security/PII

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
- [RAG Pipeline](#rag-pipeline)
- [Security & Privacy](#security--privacy)
- [Testing](#testing)
- [Concept Mapping](#concept-mapping)
- [Roadmap](#roadmap)

---

## The Problem

A university student coordinates a huge, fragmented workload alone: lectures across many courses, deadlines scattered across portals, group projects, exams, readings, and often a job. Executives get a chief of staff for far less; students get a planner app they abandon by week three. The result — missed deadlines, all-nighters, and burnout — hits first-generation, working, and neurodivergent students hardest. Existing tools are passive: they store information but don't plan, act, or remember.

## The Solution

**Atlas** is an AI chief of staff for students — a multi-agent system that reads course materials, tracks deadlines, plans study time, and drafts academic communication, always with the student's approval before anything is sent. It turns fragmented academic work into one coordinated, private system.

---

## Architecture

Atlas is a hierarchical multi-agent system on Google ADK. A central Orchestrator classifies intent and routes to one specialist agent, then composes the reply. Sensitive actions pass through a human-in-the-loop approval gate.

```
                 Student (CLI / simple chat)
                          │
                 ┌────────▼─────────┐
                 │  ORCHESTRATOR    │  classify intent → delegate
                 │  (Chief of Staff)│  approval gate on sensitive actions
                 └───┬───┬───┬───┬──┘
        ┌────────────┘   │   │   └────────────┐
        ▼                ▼   ▼                ▼
   Scheduler        Study(RAG)   Comms         Memory
   classes/         summarize/   email         durable prefs
   deadlines/       study plans  drafts        (PII-redacted)
   study blocks     w/ citations (never sends)
                          │
             Security: approval gate · PII redaction · audit log
```

| Agent (file) | Responsibility |
|---|---|
| Orchestrator (`orchestrator/agent.py`) | Intent classification, routing, reply synthesis, approval gating |
| Scheduler (`agents/scheduler.py`) | Classes, deadlines, exam dates, study blocks, conflict detection |
| Study (`agents/study.py`) | RAG summaries, key concepts, study plans, grounded answers w/ citations |
| Comms (`agents/comms.py`) | Drafts academic emails/messages — never sends |
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
- **Multi-agent coordination** via clear tool interfaces + a small MCP server.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Agent framework | Google Agent Development Kit (ADK) |
| LLM | Claude (Anthropic API), developed in Google Antigravity |
| Skills | Anthropic-style `SKILL.md` folders w/ progressive disclosure |
| Tool protocol | Model Context Protocol (small server: `document.search`, `tasks.list`) |
| Retrieval | RAG — section chunking, top-k, two-stage retrieve→answer, citations |
| Interface | CLI (ADK Runner) |
| Language | Python 3.11+ |

---

## Project Structure

```
atlas-student-chief-of-staff/
├─ README.md
├─ .env.example              # placeholders only — NO secrets
├─ .gitignore                # ignores .env
├─ requirements.txt
├─ app.py                    # CLI entry point (ADK Runner)
├─ docs/                     # architecture.png, demo-script.md, rubric-mapping.md
├─ orchestrator/
│  ├─ agent.py               # root agent + routing
│  └─ prompts.py
├─ agents/
│  ├─ scheduler.py
│  ├─ study.py               # RAG-backed
│  ├─ comms.py
│  └─ memory.py
├─ skills/                   # SKILL.md folders (progressive disclosure)
│  ├─ daily_brief/SKILL.md
│  ├─ study_plan/SKILL.md
│  ├─ assignment_breakdown/SKILL.md
│  ├─ email_draft/SKILL.md
│  ├─ document_summary/SKILL.md
│  └─ deadline_checkin/SKILL.md
├─ skills_runtime.py         # loads a skill's SKILL.md on demand
├─ tools.py                  # calendar/tasks/files/email stubs
├─ mcp/
│  ├─ server.py              # small MCP: document.search + tasks.list
│  └─ schemas.py
├─ rag/
│  ├─ ingest.py              # chunk + embed uploaded docs
│  └─ retrieve.py            # top-k grounded retrieval
├─ security/
│  ├─ approval.py            # human-in-the-loop gate
│  ├─ pii.py                 # redaction before storage
│  └─ audit.py               # tool-call logging
├─ demo_data/                # sample_syllabus.pdf, sample_notes.pdf, sample_assignments.json
└─ tests/                    # test_router.py, test_skills.py, test_rag.py, test_approval.py
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- An Anthropic API key

### Install
```bash
git clone https://github.com/<you>/atlas-student-chief-of-staff.git
cd atlas-student-chief-of-staff

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## Configuration

**Never commit secrets.** Copy the template and fill it in locally:

```bash
cp .env.example .env
```

`.env.example` (committed — placeholders only):
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

`.env` is git-ignored. Confirm `.gitignore` contains `.env` before your first push. The model never receives raw credentials.

---

## Running Atlas

Atlas runs as a command-line chat loop on the ADK Runner:

```bash
python app.py
```

Try:
- `What should I focus on this week?`
- `Summarize demo_data/sample_syllabus.pdf for exam prep`
- `Build me a study plan for finals`
- `Draft an email to my professor asking for a two-day extension` *(shows the approval gate)*

A demo mode with sample student data and three scripted scenarios (planning, study, communication) is included for quick testing.

---

## Agent Skills

Skills are reusable procedures built the Anthropic way — each is a folder with a `SKILL.md` (YAML frontmatter: `name`, `description` + markdown instructions). Loading is three-level (**progressive disclosure**): metadata always in context, the SKILL.md body only when the skill triggers, bundled scripts only when needed. This keeps behavior consistent **and** keeps token usage/cost low.

Skills: `daily_brief`, `study_plan`, `assignment_breakdown`, `email_draft`, `document_summary`, `deadline_checkin`.

---

## MCP Server

`mcp/server.py` is a minimal Model Context Protocol server exposing two of Atlas's tools as standardized MCP tools: `document.search` (RAG retrieval) and `tasks.list`. This demonstrates inspectable, standardized tool access without wiring MCP through the whole system.

---

## RAG Pipeline

Uploaded documents are chunked by section, embedded, and stored with source metadata (file name, page, chunk id). Retrieval is **two-stage**: retrieve top-k relevant chunks, then answer grounded *only* in that text, returning a citation. If the answer isn't in the documents, Atlas says so. Repeated retrievals are cached and over-long uploads are truncated before embedding to control cost.

---

## Security & Privacy

- **Human-in-the-loop** on every send/change (nothing external happens without confirmation).
- **PII redaction** (names, IDs, emails, phones) before storage; durable memory stored as short structured facts; session vs long-term memory separated; delete/export supported.
- **Untrusted uploads** — documents are treated as data, never instructions.
- **Secret hygiene** — API keys in `.env` / env vars only; never in code, logs, or prompts.
- **Audit log** — every tool call and action recorded.

---

## Testing

```bash
pytest
```

- `test_router.py` — intent routing
- `test_skills.py` — each skill runs
- `test_rag.py` — grounded answer + citation
- `test_approval.py` — no external action without confirmation

---

## Concept Mapping

Demonstrates **four** required concepts (only three needed) plus two bonuses.

| Concept | Where |
|---|---|
| Agent / Multi-agent (ADK) | `orchestrator/`, `agents/` |
| Agent skills | `skills/*/SKILL.md` + `skills_runtime.py` |
| Antigravity | Built & verified in Antigravity (see video) |
| MCP server | `mcp/server.py` |
| Security/PII *(bonus)* | `security/` |
| RAG *(bonus)* | `rag/` |

---

## Roadmap
- Real calendar/email integration (currently local stubs)
- Voice input and proactive deadline notifications
- A simple web UI (chat, file upload, approval modal, citations panel)
- Shared "study group" mode

---

*Built for the AI Agents: Intensive Vibe Coding Capstone (Google × Kaggle) — Agents for Good.*
