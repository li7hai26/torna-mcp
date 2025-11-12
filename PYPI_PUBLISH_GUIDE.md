# PyPI 发布指南

## 🚀 包已构建成功！

**生成的文件：**
- `dist/torna_mcp-1.0.0.tar.gz` - 源分发包
- `dist/torna_mcp-1.0.0-py3-none-any.whl` - Python wheel包

## 🔐 PyPI 认证要求

PyPI现在要求使用API Token或Trusted Publisher进行发布，传统的用户名/密码认证不再支持。

### 方案1：使用API Token（推荐）

1. **登录PyPI**：https://pypi.org/account/login/
2. **生成API Token**：
   - 进入 Account Settings -> API tokens
   - 点击 "Add API token"
   - 给token一个描述（如："torna-mcp发布"）
   - 选择作用域：Entire account 或 Specific project (推荐：Specific project + torna-mcp)
   - 保存token（格式类似：pypi-xxxxx...）

3. **使用token发布**：
```bash
uv publish dist/torna_mcp-1.0.0.tar.gz --username __token__ --password pypi-xxxxx
```

### 方案2：使用twine发布

1. **安装twine**：
```bash
pip install twine
```

2. **设置认证信息**（在`.pypirc`文件中）：
```ini
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-xxxxx
```

3. **发布**：
```bash
twine upload dist/*
```

## 📦 替代方案：GitHub发布

由于PyPI认证限制，您可以：

1. **发布到GitHub Releases**：
   - 在GitHub上创建Release
   - 上传wheel文件
   - 用户可以从GitHub下载安装

2. **为其他开发者提供安装方式**：
```bash
# 从GitHub直接安装
pip install git+https://github.com/li7hai26/torna-mcp.git@main
```

## ✅ 下一步操作

请选择以下选项之一：

1. **获取PyPI API Token**并继续发布
2. **创建GitHub Release**作为替代发布方式
3. **保持当前状态**，包已准备好随时发布

包已经构建完成，任何一种方式都能让用户安装使用！