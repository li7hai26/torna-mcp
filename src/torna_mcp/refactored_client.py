#!/usr/bin/env python3
"""
Torna 客户端 - 参考 Java SDK 重新设计
"""

import json
import os
import urllib.parse
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
import httpx

# 类型变量定义
T = TypeVar('T', bound='BaseResponse')


class TornaConfig:
    """配置常量类 - 参考 Java SDK 的 OpenConfig"""
    
    SUCCESS_CODE = "0"
    DEFAULT_VERSION = "1.0"
    API_NAME = "name"
    DATA_NAME = "data"
    VERSION_NAME = "version"
    TIMESTAMP_NAME = "timestamp"
    TIMESTAMP_PATTERN = "%Y-%m-%d %H:%M:%S"
    ACCESS_TOKEN_NAME = "access_token"
    LOCALE = "zh-CN"
    CONNECT_TIMEOUT = 60
    READ_TIMEOUT = 60


class TornaAPIError(Exception):
    """API 错误异常类"""
    
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Torna API Error {code}: {message}")


class BaseResponse(ABC):
    """响应基类 - 参考 Java SDK 的 BaseResponse"""
    
    def __init__(self):
        self.code: Optional[str] = None
        self.msg: Optional[str] = None
        self.data: Optional[Any] = None
    
    def is_success(self) -> bool:
        """检查是否成功"""
        return TornaConfig.SUCCESS_CODE == self.code
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """从字典创建响应对象"""
        response = cls()
        response.code = data.get("code")
        response.msg = data.get("msg")
        response.data = data.get("data")
        return response
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }


class DocListResponse(BaseResponse):
    """文档列表响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[List[Dict[str, Any]]] = None


class DocGetResponse(BaseResponse):
    """文档详情响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[Dict[str, Any]] = None


class DocPushResponse(BaseResponse):
    """文档推送响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[List[Dict[str, Any]]] = None


class ModuleGetResponse(BaseResponse):
    """模块信息响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[Dict[str, Any]] = None


class DocDetailsResponse(BaseResponse):
    """批量文档详情响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[List[Dict[str, Any]]] = None


class DocCategoryCreateResponse(BaseResponse):
    """创建分类响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[Dict[str, Any]] = None


class DocCategoryListResponse(BaseResponse):
    """分类列表响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[List[Dict[str, Any]]] = None


class DocCategoryNameUpdateResponse(BaseResponse):
    """更新分类名称响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[Dict[str, Any]] = None


class EnumPushResponse(BaseResponse):
    """枚举推送响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[Dict[str, Any]] = None


class ModuleDebugEnvSetResponse(BaseResponse):
    """设置调试环境响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[Dict[str, Any]] = None


class ModuleDebugEnvDeleteResponse(BaseResponse):
    """删除调试环境响应类"""
    
    def __init__(self):
        super().__init__()
        self.data: Optional[Dict[str, Any]] = None


class RequestForm:
    """请求表单类 - 参考 Java SDK 的 RequestForm"""
    
    def __init__(self, form_data: Dict[str, Any]):
        self.form: Dict[str, Any] = form_data.copy()
    
    def get_form(self) -> Dict[str, Any]:
        """获取表单数据"""
        return self.form.copy()


class BaseRequest(ABC, Generic[T]):
    """请求基类 - 参考 Java SDK 的 BaseRequest"""
    
    def __init__(self, token: str, response_class: Type[T]):
        self.token = token
        self.response_class: Type[T] = response_class
    
    @abstractmethod
    def name(self) -> str:
        """接口名称"""
        pass
    
    @abstractmethod
    def version(self) -> str:
        """接口版本"""
        pass
    
    def create_request_form(self) -> RequestForm:
        """创建请求表单 - 模板方法"""
        data = self.build_json_data()
        
        # 构建公共参数
        param = {
            TornaConfig.API_NAME: self.name(),
            TornaConfig.DATA_NAME: self._url_encode(data),
            TornaConfig.VERSION_NAME: self.version(),
            TornaConfig.TIMESTAMP_NAME: datetime.now().strftime(TornaConfig.TIMESTAMP_PATTERN),
            TornaConfig.ACCESS_TOKEN_NAME: self.token,
        }
        
        return RequestForm(param)
    
    def build_json_data(self) -> str:
        """构建 JSON 数据"""
        # 子类可以重写此方法来添加特定参数
        return "{}"
    
    def parse_response(self, response_text: str) -> T:
        """解析响应"""
        try:
            response_data = json.loads(response_text)
            return self.response_class.from_dict(response_data)
        except (json.JSONDecodeError, TypeError) as e:
            raise TornaAPIError("PARSE_ERROR", f"响应解析失败: {e}")
    
    def _url_encode(self, data: str) -> str:
        """URL 编码"""
        return urllib.parse.quote(data, safe='')


class DocListRequest(BaseRequest[DocListResponse]):
    """文档列表请求类 - 参考 Java SDK 的 DocListRequest"""
    
    def __init__(self, token: str):
        super().__init__(token, DocListResponse)
    
    def name(self) -> str:
        return "doc.list"
    
    def version(self) -> str:
        return "1.0"
    
    def create_request_form(self) -> RequestForm:
        """doc.list 不需要额外参数，返回空对象"""
        return super().create_request_form()


class DocGetRequest(BaseRequest[DocGetResponse]):
    """文档详情请求类"""
    
    def __init__(self, token: str, doc_id: str):
        super().__init__(token, DocGetResponse)
        self.doc_id = doc_id
    
    def name(self) -> str:
        return "doc.detail"
    
    def version(self) -> str:
        return "1.0"
    
    def build_json_data(self) -> str:
        """构建包含文档ID的JSON数据"""
        return json.dumps({"id": self.doc_id})


class DocPushRequest(BaseRequest[DocPushResponse]):
    """文档推送请求类"""
    
    def __init__(self, token: str):
        super().__init__(token, DocPushResponse)
        self.apis: Optional[List[Dict[str, Any]]] = None
        self.debug_envs: Optional[List[Dict[str, Any]]] = None
    
    def name(self) -> str:
        return "doc.push"
    
    def version(self) -> str:
        return "1.0"
    
    def build_json_data(self) -> str:
        """构建推送数据的JSON"""
        data = {}
        if self.apis:
            data["apis"] = self.apis
        if self.debug_envs:
            data["debugEnvs"] = self.debug_envs
        return json.dumps(data, ensure_ascii=False)
    
    def set_apis(self, apis: List[Dict[str, Any]]) -> 'DocPushRequest':
        """设置API列表"""
        self.apis = apis
        return self
    
    def set_debug_envs(self, debug_envs: List[Dict[str, Any]]) -> 'DocPushRequest':
        """设置调试环境"""
        self.debug_envs = debug_envs
        return self


class ModuleGetRequest(BaseRequest[ModuleGetResponse]):
    """模块信息请求类"""
    
    def __init__(self, token: str):
        super().__init__(token, ModuleGetResponse)
    
    def name(self) -> str:
        return "module.get"
    
    def version(self) -> str:
        return "1.0"


class DocDetailsRequest(BaseRequest[DocDetailsResponse]):
    """批量文档详情请求类"""
    
    def __init__(self, token: str, doc_ids: List[str]):
        super().__init__(token, DocDetailsResponse)
        self.doc_ids = doc_ids
    
    def name(self) -> str:
        return "doc.details"
    
    def version(self) -> str:
        return "1.0"
    
    def build_json_data(self) -> str:
        """构建文档ID列表的JSON"""
        return json.dumps({"ids": self.doc_ids})


class TornaClient:
    """Torna 客户端类 - 参考 Java SDK 的 OpenClient"""
    
    def __init__(self, base_url: str, token: str):
        # 处理基础URL，确保正确格式
        base_url = base_url.rstrip('/')
        # 如果URL中已经有/api路径，则不重复添加
        # 使用更精确的匹配：检查是否有/api路径而不是简单包含
        if not base_url.endswith('/api') and '/api/' not in base_url:
            base_url = base_url + '/api'
        self.base_url = base_url
        self.token = token
        self.client: Optional[httpx.Client] = None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.client = httpx.Client(timeout=60.0)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.client:
            self.client.close()
    
    def execute(self, request: BaseRequest) -> BaseResponse:
        """执行请求 - 核心方法"""
        if not self.client:
            raise TornaAPIError("CLIENT_ERROR", "客户端未初始化，请使用 with 语句")
        
        # 创建请求表单
        request_form = request.create_request_form()
        
        # 构建请求头
        headers = self._build_headers()
        
        try:
            # 发送HTTP请求
            response = self.client.post(
                self.base_url,
                json=request_form.get_form(),
                headers=headers,
                timeout=60.0
            )
            response.raise_for_status()
            
            # 解析响应
            response_text = response.text
            return request.parse_response(response_text)
            
        except httpx.HTTPStatusError as e:
            raise TornaAPIError("HTTP_ERROR", f"HTTP请求失败: {e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException as e:
            raise TornaAPIError("TIMEOUT_ERROR", f"请求超时: {e}")
        except Exception as e:
            raise TornaAPIError("UNKNOWN_ERROR", f"未知错误: {e}")
    
    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            "Accept-Language": TornaConfig.LOCALE,
            "Content-Type": "application/json"
        }
    
    # 便捷方法
    def get_documents(self) -> List[Dict[str, Any]]:
        """获取文档列表"""
        request = DocListRequest(self.token)
        response = self.execute(request)
        if not response.is_success():
            raise TornaAPIError(response.code or "UNKNOWN", response.msg or "获取文档失败")
        return response.data or []
    
    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """获取单个文档详情"""
        request = DocGetRequest(self.token, doc_id)
        response = self.execute(request)
        if not response.is_success():
            raise TornaAPIError(response.code or "UNKNOWN", response.msg or f"获取文档 {doc_id} 失败")
        return response.data
    
    def get_module_info(self) -> Dict[str, Any]:
        """获取模块信息"""
        request = ModuleGetRequest(self.token)
        response = self.execute(request)
        if not response.is_success():
            raise TornaAPIError(response.code or "UNKNOWN", response.msg or "获取模块信息失败")
        return response.data
    
    def push_document(self, doc_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """推送单个文档"""
        request = DocPushRequest(self.token)
        request.set_apis([doc_config])
        response = self.execute(request)
        if not response.is_success():
            raise TornaAPIError(response.code or "UNKNOWN", response.msg or "推送文档失败")
        return response.data or []
    
    def push_documents(self, docs: List[Dict[str, Any]], debug_envs: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """批量推送文档"""
        request = DocPushRequest(self.token)
        request.set_apis(docs)
        if debug_envs:
            request.set_debug_envs(debug_envs)
        response = self.execute(request)
        if not response.is_success():
            raise TornaAPIError(response.code or "UNKNOWN", response.msg or "批量推送文档失败")
        return response.data or []
    
    def get_batch_documents(self, doc_ids: List[str]) -> List[Dict[str, Any]]:
        """批量获取文档详情"""
        request = DocDetailsRequest(self.token, doc_ids)
        response = self.execute(request)
        if not response.is_success():
            raise TornaAPIError(response.code or "UNKNOWN", response.msg or "批量获取文档失败")
        return response.data or []


# 使用示例
def example_usage():
    """使用示例"""
    
    # 1. 基本使用（推荐）
    with TornaClient("http://localhost:7700", "your-token") as client:
        try:
            # 获取所有文档
            docs = client.get_documents()
            print(f"找到 {len(docs)} 个文档")
            
            # 获取模块信息
            module_info = client.get_module_info()
            print(f"模块信息: {module_info}")
            
            # 推送单个文档
            doc_config = {
                "name": "用户登录",
                "description": "用户登录接口",
                "url": "/api/user/login",
                "httpMethod": "POST",
                "contentType": "application/json"
            }
            result = client.push_document(doc_config)
            print(f"推送结果: {result}")
            
        except TornaAPIError as e:
            print(f"API错误: {e}")
    
    # 2. 手动请求
    client = TornaClient("http://localhost:7700", "your-token")
    
    # 创建并执行请求
    request = DocListRequest("your-token")
    with client:
        response = client.execute(request)
        print(f"响应: {response.to_dict()}")


# ==================== 新增的 Request 类 - 补充 Java SDK 所有功能 ====================

class DocCategoryCreateRequest(BaseRequest[DocCategoryCreateResponse]):
    """创建分类请求类"""
    
    def __init__(self, token: str, name: str):
        super().__init__(token, DocCategoryCreateResponse)
        self.name = name
    
    def name(self) -> str:
        return "doc.category.create"
    
    def version(self) -> str:
        return "1.0"
    
    def build_json_data(self) -> str:
        """构建分类创建数据"""
        return json.dumps({"name": self.name})


class DocCategoryListRequest(BaseRequest[DocCategoryListResponse]):
    """分类列表请求类"""
    
    def __init__(self, token: str):
        super().__init__(token, DocCategoryListResponse)
    
    def name(self) -> str:
        return "doc.category.list"
    
    def version(self) -> str:
        return "1.0"


class DocCategoryNameUpdateRequest(BaseRequest[DocCategoryNameUpdateResponse]):
    """更新分类名称请求类"""
    
    def __init__(self, token: str, category_id: str, name: str):
        super().__init__(token, DocCategoryNameUpdateResponse)
        self.category_id = category_id
        self.name = name
    
    def name(self) -> str:
        return "doc.category.name.update"
    
    def version(self) -> str:
        return "1.0"
    
    def build_json_data(self) -> str:
        """构建分类名称更新数据"""
        return json.dumps({"id": self.category_id, "name": self.name})


class EnumPushRequest(BaseRequest[EnumPushResponse]):
    """枚举推送请求类"""
    
    def __init__(self, token: str, enum_name: str, description: str = "", items: Optional[List[Dict[str, Any]]] = None):
        super().__init__(token, EnumPushResponse)
        self.enum_name = enum_name
        self.description = description
        self.items = items or []
    
    def name(self) -> str:
        return "enum.push"
    
    def version(self) -> str:
        return "1.0"
    
    def build_json_data(self) -> str:
        """构建枚举推送数据"""
        data = {
            "name": self.enum_name,
            "description": self.description,
            "items": self.items
        }
        return json.dumps(data, ensure_ascii=False)


class EnumBatchPushRequest(BaseRequest[EnumPushResponse]):
    """批量枚举推送请求类"""
    
    def __init__(self, token: str, enums: List[Dict[str, Any]]):
        super().__init__(token, EnumPushResponse)
        self.enums = enums
    
    def name(self) -> str:
        return "enum.batch.push"
    
    def version(self) -> str:
        return "1.0"
    
    def build_json_data(self) -> str:
        """构建批量枚举推送数据"""
        return json.dumps({"enums": self.enums}, ensure_ascii=False)


class ModuleDebugEnvSetRequest(BaseRequest[ModuleDebugEnvSetResponse]):
    """设置模块调试环境请求类"""
    
    def __init__(self, token: str, name: str, url: str):
        super().__init__(token, ModuleDebugEnvSetResponse)
        self.name = name
        self.url = url
    
    def name(self) -> str:
        return "module.debug.env.set"
    
    def version(self) -> str:
        return "1.0"
    
    def build_json_data(self) -> str:
        """构建调试环境设置数据"""
        return json.dumps({"name": self.name, "url": self.url})


class ModuleDebugEnvDeleteRequest(BaseRequest[ModuleDebugEnvDeleteResponse]):
    """删除模块调试环境请求类"""
    
    def __init__(self, token: str, name: str):
        super().__init__(token, ModuleDebugEnvDeleteResponse)
        self.name = name
    
    def name(self) -> str:
        return "module.debug.env.delete"
    
    def version(self) -> str:
        return "1.0"
    
    def build_json_data(self) -> str:
        """构建调试环境删除数据"""
        return json.dumps({"name": self.name})


if __name__ == "__main__":
    example_usage()