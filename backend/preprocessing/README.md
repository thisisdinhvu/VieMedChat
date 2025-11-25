# Advanced Text Preprocessing Module

This module provides three advanced preprocessing techniques for RAG optimization:

## 1. Structure-Aware Chunking (`structure_aware_chunker.py`)
Intelligently splits documents while preserving structural boundaries (headers, sections).
- Works with HTML and Markdown
- Respects semantic boundaries
- Configurable chunk size limits

## 2. Header Injection (`header_injection.py`)
Adds contextual headers to chunks to maintain meaning.
- Builds hierarchical header paths
- Ensures chunks are self-contained
- Example: `[Bệnh Alzheimer > Triệu chứng] Bệnh nhân hay quên...`

## 3. Vietnamese Word Segmentation (`vietnamese_segmenter.py`)
Proper word tokenization for Vietnamese text.
- Improves BM25 keyword search accuracy
- Uses `underthesea` library (optional)
- Preserves medical compound words

## Usage

```python
from backend.preprocessing.advanced_corpus_loader import load_corpus_advanced

# Load corpus with all techniques
docs, chunks = load_corpus_advanced(
    corpus_path="backend/database/text_corpus",
    max_chunk_size=800,
    inject_headers=True,
    use_vietnamese_segmentation=True
)

# Use chunks in RAG pipeline
for chunk in chunks:
    print(chunk.page_content)
    print(chunk.metadata['header_path'])
```

## Installation

For Vietnamese segmentation:
```bash
pip install underthesea
```
