"""
测试脚本 - Embedding Service
用于测试服务是否正常工作
"""
import asyncio
import json

import httpx
import pytest


@pytest.mark.asyncio
async def test_health():
    """测试健康检查端点"""
    print("=" * 60)
    print("Testing Health Check...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8890/health", timeout=10.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()


@pytest.mark.asyncio
async def test_single_embedding():
    """测试单个文本embedding"""
    print("=" * 60)
    print("Testing Single Text Embedding...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "input": "What is the capital of China?"
            }
            response = await client.post(
                "http://localhost:8890/v1/embeddings",
                json=payload,
                timeout=30.0
            )
            print(f"Status Code: {response.status_code}")
            result = response.json()

            # 只打印部分向量（前10维）
            if result.get("data"):
                embedding = result["data"][0]["embedding"]
                result["data"][0]["embedding"] = embedding[:10] + ["... (truncated)"]

            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()


@pytest.mark.asyncio
async def test_batch_embedding():
    """测试批量embedding"""
    print("=" * 60)
    print("Testing Batch Embedding...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "input": [
                    "What is the capital of China?",
                    "Explain gravity",
                    "What is machine learning?"
                ]
            }
            response = await client.post(
                "http://localhost:8890/v1/embeddings",
                json=payload,
                timeout=30.0
            )
            print(f"Status Code: {response.status_code}")
            result = response.json()

            # 只打印向量维度信息
            if result.get("data"):
                for item in result["data"]:
                    embedding = item["embedding"]
                    item["embedding"] = f"[{len(embedding)} dimensions]"

            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()

@pytest.mark.asyncio
async def test_with_instruction():
    """测试带指令的embedding"""
    print("=" * 60)
    print("Testing Embedding with Instruction...")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "input": [
                    "What is the capital of China?",
                    "Explain gravity"
                ],
                "instruction": "Given a web search query, retrieve relevant passages that answer the query"
            }
            response = await client.post(
                "http://localhost:8890/v1/embeddings",
                json=payload,
                timeout=30.0
            )
            print(f"Status Code: {response.status_code}")
            result = response.json()

            # 只打印向量维度信息
            if result.get("data"):
                for item in result["data"]:
                    embedding = item["embedding"]
                    item["embedding"] = f"[{len(embedding)} dimensions]"

            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Embedding Service Test Suite")
    print("=" * 60 + "\n")

    await test_health()
    await test_single_embedding()
    await test_batch_embedding()
    await test_with_instruction()

    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
