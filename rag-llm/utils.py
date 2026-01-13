import io
import json
import logging
import os
from functools import lru_cache

import fitz  # PyMuPDF
from PIL import Image
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
    RecursiveJsonSplitter,
    ExperimentalMarkdownSyntaxTextSplitter
)

logger = logging.getLogger(__name__)
try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


@lru_cache(maxsize=1)
def _load_config_cached():
    """Cache the configuration to avoid blocking I/O on every request"""
    config_path = "model_config.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file {config_path} not found")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_llm_instance(model_info: dict, temperature: float = None):
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

    # 初始化 LangChain ChatModel
    return init_chat_model(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature if temperature is not None else temperature,
        model_provider=settings['model_provider'] if "model_provider" in settings else None
    )

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


def markdown_split(markdown_text: str, headers_to_split_on: list = None):
    if headers_to_split_on is None:
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4")
        ]
    markdown_splitter = ExperimentalMarkdownSyntaxTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    return markdown_splitter.split_text(markdown_text)


def json_split(json_data: dict, min_chunk_size: int = 100, max_chunk_size: int = 1000):
    json_splitter = RecursiveJsonSplitter(min_chunk_size=min_chunk_size, max_chunk_size=max_chunk_size)
    return json_splitter.split_json(json_data)


def code_split(code_text: str, language: str, chunk_size: int = 1500, chunk_overlap: int = 0):
    language = Language(language)
    code_splitter = RecursiveCharacterTextSplitter.from_language(
        language=language, chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return code_splitter.split_text(code_text)


def plain_text_split(
        plain_text: str,
        chunk_size: int = 1000, chunk_overlap: int = 200,
        separators: list = None, force_split: bool = False,
        add_start_index: bool = True
):
    if separators is None:
        separators = ["\n\n", "\n", "。", "！", "？", "，", " "]
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
        file_path: str, chunk_size: int = 1000, chunk_overlap: int = 0,
        ocr_language: str = 'chi_sim+eng', text_threshold: int = 50
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
