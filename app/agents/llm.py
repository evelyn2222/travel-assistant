import json
import os
from typing import Any

import openai


class LLMClient:
    def __init__(self) -> None:
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def json_completion(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """
        返回 JSON 字典。若缺少 API Key 或解析失败，抛出异常供上层兜底。
        """
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
        text = response['choices'][0]['message']['content']
        return json.loads(text)
