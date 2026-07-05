"""
mcp_server/server.py
====================
Atlas's Model Context Protocol server. Exposes Atlas's tools as standardized MCP
tools. The Google tool logic lives in google_tools.py (project root) so the exact
same functions power both this server and the agents.

Resilient by design: the Google tools always register. The RAG/tasks tools only
register if matching functions are found in your project — so the server starts
cleanly even if those modules use different names. Adjust the names in the two
"try" blocks below to match your rag/tasks modules and they'll appear too.

Run:  python -m mcp_server.server
"""

import os
import sys

# project root on path so we can import google_tools, rag, tools
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp.server.fastmcp import FastMCP  # the pip package (folder renamed to mcp_server)
from google_tools import (
    maps_travel_time, maps_find_nearby,
    google_calendar_list, google_calendar_create,
    gmail_search, gmail_create_draft,
)


def build_server():
    server = FastMCP("atlas")

    # ---- Google tools (always available) -------------------------------
    server.tool()(maps_travel_time)
    server.tool()(maps_find_nearby)
    server.tool()(google_calendar_list)
    server.tool()(google_calendar_create)
    server.tool()(gmail_search)
    server.tool()(gmail_create_draft)

    # ---- RAG document search (your rag.retrieve.retrieve) --------------
    try:
        from rag.retrieve import retrieve as _rag_retrieve

        @server.tool()
        def document_search(query: str, top_k: int = 3) -> str:
            """Search the student's uploaded documents (RAG) and return the most
            relevant, grounded text with citations. Use when answering questions
            about uploaded syllabi, notes, or slides."""
            return _rag_retrieve(query, top_k)
    except Exception as e:
        print(f"[mcp] document_search not registered ({e}).")

    # ---- Tasks list (your tools.get_tasks) ----------------------------
    try:
        from tools import get_tasks as _get_tasks

        @server.tool()
        def tasks_list() -> str:
            """List the student's current assignments/tasks with deadlines and priority."""
            return _get_tasks()
    except Exception as e:
        print(f"[mcp] tasks_list not registered ({e}).")

    return server


if __name__ == "__main__":
    build_server().run()