#!/usr/bin/env python3
"""
Torna MCP Server 测试脚本

此脚本用于测试Torna MCP服务器的基本功能，确保所有工具都能正常工作。
"""

import asyncio
import os
import sys
from typing import Dict, Any

# 导入主要功能进行本地测试
sys.path.append('.')
from main import (
    torna_create_category,
    DocPushInput,
    CategoryCreateInput,
    DictCreateInput,
    ModuleCreateInput,
    ResponseFormat,
    HttpMethod
)

async def test_environment_setup():
    """测试环境变量设置"""
    print("=== 环境变量检查 ===")
    
    torna_url = os.getenv("TORNA_URL")
    torna_tokens = os.getenv("TORNA_TOKENS")
    
    if not torna_url:
        print("❌ TORNA_URL 环境变量未设置")
        return False
    
    if not torna_tokens:
        print("❌ TORNA_TOKENS 环境变量未设置")
        return False
    
    print(f"✅ TORNA_URL: {torna_url}")
    print(f"✅ TORNA_TOKENS: {'已设置' if torna_tokens else '未设置'}")
    return True

async def test_pydantic_validation():
    """测试Pydantic输入验证"""
    print("\n=== Pydantic 输入验证测试 ===")
    
    try:
        # 测试有效的文档推送输入
        doc_input = DocPushInput(
            name="测试API",
            url="/api/test",
            http_method=HttpMethod.GET,
            access_token="test_token",
            response_format=ResponseFormat.JSON
        )
        print("✅ 文档推送输入验证通过")
        
        # 测试有效的分类创建输入
        category_input = CategoryCreateInput(
            name="测试分类",
            access_token="test_token",
            response_format=ResponseFormat.JSON
        )
        print("✅ 分类创建输入验证通过")
        
        # 测试有效的字典创建输入
        dict_input = DictCreateInput(
            name="测试字典",
            access_token="test_token",
            response_format=ResponseFormat.JSON
        )
        print("✅ 字典创建输入验证通过")
        
        # 测试有效的模块创建输入
        module_input = ModuleCreateInput(
            name="测试模块",
            project_id="test_project",
            access_token="test_token",
            response_format=ResponseFormat.JSON
        )
        print("✅ 模块创建输入验证通过")
        
        return True
        
    except Exception as e:
        print(f"❌ Pydantic 验证失败: {e}")
        return False

async def test_invalid_inputs():
    """测试无效输入的处理"""
    print("\n=== 无效输入处理测试 ===")
    
    try:
        # 测试空名称 - 应该失败
        try:
            DocPushInput(
                name="",
                url="/api/test",
                http_method=HttpMethod.GET,
                access_token="test_token"
            )
            print("❌ 空名称验证未正确失败")
            return False
        except Exception:
            print("✅ 空名称验证正确失败")
        
        # 测试无效HTTP方法 - 应该失败
        try:
            DocPushInput(
                name="测试API",
                url="/api/test",
                http_method="INVALID",
                access_token="test_token"
            )
            print("❌ 无效HTTP方法验证未正确失败")
            return False
        except Exception:
            print("✅ 无效HTTP方法验证正确失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 无效输入测试异常: {e}")
        return False

def print_tool_summary():
    """打印工具摘要"""
    print("\n=== 可用的 MCP 工具 ===")
    
    tools = [
        "文档API工具:",
        "  - torna_push_document: 推送文档到Torna",
        "  - torna_create_category: 创建文档分类",
        "  - toma_update_category_name: 更新分类名称",
        "  - toma_list_documents: 列出文档",
        "  - toma_get_document_detail: 获取文档详情",
        "  - toma_get_document_details_batch: 批量获取文档详情",
        "",
        "字典API工具:",
        "  - torna_create_dictionary: 创建字典",
        "  - toma_update_dictionary: 更新字典",
        "  - toma_list_dictionaries: 列出字典",
        "  - toma_get_dictionary_detail: 获取字典详情",
        "  - toma_delete_dictionary: 删除字典",
        "",
        "模块API工具:",
        "  - torna_create_module: 创建模块",
        "  - toma_update_module: 更新模块",
        "  - toma_list_modules: 列出模块",
        "  - toma_get_module_detail: 获取模块详情",
        "  - toma_delete_module: 删除模块"
    ]
    
    for line in tools:
        print(line)

def print_usage_instructions():
    """打印使用说明"""
    print("\n=== 使用说明 ===")
    print("1. 设置环境变量:")
    print("   export TORNA_URL='http://localhost:7700/api'")
    print("   export TORNA_TOKENS='your_token1,your_token2'")
    print("")
    print("2. 安装依赖:")
    print("   pip install -r requirements.txt")
    print("")
    print("3. 运行MCP服务器:")
    print("   python main.py")
    print("")
    print("4. 在MCP客户端中配置服务器地址为 'python main.py'")

async def main():
    """主测试函数"""
    print("🚀 Torna MCP Server 测试开始")
    print("=" * 50)
    
    # 运行各项测试
    tests = [
        ("环境设置", test_environment_setup),
        ("输入验证", test_pydantic_validation),
        ("无效输入", test_invalid_inputs)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} 测试 ---")
        try:
            result = await test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    # 打印工具摘要和使用说明
    print_tool_summary()
    print_usage_instructions()
    
    # 测试结果总结
    print("\n=== 测试结果总结 ===")
    print(f"通过: {passed}/{total} 项测试")
    
    if passed == total:
        print("✅ 所有基本测试通过！MCP服务器可以正常运行。")
    else:
        print("⚠️  部分测试未通过，请检查配置和代码。")
    
    print("\n📝 提示: 进行完整的API功能测试需要连接实际的Torna服务器。")

if __name__ == "__main__":
    asyncio.run(main())