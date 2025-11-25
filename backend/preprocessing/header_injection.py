"""
Header Injection Module
Adds contextual headers to chunks to preserve semantic meaning.
"""

from typing import List, Dict


class HeaderInjector:
    """
    Injects header context into chunks to maintain semantic coherence.
    Ensures chunks remain self-contained and meaningful.
    """

    def __init__(self, separator: str = " | "):
        """
        Initialize injector.

        Args:
            separator: String to separate headers (e.g., " > " or " | ")
        """
        self.separator = separator

    def inject_headers(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add header context to chunk text.

        Args:
            chunks: List of chunks from StructureAwareChunker

        Returns:
            Chunks with headers injected into text
        """
        enriched_chunks = []

        for chunk in chunks:
            # Build header path
            header_path = self._build_header_path(chunk.get("headers", []))

            # Inject header into text
            if header_path:
                enriched_text = f"[{header_path}] {chunk['text']}"
            else:
                enriched_text = chunk["text"]

            enriched_chunks.append(
                {
                    "text": enriched_text,
                    "original_text": chunk["text"],
                    "headers": chunk.get("headers", []),
                    "header_path": header_path,
                }
            )

        return enriched_chunks

    def _build_header_path(self, headers) -> str:
        """Build hierarchical header path."""
        if isinstance(headers, list) and headers:
            # Handle markdown-style headers (dict with 'text' key)
            if isinstance(headers[0], dict):
                path = self.separator.join([h["text"] for h in headers])
            # Handle HTML-style headers (string)
            else:
                # Extract text from "h1: Title" format
                path = self.separator.join([h.split(": ", 1)[-1] for h in headers])
            return path
        return ""


# Example usage
if __name__ == "__main__":
    # Sample chunks from Structure-Aware Chunker
    chunks = [
        {
            "text": "Alzheimer là bệnh thoái hóa thần kinh tiến triển.",
            "headers": [
                {"level": 1, "text": "Bệnh Alzheimer"},
                {"level": 2, "text": "Triệu chứng"},
            ],
        },
        {
            "text": "Quên tên người quen, lạc đường.",
            "headers": [
                {"level": 1, "text": "Bệnh Alzheimer"},
                {"level": 2, "text": "Triệu chứng"},
                {"level": 3, "text": "Giai đoạn sớm"},
            ],
        },
    ]

    injector = HeaderInjector(separator=" > ")
    enriched = injector.inject_headers(chunks)

    for chunk in enriched:
        print(f"\nOriginal: {chunk['original_text'][:50]}")
        print(f"Enriched: {chunk['text'][:100]}...")
