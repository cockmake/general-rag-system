import logging
from typing import AsyncGenerator

from openai import AsyncOpenAI

from wrapper import ResponseWrapper

logger = logging.getLogger(__name__)


class OpenAIInstance:
    def __init__(
            self,
            model_name: str,
            api_key: str,
            base_url: str,
            timeout: int = 30,
            max_retries: int = 2,
            enable_thinking: bool = False
    ):
        self.model_name = model_name
        self.enable_thinking = enable_thinking
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries
        )

    async def ainvoke(self, messages: list) -> ResponseWrapper:
        extra_body = {}
        if self.enable_thinking:
            extra_body['enable_thinking'] = True

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=False,
                extra_body=extra_body if extra_body else None
            )
            content = response.choices[0].message.content
            return ResponseWrapper(content=content)
        except Exception as e:
            logger.error(f"OpenAI ainvoke error: {e}")
            raise e

    async def astream(self, messages: list) -> AsyncGenerator[ResponseWrapper, None]:
        extra_body = {}
        if self.enable_thinking:
            extra_body['enable_thinking'] = True

        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                stream=True,
                extra_body=extra_body if extra_body else None
            )

            async for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                # Handle reasoning content (e.g., DeepSeek/Qwen)
                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                    yield ResponseWrapper(content=[{"type": "reasoning", "text": delta.reasoning_content}])

                if delta.content:
                    yield ResponseWrapper(content=delta.content)

        except Exception as e:
            logger.error(f"OpenAI astream error: {e}")
            yield ResponseWrapper(content=f"Error: {str(e)}")
