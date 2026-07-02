import sys
import os

# Ensure the parent directory is in sys.path so we can import rag and tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from fastmcp import FastMCP
    except ImportError:
        # Fallback dummy implementation if mcp package is missing during early local runs
        class FastMCP:
            def __init__(self, name):
                self.name = name
            def tool(self):
                def decorator(func):
                    return func
                return decorator
            def run(self):
                print(f"Dummy FastMCP server '{self.name}' running.", file=sys.stderr)

from rag.retrieve import retrieve
from tools import get_tasks

# Initialize the FastMCP server
mcp = FastMCP("Atlas Chief of Staff MCP Server")

@mcp.tool()
def document_search(query: str, top_k: int = 3) -> str:
    """
    Search student course documents (syllabi, lecture notes, class materials)
    using semantic vector search. Returns matching chunks with source metadata.
    """
    try:
        return retrieve(query, top_k)
    except Exception as e:
        return f"Error during document search tool execution: {str(e)}"

@mcp.tool()
def tasks_list() -> str:
    """
    Retrieve the current task list, assignments, deadlines, priorities, and status.
    """
    try:
        return get_tasks()
    except Exception as e:
        return f"Error during tasks list tool execution: {str(e)}"

if __name__ == "__main__":
    mcp.run()
