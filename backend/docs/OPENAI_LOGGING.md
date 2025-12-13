# OpenAI Prompt 日志系统

## 📋 概述

本系统实现了对 OpenAI API 调用的完整 prompt 记录功能，**仅对 `is_admin=true` 的用户生效**。

### 主要特性

✅ 记录完整的 messages（system + user + history）
✅ 记录 token 使用情况（包括缓存 tokens）
✅ 仅对 admin 用户记录，保护普通用户隐私
✅ 使用 contextvars 确保线程安全
✅ JSONL 格式，方便后续分析
✅ 按天分割日志文件

---

## 🏗️ 架构设计

### 调用链

```
API 请求 → therapist_agent_service.chat()
    ↓
设置 openai_logging_context (user_id, session_id, is_admin)
    ↓
Agent.run() → OpenAIChat.invoke()
    ↓
HTTP Client (with hooks) → OpenAI API
    ↓
Request Hook: 拦截请求，记录 messages
Response Hook: 拦截响应，记录 usage
```

### 核心组件

1. **`app/core/openai_logger.py`**
   - `OpenAIPromptLogger`: 日志记录器
   - `create_logging_http_client()`: 创建带 hooks 的 HTTP client
   - `openai_logging_context()`: 上下文管理器

2. **`app/agents/therapist_agent_service.py`**
   - 在 `__init__` 中使用自定义 HTTP client
   - 在 `chat()` 中设置日志上下文

3. **`scripts/view_prompts.py`**
   - 日志查看和导出工具

---

## 📊 OpenAI Token 计费详解

### Token 类型

```json
{
  "usage": {
    "prompt_tokens": 150,           // 总输入 tokens
    "completion_tokens": 50,        // 输出 tokens
    "total_tokens": 200,            // 总计
    "prompt_tokens_details": {
      "cached_tokens": 100,         // 🔥 缓存的 tokens（便宜 50%）
      "audio_tokens": 0             // 音频输入
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,        // o1 模型的推理 tokens
      "audio_tokens": 0             // 音频输出
    }
  }
}
```

### 缓存机制（Prompt Caching）

OpenAI 会自动缓存相似的 prompt 前缀：

- **首次请求**: 150 tokens，全价 $0.15/1M
- **后续请求**:
  - 缓存命中: 100 tokens × $0.075/1M = $0.0075
  - 新 tokens: 50 tokens × $0.15/1M = $0.0075
  - **总成本降低 50%**

**触发条件**:
- System prompt 保持不变
- 历史消息部分相同
- 5 分钟内的请求

**查看缓存率**:
```bash
python scripts/view_prompts.py --last 10
# 输出会显示: 缓存: 100/150 (66.7%)
```

---

## 🚀 使用指南

### 1. 如何启用

**对于新用户**:
```sql
UPDATE users SET is_admin = true WHERE email = 'admin@example.com';
```

**对于现有会话**: 只要用户的 `is_admin=true`，后续对话会自动记录。

### 2. 查看日志

```bash
# 查看今天的所有 admin 用户日志
python scripts/view_prompts.py --today

# 查看某个用户的日志
python scripts/view_prompts.py --user-id 123

# 查看某个会话的完整对话
python scripts/view_prompts.py --session-id abc-123 --show-full

# 查看最近 5 条，显示完整内容
python scripts/view_prompts.py --last 5 --show-full

# 导出为 JSON 进行分析
python scripts/view_prompts.py --user-id 123 --export analysis.json
```

### 3. 日志内容示例

**请求日志**:
```json
{
  "timestamp": "2025-12-13T14:30:00",
  "user_id": 123,
  "session_id": "session-abc-123",
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "system",
      "content": "你是一名经验丰富的心理咨询师...\n\n## 治疗师个性化指令\n\nXX治疗师的指令...\n\n## 当前用户情况\n\n用户上下文..."
    },
    {
      "role": "user",
      "content": "我最近感觉很焦虑..."
    }
  ],
  "request_params": {
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

**响应日志**:
```json
{
  "timestamp": "2025-12-13T14:30:05",
  "user_id": 123,
  "session_id": "session-abc-123",
  "type": "response",
  "content": "我能感受到你的焦虑...",
  "usage": {
    "prompt_tokens": 1450,
    "completion_tokens": 180,
    "total_tokens": 1630,
    "prompt_tokens_details": {
      "cached_tokens": 1200
    }
  }
}
```

---

## 🔍 数据分析示例

### 分析 Prompt 效果

```python
import json
from pathlib import Path

# 加载日志
logs = []
for file in Path("logs/prompts").glob("*.jsonl"):
    with open(file) as f:
        logs.extend([json.loads(line) for line in f])

# 统计缓存率
cache_rates = []
for log in logs:
    if log.get("type") == "response":
        usage = log.get("usage", {})
        details = usage.get("prompt_tokens_details", {})
        cached = details.get("cached_tokens", 0)
        total = usage.get("prompt_tokens", 1)
        cache_rates.append(cached / total * 100)

print(f"平均缓存率: {sum(cache_rates) / len(cache_rates):.1f}%")

# 分析 prompt 长度
prompt_lengths = []
for log in logs:
    if "messages" in log:
        system_msg = next((m for m in log["messages"] if m["role"] == "system"), None)
        if system_msg:
            prompt_lengths.append(len(system_msg["content"]))

print(f"平均 Prompt 长度: {sum(prompt_lengths) / len(prompt_lengths):.0f} 字符")
```

### 对比不同治疗师的效果

```python
# 提取治疗师指令部分
therapist_prompts = {}
for log in logs:
    if "messages" in log:
        system_msg = next((m for m in log["messages"] if m["role"] == "system"), None)
        if system_msg and "## 治疗师个性化指令" in system_msg["content"]:
            # 提取治疗师部分
            content = system_msg["content"]
            start = content.find("## 治疗师个性化指令")
            end = content.find("## 当前用户情况")
            therapist_section = content[start:end]

            # 记录这个治疗师的使用情况
            user_id = log["user_id"]
            if therapist_section not in therapist_prompts:
                therapist_prompts[therapist_section] = []
            therapist_prompts[therapist_section].append(log)

# 输出每个治疗师的使用统计
for prompt, logs in therapist_prompts.items():
    print(f"\n治疗师 Prompt (前50字): {prompt[:50]}...")
    print(f"  使用次数: {len(logs)}")
```

---

## 🛠️ 维护和优化

### 日志清理

```bash
# 归档 30 天前的日志
mkdir -p logs/prompts/archive
find logs/prompts -name "*.jsonl" -mtime +30 -exec mv {} logs/prompts/archive/ \;

# 压缩归档
cd logs/prompts/archive
tar -czf prompts_2025-11.tar.gz therapist_prompts_2025-11-*.jsonl
rm therapist_prompts_2025-11-*.jsonl
```

### 监控缓存效率

添加到 crontab，每天检查缓存率：

```bash
# 每天 23:00 检查今天的缓存率
0 23 * * * cd /path/to/backend && ./venv/bin/python scripts/analyze_cache.py --today
```

创建 `scripts/analyze_cache.py`:

```python
#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

log_file = Path(f"logs/prompts/therapist_prompts_{datetime.now().strftime('%Y-%m-%d')}.jsonl")

if not log_file.exists():
    print(f"No logs for today")
    exit(0)

cache_rates = []
with open(log_file) as f:
    for line in f:
        log = json.loads(line)
        if log.get("type") == "response":
            usage = log.get("usage", {})
            details = usage.get("prompt_tokens_details", {})
            cached = details.get("cached_tokens", 0)
            total = usage.get("prompt_tokens", 1)
            if total > 0:
                cache_rates.append(cached / total * 100)

if cache_rates:
    avg = sum(cache_rates) / len(cache_rates)
    print(f"Today's cache rate: {avg:.1f}% ({len(cache_rates)} requests)")
else:
    print("No cache data available")
```

---

## ⚠️ 注意事项

1. **隐私保护**:
   - 仅 admin 用户的对话会被记录
   - 日志文件包含敏感内容，务必保护好访问权限
   - 已在 `.gitignore` 中排除日志文件

2. **磁盘空间**:
   - 每条完整 prompt 日志约 2-5 KB
   - 100 条对话约 500 KB
   - 建议定期归档

3. **性能影响**:
   - HTTP hooks 会略微增加延迟（<10ms）
   - 使用 contextvars，线程安全
   - 对非 admin 用户无影响

4. **调试**:
   ```python
   # 查看日志记录器状态
   from app.core.openai_logger import get_prompt_logger
   logger = get_prompt_logger()
   print(f"Log dir: {logger.log_dir}")
   print(f"Today's file: {logger._get_log_file_path()}")
   ```

---

## 📚 相关文档

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference/chat)
- [Prompt Caching Guide](https://platform.openai.com/docs/guides/prompt-caching)
- [httpx Event Hooks](https://www.python-httpx.org/advanced/#event-hooks)

---

## 🤝 贡献

如需改进日志系统，请：

1. 修改 `app/core/openai_logger.py` 的记录逻辑
2. 更新 `scripts/view_prompts.py` 增加新的查看功能
3. 补充本文档
