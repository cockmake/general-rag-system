"""
Rerank Service - FastAPI服务
基于vLLM的高性能Rerank推理服务
"""
import logging
import math
import time
from contextlib import asynccontextmanager
from typing import List, Optional

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from vllm.inputs.data import TokensPrompt

from config.rerank_config import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ================= 配置参数 =================
# 使用config对象替代环境变量


# ================= 数据模型 =================
class QueryDocPair(BaseModel):
    """查询-文档对"""
    query: str = Field(..., description="查询文本")
    document: str = Field(..., description="文档文本")


class RerankRequest(BaseModel):
    """Rerank请求模型"""
    pairs: List[QueryDocPair] = Field(..., description="查询-文档对列表")
    instruction: Optional[str] = Field(
        "Given a web search query, retrieve relevant passages that answer the query",
        description="任务指令"
    )
    model: Optional[str] = Field(None, description="模型名称（当前版本忽略此字段）")

    class Config:
        json_schema_extra = {
            "example": {
                "pairs": [
                    {
                        "query": "What is the capital of China?",
                        "document": "The capital of China is Beijing."
                    },
                    {
                        "query": "Explain gravity",
                        "document": "Gravity is a force that attracts two bodies towards each other."
                    }
                ],
                "instruction": "Given a web search query, retrieve relevant passages that answer the query"
            }
        }


class RerankResult(BaseModel):
    """单个Rerank结果"""
    index: int = Field(..., description="索引位置")
    score: float = Field(..., description="相关性分数")
    query: str = Field(..., description="查询文本")
    document: str = Field(..., description="文档文本")


class RerankResponse(BaseModel):
    """Rerank响应模型"""
    results: List[RerankResult] = Field(..., description="Rerank结果列表")
    model: str = Field(..., description="使用的模型名称")
    processing_time: float = Field(..., description="处理时间（秒）")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    model: str
    gpu_memory_utilization: float
    max_model_len: int
    device: str


# ================= 全局变量 =================
rerank_model: Optional[LLM] = None
tokenizer: Optional[AutoTokenizer] = None
suffix_tokens: Optional[List[int]] = None
true_token: Optional[int] = None
false_token: Optional[int] = None
sampling_params: Optional[SamplingParams] = None


# ================= 工具函数 =================
def format_instruction(instruction: str, query: str, doc: str) -> List[dict]:
    """格式化指令、查询和文档"""
    text = [
        {
            "role": "system",
            "content": "Judge whether the Document meets the requirements based on the Query and the Instruct provided. Note that the answer can only be \"yes\" or \"no\"."
        },
        {
            "role": "user",
            "content": f"<Instruct>: {instruction}\n\n<Query>: {query}\n\n<Document>: {doc}"
        }
    ]
    return text


def process_inputs(
        pairs: List[tuple],
        instruction: str,
        max_length: int,
        suffix_tokens: List[int]
) -> List[TokensPrompt]:
    """处理输入的查询-文档对"""
    messages = [format_instruction(instruction, query, doc) for query, doc in pairs]
    messages = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=False, enable_thinking=False
    )
    messages = [ele[:max_length] + suffix_tokens for ele in messages]
    messages = [TokensPrompt(prompt_token_ids=ele) for ele in messages]
    return messages


def compute_scores(
        model: LLM,
        messages: List[TokensPrompt],
        sampling_params: SamplingParams,
        true_token: int,
        false_token: int
) -> List[float]:
    """计算相关性分数"""
    outputs = model.generate(messages, sampling_params, use_tqdm=False)
    scores = []

    for i in range(len(outputs)):
        final_logits = outputs[i].outputs[0].logprobs[-1]

        # 获取yes和no的logit
        if true_token not in final_logits:
            true_logit = -10
        else:
            true_logit = final_logits[true_token].logprob

        if false_token not in final_logits:
            false_logit = -10
        else:
            false_logit = final_logits[false_token].logprob

        # 计算归一化分数
        true_score = math.exp(true_logit)
        false_score = math.exp(false_logit)
        score = true_score / (true_score + false_score)
        scores.append(score)

    return scores


# ================= 生命周期管理 =================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global rerank_model, tokenizer, suffix_tokens, true_token, false_token, sampling_params

    logger.info("=" * 60)
    logger.info("Rerank Service Starting...")
    logger.info("=" * 60)
    logger.info(f"Model: {config.model_name}")
    logger.info(f"GPU Memory Utilization: {config.gpu_memory_utilization}")
    logger.info(f"Max Model Length: {config.max_model_len}")
    logger.info(f"Tensor Parallel Size: {config.tensor_parallel_size}")
    logger.info(f"DType: {config.dtype}")

    try:
        # 检查GPU可用性
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            logger.info(f"GPU Available: {gpu_count} GPU(s) detected")
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1024 ** 3
                logger.info(f"  GPU {i}: {gpu_name} ({gpu_memory:.2f} GB)")
        else:
            logger.warning("No GPU detected, will use CPU (slower)")

        # 初始化tokenizer
        logger.info("Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        tokenizer.padding_side = "left"
        tokenizer.pad_token = tokenizer.eos_token

        # 准备suffix tokens
        suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
        suffix_tokens = tokenizer.encode(suffix, add_special_tokens=False)

        # 获取yes/no token
        true_token = tokenizer("yes", add_special_tokens=False).input_ids[0]
        false_token = tokenizer("no", add_special_tokens=False).input_ids[0]

        logger.info(f"True token (yes): {true_token}, False token (no): {false_token}")

        # 初始化模型
        logger.info("Loading rerank model...")
        start_time = time.time()

        rerank_model = LLM(
            model=config.model_name,
            tensor_parallel_size=config.tensor_parallel_size,
            max_model_len=config.max_model_len,
            enable_prefix_caching=config.enable_prefix_caching,
            gpu_memory_utilization=config.gpu_memory_utilization,
            dtype=config.dtype,
            trust_remote_code=True,
        )

        # 配置采样参数
        sampling_params = SamplingParams(
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            logprobs=config.logprobs,
            allowed_token_ids=[true_token, false_token],
        )

        load_time = time.time() - start_time
        logger.info(f"Model loaded successfully in {load_time:.2f}s")
        logger.info("=" * 60)
        logger.info("Rerank Service Ready!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Failed to initialize rerank model: {e}")
        raise

    yield

    # 清理资源
    logger.info("Shutting down Rerank Service...")
    rerank_model = None
    tokenizer = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("Rerank Service stopped")


# ================= FastAPI应用 =================
app = FastAPI(
    title="Rerank Service",
    description="基于vLLM的高性能Rerank推理服务",
    version="1.0.0",
    lifespan=lifespan
)


# ================= API端点 =================
@app.get("/", response_model=dict)
async def root():
    """根路径"""
    return {
        "service": "Rerank Service",
        "version": "1.0.0",
        "model": config.model_name,
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    if rerank_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    return HealthResponse(
        status="healthy",
        model=config.model_name,
        gpu_memory_utilization=config.gpu_memory_utilization,
        max_model_len=config.max_model_len,
        device=device
    )


@app.post("/v1/rerank", response_model=RerankResponse)
async def rerank(request: RerankRequest):
    """
    重排序查询-文档对
    计算每个文档与查询的相关性分数
    """
    if rerank_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # 检查输入
        if not request.pairs:
            raise HTTPException(status_code=400, detail="Pairs cannot be empty")

        # 验证每个pair
        for i, pair in enumerate(request.pairs):
            if not pair.query or not pair.query.strip():
                raise HTTPException(
                    status_code=400,
                    detail=f"Query at index {i} is empty"
                )
            if not pair.document or not pair.document.strip():
                raise HTTPException(
                    status_code=400,
                    detail=f"Document at index {i} is empty"
                )

        logger.info(f"Processing {len(request.pairs)} query-document pairs for reranking")

        # 准备数据
        pairs = [(pair.query, pair.document) for pair in request.pairs]
        instruction = request.instruction or "Given a web search query, retrieve relevant passages that answer the query"

        # 处理输入
        start_time = time.time()
        messages = process_inputs(
            pairs,
            instruction,
            config.max_length - len(suffix_tokens),
            suffix_tokens
        )

        # 计算分数
        scores = compute_scores(
            rerank_model,
            messages,
            sampling_params,
            true_token,
            false_token
        )

        processing_time = time.time() - start_time

        # 构建结果
        results = [
            RerankResult(
                index=i,
                score=score,
                query=pair.query,
                document=pair.document
            )
            for i, (pair, score) in enumerate(zip(request.pairs, scores))
        ]

        logger.info(
            f"Reranked {len(results)} pairs in {processing_time:.3f}s "
            f"({len(results) / processing_time:.1f} pairs/s)"
        )

        return RerankResponse(
            results=results,
            model=config.model_name,
            processing_time=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during reranking: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/rerank", response_model=RerankResponse)
async def rerank_simple(request: RerankRequest):
    """
    重排序查询-文档对（简化路径）
    与 /v1/rerank 功能相同
    """
    return await rerank(request)


# ================= 启动说明 =================
if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {config.host}:{config.port}")

    uvicorn.run(
        "rerank_service:app",
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower(),
        access_log=True
    )
