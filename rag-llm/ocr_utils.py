import asyncio
import base64
import io
from typing import List, Tuple, Optional

import fitz
from PIL import Image
from langchain_core.documents import Document
from openai import AsyncOpenAI


class AsyncPDFOCR:
    def __init__(
            self,
            model: str = "PaddleOCR-VL-1.5-0.9B",
            base_url: str = "http://localhost:8765/v1",
            api_key: str = "",
            timeout: int = 3600,
            prompt: str = "OCR:",
            mime: str = "jpeg",  # "png" or "jpeg"
            zoom: float = 1.5,
            concurrency: int = 8,
            max_retries: int = 3,
            return_usage: bool = False,
            upscale_threshold: int = 1500,
            max_pixels: int = 2048 * 28 * 28,
            remove_images: bool = False,
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.prompt = prompt
        self.mime = mime
        self.zoom = zoom
        self.concurrency = concurrency
        self.max_retries = max_retries
        self.return_usage = return_usage
        self.upscale_threshold = upscale_threshold
        self.max_pixels = max_pixels
        self.remove_images = remove_images

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    @staticmethod
    def _to_data_url(image_bytes: bytes, mime: str) -> str:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        return f"data:image/{mime};base64,{b64}"

    def _preprocess_image(self, image_bytes: bytes) -> bytes:
        """
        预处理图片：调整尺寸以优化OCR识别效果
        
        - 对于小图片（宽高都小于upscale_threshold），放大2倍以提高识别率
        - 对于大图片，按max_pixels限制进行缩放
        """
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        orig_w, orig_h = image.size
        
        # 小图片放大处理
        if orig_w < self.upscale_threshold and orig_h < self.upscale_threshold:
            process_w, process_h = orig_w * 2, orig_h * 2
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS
            image = image.resize((process_w, process_h), resample_filter)
        
        # 大图片按max_pixels限制缩放
        current_pixels = image.width * image.height
        if current_pixels > self.max_pixels:
            scale = (self.max_pixels / current_pixels) ** 0.5
            new_w = int(image.width * scale)
            new_h = int(image.height * scale)
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS
            image = image.resize((new_w, new_h), resample_filter)
        
        # 转换回bytes
        output = io.BytesIO()
        image.save(output, format='JPEG' if self.mime == 'jpeg' else 'PNG', quality=95)
        return output.getvalue()

    @staticmethod
    def _remove_images_from_page(page: fitz.Page) -> None:
        """
        移除PDF页面中的所有图片
        
        Args:
            page: PyMuPDF页面对象
        """
        # 获取页面中的所有图片
        image_list = page.get_images(full=True)
        
        # 遍历并删除每个图片
        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]  # 图片的xref引用
            try:
                # 通过xref删除图片对象
                page.parent.delete_object(xref)
            except Exception:
                # 某些情况下直接删除可能失败，尝试用其他方法
                pass
        
        # 清理页面内容，移除图片引用
        page.clean_contents()

    def _render_pdf_pages_once(self, pdf_path: str) -> List[Tuple[int, bytes]]:
        """只读取一次 PDF，渲染每页为图片字节，并进行预处理。"""
        pages: List[Tuple[int, bytes]] = []
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc):
                # 如果需要移除图片，先处理页面
                if self.remove_images:
                    self._remove_images_from_page(page)
                
                pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom), alpha=False)
                image_bytes = pix.tobytes(self.mime)
                # 预处理图片
                processed_bytes = self._preprocess_image(image_bytes)
                pages.append((i, processed_bytes))
        return pages

    async def _ocr_one_page(
            self,
            sem: asyncio.Semaphore,
            page_index: int,
            image_bytes: bytes,
    ) -> Tuple[int, str, Optional[dict]]:
        data_url = self._to_data_url(image_bytes, self.mime)
        last_err = None

        for attempt in range(self.max_retries):
            try:
                async with sem:
                    resp = await self.client.chat.completions.create(
                        model=self.model,
                        temperature=0.0,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "image_url", "image_url": {"url": data_url}},
                                    {"type": "text", "text": self.prompt},
                                ],
                            }
                        ],
                    )

                text = (resp.choices[0].message.content or "").strip()
                usage = resp.usage.model_dump() if (self.return_usage and resp.usage) else None
                return page_index, text, usage

            except Exception as e:
                last_err = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(0.8 * (attempt + 1))
                else:
                    raise RuntimeError(f"page={page_index} failed: {e}") from e

        raise RuntimeError(f"page={page_index} failed: {last_err}")

    async def aocr(self, pdf_path: str) -> List[Document]:
        pages = self._render_pdf_pages_once(pdf_path)
        if not pages:
            return []

        sem = asyncio.Semaphore(min(self.concurrency, len(pages)))
        tasks = [
            self._ocr_one_page(sem=sem, page_index=i, image_bytes=img)
            for i, img in pages
        ]
        results = await asyncio.gather(*tasks)

        # 归并并保序
        merged: List[Optional[Document]] = [None] * len(pages)
        for i, text, usage in results:
            metadata = {
                "page": i,
            }
            if usage is not None:
                metadata["usage"] = usage

            merged[i] = Document(page_content=text, metadata=metadata)

        return [d for d in merged if d is not None]

    def run(self, pdf_path: str) -> List[Document]:
        """同步调用入口。"""
        return asyncio.run(self.aocr(pdf_path))
