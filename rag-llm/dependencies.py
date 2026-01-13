import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from mq.connection import rabbit_async_client
from mq.document_embedding import document_embedding_consumer
from mq.session_name import session_name_generator


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logging.info("初始化进程")
    logging.info("Initializing RabbitMQ client and consumer...")
    consume_background_tasks = []
    
    # 手动连接而不是使用 async with，避免过早关闭连接
    await rabbit_async_client.connect()
    
    try:
        # 生成 session name
        consume_background_tasks.append(
            asyncio.create_task(
                rabbit_async_client.consume(
                    queue_name="session.name.generate.producer.queue",
                    callback=session_name_generator.on_receive_message
                )
            )
        )
        # 文档向量化
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
        logging.info("进程结束")
        logging.info("Shutting down RabbitMQ client and consumer...")
        # 先取消任务
        for task in consume_background_tasks:
            task.cancel()
        # 等待任务完成取消
        await asyncio.gather(*consume_background_tasks, return_exceptions=True)
        # 最后关闭连接
        await rabbit_async_client.close()
