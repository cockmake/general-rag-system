import os

from miniopy_async import Minio


class MinioClient:
    def __init__(self):
        endpoint = os.environ.get("MINIO_ENDPOINT")
        access_key = os.environ.get("MINIO_ACCESS_KEY")
        secret_key = os.environ.get("MINIO_SECRET_KEY")
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )

    async def get_object(self, bucket_name: str, object_name: str):
        """
        从 Minio 获取文件对象
        :param bucket_name: 存储桶名称
        :param object_name: 对象名称
        :return: Minio 响应对象 (流)
        """
        try:
            return await self.client.get_object(bucket_name, object_name)
        except Exception as e:
            print(f"Error getting object {object_name} from bucket {bucket_name}: {e}")
            return None


minio_client = MinioClient()
