#!/usr/bin/env python3
"""
Torna MCP Server

This MCP server provides tools to interact with Torna OpenAPI for managing API documentation.
Based on the real Torna API at http://localhost:7700/api with correct interface specifications.

Real Torna API interfaces:
- doc.push: Push documents to Torna
- doc.detail: Get document details
- module.get: Get application module information (version 1.0)
- doc.list: List all documents in application (version 1.0)
- doc.details: Get multiple document details (version 1.0)

Environment Variables Required:
- TORNA_URL: Torna private deployment URL (default: "http://localhost:7700/api")
- TORNA_TOKEN: Single module token for authentication
"""

import asyncio
import json
import os
import urllib.parse
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

# Initialize the MCP server
torna_mcp_server = FastMCP("torna_mcp")

# Constants
CHARACTER_LIMIT = 25000
DEFAULT_API_URL = "http://localhost:7700/api"

# Environment variables
API_BASE_URL: Optional[str] = None
TORNA_TOKEN: str = ""


def _validate_environment() -> tuple[str, str]:
    """Validate required environment variables."""
    global API_BASE_URL, TORNA_TOKEN

    API_BASE_URL = os.getenv("TORNA_URL", DEFAULT_API_URL)
    TORNA_TOKEN = os.getenv("TORNA_TOKEN", "")

    if not TORNA_TOKEN:
        raise ValueError("TORNA_TOKEN environment variable is required")

    return API_BASE_URL, TORNA_TOKEN


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
class DocPushInput(BaseModel):
    """Input model for document push operation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Document basic info
    name: str = Field(..., description="Document name", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, description="Document description")
    url: str = Field(..., description="API endpoint URL (e.g., '/api/users')")
    http_method: HttpMethod = Field(default=HttpMethod.GET, description="HTTP method")
    content_type: str = Field(default="application/json", description="Content type")
    is_folder: bool = Field(
        default=False, description="Whether this is a folder/category"
    )
    parent_id: Optional[str] = Field(default=None, description="Parent category ID")
    is_show: bool = Field(default=True, description="Whether to show this document")

    # Request parameters
    request_params: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Request parameters"
    )
    header_params: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Header parameters"
    )
    path_params: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Path parameters"
    )
    query_params: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Query parameters"
    )

    # Response parameters
    response_params: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list, description="Response parameters"
    )

    # Error codes
    error_codes: Optional[List[Dict[str, str]]] = Field(
        default_factory=list, description="Error codes"
    )

    # Debug environment
    debug_env_name: Optional[str] = Field(
        default=None, description="Debug environment name"
    )
    debug_env_url: Optional[str] = Field(
        default=None, description="Debug environment URL"
    )

    # Common error codes (applies to all documents in this push)
    common_error_codes: Optional[List[Dict[str, str]]] = Field(
        default_factory=list, description="Common error codes"
    )

    # Author
    author: Optional[str] = Field(default=None, description="Document author")

    # Response format
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format"
    )


class DocGetInput(BaseModel):
    """Input model for document get operation."""

    model_config = ConfigDict(str_strip_whitespace=True)

    doc_id: str = Field(..., description="Document ID to retrieve")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN, description="Output format"
    )


# Additional input models for new API interfaces
class ModuleGetInput(BaseModel):
    """Input model for module.get operation."""
    model_config = ConfigDict(str_strip_whitespace=True)
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")


class DocListInput(BaseModel):
    """Input model for doc.list operation."""
    model_config = ConfigDict(str_strip_whitespace=True)
    doc_ids: Optional[List[str]] = Field(default_factory=list, description="Document IDs to list (optional)")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")


class DocDetailsInput(BaseModel):
    """Input model for doc.details operation."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    doc_ids: List[str] = Field(..., description="Document IDs to retrieve details for")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")


# Shared utility functions
def _make_api_request(
    interface_name: str, version: str, data: Dict[str, Any]
) -> Dict[str, Any]:
    """Make request to Torna API with correct format."""
    # Torna API expects data to be URL-encoded JSON string
    json_data = json.dumps(data, ensure_ascii=False)
    encoded_data = urllib.parse.quote(json_data)

    request_data = {
        "name": interface_name,
        "version": version,
        "data": encoded_data,
        "access_token": TORNA_TOKEN,
    }

    with httpx.Client() as client:
        response = client.post(
            API_BASE_URL,
            json=request_data,
            timeout=30.0,
            headers={"Content-Type": "application/json"},
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
            return (
                "Error: Rate limit exceeded. Please wait before making more requests."
            )
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    elif isinstance(e, ValueError) and "TORNA" in str(e):
        return f"Configuration error: {str(e)}"
    return f"Error: Unexpected error occurred: {type(e).__name__}"


def _format_doc_push_data(input_data: DocPushInput) -> Dict[str, Any]:
    """Format input data for doc.push API according to Torna specification."""
    doc_data = {
        "name": input_data.name,
        "description": input_data.description or "",
        "url": input_data.url,
        "httpMethod": input_data.http_method.value,
        "contentType": input_data.content_type,
        "isFolder": input_data.is_folder,
        "isShow": input_data.is_show,
    }

    if input_data.parent_id:
        doc_data["parentId"] = input_data.parent_id

    if input_data.author:
        doc_data["author"] = input_data.author

    # Set parameters if provided
    if input_data.request_params:
        doc_data["requestParams"] = input_data.request_params

    if input_data.header_params:
        doc_data["headerParams"] = input_data.header_params

    if input_data.path_params:
        doc_data["pathParams"] = input_data.path_params

    if input_data.query_params:
        doc_data["queryParams"] = input_data.query_params

    if input_data.response_params:
        doc_data["responseParams"] = input_data.response_params

    if input_data.error_codes:
        doc_data["errorCodeParams"] = input_data.error_codes

    # Handle debug environment
    if input_data.debug_env_name and input_data.debug_env_url:
        doc_data["debugEnv"] = {
            "name": input_data.debug_env_name,
            "url": input_data.debug_env_url,
        }

    return {"apis": [doc_data]}


def _format_response(
    result: Dict[str, Any], response_format: ResponseFormat, interface_name: str
) -> str:
    """Format API response based on requested format."""
    if response_format == ResponseFormat.JSON:
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
                lines.append(
                    f"- **Document Name**: {result['data'].get('name', 'N/A')}"
                )
                lines.append(f"- **Document ID**: {result['data'].get('id', 'N/A')}")
                lines.append(f"- **Status**: {result['data'].get('status', 'N/A')}")
            else:
                lines.append("Documents have been pushed successfully.")

        elif interface_name == "doc.detail":
            doc = result.get("data", {})
            if doc:
                lines.append(f"## {doc.get('name', 'Document Detail')}")
                lines.append(f"- **ID**: {doc.get('id', 'N/A')}")
                lines.append(f"- **URL**: {doc.get('url', 'N/A')}")
                lines.append(f"- **Method**: {doc.get('httpMethod', 'N/A')}")
                lines.append(f"- **Content Type**: {doc.get('contentType', 'N/A')}")

                if doc.get("description"):
                    lines.append(f"- **Description**: {doc.get('description')}")

                # Handle parameters based on TornaDocParamDTO structure
                params_by_style = {
                    0: ("Header Parameters", []),
                    1: ("Request Parameters", []),
                    2: ("Response Parameters", []),
                    3: ("Error Code Parameters", [])
                }

                for param in doc.get("requestParams", []):
                    style = param.get("style", 1)  # Default to request params
                    params_by_style[style][1].append(param)

                for style_name, params in params_by_style.items():
                    if params[1]:  # If there are parameters of this type
                        lines.append(f"\n### {params[0]}")
                        for param in params[1]:
                            required_mark = "⚠️ " if param.get("required") == 1 else "✅ "
                            lines.append(
                                f"- **{param.get('name', 'N/A')}** ({param.get('type', 'N/A')}) {required_mark}"
                            )
                            if param.get("description"):
                                lines.append(f"  - {param.get('description')}")
                            if param.get("example"):
                                lines.append(f"  - Example: {param.get('example')}")
                            if param.get("maxLength"):
                                lines.append(f"  - Max Length: {param.get('maxLength')}")
            else:
                lines.append("Document not found.")

        elif interface_name == "module.get":
            module_info = result.get("data", {})
            if module_info:
                lines.append(f"## {module_info.get('name', 'Module Information')}")
                lines.append(f"- **Module ID**: {module_info.get('id', 'N/A')}")
                lines.append(f"- **Description**: {module_info.get('description', 'N/A')}")
                lines.append(f"- **Status**: {module_info.get('status', 'N/A')}")
            else:
                lines.append("Module information not found.")

        elif interface_name == "doc.list":
            docs = result.get("data", [])
            if docs:
                lines.append(f"## Document List ({len(docs)} documents)")
                lines.append("")
                for doc in docs:
                    folder_status = "📁" if doc.get("isFolder") == 1 else "📄"
                    lines.append(f"{folder_status} **{doc.get('name', 'N/A')}**")
                    lines.append(f"  - **ID**: {doc.get('id', 'N/A')}")
                    if doc.get("url"):
                        lines.append(f"  - **URL**: {doc.get('url', 'N/A')}")
                        lines.append(f"  - **Method**: {doc.get('httpMethod', 'N/A')}")
                    lines.append(f"  - **Version**: {doc.get('version', 'N/A')}")
                    if doc.get("description"):
                        lines.append(f"  - **Description**: {doc.get('description')}")
                    lines.append("")
            else:
                lines.append("No documents found.")

        elif interface_name == "doc.details":
            docs = result.get("data", [])
            if docs:
                lines.append(f"## Document Details ({len(docs)} documents)")
                lines.append("")
                for doc in docs:
                    lines.append(f"### {doc.get('name', 'Document Detail')}")
                    lines.append(f"- **ID**: {doc.get('id', 'N/A')}")
                    lines.append(f"- **URL**: {doc.get('url', 'N/A')}")
                    lines.append(f"- **Method**: {doc.get('httpMethod', 'N/A')}")
                    lines.append(f"- **Version**: {doc.get('version', 'N/A')}")

                    if doc.get("description"):
                        lines.append(f"- **Description**: {doc.get('description')}")

                    # Group parameters by style
                    params_by_style = {
                        0: ("Header Parameters", []),
                        1: ("Request Parameters", []),
                        2: ("Response Parameters", []),
                        3: ("Error Code Parameters", [])
                    }

                    for param in doc.get("requestParams", []):
                        style = param.get("style", 1)
                        if style in params_by_style:
                            params_by_style[style][1].append(param)

                    for style_name, params in params_by_style.items():
                        if params[1]:
                            lines.append(f"\n#### {params[0]}")
                            for param in params[1]:
                                required_mark = "⚠️ " if param.get("required") == 1 else "✅ "
                                lines.append(
                                    f"- **{param.get('name', 'N/A')}** ({param.get('type', 'N/A')}) {required_mark}"
                                )
                                if param.get("description"):
                                    lines.append(f"  - {param.get('description')}")
                                if param.get("example"):
                                    lines.append(f"  - Example: {param.get('example')}")
                                if param.get("maxLength"):
                                    lines.append(f"  - Max Length: {param.get('maxLength')}")
                    lines.append("")
            else:
                lines.append("No document details found.")
    else:
        lines.append("❌ **Operation failed**")
        lines.append("")
        lines.append(f"- **Error Code**: {result.get('code', 'Unknown')}")
        lines.append(f"- **Error Message**: {result.get('msg', 'Unknown error')}")

    response_text = "\n".join(lines)

    # Check character limit
    if len(response_text) > CHARACTER_LIMIT:
        truncated_text = response_text[: CHARACTER_LIMIT - 100]
        truncated_text += "\n\n... (response truncated due to length limit)"
        return truncated_text

    return response_text


# Tool implementations
@torna_mcp_server.tool(
    name="torna_push_document",
    annotations={
        "title": "Push Document to Torna",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def torna_push_document(params: DocPushInput) -> str:
    """Push a document to Torna platform.

    This tool creates or updates API documentation in Torna. Based on the real Torna API
    doc.push interface at http://localhost:7700/api.

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
            - path_params (list, optional): Path parameters
            - query_params (list, optional): Query parameters
            - response_params (list, optional): Response parameters
            - error_codes (list, optional): Error codes with structure:
              [{"code": "1001", "msg": "error message", "solution": "solution"}]
            - debug_env_name (str, optional): Debug environment name
            - debug_env_url (str, optional): Debug environment URL
            - common_error_codes (list, optional): Common error codes for all documents
            - author (str, optional): Document author

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
        - Don't use when: You only want to get existing documents (use torna_get_document_detail instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if parent category doesn't exist (404 status)
        - Returns formatted success or error message
    """
    try:
        # Format data for Torna API
        data = _format_doc_push_data(params)

        # Add common error codes if provided
        if params.common_error_codes:
            data["commonErrorCodes"] = params.common_error_codes

        # Make API request
        result = _make_api_request(interface_name="doc.push", version="1.0", data=data)

        return _format_response(result, params.response_format, "doc.push")

    except Exception as e:
        return _handle_api_error(e)


@torna_mcp_server.tool(
    name="torna_get_document_detail",
    annotations={
        "title": "Get Document from Torna",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def torna_get_document_detail(params: DocGetInput) -> str:
    """Get detailed information about a specific document in Torna.

    This tool retrieves comprehensive details about a single document including
    request parameters, response parameters, headers, and error codes.
    Based on the real Torna API doc.detail interface.

    Args:
        params (DocGetInput): Validated input parameters containing:
            - doc_id (str): Document ID to retrieve (required)

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
        - Don't use when: You need to create new documents (use torna_push_document instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid (403 status)
        - Returns "Error: Resource not found" if document doesn't exist (404 status)
        - Returns formatted detailed document information
    """
    try:
        # Format data for Torna API
        data = {"id": params.doc_id}

        # Make API request
        result = _make_api_request(interface_name="doc.detail", version="1.0", data=data)

        return _format_response(result, params.response_format, "doc.detail")

    except Exception as e:
        return _handle_api_error(e)


@torna_mcp_server.tool(
    name="torna_get_module",
    annotations={
        "title": "Get Application Module Information",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def torna_get_module(params: ModuleGetInput) -> str:
    """Get application module information from Torna.

    This tool retrieves basic information about the current module/application
    based on the real Torna API module.get interface (version 1.0).

    Args:
        params: Validated input parameters (currently no required parameters)

    Returns:
        str: JSON-formatted or markdown-formatted response containing module information
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "name": "Module Name",
                "description": "Module Description",
                "id": "module_id",
                "status": "active"
            }
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting basic information about the current module
        - Use when: Verifying module name and details
        - Don't use when: You need document details (use torna_get_document_detail instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid
        - Returns formatted success or error message
    """
    try:
        # Module.get doesn't require specific parameters
        result = _make_api_request(
            interface_name="module.get",
            version="1.0",
            data={}
        )
        
        return _format_response(result, params.response_format, "module.get")
        
    except Exception as e:
        return _handle_api_error(e)


@torna_mcp_server.tool(
    name="torna_list_documents",
    annotations={
        "title": "List All Documents in Application",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def torna_list_documents(params: DocListInput) -> str:
    """List all documents in the application from Torna.

    This tool retrieves a comprehensive list of all documents available
    in the current module based on the real Torna API doc.list interface (version 1.0).
    
    This is the key tool that solves the "获取所有文档详情" requirement!

    Args:
        params: Validated input parameters (currently no required parameters)

    Returns:
        str: JSON-formatted or markdown-formatted response containing document list
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": [
                {
                    "id": "doc_123",
                    "name": "Document Name",
                    "url": "/api/endpoint",
                    "httpMethod": "GET",
                    "description": "Document description"
                }
            ]
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting a complete list of all documents in the module
        - Use when: Discovering document IDs for subsequent detail retrieval
        - Use when: Managing document inventory
        - Don't use when: You need detailed parameters (use torna_get_document_detail_batch instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid
        - Returns formatted document list or error message
    """
    try:
        # Doc.list requires docIds parameter (even if empty)
        data = {"docIds": params.doc_ids or []}
        result = _make_api_request(
            interface_name="doc.list",
            version="1.0",
            data=data
        )
        
        return _format_response(result, params.response_format, "doc.list")
        
    except Exception as e:
        return _handle_api_error(e)


@torna_mcp_server.tool(
    name="torna_get_document_detail_batch",
    annotations={
        "title": "Get Multiple Document Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def torna_get_document_detail_batch(params: DocDetailsInput) -> str:
    """Get detailed information for multiple documents at once.

    This tool retrieves comprehensive details for multiple documents simultaneously
    based on the real Torna API doc.details interface (version 1.0).
    
    This is perfect for getting all document details after listing them!

    Args:
        params (DocDetailsInput): Validated input parameters containing:
            - doc_ids (List[str]): Array of document IDs to retrieve details for
            - response_format (str): Output format (markdown or json)

    Returns:
        str: JSON-formatted or markdown-formatted response containing detailed document information
        
        Success response:
        {
            "code": 0,
            "msg": "success",
            "data": [
                {
                    "id": "doc_123",
                    "name": "Document Name",
                    "url": "/api/endpoint",
                    "httpMethod": "GET",
                    "requestParams": [...],
                    "responseParams": [...],
                    "errorCodeParams": [...]
                }
            ]
        }

        Error response:
        "Error: <error message>"

    Examples:
        - Use when: Getting detailed parameters for multiple documents
        - Use when: Bulk processing document information
        - Use when: After using torna_list_documents to get all document IDs
        - Don't use when: You only need basic information (use torna_list_documents instead)

    Error Handling:
        - Input validation errors are handled by Pydantic model
        - Returns "Error: Permission denied" if access token is invalid
        - Returns "Error: Resource not found" if any document doesn't exist
        - Returns formatted detailed document information
    """
    try:
        # Format data for doc.details API
        data = {
            "ids": params.doc_ids
        }
        
        result = _make_api_request(
            interface_name="doc.details",
            version="1.0",
            data=data
        )
        
        return _format_response(result, params.response_format, "doc.details")
        
    except Exception as e:
        return _handle_api_error(e)


# Main function
def main():
    """Main function to start the MCP server."""
    # Check for help or version flags first
    import sys

    if len(sys.argv) > 1 and (sys.argv[1] in ["--help", "-h", "--version", "-v"]):
        if sys.argv[1] in ["--help", "-h"]:
            print("Torna MCP Server - Help")
            print("Usage: toma-mcp")
            print("")
            print("Environment Variables:")
            print(
                "  TORNA_URL: Torna API base URL (default: http://localhost:7700/api)"
            )
            print("  TORNA_TOKEN: Torna module token (required)")
            print("")
            print("Available tools:")
            print("  - torna_push_document: Push documents to Torna")
            print("  - torna_get_document_detail: Get single document details")
            print("  - torna_get_module: Get application module information")
            print("  - torna_list_documents: List all documents in application")
            print("  - torna_get_document_detail_batch: Get multiple document details")
            return
        elif sys.argv[1] in ["--version", "-v"]:
            print("toma-mcp version 0.1.0")
            return

    try:
        # Validate environment
        _validate_environment()
        print(f"Starting Torna MCP Server...")
        print(f"API Base URL: {API_BASE_URL}")
        print(
            f"Token configured: {'*' * 8}{TORNA_TOKEN[-4:] if TORNA_TOKEN else 'None'}"
        )

        # Run the server
        asyncio.run(torna_mcp_server.run())

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set TORNA_TOKEN environment variable")
        print("Usage: export TORNA_TOKEN='your-token-here'")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)
