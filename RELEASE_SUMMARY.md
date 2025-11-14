# Torna MCP Server - 版本 2.0.0 发布摘要

## 🚨 重要更正

此版本对 Torna MCP 服务器进行了重大修正，基于真实的 Torna OpenAPI 规范重新实现。

## 主要更改

### ✅ 修正的问题

1. **API 规范校正**
   - 移除了不存在的假接口
   - 基于真实的 Torna OpenAPI (http://localhost:7700/api) 重新实现
   - 修正了 API 请求格式

2. **环境变量简化**
   - 从 `TORNA_TOKENS` (多令牌) 改为 `TORNA_TOKEN` (单令牌)
   - 默认 API URL: `http://localhost:7700/api`

3. **接口精简**
   - 从 16 个假接口减少到 2 个真实接口
   - `torna_push_document` - 推送文档到 Torna
   - `torna_get_document` - 获取文档详情

### 📁 文件变更

**修改的文件:**
- `main.py` - 完全重写，移除假接口，添加真实 API
- `README.md` - 更新功能描述和使用示例
- `INSTALL.md` - 修正环境变量配置
- `.env.example` - 更新为单令牌格式
- `pyproject.toml` - 版本更新至 2.0.0

**删除的假接口:**
- `torna_create_category` ❌
- `torna_update_category_name` ❌
- `torna_list_documents` ❌
- `torna_get_document_detail` ❌
- `torna_get_document_details_batch` ❌
- 字典管理相关接口 ❌
- 模块管理相关接口 ❌

## 🔧 正确的 API 使用方法

### 环境变量配置
```bash
export TORNA_URL="http://localhost:7700/api"
export TORNA_TOKEN="your-module-token-here"
```

### 真实的 Torna API 请求格式
```json
{
  "name": "doc.push",
  "version": "1.0",
  "data": "urlencoded_json_data",
  "access_token": "module_token"
}
```

### 支持的功能
- ✅ 推送 API 文档
- ✅ 创建分类/文件夹
- ✅ 请求/响应参数定义
- ✅ 错误码配置
- ✅ 调试环境设置
- ✅ 获取文档详情

## 📦 版本信息

- **版本**: 2.0.0
- **发布日期**: 2025-11-12
- **重大变更**: 是 - API 规范完全修正
- **向后兼容性**: 否 - 从多令牌改为单令牌

## 🔗 相关链接

- [Torna 官方 OpenAPI 文档](https://torna.cn/dev/openapi.html)
- [Torna SDK 推送文档](https://torna.cn/tutorial/sdk.html)

## ⚠️ 重要说明

此版本修正了之前版本中"胡写"（基于假设而非真实 API 规范）的问题。现在所有实现都基于 Torna 官方 OpenAPI 规范。

如需使用此版本，请重新配置环境变量为单令牌格式。

---

**错误已修正，现在基于真实的 Torna API 规范实现！** ✅