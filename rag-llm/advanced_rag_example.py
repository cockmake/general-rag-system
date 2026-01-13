"""
LangChain高级RAG检索示例 - 多角度查询与并行处理
包含以下高级特性：
1. 多角度查询生成(Multi-Query Generation) - 使用LLM生成多个不同角度的查询
2. 并行检索(Parallel Retrieval) - 同时检索多个查询并去重
3. 并行文档评分(Parallel Document Grading) - 并行评估文档相关性并打分
4. 对话历史管理 - 支持多轮对话（最近5轮），理解上下文
5. 智能答案生成 - 基于检索结果和历史生成答案

流程：
1. 根据用户输入生成3-5个不同角度的查询（调用LLM）
2. 并行检索所有查询并汇总去重
3. 并行对文档进行相关性评分
4. 基于相关文档和对话历史（最近5轮）生成答案
"""
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import StateGraph, START, END, MessagesState
from pydantic import BaseModel, Field

from utils import get_llm_instance

# ============= 1. 构建知识库 =============
# 创建向量存储和检索器
# embeddings = init_embeddings(
#     model="text-embedding-v4",
#     api_key="sk-188e60cd3e844cab97bc30138dac5cd7",
#     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
#     provider="openai"
# )
embeddings = init_embeddings(
    model="text-embedding-v4",
    api_key="sk-188e60cd3e844cab97bc30138dac5cd7",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    check_embedding_ctx_length=False,
    dimensions=1536,
    provider="openai"
)
vector_store = InMemoryVectorStore(embeddings)

# 添加示例文档 - 关于机器学习的知识
documents = [
    # 监督学习相关
    "监督学习是一种机器学习方法，使用带标签的训练数据来训练模型。常见算法包括线性回归、逻辑回归、决策树、随机森林和支持向量机(SVM)。",
    "线性回归用于预测连续值，而逻辑回归用于分类问题。两者都是监督学习的基础算法。",
    "决策树通过树状结构进行决策，随机森林是多个决策树的集成，可以提高预测准确性并减少过拟合。",

    # 无监督学习相关
    "无监督学习处理没有标签的数据，主要用于聚类和降维。常见算法包括K-means聚类、层次聚类、PCA主成分分析和t-SNE。",
    "K-means是最常用的聚类算法，通过迭代将数据点分配到K个簇中。层次聚类则构建树状的簇结构。",
    "PCA主成分分析用于降维，保留数据中最重要的特征。t-SNE则常用于高维数据的可视化。",

    # 深度学习相关
    "深度学习使用多层神经网络学习数据的层次化表示。常见架构包括CNN(卷积神经网络)、RNN(循环神经网络)和Transformer。",
    "CNN特别适合处理图像数据，通过卷积层提取空间特征。常用于图像分类、目标检测等任务。",
    "RNN和LSTM适合处理序列数据如文本和时间序列。Transformer架构则是现代NLP的基础，如GPT和BERT模型。",

    # 强化学习相关
    "强化学习通过与环境交互学习最优策略。Agent通过试错获得奖励信号，逐步优化行为策略。",
    "Q-learning和Deep Q-Network(DQN)是值函数方法，Policy Gradient和Actor-Critic是策略梯度方法。",
    "强化学习应用广泛，包括游戏AI、机器人控制、推荐系统和自动驾驶等领域。",
]
max_batch = 10
for i in range(0, len(documents), max_batch):
    batch_docs = documents[i:i + max_batch]
    vector_store.add_texts(batch_docs)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}
)


# ============= 2. 定义状态结构 =============
class RAGState(MessagesState):
    """RAG系统的状态"""
    messages: list  # 对话历史
    original_query: str  # 原始查询
    query_list: list[str]  # 多角度查询列表
    documents: list[str]  # 检索到的文档
    relevance_scores: list[bool]  # 文档相关性评分
    answer: str  # 最终答案


# ============= 3. 多角度查询生成模块 =============
class MultiQueryList(BaseModel):
    """多角度查询列表"""
    queries: list[str] = Field(description="从不同角度生成的查询列表，3-5个查询")
    reasoning: str = Field(description="生成这些查询的原因")


def multi_query_generator_node(state: RAGState) -> dict:
    """
    多角度查询生成节点：根据用户问题生成多个不同角度的查询
    高级特性：
    - 考虑对话历史上下文（最近5轮）
    - 从不同语义角度理解问题
    - 生成互补性查询以提高召回率
    """
    messages = state["messages"]
    current_question = messages[-1].content

    # 构建对话历史（最近5轮，即10条消息）
    history_context = ""
    if len(messages) > 1:
        recent_history = messages[-11:-1] if len(messages) > 10 else messages[:-1]
        history_context = "\n".join([
            f"{'用户' if isinstance(m, HumanMessage) else '助手'}: {m.content}"
            for m in recent_history
        ])

    system_prompt = f"""你是一个查询优化专家。你的任务是根据用户的问题，从不同角度生成3-5个查询，以便全面检索相关信息。

生成策略：
1. 理解问题的核心意图，结合对话历史解析代词和上下文
2. 从不同语义角度拆解问题（如：定义、应用、对比、原理等）
3. 生成的查询应该互补，覆盖问题的不同方面
4. 每个查询应简洁明确，适合向量检索
5. 扩展相关概念和同义词

知识库主题：机器学习算法和概念

{'对话历史：\n' + history_context if history_context else '无对话历史'}

当前问题：{current_question}

请生成3-5个不同角度的查询。"""

    llm = get_llm_instance({
        "provider": "deepseek",
        "name": "deepseek-chat"
    }, temperature=0.5)
    structured_llm = llm.with_structured_output(MultiQueryList)

    result = structured_llm.invoke([{"role": "system", "content": system_prompt}])

    print(f"\n🔄 多角度查询生成:")
    print(f"  原始问题: {current_question}")
    print(f"  生成原因: {result.reasoning}")
    print(f"  生成的查询列表:")
    for i, q in enumerate(result.queries, 1):
        print(f"    {i}. {q}")

    return {
        "original_query": current_question,
        "query_list": result.queries
    }


# ============= 4. 并行检索模块 =============
def parallel_retrieval_node(state: RAGState) -> dict:
    """
    并行执行多个查询的向量检索，并去重
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    query_list = state["query_list"]
    all_docs = []
    doc_set = set()  # 用于去重

    print(f"\n📚 并行检索 {len(query_list)} 个查询:")

    def retrieve_single_query(query: str, index: int):
        """单个查询的检索函数"""
        docs = retriever.invoke(query)
        doc_contents = [doc.page_content for doc in docs]
        print(f"  查询{index}: 检索到 {len(doc_contents)} 个文档")
        return doc_contents

    # 并行检索所有查询
    with ThreadPoolExecutor(max_workers=len(query_list)) as executor:
        future_to_query = {
            executor.submit(retrieve_single_query, query, i + 1): query
            for i, query in enumerate(query_list)
        }

        for future in as_completed(future_to_query):
            try:
                doc_contents = future.result()
                # 去重：只添加未见过的文档
                for doc in doc_contents:
                    if doc not in doc_set:
                        doc_set.add(doc)
                        all_docs.append(doc)
            except Exception as e:
                print(f"  检索出错: {str(e)}")

    print(f"\n  去重后共 {len(all_docs)} 个唯一文档")

    return {"documents": all_docs}


# ============= 5. 并行文档相关性评分模块 =============
class RelevanceScore(BaseModel):
    """文档相关性评分"""
    is_relevant: bool = Field(description="文档是否与问题相关")
    reason: str = Field(description="判断理由")
    score: float = Field(description="相关性分数，0-1之间", ge=0, le=1)


def parallel_grade_documents_node(state: RAGState) -> dict:
    """
    并行评估检索文档的相关性并打分
    高级特性：使用LLM并行判断文档是否真正回答用户问题
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    query = state["original_query"]
    documents = state["documents"]

    print(f"\n⚖️ 并行文档相关性评分 ({len(documents)} 个文档):")

    # 如果没有文档，直接返回
    if not documents:
        print("  无文档需要评分")
        return {
            "relevance_scores": [],
            "documents": []
        }

    llm = get_llm_instance({
        "provider": "deepseek",
        "name": "deepseek-chat"
    }, temperature=0)
    structured_llm = llm.with_structured_output(RelevanceScore)

    def grade_single_document(doc: str, index: int):
        """单个文档的评分函数"""
        prompt = f"""评估以下文档是否与用户问题相关，并给出相关性分数。

用户问题：{query}

文档内容：{doc}

判断标准：
1. 文档是否直接回答问题
2. 文档是否包含问题中提到的概念
3. 文档信息是否有助于回答问题

请严格评判，只有真正相关的文档才标记为相关，并给出0-1之间的相关性分数。"""

        score = structured_llm.invoke([{"role": "user", "content": prompt}])
        return (index, doc, score)

    # 并行评分所有文档
    doc_scores = []
    with ThreadPoolExecutor(max_workers=min(len(documents), 5)) as executor:
        future_to_doc = {
            executor.submit(grade_single_document, doc, i + 1): (i, doc)
            for i, doc in enumerate(documents)
        }

        for future in as_completed(future_to_doc):
            try:
                index, doc, score = future.result()
                doc_scores.append((index, doc, score))
                print(
                    f"  文档{index}: {'✓ 相关' if score.is_relevant else '✗ 不相关'} (分数: {score.score:.2f}) - {score.reason}")
            except Exception as e:
                print(f"  评分出错: {str(e)}")

    # 按原始顺序排序
    doc_scores.sort(key=lambda x: x[0])

    # 提取相关文档（按分数排序）
    relevant_docs_with_scores = [(doc, score.score) for _, doc, score in doc_scores if score.is_relevant]
    relevant_docs_with_scores.sort(key=lambda x: x[1], reverse=True)

    relevant_docs = [doc for doc, _ in relevant_docs_with_scores]
    relevance_scores = [score.is_relevant for _, _, score in doc_scores]

    print(f"\n  共 {len(relevant_docs)} 个相关文档（已按分数排序）")

    return {
        "relevance_scores": relevance_scores,
        "documents": relevant_docs  # 只保留相关文档，按分数降序
    }


# ============= 6. 决策路由 =============
def should_generate(state: RAGState) -> Literal["generate", "end"]:
    """
    决定是否生成答案
    由于已经生成了多角度查询，如果没有相关文档则直接结束，不再重试
    """
    relevance_scores = state.get("relevance_scores", [])

    return "generate"


# ============= 7. 答案生成模块 =============
def generate_answer_node(state: RAGState) -> dict:
    """
    基于检索文档和对话历史生成答案
    高级特性：
    - 引用来源文档
    - 保持对话连贯性（包含最近5轮对话）
    - 如果文档不足以回答，明确说明
    """
    messages = state["messages"]
    documents = state["documents"]
    query = state["original_query"]

    # 构建上下文
    if documents:
        context = "\n\n".join([f"[文档{i + 1}] {doc}" for i, doc in enumerate(documents)])
    else:
        context = "无相关文档"

    # 获取对话历史（最近5轮，即10条消息）
    history_messages = messages[:-1]  # 不包括当前问题
    recent_history = history_messages[-10:] if len(history_messages) > 10 else history_messages

    system_prompt = f"""你是一个专业的机器学习助手。基于提供的文档和对话历史回答用户问题。

要求：
1. 优先使用提供的文档中的信息
2. 如果文档不足以完整回答，结合对话历史进行推理或明确说明
3. 引用具体的文档编号（如有）
4. 保持对话连贯，考虑历史上下文
5. 用清晰、简洁的语言回答

参考文档：
{context}"""

    conversation = [{"role": "system", "content": system_prompt}]

    # 添加历史对话（最近5轮）
    for msg in recent_history:
        if isinstance(msg, HumanMessage):
            conversation.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            conversation.append({"role": "assistant", "content": msg.content})

    # 添加当前问题
    conversation.append({"role": "user", "content": query})

    llm = init_chat_model(
        model="deepseek-chat",
        api_key="sk-e34cc6e3056045bea1da92160035e0df",
        base_url="https://api.deepseek.com/v1",
    )
    response = llm.invoke(conversation)

    print(f"\n💡 生成答案:")
    print(f"  {response.content}")

    return {"answer": response.content}


# ============= 8. 构建RAG工作流 =============
def build_rag_workflow():
    """
    构建完整的RAG工作流
    流程：多角度查询生成 -> 并行检索 -> 并行评分 -> 生成答案
    """
    workflow = StateGraph(RAGState)

    # 添加节点
    workflow.add_node("multi_query", multi_query_generator_node)
    workflow.add_node("parallel_retrieve", parallel_retrieval_node)
    workflow.add_node("parallel_grade", parallel_grade_documents_node)
    workflow.add_node("generate", generate_answer_node)

    # 添加边：线性流程，不再循环重试
    workflow.add_edge(START, "multi_query")
    workflow.add_edge("multi_query", "parallel_retrieve")
    workflow.add_edge("parallel_retrieve", "parallel_grade")

    # 条件路由：根据文档相关性决定下一步
    workflow.add_conditional_edges(
        "parallel_grade",
        should_generate,
        {
            "generate": "generate",
            "end": END
        }
    )

    workflow.add_edge("generate", END)

    return workflow.compile()


# ============= 9. 对话式RAG类 =============
class ConversationalRAG:
    """支持多轮对话的RAG系统"""

    def __init__(self):
        self.workflow = build_rag_workflow()
        self.conversation_history = []

    def ask(self, question: str) -> str:
        """提问并获取答案"""
        # 添加用户消息到历史
        self.conversation_history.append(HumanMessage(content=question))

        # 执行RAG工作流
        state = {
            "messages": self.conversation_history,
            "original_query": "",
            "query_list": [],
            "documents": [],
            "relevance_scores": [],
            "answer": ""
        }

        result = self.workflow.invoke(state)
        answer = result["answer"]

        # 添加助手回复到历史
        self.conversation_history.append(AIMessage(content=answer))

        return answer

    def reset(self):
        """重置对话历史"""
        self.conversation_history = []
        print("\n🔄 对话历史已清空")


# ============= 10. 使用示例 =============
if __name__ == "__main__":
    print("=" * 80)
    print("LangChain高级RAG检索示例 - 对话式问答系统")
    print("=" * 80)

    # 创建对话式RAG系统
    rag = ConversationalRAG()

    # 示例对话1：基础问答
    print("\n\n【对话轮次 1】")
    print("-" * 80)
    question1 = "什么是监督学习？"
    print(f"👤 用户: {question1}")
    answer1 = rag.ask(question1)
    print(f"🤖 助手: {answer1}")

    # 示例对话2：上下文理解（使用代词）
    print("\n\n【对话轮次 2】")
    print("-" * 80)
    question2 = "它有哪些常见算法？"  # "它"指代"监督学习"
    print(f"👤 用户: {question2}")
    answer2 = rag.ask(question2)
    print(f"🤖 助手: {answer2}")

    # 示例对话3：深入追问
    print("\n\n【对话轮次 3】")
    print("-" * 80)
    question3 = "线性回归和逻辑回归有什么区别？"
    print(f"👤 用户: {question3}")
    answer3 = rag.ask(question3)
    print(f"🤖 助手: {answer3}")

    # 示例对话4：切换话题
    print("\n\n【对话轮次 4】")
    print("-" * 80)
    question4 = "深度学习中的CNN主要用于什么？"
    print(f"👤 用户: {question4}")
    answer4 = rag.ask(question4)
    print(f"🤖 助手: {answer4}")

    # 示例对话5：对比问题（会触发查询重写）
    print("\n\n【对话轮次 5】")
    print("-" * 80)
    question5 = "监督学习和无监督学习的主要区别是什么？"
    print(f"👤 用户: {question5}")
    answer5 = rag.ask(question5)
    print(f"🤖 助手: {answer5}")

    print("\n\n" + "=" * 80)
    print("对话示例结束")
    print("=" * 80)

    # 打印高级特性说明
    print("\n\n📖 本示例展示的高级RAG特性：")
    print("-" * 80)
    print("""
1. 【多角度查询生成 (Multi-Query Generation)】
   - 根据用户问题生成3-5个不同角度的查询
   - 结合对话历史（最近5轮）解析上下文
   - 从不同语义角度提高召回率
   
2. 【并行检索 (Parallel Retrieval)】
   - 同时对多个查询进行向量检索
   - 自动去重，汇总所有检索结果
   - 提高检索效率和覆盖率
   
3. 【并行文档评分 (Parallel Document Grading)】
   - 并行评估所有检索文档的相关性
   - 使用LLM给出0-1的相关性分数
   - 按分数排序，过滤不相关文档
   
4. 【对话历史管理】
   - 维护多轮对话上下文（最近5轮）
   - 理解代词指代（如"它"、"这个"）
   - 保持对话连贯性
   
5. 【智能答案生成】
   - 基于相关文档和对话历史生成答案
   - 引用文档来源编号
   - 如无相关文档则明确说明
    """)

    print("\n💡 实践建议：")
    print("-" * 80)
    print("""
- 根据实际场景调整生成的查询数量和检索的 k 值
- 优化向量模型选择（如 text-embedding-3-large）
- 实现文档相关性评分的缓存机制
- 添加对话历史摘要功能（长对话场景）
- 调整并行线程数以平衡速度和资源消耗
- 可选：使用重排序模型进一步优化检索结果
- 多角度查询已覆盖多方面，无需额外重试机制
    """)
