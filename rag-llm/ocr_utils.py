import asyncio
import base64
from typing import List, Tuple, Optional

import fitz
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

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

    @staticmethod
    def _to_data_url(image_bytes: bytes, mime: str) -> str:
        b64 = base64.b64encode(image_bytes).decode("ascii")
        return f"data:image/{mime};base64,{b64}"

    def _render_pdf_pages_once(self, pdf_path: str) -> List[Tuple[int, bytes]]:
        """只读取一次 PDF，渲染每页为图片字节。"""
        pages: List[Tuple[int, bytes]] = []
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc):
                pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom), alpha=False)
                pages.append((i, pix.tobytes(self.mime)))
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
