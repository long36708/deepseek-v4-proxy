# DeepSeek V4 Proxy 代理服务文档

## 概述

`proxy-deepseekv4.py` 是一个基于 Flask 构建的 DeepSeek API 代理服务器，主要用于转发和增强 DeepSeek 的聊天完成接口请求。该代理服务提供了限流、缓存、推理内容补全等功能，以优化与 DeepSeek API 的交互体验。

## 主要功能特性

### 1. API 端点代理
- **聊天完成接口**: `/v1/chat/completions` 和 `/chat/completions`
- **模型列表接口**: `/v1/models` 和 `/models`

### 2. 令牌桶限流机制
- 使用 `TokenBucket` 类实现速率限制
- 默认配置：每分钟最多 5 个请求 (`rate=5/60.0`, `capacity=5`)
- 当达到限流阈值时，请求会自动等待直到获得可用令牌

### 3. 双层缓存系统
- **内存缓存**: 快速访问最近使用的数据
- **SQLite 持久化缓存**: 长期存储推理内容
- 缓存键基于消息内容的 MD5 哈希值（排除 `reasoning_content` 字段）
- 支持自动将历史 assistant 消息的推理内容从缓存中恢复

### 4. 推理内容管理
- 自动收集流式响应中的 `reasoning_content`
- 将完整的推理内容与对应的消息关联并缓存
- 在后续请求中为缺少推理内容的历史消息补全数据

### 5. 流式响应处理
- 支持 Server-Sent Events (SSE) 流式传输
- 实时转发上游响应数据
- 同时收集完整的内容、推理内容和工具调用信息

### 6. 错误处理与重试
- 对 429 (Too Many Requests) 状态码进行自动重试（最多 3 次）
- 详细的日志记录便于调试和监控
- 适当的错误响应返回给客户端

## 技术架构

### 核心组件

#### TokenBucket 类
```python
class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate          # 令牌生成速率
        self.capacity = capacity  # 桶容量
        self.tokens = capacity    # 当前令牌数
        self.last_time = time.monotonic()
        self.lock = threading.Lock()
```

#### ReasoningCache 类
- 内存字典 + SQLite 数据库的双层结构
- 线程安全的设计
- WAL 模式提高并发性能

### 数据处理流程

1. **接收请求** → 检查限流 → 获取 JSON 数据
2. **预处理** → 补全历史消息的 reasoning_content
3. **转发请求** → 发送到 DeepSeek API（带重试机制）
4. **流式处理** → 实时转发响应并收集关键信息
5. **后处理** → 缓存新的推理内容

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| UPSTREAM_URL | `https://api.deepseek.com/v1/chat/completions` | 上游 DeepSeek API 地址 |
| 限流速率 | 5/60 per second | 每分钟 5 个请求 |
| 限流容量 | 5 | 最大突发请求数 |
| 服务端口 | 9000 | Flask 应用监听端口 |
| 数据库路径 | `reasoning.db` | SQLite 缓存文件位置 |

## 使用方式

### 启动服务
```bash
python proxy-deepseekv4.py
```

### API 调用示例
```bash
curl -X POST http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true
  }'
```

## 应用场景

1. **API 调用频率控制**: 避免超出 DeepSeek API 的配额限制
2. **推理过程复用**: 通过缓存减少重复计算，节省成本
3. **对话上下文完整性**: 确保多轮对话中推理信息的一致性
4. **开发测试环境**: 提供稳定的本地代理用于开发和调试

## 注意事项

- 需要有效的 DeepSeek API 密钥才能正常工作
- 首次运行时会创建 `reasoning.db` 数据库文件
- 建议在生产环境中调整限流参数以适应实际需求
- 定期清理缓存数据库以控制存储空间增长