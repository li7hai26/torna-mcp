#!/usr/bin/env python3
"""
Torna MCP Server

This MCP server provides tools to interact with Torna OpenAPI for managing API documentation.
Based on the real Torna API at http://localhost:7700/api with correct interface specifications.

Real Torna API interfaces:
- doc.push: Push documents to Torna
- doc.get: Get document details

Environment Variables Required:
- TORNA_URL: Torna private deployment URL (default: "http://localhost:7700/api")
- TORNA_TOKEN: Single module token for authentication
"""

import os
import json
import urllib.parse
from typing import List, Dict, Any, Optional
from enum import Enum
import httpx
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("torna_mcp")

# Constants
CHARACTER_LIMIT = 25000
DEFAULT_API_URL = "http://localhost:7700/api"

# Environment variables (will be set in main function)
API_BASE_URL: Optional[str] = None
TORNA_TOKEN: str = ""

def _validate_environment():
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
    is_folder: bool = Field(default=False, description="Whether this is a folder/category")
    parent_id: Optional[str] = Field(default=None, description="Parent category ID")
    is_show: bool = Field(default=True, description="Whether to show this document")
    
    # Request parameters
    request_params: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Request parameters")
    header_params: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Header parameters")
    path_params: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Path parameters")
    query_params: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Query parameters")
    
    # Response parameters
    response_params: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Response parameters")
    
    # Error codes
    error_codes: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Error codes")
    
    # Debug environment
    debug_env_name: Optional[str] = Field(default=None, description="Debug environment name")
    debug_env_url: Optional[str] = Field(default=None, description="Debug environment URL")
    
    # Common error codes (applies to all documents in this push)
    common_error_codes: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Common error codes")
    
    # Author
    author: Optional[str] = Field(default=None, description="Document author")
    
    # Response format
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

class DocGetInput(BaseModel):
    """Input model for document get operation."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    doc_id: str = Field(..., description="Document ID to retrieve")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

# Shared utility functions
def _make_api_request(interface_name: str, version: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Make request to Torna API with correct format."""
    # Torna API expects data to be URL-encoded JSON string
    json_data = json.dumps(data, ensure_ascii=False)
    encoded_data = urllib.parse.quote(json_data)
    
    request_data = {
        "name": interface_name,
        "version": version,
        "data": encoded_data,
        "access_token": TORNA_TOKEN
    }
    
    with httpx.Client() as client:
        response = client.post(
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
    """Format input data for doc.push API according to Torna specification."""
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
            "url": input_data.debug_env_url
        }
    
    return {"apis": [doc_data]}

def _format_response(result: Dict[str, Any], response_format: ResponseFormat, interface_name: str) -> str:
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
                lines.append(f"- **Document Name**: {result['data'].get('name', 'N/A')}")
                lines.append(f"- **Document ID**: {result['data'].get('id', 'N/A')}")
                lines.append(f"- **Status**: {result['data'].get('status', 'N/A')}")
            else:
                lines.append("Documents have been pushed successfully.")
        
        elif interface_name == "doc.get":
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
        - Don't use when: You only want to get existing documents (use torna_get_document instead)

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
        result = _make_api_request(
            interface_name="doc.push",
            version="1.0",
            data=data
        )
        
        return _format_response(result, params.response_format, "doc.push")
        
    except Exception as e:
        return _handle_api_error(e)

@mcp.tool(
    name="torna_get_document",
    annotations={
        "title": "Get Document from Torna",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def toma_get_document(params: DocGetInput) -> str:
    """Get detailed information about a specific document in Torna.

    This tool retrieves comprehensive details about a single document including
    request parameters, response parameters, headers, and error codes.
    Based on the real Torna API doc.get interface.

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
        data = {
            "id": params.doc_id
        }
        
        # Make API request
        result = _make_api_request(
            interface_name="doc.get",
            version="1.0",
            data=data
        )
        
        return _format_response(result, params.response_format, "doc.get")
        
    except Exception as e:
        return _handle_api_error(e)

# Main function
def main():
    """Main function to start the MCP server."""
    # Check for help or version flags first
    import sys
    if len(sys.argv) > 1 and (sys.argv[1] in ['--help', '-h', '--version', '-v']):
        if sys.argv[1] in ['--help', '-h']:
            print("Torna MCP Server - Help")
            print("Usage: torna-mcp")
            print("")
            print("Environment Variables:")
            print("  TORNA_URL: Torna API base URL (default: http://localhost:7700/api)")
            print("  TORNA_TOKEN: Torna module token (required)")
            print("")
            print("Available tools:")
            print("  - torna_push_document: Push documents to Torna")
            print("  - torna_get_document: Get document details")
            return
    
    try:
        # Validate environment
        _validate_environment()
        print(f"Starting Torna MCP Server...")
        print(f"API Base URL: {API_BASE_URL}")
        print(f"Token configured: {'*' * 8}{TORNA_TOKEN[-4:] if TORNA_TOKEN else 'None'}")
        
        # Run the server
        mcp.run()
        
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set TORNA_TOKEN environment variable")
        print("Usage: export TORNA_TOKEN='your-token-here'")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()