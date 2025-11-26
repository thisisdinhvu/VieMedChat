# Parent-Child Chunking - Usage Guide

## 🎯 What is Parent-Child Chunking?

A hierarchical chunking strategy that solves the **precision vs context** trade-off in RAG:

**The Problem:**
- Small chunks → High precision, but **missing context**
- Large chunks → Full context, but **low precision**

**The Solution:**
- **Child chunks (500 chars):** Small, precise → Used for **search/retrieval**
- **Parent chunks (1500 chars):** Large, contextual → Used for **LLM context**

---

## 📊 Results

### Corpus Statistics
- **Parent chunks:** 9,431 (avg 1,500 chars each)
- **Child chunks:** 42,678 (avg 500 chars each)
- **Ratio:** 4.5 children per parent
- **Total size:** 50.6 MB

### Quality Improvements
| Metric | Old Chunking | Parent-Child |
|--------|--------------|--------------|
| **Context Loss** | High (63.9% violations) | **None** (parent has full section) |
| **Search Precision** | Medium (800 char chunks) | **High** (500 char children) |
| **Avg Chunk Size** | 682 chars | 500 chars (children) |

---

## 📁 Output Structure

```
backend/database/
├── parent_chunks/          # 9,431 files
│   ├── parent_00000.txt
│   ├── parent_00001.txt
│   └── ...
├── child_chunks/           # 42,678 files
│   ├── child_00000.txt
│   ├── child_00001.txt
│   └── ...
└── parent_child_mapping.json  # Links children to parents
```

### Sample Parent Chunk
```
# ID: alzheimer.txt_parent_2
# Header: Triệu chứng Alzheimer
# Source: alzheimer.txt
# Type: parent

Triệu chứng Alzheimer thường xuất hiện từ từ và tiến triển theo thời gian.
Giai đoạn sớm: Bệnh nhân hay quên tên người quen, lạc đường...
Giai đoạn giữa: Mất khả năng tự chăm sóc bản thân...
Giai đoạn muộn: Mất hoàn toàn khả năng giao tiếp...
(Full section ~1500 chars)
```

### Sample Child Chunk
```
# ID: alzheimer.txt_parent_2_child_0
# Parent ID: alzheimer.txt_parent_2
# Header: Triệu chứng Alzheimer
# Source: alzheimer.txt
# Type: child

[Triệu chứng Alzheimer] Triệu chứng Alzheimer thường xuất hiện từ từ 
và tiến triển theo thời gian. Giai đoạn sớm: Bệnh nhân hay quên tên 
người quen, lạc đường...
(~500 chars)
```

---

## 🚀 How to Use in RAG Pipeline

### Step 1: Upload to Kaggle for Embedding

**Upload ONLY child chunks** to Kaggle:
```bash
# Zip child chunks
zip -r child_chunks.zip backend/database/child_chunks/

# Upload to Kaggle dataset
# Then run embedding script with BAAI/bge-m3
```

### Step 2: Store in Pinecone with Metadata

When uploading vectors to Pinecone, include `parent_id` in metadata:

```python
# Example Pinecone upsert
vectors = []
for i, child_chunk in enumerate(child_chunks):
    vectors.append({
        'id': child_chunk['id'],
        'values': embeddings[i],
        'metadata': {
            'text': child_chunk['text'],
            'parent_id': child_chunk['parent_id'],  # ← KEY!
            'header': child_chunk['header'],
            'filename': child_chunk['filename']
        }
    })

index.upsert(vectors=vectors)
```

### Step 3: Modify Retrieval Logic

**Current (Old):**
```python
# Search
results = index.query(query_embedding, top_k=10)

# Return chunks directly to LLM
context = [r['metadata']['text'] for r in results]
```

**New (Parent-Child):**
```python
# 1. Search CHILDREN
child_results = index.query(query_embedding, top_k=10)

# 2. Get unique PARENT IDs
parent_ids = list(set([r['metadata']['parent_id'] for r in child_results]))

# 3. Load PARENT chunks from disk/database
parent_chunks = load_parents(parent_ids)  # Your implementation

# 4. Return PARENT text to LLM (full context!)
context = [p['text'] for p in parent_chunks]
```

### Step 4: Implement Parent Loader

Create a helper function to load parent chunks:

```python
import json
from pathlib import Path

def load_parents(parent_ids: list) -> list:
    """
    Load parent chunks by IDs.
    
    Args:
        parent_ids: List of parent IDs
        
    Returns:
        List of parent chunk dicts
    """
    parent_dir = Path("backend/database/parent_chunks")
    parents = []
    
    # Load mapping
    with open("backend/database/parent_child_mapping.json") as f:
        mapping = json.load(f)
    
    # Find parent files
    for parent_id in parent_ids:
        # Find file by scanning (or use a lookup table)
        for file_path in parent_dir.glob("*.txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if parent_id in first_line:
                    # Read full parent
                    f.seek(0)
                    content = f.read()
                    # Parse metadata and text
                    lines = content.split('\n')
                    text = '\n'.join(lines[5:])  # Skip metadata lines
                    parents.append({
                        'id': parent_id,
                        'text': text
                    })
                    break
    
    return parents
```

---

## 📈 Expected Performance Improvements

### Before (Single-level chunking)
- **Precision@5:** ~53%
- **MRR@10:** 76.52%
- **Context quality:** Medium (chunks cut mid-sentence)

### After (Parent-Child chunking)
- **Precision@5:** Expected **60-70%** ↑
  - Smaller children → More precise matches
- **MRR@10:** Expected **80-85%** ↑
  - Better ranking due to focused chunks
- **Context quality:** **High** ↑
  - Parents provide full section context

---

## 🔧 Advanced: Caching Parents

To avoid loading parents from disk every time:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def load_parent_cached(parent_id: str) -> dict:
    """Load and cache parent chunk."""
    # ... load logic ...
    return parent_chunk

# Usage
parents = [load_parent_cached(pid) for pid in parent_ids]
```

---

## 💡 Tips & Best Practices

1. **Deduplication:** If multiple children from same parent are retrieved, only return parent once
2. **Ranking:** Rank parents by the **highest-scoring child**
3. **Hybrid:** Combine parent-child with reranker for best results
4. **Monitoring:** Track which parents are most frequently retrieved

---

## 🚀 Next Steps

1. ✅ Export complete (9,431 parents, 42,678 children)
2. ⏳ Upload `child_chunks/` to Kaggle
3. ⏳ Run embedding with BAAI/bge-m3
4. ⏳ Upload to Pinecone with `parent_id` metadata
5. ⏳ Modify `backend/routes/rag/search.py` to use parent-child retrieval
6. ⏳ Evaluate and compare with baseline

---

## 📚 References

- [parent_child_chunker.py](file:///d:/Projects/Chatbots/VieMedChat/backend/preprocessing/parent_child_chunker.py) - Core implementation
- [export_parent_child.py](file:///d:/Projects/Chatbots/VieMedChat/backend/preprocessing/export_parent_child.py) - Export script
- [parent_child_mapping.json](file:///d:/Projects/Chatbots/VieMedChat/backend/database/parent_child_mapping.json) - ID mapping
