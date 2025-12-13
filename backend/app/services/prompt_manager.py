"""
Prompt Manager Service

管理系统提示词配置文件的读取和更新
"""
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Optional
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptManager:
    """提示词管理服务"""

    # 提示词配置定义
    PROMPT_CONFIGS = [
        {
            "key": "onboarding",
            "display_name": "Onboarding",
            "file_path": "onboarding_instructions.yaml",
            "description": "用户引导问卷系统提示词"
        },
        {
            "key": "clerk",
            "display_name": "Clerk",
            "file_path": "clerk_base_instructions.yaml",
            "description": "Clerk 基础指令"
        },
        {
            "key": "clerk_over",
            "display_name": "Clerk Over",
            "file_path": "clerk_session_over_prompt.yaml",
            "description": "Clerk 会话结束提示词"
        },
        {
            "key": "therapist-timeout",
            "display_name": "Therapist Timeout",
            "file_path": "therapist_timeout.yaml",
            "description": "治疗师超时提示词"
        }
    ]

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        初始化提示词管理器

        Args:
            prompts_dir: 提示词配置文件目录，默认为 app/config/prompts
        """
        if prompts_dir is None:
            current_file = Path(__file__)
            app_dir = current_file.parent.parent
            prompts_dir = app_dir / "config" / "prompts"

        self.prompts_dir = Path(prompts_dir)

        if not self.prompts_dir.exists():
            raise ValueError(f"Prompts directory not found: {self.prompts_dir}")

    def get_all_prompts(self) -> List[Dict]:
        """
        读取所有提示词配置

        Returns:
            提示词配置列表，每个包含 name, display_name, file_path, content, metadata
        """
        prompts = []

        for config in self.PROMPT_CONFIGS:
            file_path = self.prompts_dir / config["file_path"]

            if not file_path.exists():
                logger.warning(f"Prompt file not found: {file_path}")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                prompt_data = {
                    "name": config["name"],
                    "display_name": config["display_name"],
                    "file_path": config["file_path"],
                    "content": data.get("system_prompt", ""),
                    "metadata": data.get("metadata", {})
                }

                prompts.append(prompt_data)

            except Exception as e:
                logger.error(f"Failed to load prompt {config['name']}: {e}")
                continue

        return prompts

    def get_prompt_by_name(self, name: str) -> Optional[Dict]:
        """
        根据名称获取单个提示词配置

        Args:
            name: 提示词名称

        Returns:
            提示词配置字典，如果不存在则返回 None
        """
        for config in self.PROMPT_CONFIGS:
            if config["name"] == name:
                file_path = self.prompts_dir / config["file_path"]

                if not file_path.exists():
                    return None

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)

                    return {
                        "name": config["name"],
                        "display_name": config["display_name"],
                        "file_path": config["file_path"],
                        "content": data.get("system_prompt", ""),
                        "metadata": data.get("metadata", {})
                    }

                except Exception as e:
                    logger.error(f"Failed to load prompt {name}: {e}")
                    return None

        return None

    def update_prompt(self, name: str, content: str, metadata: Optional[Dict] = None) -> bool:
        """
        更新单个提示词配置

        Args:
            name: 提示词名称
            content: 新的提示词内容
            metadata: 新的元数据（可选）

        Returns:
            是否更新成功
        """
        # 查找配置
        config = None
        for cfg in self.PROMPT_CONFIGS:
            if cfg["name"] == name:
                config = cfg
                break

        if not config:
            logger.error(f"Prompt config not found: {name}")
            return False

        file_path = self.prompts_dir / config["file_path"]

        if not file_path.exists():
            logger.error(f"Prompt file not found: {file_path}")
            return False

        try:
            # 读取现有配置
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # 备份原文件
            self._backup_file(file_path)

            # 更新内容
            data["system_prompt"] = content

            # 更新元数据（如果提供）
            if metadata is not None:
                if "metadata" not in data:
                    data["metadata"] = {}
                data["metadata"].update(metadata)

            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            logger.info(f"Successfully updated prompt: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to update prompt {name}: {e}", exc_info=True)
            return False

    def update_prompts_batch(self, prompts: List[Dict]) -> Dict[str, int]:
        """
        批量更新提示词配置

        Args:
            prompts: 提示词列表，每个包含 name, content, metadata

        Returns:
            更新结果统计 {"success": 成功数, "failed": 失败数}
        """
        success_count = 0
        failed_count = 0

        for prompt in prompts:
            name = prompt.get("name")
            content = prompt.get("content")
            metadata = prompt.get("metadata")

            if not name or not content:
                logger.warning(f"Invalid prompt data: {prompt}")
                failed_count += 1
                continue

            if self.update_prompt(name, content, metadata):
                success_count += 1
            else:
                failed_count += 1

        return {"success": success_count, "failed": failed_count}

    def validate_yaml_content(self, content: str) -> bool:
        """
        验证 YAML 内容格式

        Args:
            content: YAML 内容字符串

        Returns:
            是否有效
        """
        try:
            yaml.safe_load(content)
            return True
        except yaml.YAMLError:
            return False

    def get_file_prompts(self) -> List[Dict]:
        """
        获取所有文件型 prompts（4个文件）

        Returns:
            提示词配置列表，每个包含 key, display_name, file_path, content
        """
        prompts = []

        for config in self.PROMPT_CONFIGS:
            file_path = self.prompts_dir / config["file_path"]

            if not file_path.exists():
                logger.warning(f"Prompt file not found: {file_path}")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                prompt_data = {
                    "key": config["key"],
                    "display_name": config["display_name"],
                    "file_path": config["file_path"],
                    "content": data.get("system_prompt", "")
                }

                prompts.append(prompt_data)

            except Exception as e:
                logger.error(f"Failed to load prompt {config['key']}: {e}")
                continue

        return prompts

    def get_prompt_by_key(self, key: str) -> Optional[Dict]:
        """
        根据 key 获取单个文件型 prompt

        Args:
            key: 提示词 key (onboarding, clerk, clerk_over, therapist-general)

        Returns:
            提示词配置字典，如果不存在则返回 None
        """
        for config in self.PROMPT_CONFIGS:
            if config["key"] == key:
                file_path = self.prompts_dir / config["file_path"]

                if not file_path.exists():
                    logger.error(f"Prompt file not found: {file_path}")
                    return None

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)

                    return {
                        "key": config["key"],
                        "display_name": config["display_name"],
                        "file_path": config["file_path"],
                        "content": data.get("system_prompt", "")
                    }

                except Exception as e:
                    logger.error(f"Failed to load prompt {key}: {e}")
                    return None

        logger.error(f"Prompt config not found for key: {key}")
        return None

    def update_prompt_by_key(self, key: str, content: str) -> bool:
        """
        根据 key 更新文件型 prompt

        Args:
            key: 提示词 key
            content: 新的提示词内容

        Returns:
            是否更新成功
        """
        # 查找配置
        config = None
        for cfg in self.PROMPT_CONFIGS:
            if cfg["key"] == key:
                config = cfg
                break

        if not config:
            logger.error(f"Prompt config not found for key: {key}")
            return False

        file_path = self.prompts_dir / config["file_path"]

        if not file_path.exists():
            logger.error(f"Prompt file not found: {file_path}")
            return False

        try:
            # 读取现有配置
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # 备份原文件
            self._backup_file(file_path)

            # 更新内容（只更新 system_prompt，保持 metadata 不变）
            data["system_prompt"] = content

            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            logger.info(f"Successfully updated prompt: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to update prompt {key}: {e}", exc_info=True)
            return False

    def _backup_file(self, file_path: Path):
        """
        备份文件到 backups 目录

        Args:
            file_path: 要备份的文件路径
        """
        try:
            backup_dir = self.prompts_dir / "backups"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_name

            shutil.copy2(file_path, backup_path)
            logger.info(f"Backed up {file_path.name} to {backup_path}")

        except Exception as e:
            logger.warning(f"Failed to backup file {file_path}: {e}")


# 全局单例实例
_prompt_manager_instance: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """
    获取全局 PromptManager 单例实例

    Returns:
        PromptManager 实例
    """
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
    return _prompt_manager_instance
