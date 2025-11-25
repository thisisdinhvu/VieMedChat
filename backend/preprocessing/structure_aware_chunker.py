"""
Structure-Aware Chunker
Intelligently splits documents based on HTML/Markdown structure.
Preserves semantic boundaries (headers, sections, paragraphs).
"""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup, NavigableString, Tag
import re


class StructureAwareChunker:
    """
    Chunks documents while respecting structural boundaries.
    Works with HTML and Markdown content.
    """

    def __init__(
        self,
        max_chunk_size: int = 800,
        min_chunk_size: int = 100,
        chunk_overlap: int = 100,
    ):
        """
        Initialize chunker.

        Args:
            max_chunk_size: Maximum characters per chunk
            min_chunk_size: Minimum characters per chunk (avoid too small chunks)
            chunk_overlap: Overlap between chunks for context
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_html(self, html_content: str) -> List[Dict]:
        """
        Chunk HTML content based on structure.

        Args:
            html_content: Raw HTML string

        Returns:
            List of chunks with metadata
        """
        soup = BeautifulSoup(html_content, "html.parser")
        chunks = []
        current_headers = []  # Stack to track header hierarchy

        # Process document recursively
        self._process_element(soup, chunks, current_headers, "")

        return self._merge_small_chunks(chunks)

    def _process_element(
        self, element, chunks: List[Dict], headers: List[str], current_text: str
    ):
        """Recursively process HTML elements."""

        if isinstance(element, NavigableString):
            text = str(element).strip()
            if text:
                current_text += text + " "
            return current_text

        if isinstance(element, Tag):
            # Check if this is a header
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                # Save previous chunk if exists
                if current_text.strip():
                    chunks.append(
                        {
                            "text": current_text.strip(),
                            "headers": headers.copy(),
                            "type": "content",
                        }
                    )
                    current_text = ""

                # Update header stack
                header_level = int(element.name[1])  # h1 -> 1, h2 -> 2, etc.
                header_text = element.get_text().strip()

                # Pop headers of same or lower level
                headers = [h for h in headers if int(h.split(":")[0][1]) < header_level]
                headers.append(f"{element.name}: {header_text}")

            # Process children
            for child in element.children:
                current_text = self._process_element(
                    child, chunks, headers, current_text
                )

                # Check if chunk is getting too large
                if len(current_text) >= self.max_chunk_size:
                    chunks.append(
                        {
                            "text": current_text[: self.max_chunk_size].strip(),
                            "headers": headers.copy(),
                            "type": "content",
                        }
                    )
                    # Keep overlap
                    current_text = current_text[-self.chunk_overlap :]

        return current_text

    def chunk_markdown(self, markdown_content: str) -> List[Dict]:
        """
        Chunk Markdown content based on headers.

        Args:
            markdown_content: Raw Markdown string

        Returns:
            List of chunks with metadata
        """
        lines = markdown_content.split("\n")
        chunks = []
        current_chunk = ""
        current_headers = []

        for line in lines:
            # Check if line is a header (# Header or ## Header)
            header_match = re.match(r"^(#{1,6})\s+(.+)$", line)

            if header_match:
                # Save previous chunk
                if current_chunk.strip():
                    chunks.append(
                        {
                            "text": current_chunk.strip(),
                            "headers": current_headers.copy(),
                            "type": "content",
                        }
                    )
                    current_chunk = ""

                # Update headers
                level = len(header_match.group(1))
                header_text = header_match.group(2)
                current_headers = [h for h in current_headers if h["level"] < level]
                current_headers.append({"level": level, "text": header_text})

            else:
                current_chunk += line + "\n"

                # Check size
                if len(current_chunk) >= self.max_chunk_size:
                    chunks.append(
                        {
                            "text": current_chunk[: self.max_chunk_size].strip(),
                            "headers": current_headers.copy(),
                            "type": "content",
                        }
                    )
                    current_chunk = current_chunk[-self.chunk_overlap :]

        # Add last chunk
        if current_chunk.strip():
            chunks.append(
                {
                    "text": current_chunk.strip(),
                    "headers": current_headers.copy(),
                    "type": "content",
                }
            )

        return self._merge_small_chunks(chunks)

    def _merge_small_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Merge chunks that are too small."""
        if not chunks:
            return []

        merged = []
        current = chunks[0]

        for next_chunk in chunks[1:]:
            # If current chunk is too small, merge with next
            if len(current["text"]) < self.min_chunk_size:
                current["text"] += " " + next_chunk["text"]
                # Keep headers from the first chunk
            else:
                merged.append(current)
                current = next_chunk

        merged.append(current)
        return merged


# Example usage
if __name__ == "__main__":
    chunker = StructureAwareChunker(max_chunk_size=500)

    # Test Markdown
    markdown = """
# Bệnh Alzheimer

## Triệu chứng

Alzheimer là bệnh thoái hóa thần kinh.

### Giai đoạn sớm
- Quên tên người quen
- Lạc đường

### Giai đoạn muộn
- Mất khả năng giao tiếp

## Điều trị

Hiện chưa có thuốc chữa khỏi hoàn toàn.
"""

    chunks = chunker.chunk_markdown(markdown)
    for i, chunk in enumerate(chunks):
        print(f"\n=== Chunk {i+1} ===")
        print(f"Headers: {chunk['headers']}")
        print(f"Text: {chunk['text'][:100]}...")
