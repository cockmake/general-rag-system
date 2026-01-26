import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from milvus_utils import MilvusClientManager
from mq.connection import rabbit_async_client
from mq.document_embedding import document_embedding_consumer
from mq.session_name import session_name_generator

logger = logging.getLogger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logger.info("初始化进程")

    consume_background_tasks = []

    # RabbitMQ
    await rabbit_async_client.connect()

    # 启动 Milvus 释放任务
    milvus_release_task = asyncio.create_task(MilvusClientManager.milvus_release_worker())

    try:
        consume_background_tasks.append(
            asyncio.create_task(
                rabbit_async_client.consume(
                    queue_name="session.name.generate.producer.queue",
                    callback=session_name_generator.on_receive_message
                )
            )
        )

        consume_background_tasks.append(
            asyncio.create_task(
                rabbit_async_client.consume(
                    queue_name="rag.document.process.queue",
                    callback=document_embedding_consumer.on_receive_message
                )
            )
        )

        yield

    finally:
        logger.info("进程结束")

        # 停止 Milvus 释放任务
        milvus_release_task.cancel()
        await asyncio.gather(milvus_release_task, return_exceptions=True)

        # 停止 MQ consumer
        for task in consume_background_tasks:
            task.cancel()
        await asyncio.gather(*consume_background_tasks, return_exceptions=True)

        # 释放所有 Milvus collection
        logger.info("Closing Milvus connections...")
        await MilvusClientManager.close_all()

        # 关闭 MQ
        await rabbit_async_client.close()
