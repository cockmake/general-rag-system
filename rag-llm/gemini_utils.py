import asyncio

from google import genai
from google.genai import types


# 统一返回结构
class ResponseWrapper:
    def __init__(self, content: str):
        self.content = content

    def __repr__(self):
        return f"ResponseWrapper(content='{self.content}')"


class GeminiInstance:
    def __init__(
            self,
            model_name: str,
            api_key: str,
            base_url: str,
            enable_web_search: bool = False,
            timeout: int = 30,
            max_retries: int = 2,
    ):
        """
        初始化 Gemini 实例
        :param api_key: API Key
        :param model_name: 模型名称，例如 "gemini-2.0-flash", "gemini-3-pro-preview"
        :param enable_web_search: 是否开启谷歌搜索 (Grounding)
        :param base_url: API 基础地址
        """
        self.model_name = model_name
        self.enable_web_search = enable_web_search

        # 配置 HTTP 选项
        retry_options = types.HttpRetryOptionsDict(attempts=max_retries)
        http_options = types.HttpOptionsDict(
            base_url=base_url,
            retry_options=retry_options,
            timeout=timeout * 1000,  # milliseconds
        )

        # 初始化客户端
        self.client = genai.Client(
            api_key=api_key,
            http_options=http_options
        )

        # 预定义搜索工具
        self.grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

    def _parse_messages(self, messages: list):
        """解析消息列表为 system_instruction 和 contents"""
        system_instruction = None
        contents = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")

            if role == "system":
                if system_instruction:
                    system_instruction += "\n" + content
                else:
                    system_instruction = content
            elif role == "user":
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=content)]
                ))
            elif role == "assistant":
                contents.append(types.Content(
                    role="model",
                    parts=[types.Part(text=content)]
                ))

        return system_instruction, contents

    def _get_config(self, system_instruction: str = None):
        """根据初始化参数动态生成配置"""
        # 根据 enable_web_search 决定是否添加工具
        tools = [self.grounding_tool] if self.enable_web_search else None

        return types.GenerateContentConfig(
            tools=tools,
            system_instruction=system_instruction
        )

    async def ainvoke(self, messages: list) -> ResponseWrapper:
        """一次性异步返回"""
        system_instruction, contents = self._parse_messages(messages)
        config = self._get_config(system_instruction)

        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config,
        )

        text = response.text if response.text else ""
        return ResponseWrapper(content=text)

    async def astream(self, messages: list):
        """异步流式返回"""
        system_instruction, contents = self._parse_messages(messages)
        config = self._get_config(system_instruction)

        response_stream = await self.client.aio.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
            config=config,
        )

        async for chunk in response_stream:
            if chunk.text:
                yield ResponseWrapper(content=chunk.text)


# --- 使用示例 ---

async def main():
    api_key = "sk-hlDrexmtGOoyUwAehGwCpWRIYJDI71tdJ1BtI4bdwuJVY8iv"
    base_url = "https://api.vectorengine.ai"
    messages = [
        {"role": "user", "content": "现在是北京什么时间？"},
    ]

    print("=== 实例 1: 开启搜索 （默认） ===")
    gemini_search = GeminiInstance(
        api_key=api_key,
        base_url=base_url,
        # model_name="gemini-3-pro-preview",
        # model_name="gemini-3-flash-preview",
        model_name="gemini-2.5-flash-thinking",
        enable_web_search=True,
    )
    async for chunk in gemini_search.astream(messages):
        print(chunk.content, end="", flush=True)
    print("\n")



if __name__ == "__main__":
    asyncio.run(main())
