#!/usr/bin/env python3
"""
查看 OpenAI Prompt 日志工具

使用示例:
    # 查看某个用户的所有 prompts
    python scripts/view_prompts.py --user-id 123

    # 查看某个会话的 prompts
    python scripts/view_prompts.py --session-id abc-123

    # 查看今天的所有 prompts
    python scripts/view_prompts.py --today

    # 查看最近 N 条记录
    python scripts/view_prompts.py --last 10

    # 导出为 JSON
    python scripts/view_prompts.py --user-id 123 --export output.json

    # 查看某条记录的完整内容
    python scripts/view_prompts.py --show-full --last 1
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sys


def load_logs(log_dir: Path, date_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    加载日志文件

    Args:
        log_dir: 日志目录
        date_filter: 日期过滤 (YYYY-MM-DD)，None 表示所有日期

    Returns:
        日志条目列表
    """
    logs = []

    if date_filter:
        # 只读取指定日期的文件
        log_file = log_dir / f"therapist_prompts_{date_filter}.jsonl"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        logs.append(json.loads(line))
    else:
        # 读取所有 .jsonl 文件
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
    log_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """过滤日志"""
    filtered = logs

    if user_id is not None:
        filtered = [log for log in filtered if log.get('user_id') == user_id]

    if session_id is not None:
        filtered = [log for log in filtered if log.get('session_id') == session_id]

    if log_type is not None:
        filtered = [log for log in filtered if log.get('type') == log_type]

    return filtered


def format_message_summary(messages: List[Dict]) -> str:
    """格式化消息摘要"""
    summary = []
    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')

        # 截取内容前 100 个字符
        if isinstance(content, str):
            preview = content[:100] + '...' if len(content) > 100 else content
        else:
            preview = str(content)[:100]

        summary.append(f"  [{role}] {preview}")

    return "\n".join(summary)


def print_log_entry(entry: Dict[str, Any], show_full: bool = False):
    """打印单条日志"""
    timestamp = entry.get('timestamp', 'unknown')
    user_id = entry.get('user_id', 'unknown')
    session_id = entry.get('session_id', 'unknown')
    log_type = entry.get('type', 'request')

    print(f"\n{'='*80}")
    print(f"时间: {timestamp}")
    print(f"用户: {user_id}")
    print(f"会话: {session_id}")
    print(f"类型: {log_type}")

    if log_type == 'request' or 'messages' in entry:
        # 请求日志
        model = entry.get('model', 'unknown')
        messages = entry.get('messages', [])

        print(f"模型: {model}")
        print(f"消息数: {len(messages)}")

        if show_full:
            print("\n完整消息:")
            print(json.dumps(messages, ensure_ascii=False, indent=2))
        else:
            print("\n消息摘要:")
            print(format_message_summary(messages))

        # 显示请求参数
        request_params = entry.get('request_params', {})
        if request_params:
            print(f"\n请求参数: {json.dumps(request_params, ensure_ascii=False)}")

    elif log_type == 'response':
        # 响应日志
        content = entry.get('content', '')
        usage = entry.get('usage', {})

        print(f"\n响应内容:")
        if show_full:
            print(content)
        else:
            preview = content[:200] + '...' if len(content) > 200 else content
            print(preview)

        # 显示 token 使用情况
        if usage:
            print(f"\nToken 使用:")
            print(f"  输入: {usage.get('prompt_tokens', 0)}")
            print(f"  输出: {usage.get('completion_tokens', 0)}")
            print(f"  总计: {usage.get('total_tokens', 0)}")

            # 缓存信息
            prompt_details = usage.get('prompt_tokens_details', {})
            if prompt_details:
                cached = prompt_details.get('cached_tokens', 0)
                total_prompt = usage.get('prompt_tokens', 0)
                if cached > 0:
                    cache_rate = (cached / total_prompt * 100) if total_prompt > 0 else 0
                    print(f"  缓存: {cached}/{total_prompt} ({cache_rate:.1f}%)")


def export_logs(logs: List[Dict[str, Any]], output_file: str):
    """导出日志为 JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    print(f"\n已导出 {len(logs)} 条记录到 {output_file}")


def main():
    parser = argparse.ArgumentParser(description='查看 OpenAI Prompt 日志')

    # 过滤参数
    parser.add_argument('--user-id', type=int, help='按用户ID过滤')
    parser.add_argument('--session-id', type=str, help='按会话ID过滤')
    parser.add_argument('--type', type=str, choices=['request', 'response'], help='日志类型')

    # 日期参数
    parser.add_argument('--today', action='store_true', help='只查看今天的日志')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)')

    # 显示参数
    parser.add_argument('--last', type=int, help='显示最近 N 条记录')
    parser.add_argument('--show-full', action='store_true', help='显示完整内容（不截断）')

    # 导出参数
    parser.add_argument('--export', type=str, help='导出到 JSON 文件')

    # 日志目录
    parser.add_argument('--log-dir', type=str, default='logs/prompts', help='日志目录路径')

    args = parser.parse_args()

    # 确定日志目录
    log_dir = Path(args.log_dir)
    if not log_dir.exists():
        print(f"错误: 日志目录不存在: {log_dir}")
        sys.exit(1)

    # 确定日期过滤
    date_filter = None
    if args.today:
        date_filter = datetime.now().strftime("%Y-%m-%d")
    elif args.date:
        date_filter = args.date

    # 加载日志
    print(f"正在加载日志... (目录: {log_dir})")
    logs = load_logs(log_dir, date_filter)
    print(f"共加载 {len(logs)} 条记录")

    # 过滤日志
    logs = filter_logs(
        logs,
        user_id=args.user_id,
        session_id=args.session_id,
        log_type=args.type
    )
    print(f"过滤后: {len(logs)} 条记录")

    if not logs:
        print("没有找到符合条件的日志")
        return

    # 按时间排序
    logs.sort(key=lambda x: x.get('timestamp', ''))

    # 限制显示数量
    if args.last:
        logs = logs[-args.last:]

    # 导出或显示
    if args.export:
        export_logs(logs, args.export)
    else:
        # 显示日志
        for entry in logs:
            print_log_entry(entry, show_full=args.show_full)

        print(f"\n{'='*80}")
        print(f"共显示 {len(logs)} 条记录")


if __name__ == '__main__':
    main()
