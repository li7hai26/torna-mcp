#!/usr/bin/env python3
"""
Torna MCP Server - 基于重构客户端版本

This MCP server provides tools to interact with Torna OpenAPI for managing API documentation.
Based on the refactored client architecture following Java SDK design patterns.

Environment Variables Required:
- TORNA_URL: Torna private deployment URL (default: "http://localhost:7700/api")
- TORNA_TOKEN: Single module token for authentication
"""

import asyncio
import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# 导入重构的客户端 (使用外部包)
from torna_sdk import (
    TornaClient,
    TornaAPIError,
    TornaConfig,
    DocListRequest,
    DocGetRequest,
    DocPushRequest,
    DocListResponse,
    DocGetResponse,
    DocPushResponse,
    ModuleGetRequest,
    ModuleGetResponse,
    DocDetailsRequest,
    DocDetailsResponse,
    # 新增的完整功能
    DocCategoryCreateRequest,
    DocCategoryListRequest,
    DocCategoryNameUpdateRequest,
    EnumPushRequest,
    EnumBatchPushRequest,
    ModuleDebugEnvSetRequest,
    ModuleDebugEnvDeleteRequest,
    DocCategoryCreateResponse,
    DocCategoryListResponse,
    DocCategoryNameUpdateResponse,
    EnumPushResponse,
    ModuleDebugEnvSetResponse,
    ModuleDebugEnvDeleteResponse,
)

# Initialize the MCP server
torna_mcp_server = FastMCP("torna_mcp_refactored")

# Constants
CHARACTER_LIMIT = 25000
DEFAULT_API_URL = "http://localhost:7700"

# Environment variables
API_BASE_URL: Optional[str] = None
TORNA_TOKEN: str = ""


def _validate_environment() -> tuple[str, str]:
    """验证必需的环境变量。"""
    global API_BASE_URL, TORNA_TOKEN

    API_BASE_URL = os.getenv("TORNA_URL", DEFAULT_API_URL)
    TORNA_TOKEN = os.getenv("TORNA_TOKEN", "")

    if not TORNA_TOKEN:
        raise ValueError(
            "TORNA_TOKEN environment variable is required. "
            "Please set it to your Torna module access token."
        )

    return API_BASE_URL, TORNA_TOKEN


# Input models
class ResponseFormat(str, Enum):
    """输出格式枚举"""
    JSON = "json"
    MARKDOWN = "markdown"


class DocListInput(BaseModel):
    """文档列表输入参数 - 使用重构客户端"""
    doc_ids: Optional[List[str]] = Field(default=None, description="要列出的文档ID列表（可选）")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class DocGetInput(BaseModel):
    """文档详情输入参数 - 使用重构客户端"""
    doc_id: str = Field(..., description="文档ID")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class DocPushInput(BaseModel):
    """文档推送输入参数 - 使用重构客户端"""
    name: str = Field(..., description="文档名称")
    description: Optional[str] = Field(None, description="文档描述")
    url: str = Field(..., description="API端点URL，例如 '/api/users'")
    http_method: str = Field(..., description="HTTP方法 (GET, POST, PUT, DELETE, PATCH)")
    content_type: str = Field(default="application/json", description="内容类型")
    is_folder: bool = Field(default=False, description="是否为文件夹/分类")
    parent_id: Optional[str] = Field(None, description="父分类ID")
    is_show: bool = Field(default=True, description="是否显示此文档")
    request_params: Optional[List[Dict[str, Any]]] = Field(default=None, description="请求参数")
    header_params: Optional[List[Dict[str, Any]]] = Field(default=None, description="头部参数")
    path_params: Optional[List[Dict[str, Any]]] = Field(default=None, description="路径参数")
    query_params: Optional[List[Dict[str, Any]]] = Field(default=None, description="查询参数")
    response_params: Optional[List[Dict[str, Any]]] = Field(default=None, description="响应参数")
    error_codes: Optional[List[Dict[str, str]]] = Field(default=None, description="错误码")
    debug_env_name: Optional[str] = Field(None, description="调试环境名称")
    debug_env_url: Optional[str] = Field(None, description="调试环境URL")
    common_error_codes: Optional[List[Dict[str, str]]] = Field(default=None, description="通用错误码")
    author: Optional[str] = Field(None, description="文档作者")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class ModuleInfoInput(BaseModel):
    """模块信息输入参数 - 使用重构客户端"""
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class BatchDocDetailInput(BaseModel):
    """批量文档详情输入参数 - 使用重构客户端"""
    doc_ids: List[str] = Field(..., description="要获取详情的文档ID列表")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


# ==================== 新增的完整功能输入模型 ====================

class DocCategoryCreateInput(BaseModel):
    """创建分类输入参数"""
    name: str = Field(..., description="分类名称")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class DocCategoryListInput(BaseModel):
    """分类列表输入参数"""
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class DocCategoryNameUpdateInput(BaseModel):
    """更新分类名称输入参数"""
    category_id: str = Field(..., description="分类ID")
    name: str = Field(..., description="新的分类名称")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class EnumPushInput(BaseModel):
    """枚举推送输入参数"""
    name: str = Field(..., description="枚举名称")
    description: Optional[str] = Field(default="", description="枚举说明")
    items: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="枚举项列表")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class EnumBatchPushInput(BaseModel):
    """批量枚举推送输入参数"""
    enums: List[Dict[str, Any]] = Field(..., description="枚举列表")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class ModuleDebugEnvSetInput(BaseModel):
    """设置调试环境输入参数"""
    name: str = Field(..., description="环境名称")
    url: str = Field(..., description="调试环境URL")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


class ModuleDebugEnvDeleteInput(BaseModel):
    """删除调试环境输入参数"""
    name: str = Field(..., description="环境名称")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="输出格式")


# Shared utility functions
def _format_response(result: Dict[str, Any], format_type: ResponseFormat, operation: str) -> str:
    """格式化响应输出 - 基于重构客户端"""
    try:
        if isinstance(result, dict) and "data" in result:
            data = result["data"]
        else:
            data = result
        
        if format_type == ResponseFormat.JSON:
            return json.dumps({
                "operation": operation,
                "success": True,
                "result": data
            }, ensure_ascii=False, indent=2)
        else:
            # Markdown format
            return _format_as_markdown(data, operation)
            
    except Exception as e:
        return f"Error formatting response: {str(e)}"


def _format_as_markdown(data: Any, operation: str) -> str:
    """将数据格式化为Markdown"""
    try:
        if isinstance(data, list):
            if not data:
                return f"## {operation}\n\n暂无数据"
            
            markdown = f"## {operation}\n\n"
            for item in data:
                if isinstance(item, dict):
                    markdown += f"### {item.get('name', 'Unknown')}\n\n"
                    for key, value in item.items():
                        if key not in ['name']:
                            markdown += f"- **{key}**: {value}\n"
                    markdown += "\n"
                else:
                    markdown += f"- {item}\n"
            return markdown
            
        elif isinstance(data, dict):
            markdown = f"## {operation}\n\n"
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    markdown += f"### {key}\n\n"
                    markdown += _format_as_markdown(value, f"{operation} - {key}")
                else:
                    markdown += f"- **{key}**: {value}\n"
            return markdown
            
        else:
            return f"## {operation}\n\n{str(data)}"
            
    except Exception as e:
        return f"## {operation}\n\nError formatting data: {str(e)}"


def _handle_api_error_refactored(e: Exception) -> str:
    """一致的错误格式化 - 基于重构客户端"""
    if isinstance(e, TornaAPIError):
        return f"Torna API Error {e.code}: {e.message}"
    elif hasattr(e, 'response'):  # httpx.HTTPStatusError
        if e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        return f"Error: API request failed with status {e.response.status_code}"
    elif "timeout" in str(e).lower():
        return "Error: Request timed out. Please try again."
    elif "TORNA_TOKEN" in str(e):
        return f"Configuration error: {str(e)}"
    return f"Error: Unexpected error occurred: {type(e).__name__}: {str(e)}"


def _format_doc_push_data_refactored(input_data: DocPushInput) -> List[Dict[str, Any]]:
    """格式化推送数据 - 基于重构客户端"""
    doc_data = {
        "name": input_data.name,
        "description": input_data.description or "",
        "url": input_data.url,
        "httpMethod": input_data.http_method.upper(),
        "contentType": input_data.content_type,
        "isFolder": "1" if input_data.is_folder else "0",
        "parentId": input_data.parent_id or "",
        "isShow": "1" if input_data.is_show else "0",
    }

    # 设置参数
    if input_data.header_params:
        doc_data["headerParams"] = input_data.header_params

    if input_data.request_params:
        doc_data["requestParams"] = input_data.request_params

    if input_data.path_params:
        doc_data["pathParams"] = input_data.path_params

    if input_data.query_params:
        doc_data["queryParams"] = input_data.query_params

    if input_data.response_params:
        doc_data["responseParams"] = input_data.response_params

    if input_data.error_codes:
        doc_data["errorCodeParams"] = input_data.error_codes

    return [doc_data]


# Tool implementations
@torna_mcp_server.tool(
    name="torna_list_documents",
    annotations={
        "title": "List Documents from Torna",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def torna_list_documents(params: DocListInput) -> str:
    """从 Torna 平台列出文档列表。

    基于重构客户端架构，参考 Java SDK 设计模式。

    Args:
        params (DocListInput): 验证的输入参数包含：
            - doc_ids (List[str], optional): 要列出的文档ID列表
            - response_format (ResponseFormat): 输出格式 (json 或 markdown)

    Returns:
        str: JSON格式化或markdown格式化的响应，包含操作结果

        成功响应:
        {
            "code": 0,
            "msg": "success", 
            "data": [...]
        }

        错误响应:
        "Error: <error message>"
    """
    try:
        # 验证环境变量
        base_url, token = _validate_environment()
        
        # 使用重构客户端
        with TornaClient(base_url, token) as client:
            if params.doc_ids:
                # 使用批量文档详情
                request = DocDetailsRequest(token, params.doc_ids)
                response = client.execute(request)
            else:
                # 使用文档列表
                request = DocListRequest(token)
                response = client.execute(request)
        
        # 检查响应是否成功
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Document List")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


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
    """从 Torna 平台获取特定文档的详细信息。

    基于重构客户端架构，参考 Java SDK 设计模式。

    Args:
        params (DocGetInput): 验证的输入参数包含：
            - doc_id (str): 文档ID（必需）
            - response_format (ResponseFormat): 输出格式 (json 或 markdown)

    Returns:
        str: JSON格式化或markdown格式化的响应，包含文档详情

        成功响应:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "doc_id",
                "name": "document_name",
                "description": "...",
                ...
            }
        }

        错误响应:
        "Error: <error message>"
    """
    try:
        # 验证环境变量
        base_url, token = _validate_environment()
        
        # 使用重构客户端
        with TornaClient(base_url, token) as client:
            request = DocGetRequest(token, params.doc_id)
            response = client.execute(request)
        
        # 检查响应是否成功
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Document Detail")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


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
    """推送文档到 Torna 平台。

    基于重构客户端架构，参考 Java SDK 设计模式。

    Args:
        params (DocPushInput): 验证的输入参数，包含所有文档信息和参数

    Returns:
        str: JSON格式化或markdown格式化的响应，包含操作结果

        成功响应:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "id": "doc_id",
                "name": "document_name", 
                "status": "created/updated"
            }
        }

        错误响应:
        "Error: <error message>"
    """
    try:
        # 验证环境变量
        base_url, token = _validate_environment()
        
        # 格式化推送数据
        apis_data = _format_doc_push_data_refactored(params)
        
        # 构建推送请求
        with TornaClient(base_url, token) as client:
            request = DocPushRequest(token)
            
            # 设置API数据
            request.set_apis(apis_data)
            
            # 设置调试环境（如果提供）
            if params.debug_env_name and params.debug_env_url:
                debug_envs = [{"name": params.debug_env_name, "url": params.debug_env_url}]
                request.set_debug_envs(debug_envs)
            
            response = client.execute(request)
        
        # 检查响应是否成功
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Document Push")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


@torna_mcp_server.tool(
    name="torna_get_module_info",
    annotations={
        "title": "Get Module Information from Torna", 
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def torna_get_module_info(params: ModuleInfoInput) -> str:
    """从 Torna 平台获取模块信息。

    基于重构客户端架构，参考 Java SDK 设计模式。

    Args:
        params (ModuleInfoInput): 验证的输入参数包含：
            - response_format (ResponseFormat): 输出格式 (json 或 markdown)

    Returns:
        str: JSON格式化或markdown格式化的响应，包含模块信息

        成功响应:
        {
            "code": 0,
            "msg": "success",
            "data": {
                "name": "module_name",
                "version": "1.0.0",
                ...
            }
        }

        错误响应:
        "Error: <error message>"
    """
    try:
        # 验证环境变量
        base_url, token = _validate_environment()
        
        # 使用重构客户端
        with TornaClient(base_url, token) as client:
            request = ModuleGetRequest(token)
            response = client.execute(request)
        
        # 检查响应是否成功
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Module Info")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


@torna_mcp_server.tool(
    name="torna_get_batch_documents",
    annotations={
        "title": "Get Multiple Document Details from Torna",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def torna_get_batch_documents(params: BatchDocDetailInput) -> str:
    """从 Torna 平台批量获取多个文档的详细信息。

    基于重构客户端架构，参考 Java SDK 设计模式。

    Args:
        params (BatchDocDetailInput): 验证的输入参数包含：
            - doc_ids (List[str]): 要获取详情的文档ID列表（必需）
            - response_format (ResponseFormat): 输出格式 (json 或 markdown)

    Returns:
        str: JSON格式化或markdown格式化的响应，包含批量文档详情

        成功响应:
        {
            "code": 0,
            "msg": "success",
            "data": [
                {"id": "doc1", "name": "API 1", ...},
                {"id": "doc2", "name": "API 2", ...}
            ]
        }

        错误响应:
        "Error: <error message>"
    """
    try:
        # 验证环境变量
        base_url, token = _validate_environment()
        
        # 使用重构客户端
        with TornaClient(base_url, token) as client:
            request = DocDetailsRequest(token, params.doc_ids)
            response = client.execute(request)
        
        # 检查响应是否成功
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Batch Document Details")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


# ==================== 新增的完整功能 MCP 工具 ====================

@torna_mcp_server.tool(
    name="torna_create_category",
    annotations={
        "title": "Create Category in Torna",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def torna_create_category(params: DocCategoryCreateInput) -> str:
    """在 Torna 平台创建分类。
    
    参考 Java SDK 的 DocCategoryCreateRequest 功能。
    
    Args:
        params (DocCategoryCreateInput): 创建分类的输入参数
        
    Returns:
        str: 分类创建结果
    """
    try:
        base_url, token = _validate_environment()
        
        with TornaClient(base_url, token) as client:
            request = DocCategoryCreateRequest(token, params.name)
            response = client.execute(request)
        
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Create Category")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


@torna_mcp_server.tool(
    name="torna_list_categories",
    annotations={
        "title": "List Categories from Torna",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def torna_list_categories(params: DocCategoryListInput) -> str:
    """从 Torna 平台获取分类列表。
    
    参考 Java SDK 的 DocCategoryListRequest 功能。
    
    Args:
        params (DocCategoryListInput): 列表分类的输入参数
        
    Returns:
        str: 分类列表结果
    """
    try:
        base_url, token = _validate_environment()
        
        with TornaClient(base_url, token) as client:
            request = DocCategoryListRequest(token)
            response = client.execute(request)
        
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "List Categories")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


@torna_mcp_server.tool(
    name="torna_update_category_name",
    annotations={
        "title": "Update Category Name in Torna",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def torna_update_category_name(params: DocCategoryNameUpdateInput) -> str:
    """更新 Torna 平台中的分类名称。
    
    参考 Java SDK 的 DocCategoryNameUpdateRequest 功能。
    
    Args:
        params (DocCategoryNameUpdateInput): 更新分类名称的输入参数
        
    Returns:
        str: 分类名称更新结果
    """
    try:
        base_url, token = _validate_environment()
        
        with TornaClient(base_url, token) as client:
            request = DocCategoryNameUpdateRequest(token, params.category_id, params.name)
            response = client.execute(request)
        
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Update Category Name")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


@torna_mcp_server.tool(
    name="torna_push_enum",
    annotations={
        "title": "Push Enum to Torna",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def torna_push_enum(params: EnumPushInput) -> str:
    """推送枚举到 Torna 平台。
    
    参考 Java SDK 的 EnumPushRequest 功能。
    
    Args:
        params (EnumPushInput): 推送枚举的输入参数
        
    Returns:
        str: 枚举推送结果
    """
    try:
        base_url, token = _validate_environment()
        
        with TornaClient(base_url, token) as client:
            request = EnumPushRequest(token, params.name, params.description, params.items)
            response = client.execute(request)
        
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Push Enum")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


@torna_mcp_server.tool(
    name="torna_batch_push_enums",
    annotations={
        "title": "Batch Push Enums to Torna",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def torna_batch_push_enums(params: EnumBatchPushInput) -> str:
    """批量推送枚举到 Torna 平台。
    
    参考 Java SDK 的 EnumBatchPushRequest 功能。
    
    Args:
        params (EnumBatchPushInput): 批量推送枚举的输入参数
        
    Returns:
        str: 批量枚举推送结果
    """
    try:
        base_url, token = _validate_environment()
        
        with TornaClient(base_url, token) as client:
            request = EnumBatchPushRequest(token, params.enums)
            response = client.execute(request)
        
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Batch Push Enums")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


@torna_mcp_server.tool(
    name="torna_set_debug_env",
    annotations={
        "title": "Set Debug Environment in Torna",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def torna_set_debug_env(params: ModuleDebugEnvSetInput) -> str:
    """设置 Torna 模块的调试环境。
    
    参考 Java SDK 的 ModuleDebugEnvSetRequest 功能。
    
    Args:
        params (ModuleDebugEnvSetInput): 设置调试环境的输入参数
        
    Returns:
        str: 调试环境设置结果
    """
    try:
        base_url, token = _validate_environment()
        
        with TornaClient(base_url, token) as client:
            request = ModuleDebugEnvSetRequest(token, params.name, params.url)
            response = client.execute(request)
        
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Set Debug Environment")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


@torna_mcp_server.tool(
    name="torna_delete_debug_env",
    annotations={
        "title": "Delete Debug Environment from Torna",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
        "openWorldHint": True,
    },
)
async def torna_delete_debug_env(params: ModuleDebugEnvDeleteInput) -> str:
    """从 Torna 模块删除调试环境。
    
    参考 Java SDK 的 ModuleDebugEnvDeleteRequest 功能。
    
    Args:
        params (ModuleDebugEnvDeleteInput): 删除调试环境的输入参数
        
    Returns:
        str: 调试环境删除结果
    """
    try:
        base_url, token = _validate_environment()
        
        with TornaClient(base_url, token) as client:
            request = ModuleDebugEnvDeleteRequest(token, params.name)
            response = client.execute(request)
        
        if not response.is_success():
            return f"Error: {response.msg} (code: {response.code})"
        
        return _format_response(response.to_dict(), params.response_format, "Delete Debug Environment")
        
    except Exception as e:
        return _handle_api_error_refactored(e)


# Main function
def main():
    """Main function to start the MCP server."""
    import sys
    import asyncio

    if len(sys.argv) > 1 and (sys.argv[1] in ["--help", "-h", "--version", "-v"]):
        if sys.argv[1] in ["--help", "-h"]:
            print("Torna MCP Server - Help")
            print("Usage: toma-mcp")
            print("")
            print("Environment Variables:")
            print("  TORNA_URL: Torna API base URL (default: http://localhost:7700/api)")
            print("  TORNA_TOKEN: Torna module token (required)")
            print("")
            print("Available tools:")
            tools = [
                "torna_list_documents: List all documents in application",
                "torna_get_document_detail: Get single document details", 
                "torna_push_document: Push documents to Torna",
                "torna_get_module_info: Get application module information",
                "torna_get_batch_documents: Get multiple document details",
                "torna_create_category: Create document category",
                "torna_list_categories: List document categories", 
                "torna_update_category_name: Update category name",
                "torna_push_enum: Push enum data",
                "torna_batch_push_enums: Push multiple enums",
                "torna_set_debug_env: Set debug environment",
                "torna_delete_debug_env: Delete debug environment"
            ]
            for tool in tools:
                print(f"  - {tool}")
            return
        elif sys.argv[1] in ["--version", "-v"]:
            print("toma-mcp version 0.1.2")
            return

    try:
        # 验证环境变量
        print("Starting Torna MCP Server...")
        
        # Run the server
        torna_mcp_server.run()

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set TORNA_TOKEN environment variable")
        print("Usage: export TORNA_TOKEN='your-token-here'")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)


# Main entry point
if __name__ == "__main__":
    main()