#!/usr/bin/env python3
"""
Torna MCP Server

This MCP server provides tools to interact with Torna API for managing API documentation,
dictionaries, and modules. It supports pushing documents, managing categories, listing documents,
and handling dictionaries.

Environment Variables Required:
- TORNA_URL: Torna private deployment URL (e.g., "http://localhost:7700/api")
- TORNA_TOKENS: Module tokens separated by commas (e.g., "token1,token2,token3")
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from enum import Enum
import httpx
from pydantic import BaseModel, Field, ConfigDict, field_validator
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("torna_mcp")

# Constants
API_BASE_URL = os.getenv("TORNA_URL")
TORNA_TOKENS = os.getenv("TORNA_TOKENS", "").split(",") if os.getenv("TORNA_TOKENS") else []
CHARACTER_LIMIT = 25000

if not API_BASE_URL:
    raise ValueError("TORNA_URL environment variable is required")

if not TORNA_TOKENS or not TORNA_TOKENS[0]:
    raise ValueError("TORNA_TOKENS environment variable is required and should contain comma-separated tokens")

# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"

class HttpMethod(str, Enum):
    """HTTP methods supported by Torna."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

# Pydantic Models for Input Validation
class TornaBaseRequest(BaseModel):
    """Base request model for Torna API calls."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    interface_name: str = Field(..., description="Interface name (e.g., 'doc.push', 'doc.list')")
    version: str = Field(default="1.0", description="Interface version number")
    access_token: str = Field(..., description="Module token for authentication")
    
    @field_validator('interface_name')
    @classmethod
    def validate_interface_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Interface name cannot be empty")
        return v.strip()

class DocPushInput(BaseModel):
    """Input model for document push operation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    # Document basic info
    name: str = Field(..., description="Document name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Document description")
    url: str = Field(..., description="API endpoint URL (e.g., '/api/users')")
    http_method: HttpMethod = Field(default=HttpMethod.GET, description="HTTP method")
    content_type: str = Field(default="application/json", description="Content type")
    is_folder: bool = Field(default=False, description="Whether this is a folder/category")
    parent_id: Optional[str] = Field(default=None, description="Parent category ID")
    is_show: bool = Field(default=True, description="Whether to show this document")
    version: str = Field(default="1.0", description="Interface version number")
    access_token: str = Field(..., description="Module token for authentication")
    
    # Request parameters
    request_params: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Request parameters")
    header_params: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Header parameters")
    
    # Response parameters
    response_params: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Response parameters")
    
    # Error codes
    error_codes: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Error codes")
    
    # Debug environment
    debug_env_name: Optional[str] = Field(default=None, description="Debug environment name")
    debug_env_url: Optional[str] = Field(default=None, description="Debug environment URL")
    
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class CategoryCreateInput(BaseModel):
    """Input model for category creation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    name: str = Field(..., description="Category name", min_length=1, max_length=100)
    parent_id: Optional[str] = Field(default=None, description="Parent category ID")
    description: Optional[str] = Field(default=None, description="Category description")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class CategoryUpdateInput(BaseModel):
    """Input model for category name update."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    category_id: str = Field(..., description="Category ID to update")
    name: str = Field(..., description="New category name", min_length=1, max_length=100)
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class DocListInput(BaseModel):
    """Input model for document listing."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    access_token: str = Field(..., description="Module token for authentication")
    limit: Optional[int] = Field(default=20, description="Maximum results to return", ge=1, le=100)
    offset: Optional[int] = Field(default=0, description="Number of results to skip for pagination", ge=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class DocDetailInput(BaseModel):
    """Input model for document detail retrieval."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    doc_id: str = Field(..., description="Document ID to retrieve")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class DocDetailsBatchInput(BaseModel):
    """Input model for batch document detail retrieval."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    doc_ids: List[str] = Field(..., description="List of document IDs to retrieve", min_items=1, max_items=50)
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

# Dictionary API Models
class DictCreateInput(BaseModel):
    """Input model for dictionary creation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    name: str = Field(..., description="Dictionary name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Dictionary description")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class DictUpdateInput(BaseModel):
    """Input model for dictionary update."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    dict_id: str = Field(..., description="Dictionary ID to update")
    name: Optional[str] = Field(default=None, description="New dictionary name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="New dictionary description")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class DictListInput(BaseModel):
    """Input model for dictionary listing."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    access_token: str = Field(..., description="Module token for authentication")
    limit: Optional[int] = Field(default=20, description="Maximum results to return", ge=1, le=100)
    offset: Optional[int] = Field(default=0, description="Number of results to skip for pagination", ge=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class DictDetailInput(BaseModel):
    """Input model for dictionary detail retrieval."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    dict_id: str = Field(..., description="Dictionary ID to retrieve")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class DictDeleteInput(BaseModel):
    """Input model for dictionary deletion."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    dict_id: str = Field(..., description="Dictionary ID to delete")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

# Module API Models
class ModuleCreateInput(BaseModel):
    """Input model for module creation."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    name: str = Field(..., description="Module name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Module description")
    project_id: str = Field(..., description="Project ID to which the module belongs")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class ModuleUpdateInput(BaseModel):
    """Input model for module update."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    module_id: str = Field(..., description="Module ID to update")
    name: Optional[str] = Field(default=None, description="New module name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="New module description")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class ModuleListInput(BaseModel):
    """Input model for module listing."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    project_id: Optional[str] = Field(default=None, description="Project ID to filter modules")
    access_token: str = Field(..., description="Module token for authentication")
    limit: Optional[int] = Field(default=20, description="Maximum results to return", ge=1, le=100)
    offset: Optional[int] = Field(default=0, description="Number of results to skip for pagination", ge=0)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class ModuleDetailInput(BaseModel):
    """Input model for module detail retrieval."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    module_id: str = Field(..., description="Module ID to retrieve")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class ModuleDeleteInput(BaseModel):
    """Input model for module deletion."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    module_id: str = Field(..., description="Module ID to delete")
    access_token: str = Field(..., description="Module token for authentication")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

# Shared utility functions
async def _make_api_request(interface_name: str, version: str, data: Dict[str, Any], access_token: str) -> Dict[str, Any]:
    """Make request to Torna API."""
    # Torna API expects data to be JSON encoded string
    import json
    import urllib.parse
    
    request_data = {
        "name": interface_name,
        "version": version,
        "data": urllib.parse.quote(json.dumps(data, ensure_ascii=False)),
        "access_token": access_token
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            API_BASE_URL,
            json=request_data,
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

def _handle_api_error(e: Exception) -> str:
    """Consistent error formatting across all tools."""
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    elif isinstance(e, ValueError) and "TORNA" in str(e):
        return f"Configuration error: {str(e)}"
    return f"Error: Unexpected error occurred: {type(e).__name__}"

def _format_doc_push_data(input_data: DocPushInput) -> Dict[str, Any]:
    """Format input data for doc.push API."""
    doc_data = {
        "name": input_data.name,
        "description": input_data.description or "",
        "url": input_data.url,
        "httpMethod": input_data.http_method.value,
        "contentType": input_data.content_type,
        "isFolder": input_data.is_folder,
        "isShow": input_data.is_show
    }
    
    if input_data.parent_id:
        doc_data["parentId"] = input_data.parent_id
    
    if input_data.request_params:
        doc_data["requestParams"] = input_data.request_params
    
    if input_data.header_params:
        doc_data["headerParams"] = input_data.header_params
    
    if input_data.response_params:
        doc_data["responseParams"] = input_data.response_params
    
    if input_data.error_codes:
        doc_data["errorCodeParams"] = input_data.error_codes
    
    # Handle debug environment
    if input_data.debug_env_name and input_data.debug_env_url:
        doc_data["debugEnv"] = {
            "name": input_data.debug_env_name,
            "url": input_data.debug_env_url
        }
    
    return {"apis": [doc_data]}

def _format_response(result: Dict[str, Any], response_format: ResponseFormat, interface_name: str) -> str:
    """Format API response based on requested format."""
    if response_format == ResponseFormat.JSON:
        import json
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    # Markdown format
    lines = [f"# {interface_name} Result", ""]
    
    # Check if this is a successful response
    if result.get("code") == 0 or result.get("code") == "0":
        lines.append("✅ **Operation completed successfully**")
        lines.append("")
        
        # Handle different response types
        if interface_name == "doc.push":
            if result.get("data"):
                lines.append("## Push Result")
                lines.append(f"- **Document Name**: {result['data'].get('name', 'N/A')}")
                lines.append(f"- **Document ID**: {result['data'].get('id', 'N/A')}")
                lines.append(f"- **Status**: {result['data'].get('status', 'N/A')}")
            else:
                lines.append("Documents have been pushed successfully.")
        
        elif interface_name == "doc.category.create":
            if result.get("data"):
                lines.append("## Category Created")
                lines.append(f"- **Category Name**: {result['data'].get('name', 'N/A')}")
                lines.append(f"- **Category ID**: {result['data'].get('id', 'N/A')}")
            else:
                lines.append("Category has been created successfully.")
        
        elif interface_name == "doc.category.name.update":
            lines.append("Category name has been updated successfully.")
        
        elif interface_name == "doc.list":
            data = result.get("data", {})
            docs = data.get("list", [])
            lines.append(f"## Document List (Total: {data.get('total', 0)})")
            lines.append("")
            
            if docs:
                for doc in docs[:10]:  # Show first 10 docs
                    lines.append(f"### {doc.get('name', 'Untitled')}")
                    lines.append(f"- **ID**: {doc.get('id', 'N/A')}")
                    lines.append(f"- **URL**: {doc.get('url', 'N/A')}")
                    lines.append(f"- **Method**: {doc.get('httpMethod', 'N/A')}")
                    if doc.get('description'):
                        lines.append(f"- **Description**: {doc.get('description')}")
                    lines.append("")
                
                if len(docs) > 10:
                    lines.append(f"... and {len(docs) - 10} more documents")
            else:
                lines.append("No documents found.")
        
        elif interface_name == "doc.detail":
            doc = result.get("data", {})
            if doc:
                lines.append(f"## {doc.get('name', 'Document Detail')}")
                lines.append(f"- **ID**: {doc.get('id', 'N/A')}")
                lines.append(f"- **URL**: {doc.get('url', 'N/A')}")
                lines.append(f"- **Method**: {doc.get('httpMethod', 'N/A')}")
                lines.append(f"- **Content Type**: {doc.get('contentType', 'N/A')}")
                
                if doc.get('description'):
                    lines.append(f"- **Description**: {doc.get('description')}")
                
                request_params = doc.get('requestParams', [])
                if request_params:
                    lines.append("")
                    lines.append("### Request Parameters")
                    for param in request_params:
                        lines.append(f"- **{param.get('name', 'N/A')}** ({param.get('type', 'N/A')})")
                        if param.get('description'):
                            lines.append(f"  - {param.get('description')}")
                        if param.get('example'):
                            lines.append(f"  - Example: {param.get('example')}")
                
                response_params = doc.get('responseParams', [])
                if response_params:
                    lines.append("")
                    lines.append("### Response Parameters")
                    for param in response_params:
                        lines.append(f"- **{param.get('name', 'N/A')}** ({param.get('type', 'N/A')})")
                        if param.get('description'):
                            lines.append(f"  - {param.get('description')}")
                        if param.get('example'):
                            lines.append(f"  - Example: {param.get('example')}")
            else:
                lines.append("Document not found.")
        
        elif interface_name == "doc.details":
            docs = result.get("data", [])
            lines.append(f"## Batch Document Details ({len(docs)} documents)")
            lines.append("")
            
            for i, doc in enumerate(docs, 1):
                lines.append(f"### {i}. {doc.get('name', 'Untitled')}")
                lines.append(f"- **ID**: {doc.get('id', 'N/A')}")
                lines.append(f"- **URL**: {doc.get('url', 'N/A')}")
                lines.append(f"- **Method**: {doc.get('httpMethod', 'N/A')}")
                if doc.get('description'):
                    lines.append(f"- **Description**: {doc.get('description')}")
                lines.append("")
    else:
        lines.append("❌ **Operation failed**")
        lines.append("")
        lines.append(f"- **Error Code**: {result.get('code', 'Unknown')}")
        lines.append(f"- **Error Message**: {result.get('msg', 'Unknown error')}")
    
    response_text = "\n".join(lines)
    
    # Check character limit
    if len(response_text) > CHARACTER_LIMIT:
        truncated_text = response_text[:CHARACTER_LIMIT - 100]
        truncated_text += "\n\n... (response truncated due to length limit)"
        return truncated_text
    
    return response_text

# Tool implementations
@mcp.tool(
    name="torna_push_document",
    annotations={
        "title": "Push Document to Torna",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def torna_push_document(params: DocPushInput) -> str:
    """Push a document to Torna platform.

    This tool allows you to create or update API documentation in Torna. You can create
    folder structures, add documents with request/response parameters, and configure
    debugging environments.

    Args:
        params (DocPushInput): Validated input parameters containing:
            - name (str): Document name (required)
            - description (str, optional): Document description
            - url (str): API endpoint URL (e.g., '/api/users')
            - http_method (str): HTTP method (GET, POST, PUT, DELETE, PATCH)
            - content_type (str): Content type (default: 'application/json')
            - is_folder (bool): Whether this is a folder/category (default: False)
            - parent_id (str, optional): Parent category ID
            - is_show (bool): Whether to show this document (default: True)
            - request_params (list, optional): Request parameters with structure:
              [{"name": "param1", "type": "string", "description": "param desc", "required": true, "example": "value"}]
            - header_params (list, optional): Header parameters
            - response_params (list, optional): Response parameters
            - error_codes (list, optional): Error codes with structure:
              [{"code": "1001", "msg": "error message", "solution": "solution"}]
            - debug_env_name (str, optional): Debug environment name
            - debug_env_url (str, optional): Debug environment URL
            - access_token (str): Module token for authentication

    Returns:
        str: JSON-formatted or markdown-formatted response containing operation results
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "doc_id",
                "name": "document_name",
                "status": "created/updated"
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Creating new API documentation
        - Use when: Organizing documents into categories
        - Use when: Adding request/response parameter documentation
        - Don't use when: You only want to list existing documents (use torna_list_documents instead)
        - Don't use when: You need to update only the category name (use torna_update_category_name instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if parent category doesn't exist (404 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = _format_doc_push_data(params)
        
        # Make API request
        result = await _make_api_request(
            interface_name="doc.push",
            version=params.version,
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "doc.push")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_create_category",
    annotations={
        "title": "Create Document Category",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def torna_create_category(params: CategoryCreateInput) -> str:
    """Create a new document category in Torna.

    This tool creates a folder/category for organizing documents in Torna. Categories
    help structure your API documentation in a hierarchical manner.

    Args:
        params (CategoryCreateInput): Validated input parameters containing:
            - name (str): Category name (required, 1-100 characters)
            - parent_id (str, optional): Parent category ID for nested categories
            - description (str, optional): Category description
            - access_token (str): Module token for authentication

    Returns:
        str: JSON-formatted or markdown-formatted response containing operation results
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "category_id",
                "name": "category_name",
                "parentId": "parent_id",
                "isFolder": true
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Organizing documents into logical groups
        - Use when: Creating hierarchical document structure
        - Use when: Setting up new API documentation sections
        - Don't use when: Creating documents themselves (use torna_push_document instead)
        - Don't use when: Just need to list existing categories (use torna_list_documents instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if parent category doesn't exist (404 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = {
            "name": params.name,
            "isFolder": True,
            "isShow": True
        }
        
        if params.parent_id:
            data["parentId"] = params.parent_id
        
        if params.description:
            data["description"] = params.description
        
        # Make API request
        result = await _make_api_request(
            interface_name="doc.category.create",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "doc.category.create")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_update_category_name",
    annotations={
        "title": "Update Category Name",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_update_category_name(params: CategoryUpdateInput) -> str:
    """Update the name of an existing category in Torna.

    This tool allows you to rename existing categories/folders in Torna while
    maintaining their hierarchical structure and associated documents.

    Args:
        params (CategoryUpdateInput): Validated input parameters containing:
            - category_id (str): Category ID to update (required)
            - name (str): New category name (required, 1-100 characters)
            - access_token (str): Module token for authentication

    Returns:
        str: JSON-formatted or markdown-formatted response containing operation results
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "category_id",
                "name": "new_category_name",
                "updated": true
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Renaming a category for better organization
        - Use when: Updating category names after restructuring
        - Don't use when: Creating new categories (use torna_create_category instead)
        - Don't use when: You need to update document details (use torna_push_document instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if category doesn't exist (404 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = {
            "name": params.name
        }
        
        # Make API request
        result = await _make_api_request(
            interface_name="doc.category.name.update",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "doc.category.name.update")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_list_documents",
    annotations={
        "title": "List Documents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_list_documents(params: DocListInput) -> str:
    """List documents in Torna with pagination support.

    This tool retrieves a list of documents from Torna with support for pagination
    to handle large datasets efficiently. It returns both folders and documents.

    Args:
        params (DocListInput): Validated input parameters containing:
            - access_token (str): Module token for authentication (required)
            - limit (int, optional): Maximum results to return, 1-100 (default: 20)
            - offset (int, optional): Number of results to skip for pagination (default: 0)

    Returns:
        str: JSON-formatted or markdown-formatted response containing document list with pagination info
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "total": 150,
                "list": [
                    {
                        "id": "doc_id",
                        "name": "document_name",
                        "url": "/api/endpoint",
                        "httpMethod": "GET",
                        "description": "document description",
                        "isFolder": false,
                        "parentId": "parent_id"
                    }
                ],
                "hasMore": true,
                "nextOffset": 20
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting an overview of all documents in a module
        - Use when: Paginating through large document collections
        - Use when: Finding specific documents by browsing the list
        - Don't use when: You need detailed information about a specific document (use torna_get_document_detail instead)
        - Don't use when: You need to create new documents (use torna_push_document instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns formatted document list with pagination info
    """
    try:
        # Format data for Torna API
        data = {
            "limit": params.limit or 20,
            "offset": params.offset or 0
        }
        
        # Make API request
        result = await _make_api_request(
            interface_name="doc.list",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "doc.list")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_get_document_detail",
    annotations={
        "title": "Get Document Detail",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_get_document_detail(params: DocDetailInput) -> str:
    """Get detailed information about a specific document in Torna.

    This tool retrieves comprehensive details about a single document including
    request parameters, response parameters, headers, and error codes.

    Args:
        params (DocDetailInput): Validated input parameters containing:
            - doc_id (str): Document ID to retrieve (required)
            - access_token (str): Module token for authentication (required)

    Returns:
        str: JSON-formatted or markdown-formatted response containing detailed document information
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "doc_id",
                "name": "document_name",
                "url": "/api/endpoint",
                "httpMethod": "GET",
                "description": "document description",
                "contentType": "application/json",
                "requestParams": [...],
                "responseParams": [...],
                "headerParams": [...],
                "errorCodeParams": [...]
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting full documentation for a specific API endpoint
        - Use when: Reviewing request/response parameters for an API
        - Use when: Checking error codes and examples
        - Don't use when: You need an overview of all documents (use torna_list_documents instead)
        - Don't use when: You need batch information for multiple documents (use torna_get_document_details_batch instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if document doesn't exist (404 status)
        - Returns formatted detailed document information
    """
    try:
        # Format data for Torna API
        data = {
            "id": params.doc_id
        }
        
        # Make API request
        result = await _make_api_request(
            interface_name="doc.detail",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "doc.detail")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_get_document_details_batch",
    annotations={
        "title": "Get Document Details (Batch)",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_get_document_details_batch(params: DocDetailsBatchInput) -> str:
    """Get detailed information about multiple documents in Torna (batch operation).

    This tool retrieves comprehensive details about multiple documents in a single
    request, which is more efficient than making individual requests.

    Args:
        params (DocDetailsBatchInput): Validated input parameters containing:
            - doc_ids (list): List of document IDs to retrieve (1-50 documents)
            - access_token (str): Module token for authentication (required)

    Returns:
        str: JSON-formatted or markdown-formatted response containing detailed information for all requested documents
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": [
                {
                    "id": "doc_id_1",
                    "name": "document_name_1",
                    "url": "/api/endpoint",
                    "httpMethod": "GET",
                    "description": "document description"
                },
                {
                    "id": "doc_id_2",
                    "name": "document_name_2",
                    "url": "/api/endpoint2",
                    "httpMethod": "POST",
                    "description": "document description"
                }
            ]
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting details for multiple related APIs at once
        - Use when: Processing multiple documents for analysis or export
        - Use when: Bulk documentation review
        - Don't use when: You need details for just one document (use torna_get_document_detail instead)
        - Don't use when: You need an overview of all documents (use torna_list_documents instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if any document doesn't exist (404 status)
        - Returns formatted detailed information for all requested documents
    """
    try:
        # Format data for Torna API
        data = {
            "ids": params.doc_ids
        }
        
        # Make API request
        result = await _make_api_request(
            interface_name="doc.details",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "doc.details")
        
    except Exception as e:
        return _handle_api_error(e)

# Dictionary API Tool implementations
@mcp.tool(
    name="torna_create_dictionary",
    annotations={
        "title": "Create Dictionary",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def torna_create_dictionary(params: DictCreateInput) -> str:
    """Create a new dictionary in Torna.

    This tool creates a dictionary/enumeration that can be referenced by API parameters.
    Dictionaries help standardize parameter values across your API documentation.

    Args:
        params (DictCreateInput): Validated input parameters containing:
            - name (str): Dictionary name (required, 1-100 characters)
            - description (str, optional): Dictionary description
            - access_token (str): Module token for authentication

    Returns:
        str: JSON-formatted or markdown-formatted response containing operation results
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "dict_id",
                "name": "dictionary_name",
                "description": "dictionary description",
                "items": []
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Creating standardized parameter values (e.g., status enums)
        - Use when: Managing business logic enumerations
        - Use when: Centralizing common parameter definitions
        - Don't use when: Creating API documentation (use torna_push_document instead)
        - Don't use when: Creating modules (use torna_create_module instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = {
            "name": params.name
        }
        
        if params.description:
            data["description"] = params.description
        
        # Make API request
        result = await _make_api_request(
            interface_name="dict.create",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "dict.create")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_update_dictionary",
    annotations={
        "title": "Update Dictionary",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def torna_update_dictionary(params: DictUpdateInput) -> str:
    """Update an existing dictionary in Torna.

    This tool allows you to modify the name and description of an existing dictionary.

    Args:
        params (DictUpdateInput): Validated input parameters containing:
            - dict_id (str): Dictionary ID to update (required)
            - name (str, optional): New dictionary name (1-100 characters)
            - description (str, optional): New dictionary description
            - access_token (str): Module token for authentication

    Returns:
        str: JSON-formatted or markdown-formatted response containing operation results
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "dict_id",
                "name": "updated_name",
                "description": "updated description",
                "updated": true
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Updating dictionary metadata
        - Use when: Renaming dictionaries for better organization
        - Use when: Adding descriptions to existing dictionaries
        - Don't use when: Creating new dictionaries (use torna_create_dictionary instead)
        - Don't use when: You need to get dictionary details (use torna_get_dictionary_detail instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if dictionary doesn't exist (404 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = {
            "id": params.dict_id
        }
        
        if params.name:
            data["name"] = params.name
        
        if params.description:
            data["description"] = params.description
        
        # Make API request
        result = await _make_api_request(
            interface_name="dict.update",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "dict.update")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_list_dictionaries",
    annotations={
        "title": "List Dictionaries",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_list_dictionaries(params: DictListInput) -> str:
    """List dictionaries in Torna with pagination support.

    This tool retrieves a list of dictionaries with support for pagination
    to handle large collections efficiently.

    Args:
        params (DictListInput): Validated input parameters containing:
            - access_token (str): Module token for authentication (required)
            - limit (int, optional): Maximum results to return, 1-100 (default: 20)
            - offset (int, optional): Number of results to skip for pagination (default: 0)

    Returns:
        str: JSON-formatted or markdown-formatted response containing dictionary list with pagination info
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "total": 50,
                "list": [
                    {
                        "id": "dict_id",
                        "name": "status_enum",
                        "description": "Status enumeration",
                        "items": [...],
                        "createdAt": "2024-01-01T00:00:00Z"
                    }
                ],
                "hasMore": true,
                "nextOffset": 20
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting an overview of all dictionaries in a module
        - Use when: Finding specific dictionaries by browsing the list
        - Use when: Managing dictionary collections
        - Don't use when: You need details about a specific dictionary (use torna_get_dictionary_detail instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns formatted dictionary list with pagination info
    """
    try:
        # Format data for Torna API
        data = {
            "limit": params.limit or 20,
            "offset": params.offset or 0
        }
        
        # Make API request
        result = await _make_api_request(
            interface_name="dict.list",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "dict.list")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_get_dictionary_detail",
    annotations={
        "title": "Get Dictionary Detail",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_get_dictionary_detail(params: DictDetailInput) -> str:
    """Get detailed information about a specific dictionary in Torna.

    This tool retrieves comprehensive details about a dictionary including
    all its items/entries.

    Args:
        params (DictDetailInput): Validated input parameters containing:
            - dict_id (str): Dictionary ID to retrieve (required)
            - access_token (str): Module token for authentication (required)

    Returns:
        str: JSON-formatted or markdown-formatted response containing detailed dictionary information
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "dict_id",
                "name": "status_enum",
                "description": "Status enumeration for orders",
                "items": [
                    {
                        "name": "PENDING",
                        "value": "0",
                        "description": "Order is pending"
                    },
                    {
                        "name": "COMPLETED",
                        "value": "1",
                        "description": "Order is completed"
                    }
                ],
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z"
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting full details of a specific dictionary
        - Use when: Reviewing dictionary items/entries
        - Use when: Checking dictionary metadata
        - Don't use when: You need an overview of all dictionaries (use torna_list_dictionaries instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if dictionary doesn't exist (404 status)
        - Returns formatted detailed dictionary information
    """
    try:
        # Format data for Torna API
        data = {
            "id": params.dict_id
        }
        
        # Make API request
        result = await _make_api_request(
            interface_name="dict.detail",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "dict.detail")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_delete_dictionary",
    annotations={
        "title": "Delete Dictionary",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_delete_dictionary(params: DictDeleteInput) -> str:
    """Delete a dictionary from Torna.

    This tool permanently removes a dictionary from Torna. This operation cannot be undone.

    Args:
        params (DictDeleteInput): Validated input parameters containing:
            - dict_id (str): Dictionary ID to delete (required)
            - access_token (str): Module token for authentication (required)

    Returns:
        str: JSON-formatted or markdown-formatted response containing operation results
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "dict_id",
                "deleted": true
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Removing obsolete dictionaries
        - Use when: Cleaning up dictionary collections
        - Don't use when: You need to keep the dictionary (use torna_update_dictionary instead)
        - Don't use when: You just want to check dictionary details (use torna_get_dictionary_detail instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if dictionary doesn't exist (404 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = {
            "id": params.dict_id
        }
        
        # Make API request
        result = await _make_api_request(
            interface_name="dict.delete",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "dict.delete")
        
    except Exception as e:
        return _handle_api_error(e)

# Module API Tool implementations
@mcp.tool(
    name="torna_create_module",
    annotations={
        "title": "Create Module",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def torna_create_module(params: ModuleCreateInput) -> str:
    """Create a new module in Torna.

    This tool creates a new module within a project. Modules help organize
    related API documentation and functionality.

    Args:
        params (ModuleCreateInput): Validated input parameters containing:
            - name (str): Module name (required, 1-100 characters)
            - description (str, optional): Module description
            - project_id (str): Project ID to which the module belongs (required)
            - access_token (str): Module token for authentication

    Returns:
        str: JSON-formatted or markdown-formatted response containing operation results
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "module_id",
                "name": "module_name",
                "description": "module description",
                "projectId": "project_id",
                "token": "generated_token"
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Creating new modules for project organization
        - Use when: Setting up new API functionality areas
        - Use when: Organizing related API endpoints
        - Don't use when: Creating dictionaries (use torna_create_dictionary instead)
        - Don't use when: Creating documents (use torna_push_document instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if project doesn't exist (404 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = {
            "name": params.name,
            "projectId": params.project_id
        }
        
        if params.description:
            data["description"] = params.description
        
        # Make API request
        result = await _make_api_request(
            interface_name="module.create",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "module.create")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_update_module",
    annotations={
        "title": "Update Module",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def torna_update_module(params: ModuleUpdateInput) -> str:
    """Update an existing module in Torna.

    This tool allows you to modify the name and description of an existing module.

    Args:
        params (ModuleUpdateInput): Validated input parameters containing:
            - module_id (str): Module ID to update (required)
            - name (str, optional): New module name (1-100 characters)
            - description (str, optional): New module description
            - access_token (str): Module token for authentication

    Returns:
        str: JSON-formatted or markdown-formatted response containing operation results
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "module_id",
                "name": "updated_name",
                "description": "updated description",
                "updated": true
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Updating module metadata
        - Use when: Renaming modules for better organization
        - Use when: Adding descriptions to existing modules
        - Don't use when: Creating new modules (use torna_create_module instead)
        - Don't use when: You need to get module details (use toma_get_module_detail instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if module doesn't exist (404 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = {
            "id": params.module_id
        }
        
        if params.name:
            data["name"] = params.name
        
        if params.description:
            data["description"] = params.description
        
        # Make API request
        result = await _make_api_request(
            interface_name="module.update",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "module.update")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_list_modules",
    annotations={
        "title": "List Modules",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_list_modules(params: ModuleListInput) -> str:
    """List modules in Torna with pagination support.

    This tool retrieves a list of modules with support for pagination
    to handle large collections efficiently. You can filter by project ID.

    Args:
        params (ModuleListInput): Validated input parameters containing:
            - project_id (str, optional): Project ID to filter modules
            - access_token (str): Module token for authentication (required)
            - limit (int, optional): Maximum results to return, 1-100 (default: 20)
            - offset (int, optional): Number of results to skip for pagination (default: 0)

    Returns:
        str: JSON-formatted or markdown-formatted response containing module list with pagination info
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "total": 30,
                "list": [
                    {
                        "id": "module_id",
                        "name": "user_module",
                        "description": "User management module",
                        "projectId": "project_id",
                        "token": "module_token",
                        "createdAt": "2024-01-01T00:00:00Z"
                    }
                ],
                "hasMore": true,
                "nextOffset": 20
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting an overview of all modules in a project
        - Use when: Finding specific modules by browsing the list
        - Use when: Managing module collections
        - Don't use when: You need details about a specific module (use toma_get_module_detail instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns formatted module list with pagination info
    """
    try:
        # Format data for Torna API
        data = {
            "limit": params.limit or 20,
            "offset": params.offset or 0
        }
        
        if params.project_id:
            data["projectId"] = params.project_id
        
        # Make API request
        result = await _make_api_request(
            interface_name="module.list",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "module.list")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_get_module_detail",
    annotations={
        "title": "Get Module Detail",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_get_module_detail(params: ModuleDetailInput) -> str:
    """Get detailed information about a specific module in Torna.

    This tool retrieves comprehensive details about a module including
    its configuration and metadata.

    Args:
        params (ModuleDetailInput): Validated input parameters containing:
            - module_id (str): Module ID to retrieve (required)
            - access_token (str): Module token for authentication (required)

    Returns:
        str: JSON-formatted or markdown-formatted response containing detailed module information
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "module_id",
                "name": "user_management",
                "description": "User management and authentication module",
                "projectId": "project_id",
                "token": "module_token",
                "docsCount": 25,
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z"
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting full details of a specific module
        - Use when: Reviewing module configuration and statistics
        - Use when: Checking module metadata
        - Don't use when: You need an overview of all modules (use toma_list_modules instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if module doesn't exist (404 status)
        - Returns formatted detailed module information
    """
    try:
        # Format data for Torna API
        data = {
            "id": params.module_id
        }
        
        # Make API request
        result = await _make_api_request(
            interface_name="module.detail",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "module.detail")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_delete_module",
    annotations={
        "title": "Delete Module",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def torna_delete_module(params: ModuleDeleteInput) -> str:
    """Delete a module from Torna.

    This tool permanently removes a module from Torna. This operation cannot be undone.

    Args:
        params (ModuleDeleteInput): Validated input parameters containing:
            - module_id (str): Module ID to delete (required)
            - access_token (str): Module token for authentication

    Returns:
        str: JSON-formatted or markdown-formatted response containing operation results
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "module_id",
                "deleted": true
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Removing obsolete modules
        - Use when: Cleaning up module collections
        - Don't use when: You need to keep the module (use toma_update_module instead)
        - Don't use when: You just want to check module details (use toma_get_module_detail instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if module doesn't exist (404 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = {
            "id": params.module_id
        }
        
        # Make API request
        result = await _make_api_request(
            interface_name="module.delete",
            version="1.0",
            data=data,
            access_token=params.access_token
        )
        
        return _format_response(result, params.response_format, "module.delete")
        
    except Exception as e:
        return _handle_api_error(e)

if __name__ == "__main__":
    mcp.run()
