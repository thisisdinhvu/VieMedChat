"""
Advanced Corpus Loader
Integrates all three preprocessing techniques:
1. Structure-Aware Chunking
2. Header Injection
3. Vietnamese Word Segmentation
"""

import os
from typing import List, Tuple
from pathlib import Path
from langchain_core.documents import Document
from bs4 import BeautifulSoup

from .structure_aware_chunker import StructureAwareChunker
from .header_injection import HeaderInjector
from .vietnamese_segmenter import VietnameseSegmenter


def load_corpus_advanced(
    corpus_path: str,
    max_chunk_size: int = 800,
    min_chunk_size: int = 100,
    chunk_overlap: int = 100,
    use_vietnamese_segmentation: bool = True,
    inject_headers: bool = True,
) -> Tuple[List[Document], List[Document]]:
    """
    Load and preprocess corpus with advanced techniques.

    Args:
        corpus_path: Path to corpus directory
        max_chunk_size: Maximum chunk size
        min_chunk_size: Minimum chunk size
        chunk_overlap: Overlap between chunks
        use_vietnamese_segmentation: Whether to segment Vietnamese text
        inject_headers: Whether to inject headers into chunks

    Returns:
        (original_docs, processed_chunks)
    """
    print(f"📂 Loading corpus from: {corpus_path}")

    # Initialize processors
    chunker = StructureAwareChunker(max_chunk_size, min_chunk_size, chunk_overlap)
    injector = HeaderInjector(separator=" > ")
    segmenter = VietnameseSegmenter() if use_vietnamese_segmentation else None

    original_docs = []
    all_chunks = []

    # Load all files
    corpus_dir = Path(corpus_path)
    file_count = 0

    for file_path in corpus_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix in [".txt", ".html", ".htm"]:
            file_count += 1
            print(f"   Processing: {file_path.name}")

            # Read file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Store original
            original_docs.append(
                Document(
                    page_content=content,
                    metadata={"source": str(file_path), "filename": file_path.name},
                )
            )

            # Determine type and chunk
            if file_path.suffix in [".html", ".htm"]:
                # Clean HTML first
                soup = BeautifulSoup(content, "html.parser")
                chunks = chunker.chunk_html(str(soup))
            else:
                # Treat as Markdown/plain text
                chunks = chunker.chunk_markdown(content)

            # Inject headers if enabled
            if inject_headers:
                chunks = injector.inject_headers(chunks)

            # Convert to LangChain Documents
            for i, chunk in enumerate(chunks):
                text = chunk["text"]

                # Apply Vietnamese segmentation if enabled
                if segmenter:
                    text_segmented = segmenter.segment(text)
                else:
                    text_segmented = text

                doc = Document(
                    page_content=text_segmented,
                    metadata={
                        "source": str(file_path),
                        "filename": file_path.name,
                        "chunk_id": i,
                        "header_path": chunk.get("header_path", ""),
                        "original_text": chunk.get("original_text", text),
                    },
                )
                all_chunks.append(doc)

    print(f"\n✅ Corpus loaded successfully")
    print(f"   Files processed: {file_count}")
    print(f"   Total chunks: {len(all_chunks)}")

    return original_docs, all_chunks


# Example usage
if __name__ == "__main__":
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

    # Test with sample corpus
    corpus_path = "backend/database/text_corpus"

    if os.path.exists(corpus_path):
        docs, chunks = load_corpus_advanced(corpus_path)

        print("\n=== Sample Chunks ===")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(f"  Header: {chunk.metadata.get('header_path', 'N/A')}")
            print(f"  Text: {chunk.page_content[:150]}...")
    else:
        print(f"❌ Corpus path not found: {corpus_path}")
