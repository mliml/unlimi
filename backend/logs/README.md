# 日志目录

## 目录结构

```
logs/
├── README.md           # 本文件
├── prompts/            # OpenAI Prompt 日志（仅 admin 用户）
│   ├── latest.html     # 🔥 实时 HTML 查看器（双击打开）
│   ├── therapist_prompts_2025-12-13.jsonl
│   ├── therapist_prompts_2025-12-14.jsonl
│   └── archive/        # 归档旧日志（可选）
└── app.log             # 应用日志（如果配置）
```

## 🚀 快速查看日志

### 方式 1: 双击 HTML 文件（推荐）⭐

```bash
# 直接双击打开
open logs/prompts/latest.html

# 或在 Finder 中找到 logs/prompts/latest.html，双击即可
```

**特点**:
- ✅ 自动更新 - 每次记录日志后自动更新文件
- ✅ 无需运行脚本 - 刷新页面即可看到最新日志
- ✅ 漂亮的 UI - 响应式设计，支持搜索和展开/折叠
- ✅ 实时统计 - 显示 Token 使用、缓存率等

## Prompt 日志

### 记录规则
- **仅记录 `is_admin=true` 的用户**
- 每天一个日志文件，格式: `therapist_prompts_YYYY-MM-DD.jsonl`
- 使用 JSONL 格式（每行一个 JSON 对象）

### 日志内容

#### 请求日志
```json
{
  "timestamp": "2025-12-13T10:30:00",
  "user_id": 123,
  "session_id": "abc-123",
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "完整的系统提示词..."},
    {"role": "user", "content": "用户消息"}
  ],
  "request_params": {
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

#### 响应日志
```json
{
  "timestamp": "2025-12-13T10:30:05",
  "user_id": 123,
  "session_id": "abc-123",
  "type": "response",
  "content": "AI 回复内容...",
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 50,
    "total_tokens": 200,
    "prompt_tokens_details": {
      "cached_tokens": 100
    }
  }
}
```

### 方式 2: 命令行工具

使用 `scripts/view_prompts.py` 查看日志：

```bash
# 查看某个用户的所有 prompts
python scripts/view_prompts.py --user-id 123

# 查看某个会话的 prompts
python scripts/view_prompts.py --session-id abc-123

# 查看今天的所有 prompts
python scripts/view_prompts.py --today

# 查看最近 10 条记录
python scripts/view_prompts.py --last 10

# 显示完整内容（不截断）
python scripts/view_prompts.py --show-full --last 1

# 导出为 JSON
python scripts/view_prompts.py --user-id 123 --export output.json
```

### 方式 3: 导出自定义 HTML

```bash
# 导出指定日期的日志为独立 HTML
python scripts/export_html.py --date 2025-12-13

# 导出某个用户的所有日志
python scripts/export_html.py --user-id 123 --output user_123_logs.html
```

### Token 计费说明

OpenAI 的 token 使用分为：
- **prompt_tokens**: 输入 tokens 总数
- **completion_tokens**: 输出 tokens 总数
- **cached_tokens**: 使用缓存的 tokens（便宜 50%）

示例：
- 总输入: 150 tokens
- 缓存: 100 tokens
- 新 tokens: 50 tokens
- 成本: 50 × $0.15/1M + 100 × $0.075/1M = 更便宜！

### 归档建议

建议定期归档旧日志：

```bash
# 归档 30 天前的日志
mkdir -p logs/prompts/archive
find logs/prompts -name "therapist_prompts_*.jsonl" -mtime +30 -exec mv {} logs/prompts/archive/ \;
```

或压缩归档：

```bash
# 压缩并归档
cd logs/prompts
tar -czf archive/prompts_$(date +%Y-%m).tar.gz therapist_prompts_$(date +%Y-%m)-*.jsonl
rm therapist_prompts_$(date +%Y-%m)-*.jsonl
```
