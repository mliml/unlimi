#!/usr/bin/env python3
"""
测试 OpenAI 日志功能

这个脚本验证日志系统的基本功能
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.openai_logger import (
    get_prompt_logger,
    openai_logging_context,
    get_current_user_context
)


def test_prompt_logger():
    """测试 prompt logger 基本功能"""
    print("=" * 60)
    print("测试 1: Prompt Logger 初始化")
    print("=" * 60)

    logger = get_prompt_logger()
    print(f"✓ Logger 初始化成功")
    print(f"  日志目录: {logger.log_dir}")
    print(f"  今日日志文件: {logger._get_log_file_path()}")

    # 检查目录是否存在
    assert logger.log_dir.exists(), "日志目录不存在"
    print(f"✓ 日志目录存在")


def test_logging_context():
    """测试日志上下文"""
    print("\n" + "=" * 60)
    print("测试 2: 日志上下文")
    print("=" * 60)

    # 测试上下文外
    ctx = get_current_user_context()
    assert ctx is None, "上下文应该为空"
    print("✓ 上下文外: None")

    # 测试上下文内
    with openai_logging_context(user_id=999, session_id="test-session", is_admin=True):
        ctx = get_current_user_context()
        assert ctx is not None, "上下文不应该为空"
        assert ctx["user_id"] == 999
        assert ctx["session_id"] == "test-session"
        assert ctx["is_admin"] is True
        print("✓ 上下文内: user_id=999, session_id=test-session, is_admin=True")

    # 测试上下文退出后
    ctx = get_current_user_context()
    assert ctx is None, "上下文应该被清除"
    print("✓ 上下文退出后: None")


def test_should_log():
    """测试是否应该记录的逻辑"""
    print("\n" + "=" * 60)
    print("测试 3: 是否记录判断")
    print("=" * 60)

    logger = get_prompt_logger()

    # Admin 用户应该记录
    should_log = logger.should_log_for_user(user_id=123, is_admin=True)
    assert should_log is True, "Admin 用户应该记录"
    print("✓ Admin 用户 (is_admin=True): 应该记录")

    # 非 Admin 用户不应该记录
    should_log = logger.should_log_for_user(user_id=456, is_admin=False)
    assert should_log is False, "非 Admin 用户不应该记录"
    print("✓ 普通用户 (is_admin=False): 不记录")

    # None user_id 不应该记录
    should_log = logger.should_log_for_user(user_id=None, is_admin=True)
    assert should_log is False, "None user_id 不应该记录"
    print("✓ None user_id: 不记录")


def test_log_request():
    """测试日志写入"""
    print("\n" + "=" * 60)
    print("测试 4: 日志写入")
    print("=" * 60)

    logger = get_prompt_logger()

    # 写入测试日志
    test_messages = [
        {"role": "system", "content": "你是一个测试助手"},
        {"role": "user", "content": "你好"}
    ]

    logger.log_request(
        user_id=999,
        session_id="test-session-123",
        model="gpt-4o-mini",
        messages=test_messages,
        request_params={"temperature": 0.7}
    )

    print("✓ 日志写入成功")

    # 检查文件是否存在
    log_file = logger._get_log_file_path()
    assert log_file.exists(), "日志文件不存在"
    print(f"✓ 日志文件存在: {log_file}")

    # 读取并验证内容
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    last_log = json.loads(lines[-1])
    assert last_log["user_id"] == 999
    assert last_log["session_id"] == "test-session-123"
    assert last_log["model"] == "gpt-4o-mini"
    assert len(last_log["messages"]) == 2
    print("✓ 日志内容验证通过")
    print(f"  记录的消息数: {len(last_log['messages'])}")


def test_log_response():
    """测试响应日志"""
    print("\n" + "=" * 60)
    print("测试 5: 响应日志")
    print("=" * 60)

    logger = get_prompt_logger()

    # 写入响应日志
    test_usage = {
        "prompt_tokens": 150,
        "completion_tokens": 50,
        "total_tokens": 200,
        "prompt_tokens_details": {
            "cached_tokens": 100
        }
    }

    logger.log_response(
        user_id=999,
        session_id="test-session-123",
        response_content="这是测试响应",
        usage=test_usage
    )

    print("✓ 响应日志写入成功")

    # 验证内容
    log_file = logger._get_log_file_path()
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    last_log = json.loads(lines[-1])
    assert last_log["type"] == "response"
    assert last_log["usage"]["prompt_tokens"] == 150
    assert last_log["usage"]["prompt_tokens_details"]["cached_tokens"] == 100
    print("✓ 响应日志内容验证通过")
    print(f"  Tokens: {last_log['usage']['total_tokens']}")
    print(f"  缓存: {last_log['usage']['prompt_tokens_details']['cached_tokens']}")


def main():
    print("\n" + "🧪 OpenAI 日志系统测试\n")

    try:
        test_prompt_logger()
        test_logging_context()
        test_should_log()
        test_log_request()
        test_log_response()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        print("\n💡 提示: 使用以下命令查看测试日志:")
        print("   python scripts/view_prompts.py --user-id 999 --show-full")
        print()

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
