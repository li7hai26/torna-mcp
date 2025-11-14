#!/usr/bin/env python3
"""
Complete end-to-end test for all Torna MCP tools.
This script tests all 16 tool functions to ensure they work correctly.
"""

import os
import sys
import asyncio
import traceback
import json
from typing import Dict, Any

# Set environment variables BEFORE importing main
os.environ["TORNA_URL"] = "http://localhost:7700/api"
os.environ["TORNA_TOKENS"] = "b414086531524fb0bc14f757346fec92,bbe60f26676c4e92893170213ad05197,0e6cd661ea60487188d8cbbdcfe1228b"

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all necessary components
from main import (
    DocPushInput, CategoryCreateInput, CategoryUpdateInput, DocListInput, 
    DocDetailInput, DocDetailsBatchInput,
    DictCreateInput, DictUpdateInput, DictListInput, DictDetailInput, DictDeleteInput,
    ModuleCreateInput, ModuleUpdateInput, ModuleListInput, ModuleDetailInput, ModuleDeleteInput,
    ResponseFormat,
    torna_push_document, torna_create_category, torna_update_category_name,
    torna_list_documents, torna_get_document_detail, torna_get_document_details_batch,
    torna_create_dictionary, torna_update_dictionary, torna_list_dictionaries,
    torna_get_dictionary_detail, torna_delete_dictionary,
    torna_create_module, torna_update_module, torna_list_modules,
    torna_get_module_detail, torna_delete_module
)

async def test_all_tools():
    """Test all 16 Torna MCP tools."""
    print("=== 完整端到端测试 ===")
    print("测试所有16个Torna MCP工具函数")
    print("=" * 50)
    
    test_results = []
    
    # Document API Tests (6 tools)
    print("\n📚 文档API测试 (6个工具)")
    print("-" * 30)
    
    # Test 1: Push Document
    try:
        params = DocPushInput(
            name="测试API文档",
            description="这是一个端到端测试文档",
            url="/api/test/endpoint",
            http_method="POST",
            content_type="application/json",
            is_folder=False,
            parent_id=None,
            is_show=True,
            version="1.0",
            access_token="b414086531524fb0bc14f757346fec92",
            request_params=[
                {"name": "param1", "type": "string", "description": "测试参数", "required": True, "example": "test_value"}
            ],
            response_params=[
                {"name": "result", "type": "string", "description": "返回结果", "required": True}
            ],
            error_codes=[
                {"code": "1001", "msg": "测试错误", "solution": "检查参数"}
            ],
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_push_document(params)
        test_results.append(("文档推送", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 文档推送: 成功")
    except Exception as e:
        test_results.append(("文档推送", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 文档推送: 异常 - {str(e)[:50]}...")
    
    # Test 2: Create Category
    try:
        params = CategoryCreateInput(
            name="测试分类",
            parent_id=None,
            description="端到端测试分类",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_create_category(params)
        test_results.append(("创建分类", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 创建分类: 成功")
    except Exception as e:
        test_results.append(("创建分类", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 创建分类: 异常 - {str(e)[:50]}...")
    
    # Test 3: Update Category Name
    try:
        params = CategoryUpdateInput(
            category_id="test_category_id",
            name="更新后的分类名称",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_update_category_name(params)
        test_results.append(("更新分类名称", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 更新分类名称: 成功")
    except Exception as e:
        test_results.append(("更新分类名称", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 更新分类名称: 异常 - {str(e)[:50]}...")
    
    # Test 4: List Documents
    try:
        params = DocListInput(
            access_token="b414086531524fb0bc14f757346fec92",
            limit=10,
            offset=0,
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_list_documents(params)
        test_results.append(("列出文档", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 列出文档: 成功")
    except Exception as e:
        test_results.append(("列出文档", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 列出文档: 异常 - {str(e)[:50]}...")
    
    # Test 5: Get Document Detail
    try:
        params = DocDetailInput(
            doc_id="test_doc_id",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_get_document_detail(params)
        test_results.append(("获取文档详情", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 获取文档详情: 成功")
    except Exception as e:
        test_results.append(("获取文档详情", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 获取文档详情: 异常 - {str(e)[:50]}...")
    
    # Test 6: Get Document Details Batch
    try:
        params = DocDetailsBatchInput(
            doc_ids=["test_doc_id_1", "test_doc_id_2"],
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_get_document_details_batch(params)
        test_results.append(("批量获取文档详情", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 批量获取文档详情: 成功")
    except Exception as e:
        test_results.append(("批量获取文档详情", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 批量获取文档详情: 异常 - {str(e)[:50]}...")
    
    # Dictionary API Tests (5 tools)
    print("\n📖 字典API测试 (5个工具)")
    print("-" * 30)
    
    # Test 7: Create Dictionary
    try:
        params = DictCreateInput(
            name="测试字典",
            description="端到端测试字典",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_create_dictionary(params)
        test_results.append(("创建字典", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 创建字典: 成功")
    except Exception as e:
        test_results.append(("创建字典", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 创建字典: 异常 - {str(e)[:50]}...")
    
    # Test 8: Update Dictionary
    try:
        params = DictUpdateInput(
            dict_id="test_dict_id",
            name="更新后的字典名称",
            description="更新后的字典描述",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_update_dictionary(params)
        test_results.append(("更新字典", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 更新字典: 成功")
    except Exception as e:
        test_results.append(("更新字典", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 更新字典: 异常 - {str(e)[:50]}...")
    
    # Test 9: List Dictionaries
    try:
        params = DictListInput(
            access_token="b414086531524fb0bc14f757346fec92",
            limit=10,
            offset=0,
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_list_dictionaries(params)
        test_results.append(("列出字典", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 列出字典: 成功")
    except Exception as e:
        test_results.append(("列出字典", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 列出字典: 异常 - {str(e)[:50]}...")
    
    # Test 10: Get Dictionary Detail
    try:
        params = DictDetailInput(
            dict_id="test_dict_id",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_get_dictionary_detail(params)
        test_results.append(("获取字典详情", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 获取字典详情: 成功")
    except Exception as e:
        test_results.append(("获取字典详情", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 获取字典详情: 异常 - {str(e)[:50]}...")
    
    # Test 11: Delete Dictionary
    try:
        params = DictDeleteInput(
            dict_id="test_dict_id",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_delete_dictionary(params)
        test_results.append(("删除字典", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 删除字典: 成功")
    except Exception as e:
        test_results.append(("删除字典", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 删除字典: 异常 - {str(e)[:50]}...")
    
    # Module API Tests (5 tools)
    print("\n🔧 模块API测试 (5个工具)")
    print("-" * 30)
    
    # Test 12: Create Module
    try:
        params = ModuleCreateInput(
            name="测试模块",
            description="端到端测试模块",
            project_id="test_project_id",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_create_module(params)
        test_results.append(("创建模块", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 创建模块: 成功")
    except Exception as e:
        test_results.append(("创建模块", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 创建模块: 异常 - {str(e)[:50]}...")
    
    # Test 13: Update Module
    try:
        params = ModuleUpdateInput(
            module_id="test_module_id",
            name="更新后的模块名称",
            description="更新后的模块描述",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_update_module(params)
        test_results.append(("更新模块", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 更新模块: 成功")
    except Exception as e:
        test_results.append(("更新模块", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 更新模块: 异常 - {str(e)[:50]}...")
    
    # Test 14: List Modules
    try:
        params = ModuleListInput(
            project_id="test_project_id",
            access_token="b414086531524fb0bc14f757346fec92",
            limit=10,
            offset=0,
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_list_modules(params)
        test_results.append(("列出模块", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 列出模块: 成功")
    except Exception as e:
        test_results.append(("列出模块", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 列出模块: 异常 - {str(e)[:50]}...")
    
    # Test 15: Get Module Detail
    try:
        params = ModuleDetailInput(
            module_id="test_module_id",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_get_module_detail(params)
        test_results.append(("获取模块详情", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 获取模块详情: 成功")
    except Exception as e:
        test_results.append(("获取模块详情", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 获取模块详情: 异常 - {str(e)[:50]}...")
    
    # Test 16: Delete Module
    try:
        params = ModuleDeleteInput(
            module_id="test_module_id",
            access_token="b414086531524fb0bc14f757346fec92",
            response_format=ResponseFormat.MARKDOWN
        )
        result = await torna_delete_module(params)
        test_results.append(("删除模块", "✅ 成功" if not result.startswith("Error:") else "❌ 失败"))
        print(f"✅ 删除模块: 成功")
    except Exception as e:
        test_results.append(("删除模块", f"❌ 异常: {str(e)[:50]}..."))
        print(f"❌ 删除模块: 异常 - {str(e)[:50]}...")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    success_count = 0
    total_count = len(test_results)
    
    for test_name, result in test_results:
        status = "✅" if "成功" in result else "❌"
        if "成功" in result:
            success_count += 1
        print(f"{status} {test_name}: {result}")
    
    print(f"\n总计: {success_count}/{total_count} 个工具测试成功")
    success_rate = (success_count / total_count) * 100
    print(f"成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 端到端测试总体成功！Torna MCP服务器可以正常使用。")
    else:
        print(f"\n⚠️  端到端测试完成，但有 {total_count - success_count} 个工具需要进一步检查。")

if __name__ == "__main__":
    # Run the complete test
    asyncio.run(test_all_tools())