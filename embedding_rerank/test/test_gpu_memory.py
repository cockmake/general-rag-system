"""
显存占用测试脚本 - Embedding Service
测试 batch_size=10, max_length=8192 场景下的 GPU 显存占用
用于确定合适的 gpu_memory_utilization 配置

注意：vLLM 通过 spawn 子进程管理 GPU，父进程的 torch.cuda 接口无法读取子进程的显存。
      本脚本改用 nvidia-smi 读取系统级真实显存，同时解析 vLLM 日志中的关键数据。
"""
import time
import sys
import os
import subprocess
import re

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
from vllm import LLM

# ==================== 测试配置 ====================
MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"
MAX_MODEL_LEN = 8192
BATCH_SIZE = 10
GPU_MEMORY_UTILIZATION = 0.9  # 先用较高值加载，确保模型能跑起来，再观察实际使用量
DTYPE = "float16"
TENSOR_PARALLEL_SIZE = 1


def get_gpu_memory_info():
    """
    通过 nvidia-smi 获取系统级 GPU 显存信息（GB）。
    可跨进程读取，解决 vLLM 子进程分配显存在父进程不可见的问题。
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,name,memory.total,memory.used,memory.free",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        info = []
        for line in result.stdout.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 5:
                continue
            info.append({
                "gpu_id": int(parts[0]),
                "name": parts[1],
                "total_gb": float(parts[2]) / 1024,
                "used_gb": float(parts[3]) / 1024,
                "free_gb": float(parts[4]) / 1024,
            })
        return info
    except Exception:
        return None


def print_gpu_memory(tag: str):
    """打印 GPU 显存状态（来自 nvidia-smi，跨进程可见）"""
    info = get_gpu_memory_info()
    if info is None:
        print(f"[{tag}] nvidia-smi 不可用")
        return
    print(f"\n{'='*60}")
    print(f"[{tag}]")
    for g in info:
        print(f"  GPU {g['gpu_id']} ({g['name']}):")
        print(f"    Total : {g['total_gb']:.2f} GB")
        print(f"    Used  : {g['used_gb']:.2f} GB")
        print(f"    Free  : {g['free_gb']:.2f} GB")
    print(f"{'='*60}")
    return info


def generate_test_texts(batch_size: int, target_token_len: int) -> list[str]:
    """
    生成接近 target_token_len 长度的测试文本
    每个中文字符约 1.5 token，英文单词约 1.3 token
    这里用重复中文段落来近似填满 token 长度
    """
    # 约 500 字的中文段落（约 750 tokens）
    paragraph = (
        "机器学习是人工智能的一个子领域，专注于开发能够从数据中自动学习和改进的算法。"
        "深度学习作为机器学习的重要分支，通过多层神经网络来模拟人脑的工作方式。"
        "自然语言处理技术使计算机能够理解、解释和生成人类语言，广泛应用于机器翻译、"
        "情感分析、文本摘要和问答系统等领域。向量检索技术通过将文本转化为高维向量，"
        "实现语义层面的相似度搜索，是现代信息检索系统的核心技术之一。"
    )
    # 重复段落直到接近目标 token 数（1 中文字符 ≈ 1.5 token，保守估算 1 字符 = 1 token）
    repeat_times = max(1, target_token_len // len(paragraph))
    long_text = paragraph * repeat_times
    # 截断到 target_token_len 个字符（字符数近似 token 数）
    long_text = long_text[:target_token_len]
    return [long_text] * batch_size


def run_memory_test():
    print("\n" + "=" * 60)
    print("Embedding Service GPU Memory Test")
    print(f"  Model         : {MODEL_NAME}")
    print(f"  Max Model Len : {MAX_MODEL_LEN}")
    print(f"  Batch Size    : {BATCH_SIZE}")
    print(f"  DType         : {DTYPE}")
    print("=" * 60)

    # -------- 阶段 0: 基线（加载模型前）--------
    print_gpu_memory("阶段 0: 基线（模型加载前）")
    baseline_info = get_gpu_memory_info()

    # -------- 阶段 1: 加载模型 --------
    print(f"\n正在加载模型 {MODEL_NAME}，max_model_len={MAX_MODEL_LEN} ...")
    load_start = time.time()
    try:
        model = LLM(
            model=MODEL_NAME,
            task="embed",
            gpu_memory_utilization=GPU_MEMORY_UTILIZATION,
            max_model_len=MAX_MODEL_LEN,
            tensor_parallel_size=TENSOR_PARALLEL_SIZE,
            dtype=DTYPE,
            trust_remote_code=True,
        )
    except Exception as e:
        print(f"\n[ERROR] 模型加载失败: {e}")
        print("请检查模型路径或显存是否充足。")
        sys.exit(1)

    load_time = time.time() - load_start
    print(f"模型加载完成，耗时 {load_time:.2f}s")
    print_gpu_memory("阶段 1: 模型加载后（空闲状态）")
    model_loaded_info = get_gpu_memory_info()

    # -------- 阶段 2: 短文本推理（warmup）--------
    warmup_texts = ["这是一段用于热身的短文本。"] * BATCH_SIZE
    print(f"\n执行 warmup 推理（{BATCH_SIZE} 条短文本）...")
    model.embed(warmup_texts)
    print_gpu_memory("阶段 2: Warmup 推理后")

    # -------- 阶段 3: 接近 max_length 的批量推理 --------
    long_texts = generate_test_texts(BATCH_SIZE, MAX_MODEL_LEN)
    actual_char_len = len(long_texts[0])
    print(f"\n执行压力推理（{BATCH_SIZE} 条文本，每条 ~{actual_char_len} 字符 ≈ {MAX_MODEL_LEN} tokens）...")

    infer_start = time.time()
    try:
        outputs = model.embed(long_texts)
        infer_time = time.time() - infer_start
        embed_dim = len(outputs[0].outputs.embedding)
        print(f"推理完成，耗时 {infer_time:.3f}s，向量维度: {embed_dim}")
    except Exception as e:
        print(f"\n[ERROR] 推理失败: {e}")
        infer_time = None

    print_gpu_memory("阶段 3: 长文本批量推理后")
    peak_info = get_gpu_memory_info()

    # -------- 汇总报告 --------
    print("\n" + "=" * 60)
    print("显存占用汇总报告")
    print("=" * 60)
    if baseline_info and model_loaded_info and peak_info:
        for i, (b, m, p) in enumerate(zip(baseline_info, model_loaded_info, peak_info)):
            total = b["total_gb"]
            baseline_used = b["used_gb"]
            model_used = m["used_gb"]
            peak_used = p["used_gb"]
            model_delta = model_used - baseline_used
            peak_delta = peak_used - baseline_used
            peak_ratio = peak_used / total

            print(f"\nGPU {i} ({b['name']}):")
            print(f"  总显存                  : {total:.2f} GB")
            print(f"  基线占用                : {baseline_used:.2f} GB")
            print(f"  模型加载后占用          : {model_used:.2f} GB  (+{model_delta:.2f} GB)")
            print(f"  峰值占用（长文本推理后）: {peak_used:.2f} GB  (+{peak_delta:.2f} GB, {peak_ratio*100:.1f}%)")
            print(f"  剩余空闲显存            : {total - peak_used:.2f} GB")

            print(f"\n  ── 建议配置（仅 GPU {i}）──")
            suggested_util = min(0.95, round(peak_ratio + 0.10, 2))
            tight_util = min(0.95, round(peak_ratio + 0.05, 2))
            print(f"  gpu_memory_utilization (宽松, +10% buffer): {suggested_util}")
            print(f"  gpu_memory_utilization (紧凑, +5%  buffer): {tight_util}")
            print(f"  max_model_len                             : {MAX_MODEL_LEN}")
            print(f"  max_batch_size                            : {BATCH_SIZE}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_memory_test()
