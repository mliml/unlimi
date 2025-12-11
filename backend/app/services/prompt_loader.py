import yaml
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PromptLoader:
    """
    系统提示词加载器
    从 YAML 配置文件中加载 LLM 系统提示词
    """

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        初始化提示词加载器

        Args:
            prompts_dir: 提示词配置文件目录，默认为 app/config/prompts
        """
        if prompts_dir is None:
            # 默认指向 app/config/prompts 目录
            current_file = Path(__file__)
            app_dir = current_file.parent.parent  # 从 services 回到 app
            prompts_dir = app_dir / "config" / "prompts"

        self.prompts_dir = Path(prompts_dir)
        self._cache: Dict[str, str] = {}  # 缓存已加载的提示词

        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")

    def get_prompt(self, prompt_file: str) -> str:
        """
        获取指定配置文件中的系统提示词

        Args:
            prompt_file: YAML 配置文件名（如 "clerk_onboarding_prompt.yaml"）

        Returns:
            系统提示词字符串

        Raises:
            FileNotFoundError: 配置文件不存在
            ValueError: 配置文件格式错误或缺少 system_prompt 字段
        """
        # 检查缓存
        if prompt_file in self._cache:
            logger.debug(f"Loading prompt from cache: {prompt_file}")
            return self._cache[prompt_file]

        # 构建文件路径
        file_path = self.prompts_dir / prompt_file

        if not file_path.exists():
            error_msg = f"Prompt file not found: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            # 读取 YAML 文件
            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            # 提取 system_prompt
            if not isinstance(config, dict):
                raise ValueError(f"Invalid YAML format in {prompt_file}: expected dict")

            system_prompt = config.get("system_prompt")
            if not system_prompt:
                raise ValueError(f"Missing 'system_prompt' field in {prompt_file}")

            # 缓存提示词
            self._cache[prompt_file] = system_prompt
            logger.info(f"Successfully loaded prompt from {prompt_file}")

            return system_prompt

        except yaml.YAMLError as e:
            error_msg = f"Failed to parse YAML file {prompt_file}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Failed to load prompt from {prompt_file}: {e}"
            logger.error(error_msg)
            raise

    def reload(self, prompt_file: Optional[str] = None):
        """
        重新加载配置文件（清除缓存）

        Args:
            prompt_file: 指定要重新加载的文件，None 则清除全部缓存
        """
        if prompt_file:
            if prompt_file in self._cache:
                del self._cache[prompt_file]
                logger.info(f"Reloaded prompt: {prompt_file}")
        else:
            self._cache.clear()
            logger.info("Cleared all prompt cache")

    def get_metadata(self, prompt_file: str) -> Dict:
        """
        获取配置文件的元数据信息

        Args:
            prompt_file: YAML 配置文件名

        Returns:
            元数据字典，如果不存在则返回空字典
        """
        file_path = self.prompts_dir / prompt_file

        if not file_path.exists():
            logger.warning(f"Prompt file not found: {file_path}")
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            return config.get("metadata", {})

        except Exception as e:
            logger.error(f"Failed to load metadata from {prompt_file}: {e}")
            return {}


# 全局单例实例（可选）
_prompt_loader_instance: Optional[PromptLoader] = None


def get_prompt_loader() -> PromptLoader:
    """
    获取全局 PromptLoader 单例实例

    Returns:
        PromptLoader 实例
    """
    global _prompt_loader_instance
    if _prompt_loader_instance is None:
        _prompt_loader_instance = PromptLoader()
    return _prompt_loader_instance
