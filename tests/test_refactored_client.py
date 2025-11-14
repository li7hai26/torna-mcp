"""
Torna Python SDK 测试套件 - 参考 Java SDK 的测试结构
"""

import unittest
import json
from unittest.mock import Mock, patch
from typing import Dict, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from torna_mcp.refactored_client import (
    TornaClient,
    TornaAPIError,
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
    RequestForm,
    TornaConfig
)


class BaseTest(unittest.TestCase):
    """测试基类 - 参考 Java SDK 的 BaseTest"""
    
    def setUp(self):
        """测试初始化"""
        self.base_url = "http://localhost:7700/api"
        self.token = "test-token-123456"
        
        # 创建模拟响应数据
        self.mock_success_response = {
            "code": "0",
            "msg": "success",
            "data": [
                {
                    "id": "doc123",
                    "name": "用户登录接口",
                    "description": "用户登录验证接口",
                    "url": "/api/user/login",
                    "httpMethod": "POST"
                }
            ]
        }
        
        self.mock_error_response = {
            "code": "-1",
            "msg": "Token无效",
            "data": None
        }
    
    def print_response(self, response):
        """打印响应结果 - 参考 Java SDK"""
        if response.is_success():
            print(f"✅ 成功: {json.dumps(response.data, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 失败: code={response.code}, msg={response.msg}")


class TestDocListRequest(BaseTest):
    """文档列表请求测试 - 参考 Java SDK 的 testDocList()"""
    
    def test_doc_list_creation(self):
        """测试文档列表请求创建"""
        request = DocListRequest(self.token)
        
        self.assertEqual(request.name(), "doc.list")
        self.assertEqual(request.version(), "1.0")
        self.assertEqual(request.token, self.token)
    
    def test_doc_list_form_creation(self):
        """测试文档列表请求表单创建"""
        request = DocListRequest(self.token)
        form = request.create_request_form()
        
        self.assertIsInstance(form, RequestForm)
        self.assertEqual(form.get_form()["name"], "doc.list")
        self.assertEqual(form.get_form()["version"], "1.0")
        self.assertEqual(form.get_form()["access_token"], self.token)
        
        # 验证data字段编码正确
        data = form.get_form()["data"]
        self.assertEqual(data, "%7B%7D")  # URL编码的空JSON对象
    
    @patch('torna_mcp.refactored_client.httpx.Client.post')
    def test_doc_list_execution(self, mock_post):
        """测试文档列表请求执行"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.text = json.dumps(self.mock_success_response)
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # 创建客户端并执行请求
        with TornaClient(self.base_url, self.token) as client:
            request = DocListRequest(self.token)
            response = client.execute(request)
        
        self.assertTrue(response.is_success())
        self.assertEqual(response.code, "0")
        self.assertEqual(response.msg, "success")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "用户登录接口")


class TestDocGetRequest(BaseTest):
    """文档详情请求测试 - 参考 Java SDK 的 testDocGetRequest()"""
    
    def test_doc_get_creation(self):
        """测试文档详情请求创建"""
        doc_id = "test-doc-123"
        request = DocGetRequest(self.token, doc_id)
        
        self.assertEqual(request.name(), "doc.detail")
        self.assertEqual(request.version(), "1.0")
        self.assertEqual(request.doc_id, doc_id)
    
    def test_doc_get_json_data(self):
        """测试文档详情请求 JSON 数据构建"""
        doc_id = "test-doc-123"
        request = DocGetRequest(self.token, doc_id)
        
        json_data = json.loads(request.build_json_data())
        self.assertEqual(json_data["id"], doc_id)
    
    @patch('torna_mcp.refactored_client.httpx.Client.post')
    def test_doc_get_execution(self, mock_post):
        """测试文档详情请求执行"""
        doc_id = "test-doc-123"
        mock_response_data = {
            "code": "0",
            "msg": "success",
            "data": {
                "id": doc_id,
                "name": "用户登录接口",
                "description": "用户登录验证接口",
                "url": "/api/user/login",
                "httpMethod": "POST"
            }
        }
        
        mock_response = Mock()
        mock_response.text = json.dumps(mock_response_data)
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        with TornaClient(self.base_url, self.token) as client:
            request = DocGetRequest(self.token, doc_id)
            response = client.execute(request)
        
        self.assertTrue(response.is_success())
        self.assertEqual(response.data["id"], doc_id)
        self.assertEqual(response.data["name"], "用户登录接口")


class TestDocPushRequest(BaseTest):
    """文档推送请求测试 - 参考 Java SDK 的 testDocPushRequest()"""
    
    def test_doc_push_creation(self):
        """测试文档推送请求创建"""
        request = DocPushRequest(self.token)
        
        self.assertEqual(request.name(), "doc.push")
        self.assertEqual(request.version(), "1.0")
        self.assertIsNone(request.apis)
        self.assertIsNone(request.debug_envs)
    
    def test_doc_push_apis_setting(self):
        """测试文档推送 API 设置"""
        request = DocPushRequest(self.token)
        apis = [
            {
                "name": "用户登录",
                "description": "用户登录接口",
                "url": "/api/user/login",
                "httpMethod": "POST"
            }
        ]
        
        result = request.set_apis(apis)
        self.assertIs(result, request)  # 支持链式调用
        self.assertEqual(request.apis, apis)
    
    def test_doc_push_debug_envs_setting(self):
        """测试文档推送调试环境设置"""
        request = DocPushRequest(self.token)
        debug_envs = [
            {"name": "测试环境", "url": "http://localhost:8080"}
        ]
        
        result = request.set_debug_envs(debug_envs)
        self.assertIs(result, request)
        self.assertEqual(request.debug_envs, debug_envs)
    
    def test_doc_push_json_data_building(self):
        """测试文档推送 JSON 数据构建"""
        request = DocPushRequest(self.token)
        
        # 只有 API 数据
        apis = [{"name": "用户登录", "url": "/api/login"}]
        request.set_apis(apis)
        json_data = json.loads(request.build_json_data())
        self.assertIn("apis", json_data)
        self.assertEqual(json_data["apis"], apis)
        
        # 同时有 API 和调试环境数据
        debug_envs = [{"name": "测试", "url": "http://test.com"}]
        request.set_debug_envs(debug_envs)
        json_data = json.loads(request.build_json_data())
        self.assertIn("apis", json_data)
        self.assertIn("debugEnvs", json_data)
        self.assertEqual(json_data["apis"], apis)
        self.assertEqual(json_data["debugEnvs"], debug_envs)


class TestModuleGetRequest(BaseTest):
    """模块信息请求测试 - 参考 Java SDK 的相关测试"""
    
    def test_module_get_creation(self):
        """测试模块信息请求创建"""
        request = ModuleGetRequest(self.token)
        
        self.assertEqual(request.name(), "module.get")
        self.assertEqual(request.version(), "1.0")
        self.assertEqual(request.token, self.token)


class TestDocDetailsRequest(BaseTest):
    """批量文档详情请求测试"""
    
    def test_doc_details_creation(self):
        """测试批量文档详情请求创建"""
        doc_ids = ["doc1", "doc2", "doc3"]
        request = DocDetailsRequest(self.token, doc_ids)
        
        self.assertEqual(request.name(), "doc.details")
        self.assertEqual(request.version(), "1.0")
        self.assertEqual(request.doc_ids, doc_ids)
    
    def test_doc_details_json_data(self):
        """测试批量文档详情请求 JSON 数据构建"""
        doc_ids = ["doc1", "doc2", "doc3"]
        request = DocDetailsRequest(self.token, doc_ids)
        
        json_data = json.loads(request.build_json_data())
        self.assertEqual(json_data["ids"], doc_ids)


class TestTornaClient(BaseTest):
    """Torna 客户端测试"""
    
    def test_client_creation(self):
        """测试客户端创建"""
        client = TornaClient(self.base_url, self.token)
        self.assertEqual(client.base_url, "http://localhost:7700/api")
        self.assertEqual(client.token, self.token)
        self.assertIsNone(client.client)
    
    def test_client_context_manager(self):
        """测试客户端上下文管理器"""
        with TornaClient(self.base_url, self.token) as client:
            self.assertIsNotNone(client.client)
        
        # 退出上下文管理器后客户端应该被关闭
        # 注意：这里不能直接测试client.client是否为None，因为对象已经销毁
    
    @patch('torna_mcp.refactored_client.httpx.Client.post')
    def test_client_execution_success(self, mock_post):
        """测试客户端请求执行成功"""
        mock_response = Mock()
        mock_response.text = json.dumps(self.mock_success_response)
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        with TornaClient(self.base_url, self.token) as client:
            request = DocListRequest(self.token)
            response = client.execute(request)
        
        self.assertTrue(response.is_success())
        mock_post.assert_called_once()
    
    def test_client_convenience_methods(self):
        """测试客户端便捷方法"""
        with TornaClient(self.base_url, self.token) as client:
            # 测试便捷方法存在
            self.assertTrue(hasattr(client, 'get_documents'))
            self.assertTrue(hasattr(client, 'get_document'))
            self.assertTrue(hasattr(client, 'get_module_info'))
            self.assertTrue(hasattr(client, 'push_document'))
            self.assertTrue(hasattr(client, 'push_documents'))
            self.assertTrue(hasattr(client, 'get_batch_documents'))


class TestTornaConfig(unittest.TestCase):
    """Torna 配置常量测试"""
    
    def test_config_constants(self):
        """测试配置常量"""
        self.assertEqual(TornaConfig.SUCCESS_CODE, "0")
        self.assertEqual(TornaConfig.DEFAULT_VERSION, "1.0")
        self.assertEqual(TornaConfig.API_NAME, "name")
        self.assertEqual(TornaConfig.DATA_NAME, "data")
        self.assertEqual(TornaConfig.VERSION_NAME, "version")
        self.assertEqual(TornaConfig.ACCESS_TOKEN_NAME, "access_token")


class TestRequestForm(unittest.TestCase):
    """请求表单测试"""
    
    def test_request_form_creation(self):
        """测试请求表单创建"""
        form_data = {"name": "test", "value": "123"}
        request_form = RequestForm(form_data)
        
        self.assertEqual(request_form.get_form(), form_data)
        # 确保返回的是副本，不是原对象
        self.assertIsNot(request_form.get_form(), form_data)


if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)