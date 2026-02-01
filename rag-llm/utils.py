import base64
import io
import json
import logging
import os
import re
from functools import lru_cache

import fitz  # PyMuPDF
import tiktoken
from PIL import Image
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.language_models import BaseChatModel
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
    RecursiveJsonSplitter,
    MarkdownHeaderTextSplitter
)

from gemini_utils import GeminiInstance
from openai_utils import OpenAIInstance

logger = logging.getLogger(__name__)
try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


# 统一返回结构


@lru_cache(maxsize=1)
def _load_config_cached():
    """Cache the configuration to avoid blocking I/O on every request"""
    config_path = "model_config.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_llm_instance(
        model_info: dict,
        temperature: float = None,
        enable_web_search: bool = False,
        timeout: int = 60,
        max_retries: int = 5,
):
    """根据模型信息加载配置并初始化 LLM"""
    provider = model_info.get("provider")
    model_name = model_info.get("name")

    if not provider or not model_name:
        raise ValueError("Model provider and name are required")

    config = _load_config_cached()
    config = config['chat']

    provider_config = config.get(provider)
    if not provider_config:
        raise ValueError(f"Provider '{provider}' not found in configuration")

    # 合并配置：公共配置 < 模型特定配置
    settings = provider_config.get("settings", {}).copy()
    model_specific_settings = provider_config.get(model_name, {})
    settings.update(model_specific_settings)

    api_key = settings.get("api_key")
    base_url = settings.get("base_url")

    if model_name.startswith("gemini"):
        return GeminiInstance(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            enable_web_search=enable_web_search,
            timeout=timeout,
            max_retries=max_retries,
        )
    # 初始化 LangChain ChatModel
    llm = init_chat_model(
        model=model_name,
        api_key=api_key,
        base_url=settings["response_base_url"] if enable_web_search and "response_base_url" in settings else base_url,
        temperature=temperature if temperature is not None else temperature,
        model_provider=settings['model_provider'] if "model_provider" in settings else None,
        timeout=timeout,
        max_retries=max_retries,
    )
    # thinking配置
    if model_name.startswith("gpt-5.2-chat"):
        llm = llm.bind(
            reasoning={
                "effort": "medium",
                "summary": "detailed"
            },
        )
    # tools配置
    if enable_web_search:
        if model_name == "qwen3-max":
            llm = llm.bind(
                extra_body={"enable_search": True}
            )
        elif model_name == "qwen3-max-2026-01-23":
            llm = llm.bind(
                tools=[
                    {"type": "web_search"},
                    {"type": "web_extractor"},
                    {"type": "code_interpreter"},
                ],
                extra_body={"enable_thinking": True}
            )
        elif model_name.startswith("gpt-5.2-chat"):
            llm = llm.bind(
                tools=[
                    {"type": "web_search_preview"},
                ],
            )
        elif model_name.startswith("doubao-seed"):
            llm = llm.bind(
                tools=[
                    {"type": "web_search"},
                ]
            )
    return llm


def get_embedding_instance(embedding_info: dict):
    """根据嵌入模型信息加载配置并初始化 Embedding"""
    provider = embedding_info.get("provider")
    model_name = embedding_info.get("name")

    if not provider or not model_name:
        raise ValueError("Embedding provider and name are required")

    config = _load_config_cached()
    config = config['embedding']

    provider_config = config.get(provider)
    if not provider_config:
        raise ValueError(f"Provider '{provider}' not found in configuration")

    # 合并配置：公共配置 < 模型特定配置
    settings = provider_config.get("settings", {}).copy()
    model_specific_settings = provider_config.get(model_name, {})
    settings.update(model_specific_settings)

    api_key = settings.get("api_key")
    base_url = settings.get("base_url")

    # 初始化 LangChain Embedding
    return init_embeddings(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        provider=settings['provider'] if "provider" in settings else None,
        dimensions=settings['dimensions'] if "dimensions" in settings else None,
        check_embedding_ctx_length=settings.get('check_embedding_ctx_length', False)
    )


def get_structured_data_agent(llm: BaseChatModel, data_type):
    return create_agent(
        model=llm,
        response_format=data_type
    )


def markdown_split(
        markdown_text: str,
        headers_to_split_on: list = None,
        chunk_size: int = 2048,
        chunk_overlap: int = 150,
):
    if headers_to_split_on is None:
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3")
        ]
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )
    markdown_splits = markdown_splitter.split_text(markdown_text)
    separators = [
        "\n\n", "\n",
        "。", "！", "？",
        ".", "!", "?",
        "，", ",", " "
    ]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        add_start_index=True
    )
    return text_splitter.split_documents(markdown_splits)


def json_split(json_data: dict, min_chunk_size: int = 100, max_chunk_size: int = 1000):
    json_splitter = RecursiveJsonSplitter(min_chunk_size=min_chunk_size, max_chunk_size=max_chunk_size)
    return json_splitter.split_json(json_data)


def code_split(code_text: str, language: str, chunk_size: int = 1500, chunk_overlap: int = 200):
    language = Language(language)
    code_splitter = RecursiveCharacterTextSplitter.from_language(
        language=language, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return code_splitter.split_text(code_text)


def plain_text_split(
        plain_text: str,
        chunk_size: int = 1000, chunk_overlap: int = 150,
        separators: list = None, force_split: bool = False,
        add_start_index: bool = True
):
    pattern = r'(?<=[\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef])\s+(?=[\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef])'
    plain_text = re.sub(pattern, '', plain_text)
    if separators is None:
        separators = [
            "\n\n", "\n",
            "。", "！", "？",
            ".", "!", "?",
            "，", ",", " "
        ]
    if force_split:
        if "" not in separators:
            separators.append("")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        add_start_index=add_start_index
    )
    return text_splitter.split_text(plain_text)


def _extract_text_with_ocr(pdf_path: str, language: str = 'chi_sim+eng'):
    """
    使用OCR从图片型PDF中提取文本

    Args:
        pdf_path: PDF文件路径
        language: OCR识别语言，默认中英文 (chi_sim+eng)

    Returns:
        提取的文本内容
    """
    if not TESSERACT_AVAILABLE:
        raise ImportError("pytesseract not installed. Install with: pip install pytesseract")

    doc = fitz.open(pdf_path)
    all_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # 将页面转换为图片（使用较高DPI以提高OCR准确率）
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍放大
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))

        # 使用pytesseract进行OCR识别
        text = pytesseract.image_to_string(img, lang=language)
        all_text.append(text)

        logger.info(f"OCR处理进度: {page_num + 1}/{len(doc)}")

    doc.close()
    return "\n".join(all_text)


def pdf_split(
        file_path: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
        text_threshold: int = 20,
        ocr_language: str = 'chi_sim+eng',
):
    """
    对PDF进行完美划分：全文合并后切分，解决跨页段落问题。
    自动检测图片型PDF并使用OCR提取文本。

    Args:
        file_path: PDF文件路径
        chunk_size: 文本块大小
        chunk_overlap: 文本块重叠大小
        ocr_language: OCR识别语言，默认中英文 (chi_sim+eng)
        text_threshold: 文本长度阈值，低于此值则认为是图片型PDF
    Returns:
        切分后的文本块列表
    """
    # 首先尝试常规文本提取
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    logger.info(f"PDF加载完成，页数：{len(docs)}")

    # 合并所有页面的文本
    text = "".join([doc.page_content for doc in docs]).replace('\n', '')

    # 检测是否为图片型PDF（文本内容过少）
    if len(text.strip()) < text_threshold:
        logger.info(f"检测到图片型PDF（文本长度: {len(text)}），启动OCR识别...")
        if not TESSERACT_AVAILABLE:
            logger.warning("警告: pytesseract未安装，无法进行OCR识别")
            logger.warning("安装方法: pip install pytesseract")
            logger.warning("还需要安装Tesseract-OCR: https://github.com/tesseract-ocr/tesseract")
            return []

        try:
            # 放到线程中执行以避免阻塞
            # text = _extract_text_with_ocr(file_path, ocr_language)
            text = _extract_text_with_ocr(file_path, ocr_language)
            text = text.replace('\n', ' ')
            logger.info(f"OCR识别完成，提取文本长度: {len(text)}")
        except Exception as e:
            logger.error(f"OCR识别失败: {str(e)}")
            return []
    else:
        logger.info(f"文本型PDF，直接提取文本（长度: {len(text)}）")

    # 切分文本
    return plain_text_split(
        plain_text=text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )


async def image_split(
        file_input,
        chunk_size: int = 2048,
        chunk_overlap: int = 150,
):
    # 1. 读取图片数据并转Base64
    image_data = None
    if isinstance(file_input, str):
        with open(file_input, "rb") as f:
            image_data = f.read()
    else:
        # 假设是 file-like object
        if hasattr(file_input, 'seek'):
            file_input.seek(0)
        image_data = file_input.read()

    base64_image = base64.b64encode(image_data).decode('utf-8')

    # 2. 获取配置 (优先读取配置，兜底使用 t.py 中的 key)
    model_info = {
        'name': 'qwen3-vl-flash',
        'provider': 'qwen'
    }
    config = _load_config_cached()
    config = config['chat']
    provider_config = config.get(model_info['provider'])
    if not provider_config:
        raise ValueError(f"Provider '{model_info['provider']}' not found in configuration")
    # 合并配置：公共配置 < 模型特定配置
    settings = provider_config.get("settings", {}).copy()
    model_specific_settings = provider_config.get(model_info['name'], {})
    settings.update(model_specific_settings)

    api_key = settings.get('api_key', None)
    base_url = settings.get('base_url', None)

    if not api_key or not base_url:
        raise ValueError("API key and base URL must be provided in configuration for Qwen models.")

    # 3. 初始化 LLM
    llm = OpenAIInstance(
        model_name=model_info['name'],
        api_key=api_key,
        base_url=base_url
    )

    # 4. 构造 Prompt
    prompt = (
        "你是一个图像详细描述生成模型，请根据提供的图片内容生成清晰的文本描述。\n"
        "遵循以下要求：\n"
        "1. 请详细描述这张图片的内容。如果图片为纯文字图，请完整转录文字；\n"
        "2. 如果图片是架构图、流程图或图表等，请详细解释其结构、组件、关系和流程。\n"
    )
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
                {"type": "text", "text": prompt},
            ],
        },
    ]

    # 5. 调用模型
    try:
        response = await llm.ainvoke(messages)
        text = response.content
        logger.info(f"Image description generated, length: {len(text)}")
    except Exception as e:
        logger.error(f"Failed to generate image description: {e}")
        # 降级处理：如果调用失败，尝试返回空或者报错，这里选择返回空列表
        return []
    return markdown_split(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def get_token_count(text: str, encoding_name: str = "cl100k_base") -> int:
    """计算文本的token数量"""
    try:
        encoding = tiktoken.get_encoding(encoding_name)
    except Exception:
        # Fallback to cl100k_base if specific encoding not found
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def cut_history(history: list, model: dict):
    current_msg = history[-1]
    previous_msgs = history[:-1]

    processed_context = []
    current_token_count = get_token_count(current_msg.get('content') or "")
    n = len(previous_msgs)
    model_name = model.get("name", "")

    max_tokens = 15360
    if (model_name.startswith("gpt-5.2-chat") or
            model_name.startswith("gemini-3-pro") or
            model_name == "grok-4.1" or
            model_name.startswith("kimi-k2")
    ):
        max_tokens = 12800
    elif model_name.startswith("gemini-3-flash"):
        max_tokens = 20480

    for i in range(n, 1, -2):
        pair = previous_msgs[i - 2: i]
        pair_tokens = sum(get_token_count(m.get('content') or "") for m in pair)

        if current_token_count + pair_tokens < max_tokens:
            current_token_count += pair_tokens
            processed_context = pair + processed_context
        else:
            logger.info(f"截断历史对话触发")
            break
    return processed_context + [current_msg], current_token_count


def content_extractor(content):
    """提取content中的文本和推理内容"""
    think_content = ""
    text_content = ""
    if isinstance(content, str):
        text_content = content
    elif isinstance(content, list):
        item = content[0]
        if item['type'] == 'text':
            if isinstance(item, str):
                text_content += item
            elif isinstance(item, dict) and "text" in item:
                text_content += item["text"]
        elif item['type'] == 'reasoning':
            if "text" in item:
                think_content += item["text"]
            elif "summary" in item:
                summary = item["summary"]
                if len(summary) > 0:
                    summary = summary[0]
                    if "text" in summary:
                        think_content += summary["text"]
    return think_content, text_content


def get_display_docs(documents: list, max_tokens: int = 2048, min_docs: int = 1):
    """根据token限制筛选展示的文档"""
    if len(documents) <= min_docs:
        return documents
    display_docs = [documents[i] for i in range(min_docs)]
    total_tokens = sum(get_token_count(documents[i].page_content) for i in range(min_docs))
    if total_tokens >= max_tokens:
        return display_docs
    for doc in documents[min_docs:]:
        content = doc.page_content
        doc_tokens = get_token_count(content)
        if total_tokens + doc_tokens <= max_tokens:
            display_docs.append(doc)
            total_tokens += doc_tokens
        else:
            break
    return display_docs


def reasoning_content_wrapper(chunk):
    if chunk.response_metadata:
        response_metadata = chunk.response_metadata
        if response_metadata.get("model_provider", ""):
            additional_kwargs = chunk.additional_kwargs
            reasoning_content = additional_kwargs.get("reasoning_content", "")
            if reasoning_content:
                return [{"type": "reasoning", "text": reasoning_content}]
    return ""
