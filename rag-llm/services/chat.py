import json
import logging
import time
from typing import Optional

from fastapi import APIRouter, Body, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage

from rag_utils import rag_service
from utils import get_llm_instance, cut_history, get_token_count

logger = logging.getLogger(__name__)

chat_service = APIRouter(prefix="/chat", tags=["chat"])


async def stream_generator(model_instance, messages, prompt_tokens: int = 0, options: dict = None):
    """纯LLM流式响应生成器"""
    full_content = ""
    start_time = time.time()  # Start timing

    async for chunk in model_instance.astream(messages):
        content = chunk.content
        if content:
            if isinstance(content, list):
                text_content = ""
                for item in content:
                    if isinstance(item, str):
                        text_content += item
                    elif isinstance(item, dict) and "text" in item:
                        text_content += item["text"]
                content = text_content

            full_content += content
            # 对content进行json.dumps包裹，防止特殊字符导致JSON解析错误
            data = {
                "type": "content",
                "payload": json.dumps(content, ensure_ascii=False)
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    end_time = time.time()
    latency_ms = int((end_time - start_time) * 1000)  # Calculate latency
    completion_tokens = get_token_count(full_content)
    usage_data = {
        "type": "usage",
        "payload": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "latency_ms": latency_ms  # Add latency_ms
        }
    }
    yield f"data: {json.dumps(usage_data)}\n\n"


async def rag_stream_generator(
        question: str,
        history: list,
        model_info: dict,
        kb_id: Optional[int] = None,
        user_id: Optional[int] = None,
        system_prompt: Optional[str] = None,
        prompt_tokens: int = 0,
        options: dict = None,
):
    """
    RAG流式响应生成器

    流程：
    1. 生成多角度查询
    2. 并行检索知识库
    3. 并行评估文档相关性
    4. 流式生成答案
    """
    full_content = ""
    rag_process_data = []
    start_time = time.time()  # Start timing

    async for item in rag_service.stream_rag_response_with_process(
            question=question,
            history=history,
            model_info=model_info,
            kb_id=kb_id,
            user_id=user_id,
            system_prompt=system_prompt,
            options=options,
            top_k=20,

            grade_top_n=30,
            grade_score_threshold=0.5,

            top_n=18,
    ):
        if item["type"] == "process":
            # 检索过程信息
            rag_process_data.append(item["payload"])
            # 对payload进行json.dumps包裹，防止特殊字符导致JSON解析错误
            process_data = {
                "type": "process",
                "payload": json.dumps(item["payload"], ensure_ascii=False)
            }
            yield f"data: {json.dumps(process_data, ensure_ascii=False)}\n\n"
        elif item["type"] == "content":
            # 答案内容
            content = item["payload"]
            if content:
                full_content += content
                # 对content进行json.dumps包裹，防止特殊字符导致JSON解析错误
                data = {
                    "type": "content",
                    "payload": json.dumps(content, ensure_ascii=False)
                }
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    # 发送RAG过程汇总
    if rag_process_data:
        # 对payload进行json.dumps包裹，防止特殊字符导致JSON解析错误
        rag_summary = {
            "type": "rag_summary",
            "payload": json.dumps(rag_process_data, ensure_ascii=False)
        }
        yield f"data: {json.dumps(rag_summary, ensure_ascii=False)}\n\n"

    # 发送使用统计
    end_time = time.time()
    latency_ms = int((end_time - start_time) * 1000)  # Calculate latency

    completion_tokens = get_token_count(full_content)
    usage_data = {
        "type": "usage",
        "payload": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": completion_tokens + prompt_tokens,
            "latency_ms": latency_ms  # Add latency_ms
        }
    }
    yield f"data: {json.dumps(usage_data)}\n\n"


def build_langchain_messages(history: list) -> list:
    """
    将历史消息转换为LangChain消息格式

    Args:
        history: 原始历史消息列表

    Returns:
        LangChain消息列表
    """
    langchain_messages = []
    for msg in history:
        role = msg.get('role')
        content = msg.get('content')
        if role == 'user':
            langchain_messages.append(HumanMessage(content=content))
        elif role == 'assistant':
            langchain_messages.append(AIMessage(content=content))
    return langchain_messages


"""
history:
[{'id': 1, 'role': 'user|assistant', 'content': '...', 'ragContext': '...'}]
model:
{'id': 7, 'name': 'gemini-2.5-flash', 'provider': 'gemini', 'metadata': '{}'}
options:
{'kbId': 123, 'userId': 456, 'systemPrompt': '...'}
"""


@chat_service.post("/stream")
async def chat_stream(
        request: Request,
        history: list = Body(default=[]),
        model: dict = Body(),
        options: dict = Body(default={})
):
    logger.info(f"Received chat stream request: model={model}, options={options}")
    """
    流式对话接口

    支持两种模式：
    1. 纯LLM模式：当options中没有kbId时，直接使用LLM生成回复
    2. RAG模式：当options中有kbId时，执行多角度查询、并行检索、评分后生成回复

    流程（RAG模式）：
    1. 根据用户问题生成3-5个不同角度的查询（调用LLM）
    2. 并行检索知识库获取相关文档
    3. 并行评估文档相关性并打分
    4. 合并连续的文档切片
    5. 汇总相关文档并流式生成答案
    """
    # 从options中提取参数
    user_id = options.get('userId')  # 注意这个userId是指知识库持有者的ID，不是当前提问用户的ID
    kb_id = options.get('kbId')
    system_prompt = options.get('systemPrompt')

    # 有些模型暂时自动开启联网模型
    model_name = model.get('name', '')
    if model_name == 'qwen3-max' or model_name.startswith("gpt-5.2-chat"):
        options['webSearch'] = True

    # 截断策略：保留最新用户问题，其余历史按(user, assistant)成组，总token数<20480
    prompt_tokens = 0
    if history:
        history, prompt_tokens = cut_history(history, model)

    logger.info(f"保留历史对话消息数: {len(history) // 2} + 1")
    # 构建LangChain消息列表（不包含最后一条用户消息）
    langchain_messages = build_langchain_messages(history[:-1] if history else [])

    # 提取当前用户问题
    current_question = history[-1]['content']

    if not current_question:
        # 如果没有用户问题，返回错误
        async def error_generator():
            error_data = {
                "type": "error",
                "payload": "No user question found in history"
            }
            yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream"
        )

    # 如果有知识库ID，使用RAG模式
    if kb_id and user_id:
        logger.info(f"使用RAG模式，知识库ID: {kb_id}, 用户ID: {user_id}")
        return StreamingResponse(
            rag_stream_generator(
                question=current_question,
                history=langchain_messages,
                model_info=model,
                kb_id=kb_id,
                user_id=user_id,
                system_prompt=system_prompt,
                prompt_tokens=prompt_tokens,
                options=options
            ),
            media_type="text/event-stream"
        )

    # 否则使用纯LLM模式
    else:
        logger.info("使用纯LLM模式")
        llm = get_llm_instance(model, enable_web_search=options.get('webSearch', False))

        # 添加当前问题到消息列表
        all_messages = langchain_messages + [HumanMessage(content=current_question)]

        messages_with_system = []
        # messages_with_system = [{"role": "system", "content": system_prompt}]
        for msg in all_messages:
            if isinstance(msg, HumanMessage):
                messages_with_system.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages_with_system.append({"role": "assistant", "content": msg.content})
        all_messages = messages_with_system

        return StreamingResponse(
            stream_generator(llm, all_messages, prompt_tokens=prompt_tokens, options=options),
            media_type="text/event-stream"
        )
