# Token自动选择机制改进计划

## 当前问题
- 用户需要手动在每个工具中传入 access_token
- 不够用户友好，应该从环境变量自动选择

## 改进方案

### 1. 智能Token选择机制
```python
def _select_access_token(provided_token: Optional[str] = None, tool_type: str = None) -> str:
    """
    智能选择访问令牌
    
    Args:
        provided_token: 用户提供的token（如果有）
        tool_type: 工具类型（doc/dict/module）
    
    Returns:
        str: 选中的访问令牌
    """
    if provided_token:
        return provided_token
    
    # 如果没有提供token，使用默认的第一个token
    if TORNA_TOKENS:
        return TORNA_TOKENS[0]
    
    raise ValueError("No access token available. Please provide access_token or set TORNA_TOKENS environment variable.")
```

### 2. 修改所有工具函数的access_token字段
```python
# 从必需改为可选
access_token: Optional[str] = Field(default=None, description="Module token for authentication (optional, will auto-select from environment if not provided)")
```

### 3. 更新工具调用逻辑
在每个工具函数中：
```python
# 获取实际要使用的token
actual_token = _select_access_token(params.access_token, "doc")

# 使用实际token调用API
result = await _make_api_request(
    interface_name="doc.push",
    version=params.version,
    data=data,
    access_token=actual_token
)
```

## 优势
1. **向后兼容**：如果用户已经习惯了手动传token，代码仍然可以正常工作
2. **用户友好**：新用户可以直接使用，不需要了解token细节
3. **灵活配置**：支持用户基于工具类型选择不同token
4. **简单配置**：设置TORNA_TOKENS环境变量即可开始使用

## 实现步骤
1. 添加_select_access_token函数
2. 修改所有Input模型中的access_token字段
3. 更新所有工具函数的调用逻辑
4. 更新文档说明
5. 测试和验证