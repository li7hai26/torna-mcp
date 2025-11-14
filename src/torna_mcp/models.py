"""
Data models for Torna MCP Server.

This module contains Pydantic models for input validation and data structures.
"""

from .server import DocGetInput, DocPushInput, HttpMethod, ResponseFormat

# Import new models from server module to avoid circular imports
try:
    from .server import ModuleGetInput, DocListInput, DocDetailsInput
except ImportError:
    # If circular import issue, define them here
    from pydantic import BaseModel, Field, ConfigDict
    from typing import List, Optional
    
    class ModuleGetInput(BaseModel):
        """Input model for module.get operation."""
        model_config = ConfigDict(str_strip_whitespace=True)
        response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

    class DocListInput(BaseModel):
        """Input model for doc.list operation."""
        model_config = ConfigDict(str_strip_whitespace=True)
        response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

    class DocDetailsInput(BaseModel):
        """Input model for doc.details operation."""
        model_config = ConfigDict(str_strip_whitespace=True)
        
        doc_ids: List[str] = Field(..., description="Document IDs to retrieve details for")
        response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

__all__ = [
    "DocPushInput",
    "DocGetInput", 
    "ModuleGetInput",
    "DocListInput",
    "DocDetailsInput",
    "ResponseFormat",
    "HttpMethod",
]
