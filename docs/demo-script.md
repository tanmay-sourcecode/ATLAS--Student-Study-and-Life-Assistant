# Video Demo Script: Atlas — AI Student Chief of Staff

This script outlines the flow for the ≤ 5-minute project demonstration video.

---

## Part 1: Introduction (45 seconds)
* **Visual:** Display the title slide: "Atlas: Your AI Student Chief of Staff". Transition to showing the CLI startup screen with the Atlas banner.
* **Audio/Narration:** 
  > "Hello, my name is [Your Name], and this is Atlas—an AI Student Chief of Staff designed to help university students manage their schedules, master course materials, and draft communications securely and efficiently. Atlas is built on Google's Agent Development Kit, or ADK, utilizing Claude, and developed in Google Antigravity. Let's see it in action."

---

## Part 2: Weekly Planning Scenario (1 minute)
* **Visual:** Type in the CLI: `What should I focus on this week?`
* **Action:** Atlas routes the request to the **Scheduler Agent**, loads the `daily_brief` skill dynamically, reads mock tasks/calendar files, and outputs a daily brief with focus blocks.
* **Audio/Narration:**
  > "We'll start with a typical student question: 'What should I focus on this week?'. Under the hood, Atlas's central Orchestrator identifies the scheduling intent and routes it to our Scheduler specialist agent. It dynamically loads our daily brief skill, pulls current tasks and calendar items, and produces a realistic daily dashboard. Note how it schedules study sessions around existing classes."

---

## Part 3: Study & RAG Scenario (1 minute 30 seconds)
* **Visual:** 
  1. Ingest document: Show a terminal command or ask study agent: `Summarize demo_data/sample_syllabus.txt for exam prep`
  2. Display response: Grounded summary + key definitions + exam topics + 5 review questions + file citations.
* **Audio/Narration:**
  > "Next, let's ask Atlas to summarize a syllabus we've ingested. This triggers the Study Agent. The agent runs a semantic query against our vector store using ChromaDB, retrieves the top relevant text chunks, and feeds them into the model. The output is a structured summary including grading policy and office hours, with precise file citations. If the information isn't in the syllabus, Atlas will say so rather than hallucinating."

---

## Part 4: Communication & Approval Gate (1 minute)
* **Visual:** Type: `Draft an email to my professor asking for a two-day extension on Assignment 3`
* **Action:** Comms Agent drafts the email. Before saving/sending, the **human-in-the-loop approval gate** triggers:
  `🔒 SECURITY WARNING: A sensitive action requires your approval: Approve and SEND email draft...`
  `Do you approve this action? (yes/no) [no]:`
  Type `yes` and show execution success.
* **Audio/Narration:**
  > "Finally, let's look at the security layer. I ask Atlas to draft an email asking for a deadline extension. The Comms Agent uses our email draft skill to formulate a respectful draft. However, before any state change or simulated external action occurs, our human-in-the-loop approval gate intercepts the execution. It blocks the runtime and prints a security warning. No email is sent and no calendar entry is changed until I explicitly type 'yes'."

---

## Part 5: Outro (15 seconds)
* **Visual:** Show the architecture diagram from the README, highlighting the multi-agent hierarchy, PII scrubs, audit logging, and MCP server interface.
* **Audio/Narration:**
  > "Atlas combines the power of multi-agent collaboration with student privacy and control, grounded in local files. Thank you for watching!"
