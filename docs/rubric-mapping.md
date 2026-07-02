# Capstone Rubric Mapping: Atlas — AI Student Chief of Staff

This document maps the project deliverables to the intensive capstone rubric requirements (100 points total).

---

## 1. Pitch: Core Concept & Value (10 points)
* **Requirement:** Clear problem statement, target audience, and how AI agents solve the problem uniquely.
* **Atlas Implementation:**
  - **Problem Statement:** Section "The Problem" in [README.md](file:///c:/Users/Dev/Downloads/atlas1/ATLAS--Student-Study-and-Life-Assistant/README.md) details the fragmented, heavy coordination workload of university students.
  - **Target Audience:** University students balancing studies, jobs, and executive functioning demands.
  - **Agent Value:** Atlas acts as a proactive, stateful, and secure multi-agent planner and assistant rather than a static database.

---

## 2. Pitch: Video Demo (10 points)
* **Requirement:** A short (≤5 min) walkthrough showing the app running in real-time, explaining the multi-agent orchestration and design choices.
* **Atlas Implementation:**
  - Video outline prepared in [demo-script.md](file:///c:/Users/Dev/Downloads/atlas1/ATLAS--Student-Study-and-Life-Assistant/docs/demo-script.md). Shows 4 specialist agents routing, progressive disclosure skills loading, RAG citations, and security gates.

---

## 3. Pitch: Writeup (10 points)
* **Requirement:** A detailed writeup (≤2,500 words) explaining concept design, architectural journey, and technical choices.
* **Atlas Implementation:**
  - Detailed design process recorded in [Atlas_Design_and_Plan.md](file:///c:/Users/Dev/Downloads/atlas1/ATLAS--Student-Study-and-Life-Assistant/Atlas_Design_and_Plan.md).

---

## 4. Technical Implementation (50 points)
* **Requirement:** Functional multi-agent setup, custom tools, skills representation, security guidelines, and RAG capabilities with zero hardcoded API keys.
* **Atlas Implementation:**
  - **Multi-Agent System:** Google ADK `Agent` configurations with a central Orchestrator (`orchestrator/agent.py`) and subagents (`agents/scheduler.py`, `agents/study.py`, `agents/comms.py`, `agents/memory.py`).
  - **Agent Skills:** Dynamic, progressive disclosure loading using `skills_runtime.py` and `skills/*/SKILL.md` documents.
  - **RAG Pipeline:** Ingestion (`rag/ingest.py`) and retrieval (`rag/retrieve.py`) using ChromaDB for semantic vector searches, returning citations.
  - **Security Layer:** Regex-based PII scrub (`security/pii.py`), audit trail logger (`security/audit.py`), and human-in-the-loop terminal approval blocking (`security/approval.py`).
  - **Secret Hygiene:** Environment variables loaded via `dotenv` in `app.py` with zero secrets committed.
  - **MCP Integration:** Standardized `fastmcp` server (`mcp/server.py`) exposing RAG and tasks as MCP tools.

---

## 5. Documentation (20 points)
* **Requirement:** Fully-documented codebase, setup instructions, dependencies, and architecture diagrams.
* **Atlas Implementation:**
  - Complete, step-by-step setup guides, folder diagrams, and concept mappings are fully detailed in [README.md](file:///c:/Users/Dev/Downloads/atlas1/ATLAS--Student-Study-and-Life-Assistant/README.md).
