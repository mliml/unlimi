"""
OpenAI API Logger

记录发送到 OpenAI API 的完整 prompt（仅对 admin 用户）
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import contextvars
from contextlib import contextmanager

import httpx

logger = logging.getLogger(__name__)

# 上下文变量：存储当前请求的用户信息
_current_user_context = contextvars.ContextVar('openai_user_context', default=None)


class OpenAIPromptLogger:
    """记录 OpenAI API 请求的完整 prompt"""

    def __init__(self, log_dir: str = "logs/prompts", auto_update_html: bool = True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.auto_update_html = auto_update_html
        self._update_counter = 0  # 用于控制 HTML 更新频率
        logger.info(f"OpenAI Prompt Logger initialized, log_dir: {self.log_dir}")

    def _get_log_file_path(self) -> Path:
        """获取今天的日志文件路径"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"therapist_prompts_{today}.jsonl"

    def should_log_for_user(self, user_id: Optional[int], is_admin: bool) -> bool:
        """判断是否应该为该用户记录日志"""
        if user_id is None:
            return False
        return is_admin

    def log_request(
        self,
        user_id: int,
        session_id: str,
        model: str,
        messages: list,
        session_state: Optional[Dict[str, Any]] = None,
        request_params: Optional[Dict[str, Any]] = None,
    ):
        """
        记录 OpenAI API 请求

        Args:
            user_id: 用户ID
            session_id: 会话ID
            model: 模型名称
            messages: 完整的 messages 列表
            session_state: 会话状态
            request_params: 请求参数
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "model": model,
                "messages": messages,
                "session_state": session_state or {},
                "request_params": request_params or {},
            }

            # 写入 JSONL 文件（每行一个 JSON）
            log_file = self._get_log_file_path()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            logger.info(
                f"[OPENAI_PROMPT_LOG] Logged request for user={user_id}, "
                f"session={session_id}, messages_count={len(messages)}"
            )

            # 每次记录后更新 HTML（异步）
            self._maybe_update_html()
        except Exception as e:
            logger.error(f"Failed to log OpenAI request: {e}", exc_info=True)

    def log_response(
        self,
        user_id: int,
        session_id: str,
        response_content: str,
        usage: Optional[Dict[str, Any]] = None,
    ):
        """
        记录 OpenAI API 响应（可选）

        Args:
            user_id: 用户ID
            session_id: 会话ID
            response_content: 响应内容
            usage: token 使用情况
        """
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "session_id": session_id,
                "type": "response",
                "content": response_content,
                "usage": usage or {},
            }

            log_file = self._get_log_file_path()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            # 如果有缓存 token，记录一下
            if usage and usage.get("prompt_tokens_details"):
                cached_tokens = usage["prompt_tokens_details"].get("cached_tokens", 0)
                total_prompt_tokens = usage.get("prompt_tokens", 0)
                if cached_tokens > 0:
                    cache_rate = (cached_tokens / total_prompt_tokens * 100) if total_prompt_tokens > 0 else 0
                    logger.info(
                        f"[OPENAI_CACHE] user={user_id}, session={session_id}, "
                        f"cached={cached_tokens}/{total_prompt_tokens} ({cache_rate:.1f}%)"
                    )

            # 每次记录响应后更新 HTML
            self._maybe_update_html()
        except Exception as e:
            logger.error(f"Failed to log OpenAI response: {e}", exc_info=True)

    def _maybe_update_html(self):
        """每 N 次记录后更新一次 HTML（避免频繁写入）"""
        if not self.auto_update_html:
            return

        self._update_counter += 1

        # 每 2 次记录更新一次（1 request + 1 response = 更新 1 次）
        if self._update_counter >= 2:
            self._update_counter = 0
            try:
                # 在后台线程更新 HTML，避免阻塞主线程
                import threading
                threading.Thread(target=self._update_html_file, daemon=True).start()
            except Exception as e:
                logger.debug(f"Failed to schedule HTML update: {e}")

    def _update_html_file(self):
        """生成/更新 HTML 文件"""
        try:
            # 读取今天的所有日志
            logs = []
            log_file = self._get_log_file_path()

            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            logs.append(json.loads(line))

            if not logs:
                return

            # 生成 HTML 到后端 logs 目录
            from datetime import datetime
            html_file = self.log_dir / "latest.html"
            self._generate_html(logs, html_file)

            # 同时复制到前端可访问的位置（如果存在）
            frontend_public = Path(__file__).parent.parent.parent.parent / "frontend" / "app" / "dist"
            if frontend_public.exists():
                frontend_html = frontend_public / "prompts.html"
                self._generate_html(logs, frontend_html)
                logger.debug(f"Also updated frontend HTML: {frontend_html}")

            logger.debug(f"Updated HTML file: {html_file} ({len(logs)} logs)")
        except Exception as e:
            logger.error(f"Failed to update HTML file: {e}", exc_info=True)

    def _generate_html(self, logs: list, output_file: Path):
        """生成 HTML 内容（精简版，只保留核心功能）"""
        # 按时间排序
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # 统计
        total_requests = len([l for l in logs if l.get('type') != 'response'])
        total_responses = len([l for l in logs if l.get('type') == 'response'])
        unique_users = len(set(l.get('user_id') for l in logs if l.get('user_id')))

        # 计算平均缓存率
        cache_rates = []
        total_tokens = 0
        for log in logs:
            if log.get('type') == 'response':
                usage = log.get('usage', {})
                total_tokens += usage.get('total_tokens', 0)
                details = usage.get('prompt_tokens_details', {})
                cached = details.get('cached_tokens', 0)
                prompt = usage.get('prompt_tokens', 1)
                if prompt > 0:
                    cache_rates.append(cached / prompt * 100)

        avg_cache_rate = sum(cache_rates) / len(cache_rates) if cache_rates else 0
        logs_json = json.dumps(logs, ensure_ascii=False)

        # HTML 模板（精简版）
        html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenAI Prompt 日志 - 实时查看</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header .subtitle {{ opacity: 0.9; font-size: 14px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stat-card .label {{ font-size: 12px; color: #666; text-transform: uppercase; margin-bottom: 8px; }}
        .stat-card .value {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .cache-rate {{ color: #4caf50; }}
        .controls {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .controls input, .controls select {{ padding: 10px 15px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; margin-right: 10px; }}
        .log-entry {{ background: white; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden; }}
        .log-header {{ padding: 20px; cursor: pointer; background: #fafafa; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }}
        .log-header:hover {{ background: #f5f5f5; }}
        .log-type {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; }}
        .log-type.request {{ background: #e3f2fd; color: #1976d2; }}
        .log-type.response {{ background: #e8f5e9; color: #388e3c; }}
        .timestamp {{ font-size: 13px; color: #666; margin-right: 15px; }}
        .expand-icon {{ font-size: 20px; color: #999; }}
        .log-entry.expanded .expand-icon {{ transform: rotate(180deg); }}
        .log-body {{ padding: 20px; display: none; border-top: 1px solid #eee; }}
        .log-entry.expanded .log-body {{ display: block; }}
        .prompt-box {{ background: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
        .prompt-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .prompt-title {{ font-size: 14px; font-weight: bold; color: #666; }}
        .copy-btn {{ padding: 6px 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; }}
        .copy-btn:hover {{ background: #5568d3; }}
        .prompt-content {{ background: white; border: 1px solid #e0e0e0; border-radius: 6px; padding: 15px; font-family: 'Monaco', 'Menlo', 'Courier New', monospace; font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; max-height: 600px; overflow-y: auto; }}
        .view-toggle {{ padding: 6px 12px; background: #f5f5f5; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; font-size: 12px; margin-left: 10px; }}
        .view-toggle.active {{ background: #667eea; color: white; border-color: #667eea; }}
        .message {{ margin-bottom: 15px; padding: 15px; border-radius: 6px; border-left: 4px solid #ddd; }}
        .message.system {{ background: #fff3e0; border-left-color: #ff9800; }}
        .message.user {{ background: #e3f2fd; border-left-color: #2196f3; }}
        .message.assistant {{ background: #e8f5e9; border-left-color: #4caf50; }}
        .message-role {{ font-size: 12px; font-weight: bold; text-transform: uppercase; color: #666; margin-bottom: 8px; }}
        .message-content {{ white-space: pre-wrap; word-break: break-word; font-size: 14px; max-height: 300px; overflow-y: auto; }}
        .usage-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; padding: 15px; background: #f9f9f9; border-radius: 6px; }}
        .usage-item {{ text-align: center; }}
        .usage-label {{ font-size: 11px; color: #666; text-transform: uppercase; }}
        .usage-value {{ font-size: 20px; font-weight: bold; color: #333; }}
        .hidden {{ display: none !important; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 OpenAI Prompt 日志 - 实时查看</h1>
            <div class="subtitle">最后更新: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | 自动刷新页面查看最新日志</div>
        </div>
        <div class="stats">
            <div class="stat-card"><div class="label">总请求数</div><div class="value">{total_requests}</div></div>
            <div class="stat-card"><div class="label">总响应数</div><div class="value">{total_responses}</div></div>
            <div class="stat-card"><div class="label">用户数</div><div class="value">{unique_users}</div></div>
            <div class="stat-card"><div class="label">总 Tokens</div><div class="value">{total_tokens:,}</div></div>
            <div class="stat-card"><div class="label">平均缓存率</div><div class="value cache-rate">{avg_cache_rate:.1f}%</div></div>
        </div>
        <div class="controls">
            <input type="text" id="searchInput" placeholder="搜索...">
            <button onclick="applyFilters()" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">搜索</button>
            <button onclick="location.reload()" style="padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 6px; cursor: pointer;">刷新</button>
        </div>
        <div id="logContainer"></div>
    </div>
    <script>
        const logsData = {logs_json};
        function renderLogs(logs) {{
            const container = document.getElementById('logContainer');
            container.innerHTML = logs.map((log, index) => {{
                const type = log.type || 'request';
                const isRequest = type === 'request' || log.messages;
                let bodyHtml = '';
                if (isRequest) {{
                    const messages = log.messages || [];

                    // 合并所有 messages 为完整 prompt
                    const fullPrompt = messages.map(msg => `[${{msg.role.toUpperCase()}}]\\n${{msg.content}}`).join('\\n\\n' + '='.repeat(80) + '\\n\\n');

                    bodyHtml = `
                        <div class="prompt-box">
                            <div class="prompt-header">
                                <div class="prompt-title">完整 Prompt（${{messages.length}} 条消息）</div>
                                <div>
                                    <button class="view-toggle active" onclick="toggleView(${{index}}, 'merged')">合并视图</button>
                                    <button class="view-toggle" onclick="toggleView(${{index}}, 'split')">分散视图</button>
                                    <button class="copy-btn" onclick="copyPrompt(${{index}})">📋 复制</button>
                                </div>
                            </div>
                            <div class="prompt-content" id="prompt-merged-${{index}}">${{escapeHtml(fullPrompt)}}</div>
                            <div class="prompt-content" id="prompt-split-${{index}}" style="display: none;">
                                ${{messages.map(msg => `
                                    <div class="message ${{msg.role}}">
                                        <div class="message-role">${{msg.role}}</div>
                                        <div class="message-content">${{escapeHtml(msg.content)}}</div>
                                    </div>
                                `).join('')}}
                            </div>
                        </div>
                        ${{log.request_params && Object.keys(log.request_params).length > 0 ? `
                            <details style="margin-top: 10px;">
                                <summary style="cursor: pointer; color: #666; font-size: 13px;">请求参数</summary>
                                <pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; margin-top: 10px; font-size: 12px;">${{JSON.stringify(log.request_params, null, 2)}}</pre>
                            </details>
                        ` : ''}}
                    `;
                }} else {{
                    const usage = log.usage || {{}};
                    const details = usage.prompt_tokens_details || {{}};
                    const cached = details.cached_tokens || 0;
                    const promptTokens = usage.prompt_tokens || 0;
                    const cacheRate = promptTokens > 0 ? (cached / promptTokens * 100).toFixed(1) : 0;
                    bodyHtml = `
                        <div class="message assistant">
                            <div class="message-role">响应内容</div>
                            <div class="message-content">${{escapeHtml(log.content || '')}}</div>
                        </div>
                        ${{usage.total_tokens ? `
                            <div class="usage-info">
                                <div class="usage-item"><div class="usage-label">输入</div><div class="usage-value">${{usage.prompt_tokens || 0}}</div></div>
                                <div class="usage-item"><div class="usage-label">输出</div><div class="usage-value">${{usage.completion_tokens || 0}}</div></div>
                                <div class="usage-item"><div class="usage-label">总计</div><div class="usage-value">${{usage.total_tokens || 0}}</div></div>
                                ${{cached > 0 ? `<div class="usage-item"><div class="usage-label">缓存</div><div class="usage-value cache-rate">${{cached}}</div></div>
                                <div class="usage-item"><div class="usage-label">缓存率</div><div class="usage-value cache-rate">${{cacheRate}}%</div></div>` : ''}}
                            </div>
                        ` : ''}}
                    `;
                }}
                return `
                    <div class="log-entry" data-index="${{index}}">
                        <div class="log-header" onclick="toggleLog(${{index}})">
                            <div><span class="log-type ${{type}}">${{type}}</span>
                            <span class="timestamp">${{log.timestamp}}</span>
                            <span class="timestamp">User: ${{log.user_id}} | Session: ${{(log.session_id || '').substring(0, 15)}}...</span></div>
                            <div class="expand-icon">▼</div>
                        </div>
                        <div class="log-body">${{bodyHtml}}</div>
                    </div>
                `;
            }}).join('');
        }}
        function toggleLog(index) {{
            document.querySelector(`[data-index="${{index}}"]`).classList.toggle('expanded');
        }}
        function toggleView(index, view) {{
            const mergedEl = document.getElementById(`prompt-merged-${{index}}`);
            const splitEl = document.getElementById(`prompt-split-${{index}}`);
            const entry = document.querySelector(`[data-index="${{index}}"]`);
            const buttons = entry.querySelectorAll('.view-toggle');

            if (view === 'merged') {{
                mergedEl.style.display = 'block';
                splitEl.style.display = 'none';
                buttons[0].classList.add('active');
                buttons[1].classList.remove('active');
            }} else {{
                mergedEl.style.display = 'none';
                splitEl.style.display = 'block';
                buttons[0].classList.remove('active');
                buttons[1].classList.add('active');
            }}
        }}
        function copyPrompt(index) {{
            const promptEl = document.getElementById(`prompt-merged-${{index}}`);
            const text = promptEl.textContent;
            navigator.clipboard.writeText(text).then(() => {{
                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✓ 已复制';
                setTimeout(() => {{ btn.textContent = originalText; }}, 2000);
            }});
        }}
        function applyFilters() {{
            const searchText = document.getElementById('searchInput').value.toLowerCase();
            const filtered = searchText ? logsData.filter(log => JSON.stringify(log).toLowerCase().includes(searchText)) : logsData;
            renderLogs(filtered);
        }}
        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}
        renderLogs(logsData);
    </script>
</body>
</html>'''

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)


# 全局单例
_prompt_logger: Optional[OpenAIPromptLogger] = None


def get_prompt_logger() -> OpenAIPromptLogger:
    """获取全局 prompt logger 单例"""
    global _prompt_logger
    if _prompt_logger is None:
        _prompt_logger = OpenAIPromptLogger()
    return _prompt_logger


@contextmanager
def openai_logging_context(user_id: int, session_id: str, is_admin: bool):
    """
    设置 OpenAI 日志上下文

    使用示例：
        with openai_logging_context(user_id=123, session_id="abc", is_admin=True):
            agent.run(...)
    """
    token = _current_user_context.set({
        "user_id": user_id,
        "session_id": session_id,
        "is_admin": is_admin,
    })
    try:
        yield
    finally:
        _current_user_context.reset(token)


def get_current_user_context() -> Optional[Dict[str, Any]]:
    """获取当前用户上下文"""
    return _current_user_context.get()


def create_logging_http_client() -> httpx.Client:
    """
    创建带日志功能的 HTTP client（用于 OpenAI SDK）

    通过 event hooks 拦截请求和响应
    """

    def log_request(request: httpx.Request):
        """请求前的钩子"""
        # 检查是否是 OpenAI API 请求
        if "api.openai.com" not in str(request.url):
            return

        # 获取当前用户上下文
        user_context = get_current_user_context()
        if not user_context:
            return

        # 检查是否应该记录
        logger_instance = get_prompt_logger()
        if not logger_instance.should_log_for_user(
            user_context.get("user_id"),
            user_context.get("is_admin", False)
        ):
            return

        # 解析请求体
        try:
            if request.content:
                body = json.loads(request.content)

                # 只记录 chat completions 请求
                if "/chat/completions" in str(request.url):
                    logger_instance.log_request(
                        user_id=user_context["user_id"],
                        session_id=user_context["session_id"],
                        model=body.get("model", "unknown"),
                        messages=body.get("messages", []),
                        request_params={
                            k: v for k, v in body.items()
                            if k not in ["messages", "model"]
                        }
                    )
        except Exception as e:
            logger.error(f"Error in request logging hook: {e}", exc_info=True)

    def log_response(response: httpx.Response):
        """响应后的钩子"""
        # 检查是否是 OpenAI API 响应
        if "api.openai.com" not in str(response.request.url):
            return

        # 获取当前用户上下文
        user_context = get_current_user_context()
        if not user_context:
            return

        # 检查是否应该记录
        logger_instance = get_prompt_logger()
        if not logger_instance.should_log_for_user(
            user_context.get("user_id"),
            user_context.get("is_admin", False)
        ):
            return

        # 解析响应体
        try:
            # 检查是否是 chat/completions 请求
            if "/chat/completions" not in str(response.request.url):
                return

            # 检查响应是否已被消费（避免流式响应错误）
            if not response.is_stream_consumed:
                logger.debug("Response stream not consumed yet, skipping response logging")
                return

            # 解析响应内容
            if response.content:
                resp_data = json.loads(response.content)

                # 提取响应内容和 usage
                choices = resp_data.get("choices", [])
                content = choices[0]["message"]["content"] if choices else ""
                usage = resp_data.get("usage", {})

                logger_instance.log_response(
                    user_id=user_context["user_id"],
                    session_id=user_context["session_id"],
                    response_content=content,
                    usage=usage
                )
        except Exception as e:
            logger.error(f"Error in response logging hook: {e}", exc_info=True)

    # 创建 HTTP client with event hooks
    client = httpx.Client(
        event_hooks={
            "request": [log_request],
            "response": [log_response],
        },
        timeout=60.0,
    )

    return client
