"""
Rerank Service 测试脚本
测试rerank服务的基本功能
"""
import time

import requests


def test_health_check(base_url: str = "http://localhost:8891"):
    """测试健康检查"""
    print("=" * 70)
    print("Testing Health Check...")
    print("=" * 70)

    try:
        response = requests.get(f"{base_url}/health")
        response.raise_for_status()
        data = response.json()

        print(f"✓ Status: {data['status']}")
        print(f"✓ Model: {data['model']}")
        print(f"✓ Device: {data['device']}")
        print(f"✓ GPU Memory Utilization: {data['gpu_memory_utilization']}")
        print(f"✓ Max Model Length: {data['max_model_len']}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_rerank_single(base_url: str = "http://localhost:8891"):
    """测试单个查询-文档对"""
    print("\n" + "=" * 70)
    print("Testing Single Query-Document Pair...")
    print("=" * 70)

    payload = {
        "pairs": [
            {
                "query": "What is the capital of China?",
                "document": "The capital of China is Beijing."
            }
        ],
        "instruction": "Given a web search query, retrieve relevant passages that answer the query"
    }

    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/v1/rerank", json=payload)
        response.raise_for_status()
        elapsed = time.time() - start_time

        data = response.json()
        result = data["results"][0]

        print(f"✓ Query: {result['query']}")
        print(f"✓ Document: {result['document']}")
        print(f"✓ Score: {result['score']:.4f}")
        print(f"✓ Processing Time: {data['processing_time']:.3f}s")
        print(f"✓ Total Time: {elapsed:.3f}s")
        return True
    except Exception as e:
        print(f"✗ Single pair test failed: {e}")
        return False


def test_rerank_batch(base_url: str = "http://localhost:8891"):
    """测试批量查询-文档对"""
    print("\n" + "=" * 70)
    print("Testing Batch Query-Document Pairs...")
    print("=" * 70)

    query = "What is the capital of China?"
    documents = [
        "Shanghai is the largest city in China.",
        "The capital of China is Beijing.",
        "China has a long history of over 5000 years.",
        "Beijing is known for its historical landmarks.",
        "The Great Wall of China is a famous tourist attraction."
    ]

    pairs = [{"query": query, "document": doc} for doc in documents]
    payload = {
        "pairs": pairs,
        "instruction": "Given a web search query, retrieve relevant passages that answer the query"
    }

    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/v1/rerank", json=payload)
        response.raise_for_status()
        elapsed = time.time() - start_time

        data = response.json()

        print(f"✓ Query: {query}")
        print(f"✓ Number of documents: {len(data['results'])}")
        print(f"✓ Processing Time: {data['processing_time']:.3f}s")
        print(f"✓ Total Time: {elapsed:.3f}s")
        print(f"✓ Throughput: {len(data['results']) / data['processing_time']:.1f} pairs/s")

        # 按分数排序并显示
        sorted_results = sorted(data["results"], key=lambda x: x["score"], reverse=True)
        for i, result in enumerate(sorted_results, 1):
            print(f"{result['index']}. Score: {result['score']:.4f} - {result['document'][:60]}...")

        return True
    except Exception as e:
        print(f"✗ Batch test failed: {e}")
        return False


def test_rerank_different_queries(base_url: str = "http://localhost:8891"):
    """测试不同的查询-文档对"""
    print("\n" + "=" * 70)
    print("Testing Different Query-Document Pairs...")
    print("=" * 70)

    pairs = [
        {
            "query": "What is the capital of China?",
            "document": "The capital of China is Beijing."
        },
        {
            "query": "Explain gravity",
            "document": "Gravity is a force that attracts two bodies towards each other."
        },
        {
            "query": "What is Python?",
            "document": "Python is a high-level programming language."
        }
    ]

    payload = {
        "pairs": pairs,
        "instruction": "Given a web search query, retrieve relevant passages that answer the query"
    }

    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/v1/rerank", json=payload)
        response.raise_for_status()
        elapsed = time.time() - start_time

        data = response.json()

        print(f"✓ Number of pairs: {len(data['results'])}")
        print(f"✓ Processing Time: {data['processing_time']:.3f}s")
        print(f"✓ Total Time: {elapsed:.3f}s")

        print("\nResults:")
        for result in data["results"]:
            print(f"  Query: {result['query'][:40]}...")
            print(f"  Score: {result['score']:.4f}")
            print(f"  Document: {result['document'][:50]}...")
            print()

        return True
    except Exception as e:
        print(f"✗ Different queries test failed: {e}")
        return False


def test_simplified_endpoint(base_url: str = "http://localhost:8891"):
    """测试简化端点"""
    print("\n" + "=" * 70)
    print("Testing Simplified Endpoint (/rerank)...")
    print("=" * 70)

    payload = {
        "pairs": [
            {
                "query": "What is machine learning?",
                "document": "Machine learning is a subset of artificial intelligence."
            }
        ]
    }

    try:
        response = requests.post(f"{base_url}/rerank", json=payload)
        response.raise_for_status()
        data = response.json()

        print(f"✓ Simplified endpoint works!")
        print(f"✓ Score: {data['results'][0]['score']:.4f}")
        return True
    except Exception as e:
        print(f"✗ Simplified endpoint test failed: {e}")
        return False


def main():
    """运行所有测试"""
    base_url = "http://localhost:8891"

    print("\n" + "=" * 70)
    print("Rerank Service Test Suite")
    print("=" * 70)
    print(f"Base URL: {base_url}")

    tests = [
        ("Health Check", test_health_check),
        ("Single Pair", test_rerank_single),
        ("Batch Pairs", test_rerank_batch),
        ("Different Queries", test_rerank_different_queries),
        ("Simplified Endpoint", test_simplified_endpoint),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func(base_url)
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results[test_name] = False

    # 总结
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    import sys

    success = main()
    sys.exit(0 if success else 1)
