#!/usr/bin/env python3
"""
导出 OpenAI Prompt 日志为 HTML 页面

使用示例:
    # 导出今天的日志
    python scripts/export_html.py --today

    # 导出某个用户的日志
    python scripts/export_html.py --user-id 123

    # 导出指定日期的日志
    python scripts/export_html.py --date 2025-12-13

    # 自定义输出文件名
    python scripts/export_html.py --today --output my_logs.html
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


def load_logs(log_dir: Path, date_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """加载日志文件"""
    logs = []

    if date_filter:
        log_file = log_dir / f"therapist_prompts_{date_filter}.jsonl"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
    else:
        for log_file in sorted(log_dir.glob("therapist_prompts_*.jsonl")):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))

    return logs


def filter_logs(
    logs: List[Dict[str, Any]],
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """过滤日志"""
    filtered = logs

    if user_id is not None:
        filtered = [log for log in filtered if log.get('user_id') == user_id]

    if session_id is not None:
        filtered = [log for log in filtered if log.get('session_id') == session_id]

    return filtered


def generate_html(logs: List[Dict[str, Any]], output_file: str):
    """生成 HTML 页面"""

    # 按时间排序
    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    # 统计信息
    total_requests = len([l for l in logs if l.get('type') != 'response'])
    total_responses = len([l for l in logs if l.get('type') == 'response'])
    unique_users = len(set(l.get('user_id') for l in logs if l.get('user_id')))
    unique_sessions = len(set(l.get('session_id') for l in logs if l.get('session_id')))

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

    # 将日志转换为 JSON 字符串（嵌入 HTML）
    logs_json = json.dumps(logs, ensure_ascii=False, indent=2)

    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenAI Prompt 日志查看器</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            opacity: 0.9;
            font-size: 14px;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .stat-card .label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .stat-card .value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}

        .controls {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .controls input,
        .controls select {{
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            margin-right: 10px;
            margin-bottom: 10px;
        }}

        .controls input[type="text"] {{
            width: 250px;
        }}

        .log-entry {{
            background: white;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .log-entry:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}

        .log-header {{
            padding: 20px;
            cursor: pointer;
            user-select: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #fafafa;
            border-bottom: 1px solid #eee;
        }}

        .log-header:hover {{
            background: #f5f5f5;
        }}

        .log-meta {{
            flex: 1;
        }}

        .log-type {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            margin-right: 10px;
        }}

        .log-type.request {{
            background: #e3f2fd;
            color: #1976d2;
        }}

        .log-type.response {{
            background: #e8f5e9;
            color: #388e3c;
        }}

        .timestamp {{
            font-size: 13px;
            color: #666;
            margin-right: 15px;
        }}

        .user-info {{
            font-size: 13px;
            color: #666;
        }}

        .expand-icon {{
            font-size: 20px;
            color: #999;
            transition: transform 0.3s ease;
        }}

        .log-entry.expanded .expand-icon {{
            transform: rotate(180deg);
        }}

        .log-body {{
            padding: 20px;
            display: none;
            border-top: 1px solid #eee;
        }}

        .log-entry.expanded .log-body {{
            display: block;
        }}

        .message-list {{
            margin-bottom: 20px;
        }}

        .message {{
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #ddd;
        }}

        .message.system {{
            background: #fff3e0;
            border-left-color: #ff9800;
        }}

        .message.user {{
            background: #e3f2fd;
            border-left-color: #2196f3;
        }}

        .message.assistant {{
            background: #e8f5e9;
            border-left-color: #4caf50;
        }}

        .message-role {{
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 8px;
        }}

        .message-content {{
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 14px;
            line-height: 1.6;
        }}

        .message-content.collapsed {{
            max-height: 150px;
            overflow: hidden;
            position: relative;
        }}

        .message-content.collapsed::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 50px;
            background: linear-gradient(transparent, white);
        }}

        .expand-message {{
            color: #667eea;
            cursor: pointer;
            font-size: 12px;
            margin-top: 5px;
            display: inline-block;
        }}

        .expand-message:hover {{
            text-decoration: underline;
        }}

        .usage-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 6px;
        }}

        .usage-item {{
            text-align: center;
        }}

        .usage-label {{
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}

        .usage-value {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }}

        .cache-rate {{
            color: #4caf50;
        }}

        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }}

        .no-results .icon {{
            font-size: 48px;
            margin-bottom: 15px;
        }}

        pre {{
            background: #f5f5f5;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 13px;
        }}

        .hidden {{
            display: none !important;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 OpenAI Prompt 日志查看器</h1>
            <div class="subtitle">生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="label">总请求数</div>
                <div class="value">{total_requests}</div>
            </div>
            <div class="stat-card">
                <div class="label">总响应数</div>
                <div class="value">{total_responses}</div>
            </div>
            <div class="stat-card">
                <div class="label">用户数</div>
                <div class="value">{unique_users}</div>
            </div>
            <div class="stat-card">
                <div class="label">会话数</div>
                <div class="value">{unique_sessions}</div>
            </div>
            <div class="stat-card">
                <div class="label">总 Tokens</div>
                <div class="value">{total_tokens:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">平均缓存率</div>
                <div class="value cache-rate">{avg_cache_rate:.1f}%</div>
            </div>
        </div>

        <div class="controls">
            <input type="text" id="searchInput" placeholder="搜索内容...">
            <select id="typeFilter">
                <option value="">所有类型</option>
                <option value="request">请求</option>
                <option value="response">响应</option>
            </select>
            <select id="userFilter">
                <option value="">所有用户</option>
            </select>
            <button onclick="applyFilters()" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">筛选</button>
            <button onclick="expandAll()" style="padding: 10px 20px; background: #4caf50; color: white; border: none; border-radius: 6px; cursor: pointer; margin-left: 10px;">全部展开</button>
            <button onclick="collapseAll()" style="padding: 10px 20px; background: #999; color: white; border: none; border-radius: 6px; cursor: pointer;">全部折叠</button>
        </div>

        <div id="logContainer"></div>
        <div id="noResults" class="no-results hidden">
            <div class="icon">📭</div>
            <div>没有找到匹配的日志</div>
        </div>
    </div>

    <script>
        // 嵌入日志数据
        const logsData = {logs_json};

        // 渲染日志
        function renderLogs(logs) {{
            const container = document.getElementById('logContainer');
            const noResults = document.getElementById('noResults');

            if (logs.length === 0) {{
                container.innerHTML = '';
                noResults.classList.remove('hidden');
                return;
            }}

            noResults.classList.add('hidden');
            container.innerHTML = logs.map((log, index) => {{
                const type = log.type || 'request';
                const isRequest = type === 'request' || log.messages;

                let bodyHtml = '';

                if (isRequest) {{
                    // 请求日志
                    const messages = log.messages || [];
                    bodyHtml = `
                        <div class="message-list">
                            ${{messages.map((msg, idx) => `
                                <div class="message ${{msg.role}}">
                                    <div class="message-role">${{msg.role}}</div>
                                    <div class="message-content ${{msg.content.length > 500 ? 'collapsed' : ''}}" id="msg-${{index}}-${{idx}}">
                                        ${{escapeHtml(msg.content)}}
                                    </div>
                                    ${{msg.content.length > 500 ? `
                                        <div class="expand-message" onclick="toggleMessage(${{index}}, ${{idx}})">
                                            展开完整内容 ▼
                                        </div>
                                    ` : ''}}
                                </div>
                            `).join('')}}
                        </div>
                        ${{log.request_params ? `
                            <details>
                                <summary style="cursor: pointer; margin-bottom: 10px;">请求参数</summary>
                                <pre>${{JSON.stringify(log.request_params, null, 2)}}</pre>
                            </details>
                        ` : ''}}
                    `;
                }} else {{
                    // 响应日志
                    const usage = log.usage || {{}};
                    const details = usage.prompt_tokens_details || {{}};
                    const cached = details.cached_tokens || 0;
                    const promptTokens = usage.prompt_tokens || 0;
                    const cacheRate = promptTokens > 0 ? (cached / promptTokens * 100).toFixed(1) : 0;

                    bodyHtml = `
                        <div class="message assistant">
                            <div class="message-role">响应内容</div>
                            <div class="message-content">
                                ${{escapeHtml(log.content || '')}}
                            </div>
                        </div>
                        ${{usage.total_tokens ? `
                            <div class="usage-info">
                                <div class="usage-item">
                                    <div class="usage-label">输入 Tokens</div>
                                    <div class="usage-value">${{usage.prompt_tokens || 0}}</div>
                                </div>
                                <div class="usage-item">
                                    <div class="usage-label">输出 Tokens</div>
                                    <div class="usage-value">${{usage.completion_tokens || 0}}</div>
                                </div>
                                <div class="usage-item">
                                    <div class="usage-label">总计</div>
                                    <div class="usage-value">${{usage.total_tokens || 0}}</div>
                                </div>
                                ${{cached > 0 ? `
                                    <div class="usage-item">
                                        <div class="usage-label">缓存 Tokens</div>
                                        <div class="usage-value cache-rate">${{cached}}</div>
                                    </div>
                                    <div class="usage-item">
                                        <div class="usage-label">缓存率</div>
                                        <div class="usage-value cache-rate">${{cacheRate}}%</div>
                                    </div>
                                ` : ''}}
                            </div>
                        ` : ''}}
                    `;
                }}

                return `
                    <div class="log-entry" data-index="${{index}}">
                        <div class="log-header" onclick="toggleLog(${{index}})">
                            <div class="log-meta">
                                <span class="log-type ${{type}}">${{type}}</span>
                                <span class="timestamp">${{log.timestamp || 'Unknown'}}</span>
                                <span class="user-info">用户: ${{log.user_id || 'N/A'}} | 会话: ${{(log.session_id || 'N/A').substring(0, 20)}}...</span>
                                ${{log.model ? `<span class="user-info">| 模型: ${{log.model}}</span>` : ''}}
                            </div>
                            <div class="expand-icon">▼</div>
                        </div>
                        <div class="log-body">
                            ${{bodyHtml}}
                        </div>
                    </div>
                `;
            }}).join('');

            // 填充用户过滤器
            populateUserFilter(logs);
        }}

        function populateUserFilter(logs) {{
            const userFilter = document.getElementById('userFilter');
            const users = [...new Set(logs.map(l => l.user_id).filter(Boolean))];

            const currentValue = userFilter.value;
            userFilter.innerHTML = '<option value="">所有用户</option>' +
                users.map(uid => `<option value="${{uid}}">${{uid}}</option>`).join('');
            userFilter.value = currentValue;
        }}

        function toggleLog(index) {{
            const entry = document.querySelector(`[data-index="${{index}}"]`);
            entry.classList.toggle('expanded');
        }}

        function toggleMessage(logIndex, msgIndex) {{
            const msgEl = document.getElementById(`msg-${{logIndex}}-${{msgIndex}}`);
            msgEl.classList.toggle('collapsed');
            const btn = msgEl.nextElementSibling;
            if (btn) {{
                btn.textContent = msgEl.classList.contains('collapsed') ? '展开完整内容 ▼' : '折叠内容 ▲';
            }}
        }}

        function expandAll() {{
            document.querySelectorAll('.log-entry').forEach(el => el.classList.add('expanded'));
        }}

        function collapseAll() {{
            document.querySelectorAll('.log-entry').forEach(el => el.classList.remove('expanded'));
        }}

        function applyFilters() {{
            const searchText = document.getElementById('searchInput').value.toLowerCase();
            const typeFilter = document.getElementById('typeFilter').value;
            const userFilter = document.getElementById('userFilter').value;

            const filtered = logsData.filter(log => {{
                // 类型过滤
                const logType = log.type || 'request';
                if (typeFilter && logType !== typeFilter) return false;

                // 用户过滤
                if (userFilter && log.user_id != userFilter) return false;

                // 搜索过滤
                if (searchText) {{
                    const searchable = JSON.stringify(log).toLowerCase();
                    if (!searchable.includes(searchText)) return false;
                }}

                return true;
            }});

            renderLogs(filtered);
        }}

        function escapeHtml(text) {{
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }}

        // 初始渲染
        renderLogs(logsData);
        populateUserFilter(logsData);
    </script>
</body>
</html>"""

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✅ HTML 文件已生成: {output_file}")
    print(f"📊 共包含 {len(logs)} 条日志记录")
    print(f"\n💡 双击打开文件即可在浏览器中查看")


def main():
    parser = argparse.ArgumentParser(description='导出 OpenAI Prompt 日志为 HTML')

    # 过滤参数
    parser.add_argument('--user-id', type=int, help='按用户ID过滤')
    parser.add_argument('--session-id', type=str, help='按会话ID过滤')

    # 日期参数
    parser.add_argument('--today', action='store_true', help='只导出今天的日志')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)')

    # 输出参数
    parser.add_argument('--output', type=str, help='输出文件名')
    parser.add_argument('--log-dir', type=str, default='logs/prompts', help='日志目录路径')

    args = parser.parse_args()

    # 确定日志目录
    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        print(f"❌ 错误: 日志目录不存在: {log_dir}")
        return

    # 确定日期过滤
    date_filter = None
    if args.today:
        date_filter = datetime.now().strftime("%Y-%m-%d")
    elif args.date:
        date_filter = args.date

    # 确定输出文件名
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if date_filter:
            output_file = f"prompts_{date_filter}.html"
        elif args.user_id:
            output_file = f"prompts_user_{args.user_id}_{timestamp}.html"
        else:
            output_file = f"prompts_all_{timestamp}.html"

    # 加载日志
    print(f"📂 正在加载日志... (目录: {log_dir})")
    logs = load_logs(log_dir, date_filter)
    print(f"   共加载 {len(logs)} 条记录")

    # 过滤日志
    logs = filter_logs(logs, user_id=args.user_id, session_id=args.session_id)
    print(f"   过滤后: {len(logs)} 条记录")

    if not logs:
        print("\n⚠️  没有找到符合条件的日志")
        return

    # 生成 HTML
    generate_html(logs, output_file)


if __name__ == '__main__':
    main()
