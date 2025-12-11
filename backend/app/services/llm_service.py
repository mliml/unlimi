import os
from typing import List, Dict
from openai import OpenAI
import logging


logger = logging.getLogger(__name__)


class LLMService:
    """
    统一的 LLM 服务，封装所有 OpenAI API 调用
    """

    def __init__(self, api_key: str = None):
        """
        Initialize LLM service.

        Args:
            api_key: OpenAI API key. If None, reads from environment variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key)

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        统一的 completion 方法，返回纯文本

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            model: 模型名称 (default: gpt-4o)
            temperature: 温度参数 (default: 0.7)
            max_tokens: 最大 token 数 (default: 2000)

        Returns:
            生成的文本内容

        Raises:
            Exception: If the API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM API error: {e}", exc_info=True)
            raise Exception(f"Error calling OpenAI API: {str(e)}")

    def ask_simple(self, prompt: str, model: str = "gpt-4o") -> str:
        """
        简单的单轮对话（向后兼容 ask_gpt）

        Args:
            prompt: 用户提示词
            model: 模型名称 (default: gpt-4o)

        Returns:
            生成的文本内容
        """
        messages = [{"role": "user", "content": prompt}]
        return self.generate_completion(messages, model=model, temperature=0.7, max_tokens=2000)