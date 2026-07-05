# MCP Schemas for Atlas tools (optional structured models)
# Exposes definitions for the Model Context Protocol server tools

from pydantic import BaseModel, Field

class DocumentSearchInput(BaseModel):
    query: str = Field(..., description="Semantic search query to search course documents.")
    top_k: int = Field(3, description="Number of document chunks to retrieve.")

class TasksListInput(BaseModel):
    pass
