# RAG Evaluation Test Dataset

Đây là dataset mẫu để đánh giá chất lượng retrieval của RAG system.

## Cách tạo Test Dataset chất lượng cao

### Bước 1: Thu thập queries thực tế
- Lấy từ user logs (nếu có)
- Hoặc tự tạo dựa trên các câu hỏi phổ biến

### Bước 2: Label ground truth
- Với mỗi query, xác định documents nào là relevant
- Cần có chuyên gia y tế review (quan trọng!)
- Format:
```json
{
  "query": "triệu chứng suy thận",
  "relevant_doc_ids": [0, 5, 12],
  "difficulty": "easy|medium|hard"
}
```

### Bước 3: Đa dạng hóa
- Queries dễ (exact match keywords)
- Queries trung bình (paraphrase)
- Queries khó (semantic understanding required)

## Sample Test Cases

```json
[
  {
    "id": 1,
    "query": "triệu chứng suy thận",
    "relevant_doc_ids": [0, 5, 12],
    "difficulty": "easy",
    "category": "symptoms"
  },
  {
    "id": 2,
    "query": "làm sao biết mình bị suy thận?",
    "relevant_doc_ids": [0, 5, 12],
    "difficulty": "medium",
    "category": "symptoms",
    "note": "Paraphrase của query 1"
  },
  {
    "id": 3,
    "query": "tôi bị tiểu ít, mệt mỏi, chán ăn",
    "relevant_doc_ids": [0, 5, 12, 18],
    "difficulty": "hard",
    "category": "symptoms",
    "note": "Mô tả triệu chứng thay vì hỏi trực tiếp"
  },
  {
    "id": 4,
    "query": "cách điều trị tiểu đường type 2",
    "relevant_doc_ids": [3, 8, 15, 20],
    "difficulty": "easy",
    "category": "treatment"
  },
  {
    "id": 5,
    "query": "thuốc gì cho người tiểu đường?",
    "relevant_doc_ids": [3, 8, 15, 20, 25],
    "difficulty": "medium",
    "category": "treatment"
  },
  {
    "id": 6,
    "query": "paracetamol có tác dụng phụ gì?",
    "relevant_doc_ids": [10, 25],
    "difficulty": "easy",
    "category": "medication"
  },
  {
    "id": 7,
    "query": "uống paracetamol nhiều có sao không?",
    "relevant_doc_ids": [10, 25, 30],
    "difficulty": "medium",
    "category": "medication"
  },
  {
    "id": 8,
    "query": "chế độ ăn cho người cao huyết áp",
    "relevant_doc_ids": [7, 14, 22],
    "difficulty": "easy",
    "category": "diet"
  },
  {
    "id": 9,
    "query": "người huyết áp cao nên ăn gì?",
    "relevant_doc_ids": [7, 14, 22],
    "difficulty": "easy",
    "category": "diet"
  },
  {
    "id": 10,
    "query": "dấu hiệu nhồi máu cơ tim",
    "relevant_doc_ids": [2, 9, 18],
    "difficulty": "easy",
    "category": "symptoms"
  },
  {
    "id": 11,
    "query": "đau ngực dữ dội, khó thở, đổ mồ hôi",
    "relevant_doc_ids": [2, 9, 18, 35],
    "difficulty": "hard",
    "category": "symptoms",
    "note": "Emergency case - mô tả triệu chứng"
  },
  {
    "id": 12,
    "query": "phòng ngừa đột quỵ",
    "relevant_doc_ids": [11, 16, 23],
    "difficulty": "easy",
    "category": "prevention"
  },
  {
    "id": 13,
    "query": "làm gì để không bị đột quỵ?",
    "relevant_doc_ids": [11, 16, 23],
    "difficulty": "medium",
    "category": "prevention"
  },
  {
    "id": 14,
    "query": "xét nghiệm gì để biết bị tiểu đường?",
    "relevant_doc_ids": [4, 13, 19],
    "difficulty": "medium",
    "category": "diagnosis"
  },
  {
    "id": 15,
    "query": "chỉ số đường huyết bao nhiêu là bình thường?",
    "relevant_doc_ids": [4, 13, 19, 27],
    "difficulty": "easy",
    "category": "diagnosis"
  }
]
```

## Metrics Giải thích

### MRR@10 (Mean Reciprocal Rank)
- **Ý nghĩa**: Đo lường vị trí của document relevant **đầu tiên**
- **Công thức**: MRR = (1/Q) × Σ(1/rank_i)
- **Ví dụ**: 
  - Relevant doc ở vị trí 1 → RR = 1.0
  - Relevant doc ở vị trí 3 → RR = 0.33
  - Không có relevant doc trong top-10 → RR = 0.0
- **Tốt khi**: > 0.7

### Recall@10
- **Ý nghĩa**: Tỷ lệ relevant docs được tìm thấy trong top-10
- **Công thức**: Recall = (# relevant found) / (# total relevant)
- **Ví dụ**: Có 5 relevant docs, tìm được 3 → Recall = 0.6
- **Tốt khi**: > 0.8

### Precision@10
- **Ý nghĩa**: Tỷ lệ docs trong top-10 là relevant
- **Công thức**: Precision = (# relevant in top-10) / 10
- **Ví dụ**: Top-10 có 7 relevant docs → Precision = 0.7
- **Tốt khi**: > 0.5

### NDCG@10 (Normalized Discounted Cumulative Gain)
- **Ý nghĩa**: Đo lường chất lượng ranking (vị trí càng cao càng tốt)
- **Tốt khi**: > 0.7

### Hit Rate@10
- **Ý nghĩa**: Tỷ lệ queries có ít nhất 1 relevant doc trong top-10
- **Công thức**: Hit Rate = (# queries with hits) / (# total queries)
- **Tốt khi**: > 0.9

## Benchmark Targets (Medical RAG)

| Metric | Good | Excellent |
|--------|------|-----------|
| MRR@10 | > 0.7 | > 0.85 |
| Recall@10 | > 0.75 | > 0.9 |
| Precision@10 | > 0.5 | > 0.7 |
| NDCG@10 | > 0.7 | > 0.85 |
| Hit Rate@10 | > 0.85 | > 0.95 |

## Cách chạy evaluation

```bash
cd backend
python evaluation/rag_evaluator.py
```

## Cách cải thiện metrics

### Nếu MRR thấp:
- Cải thiện reranking
- Tune embedding model
- Thêm query expansion

### Nếu Recall thấp:
- Tăng k1, k2 (retrieve nhiều docs hơn)
- Cải thiện chunking strategy
- Thêm synonyms/medical terms

### Nếu Precision thấp:
- Cải thiện reranking
- Filter out irrelevant docs
- Better query understanding

### Nếu NDCG thấp:
- Tune reranker weights
- Better relevance scoring
- Improve document quality
