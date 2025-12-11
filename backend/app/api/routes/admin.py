"""
Admin API Routes

管理后台相关的 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging
import os

from app.schemas.admin import (
    FilePromptItem,
    FilePromptsResponse,
    FilePromptUpdateRequest,
    FilePromptUpdateResponse,
    SessionConfigResponse,
    SessionConfigUpdateRequest,
    SessionConfigUpdateResponse
)
from app.services.prompt_manager import get_prompt_manager
from app.core.config import settings
from app.core.deps import get_current_admin
from app.db.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/prompts/files", response_model=FilePromptsResponse)
async def get_file_prompts(admin: User = Depends(get_current_admin)):
    """
    获取所有文件型提示词配置

    返回 4 个文件型 prompts：
    - onboarding: 用户引导问卷
    - clerk: Clerk 基础指令
    - clerk_over: Clerk 会话结束
    - therapist-general: 治疗师通用指令

    Returns:
        所有文件型提示词配置列表
    """
    try:
        manager = get_prompt_manager()
        prompts_data = manager.get_file_prompts()

        # 转换为 FilePromptItem 对象
        prompts = []
        for data in prompts_data:
            prompt = FilePromptItem(
                key=data["key"],
                display_name=data["display_name"],
                file_path=data["file_path"],
                content=data["content"]
            )
            prompts.append(prompt)

        return FilePromptsResponse(prompts=prompts)

    except Exception as e:
        logger.error(f"Failed to get file prompts: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load file prompts: {str(e)}"
        )


@router.put("/prompts/files/{prompt_key}", response_model=FilePromptUpdateResponse)
async def update_file_prompt(
    prompt_key: str,
    request: FilePromptUpdateRequest,
    admin: User = Depends(get_current_admin)
):
    """
    更新单个文件型提示词配置

    支持的 prompt_key：
    - onboarding
    - clerk
    - clerk_over
    - therapist-general

    Args:
        prompt_key: 提示词 key
        request: 包含新的 content

    Returns:
        更新结果
    """
    try:
        manager = get_prompt_manager()

        # 验证 key 是否存在
        valid_keys = ["onboarding", "clerk", "clerk_over", "therapist-general"]
        if prompt_key not in valid_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid prompt key: {prompt_key}. Valid keys: {', '.join(valid_keys)}"
            )

        # 更新 prompt
        success = manager.update_prompt_by_key(prompt_key, request.content)

        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update prompt: {prompt_key}"
            )

        # 清除 PromptLoader 缓存，让新配置生效
        from app.services.prompt_loader import get_prompt_loader
        prompt_loader = get_prompt_loader()
        prompt_loader.reload()

        # 获取更新后的 prompt
        updated_prompt_data = manager.get_prompt_by_key(prompt_key)
        if not updated_prompt_data:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve updated prompt: {prompt_key}"
            )

        updated_prompt = FilePromptItem(
            key=updated_prompt_data["key"],
            display_name=updated_prompt_data["display_name"],
            file_path=updated_prompt_data["file_path"],
            content=updated_prompt_data["content"]
        )

        logger.info(f"Updated file prompt: {prompt_key}")

        return FilePromptUpdateResponse(
            success=True,
            message=f"Successfully updated prompt: {prompt_key}",
            prompt=updated_prompt
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update file prompt {prompt_key}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update prompt: {str(e)}"
        )


@router.get("/session-config", response_model=SessionConfigResponse)
async def get_session_config(admin: User = Depends(get_current_admin)):
    """
    获取 Session 时间和轮数控制配置

    Returns:
        当前配置值
    """
    try:
        return SessionConfigResponse(
            suggested_duration_minutes=settings.SESSION_SUGGESTED_DURATION_MINUTES,
            suggested_turns=settings.SESSION_SUGGESTED_TURNS,
            reminder_interval=settings.SESSION_REMINDER_INTERVAL
        )
    except Exception as e:
        logger.error(f"Failed to get session config: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session config: {str(e)}"
        )


@router.put("/session-config", response_model=SessionConfigUpdateResponse)
async def update_session_config(
    request: SessionConfigUpdateRequest,
    admin: User = Depends(get_current_admin)
):
    """
    更新 Session 时间和轮数控制配置

    将配置写入 .env 文件，需要重启服务生效

    Args:
        request: 包含新的配置值

    Returns:
        更新结果
    """
    try:
        # .env 文件路径
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')

        # 读取现有 .env 内容
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []

        # 更新或添加配置
        config_keys = {
            'SESSION_SUGGESTED_DURATION_MINUTES': str(request.suggested_duration_minutes),
            'SESSION_SUGGESTED_TURNS': str(request.suggested_turns),
            'SESSION_REMINDER_INTERVAL': str(request.reminder_interval)
        }

        updated_keys = set()
        new_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                key = stripped.split('=')[0].strip()
                if key in config_keys:
                    new_lines.append(f"{key}={config_keys[key]}\n")
                    updated_keys.add(key)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        # 添加未更新的配置（新增）
        for key, value in config_keys.items():
            if key not in updated_keys:
                new_lines.append(f"\n# Session 时间和轮数控制\n{key}={value}\n")

        # 写回 .env 文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        logger.info(f"Updated session config: {config_keys}")

        return SessionConfigUpdateResponse(
            success=True,
            message="配置已更新，需要重启服务生效",
            config=SessionConfigResponse(
                suggested_duration_minutes=request.suggested_duration_minutes,
                suggested_turns=request.suggested_turns,
                reminder_interval=request.reminder_interval
            )
        )

    except Exception as e:
        logger.error(f"Failed to update session config: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session config: {str(e)}"
        )
