# Ground Truth Generation Guide

## 🎯 Mục đích

Script này giúp bạn tạo **ground truth thật** cho RAG evaluation bằng cách kết hợp:
- **LLM-as-Judge**: Gemini tự động đánh giá relevance
- **Manual Review**: Bạn review và override nếu cần

## 🚀 Cách sử dụng

### Option 1: Hybrid Mode (Khuyên dùng)
LLM đánh giá trước, bạn review và xác nhận:

```bash
cd backend
python evaluation/generate_ground_truth.py --mode hybrid
```

**Flow:**
1. Script hiển thị document
2. LLM đánh giá: ✅ RELEVANT hoặc ❌ NOT RELEVANT
3. Bạn xác nhận: `y` (đồng ý), `n` (không đồng ý), Enter (chấp nhận LLM)

### Option 2: Auto Mode
LLM tự động đánh giá tất cả:

```bash
python evaluation/generate_ground_truth.py --mode auto
```

**Ưu điểm:** Nhanh, không cần manual work
**Nhược điểm:** Có thể sai ~10-15%

### Option 3: Manual Mode
Bạn tự đánh giá tất cả:

```bash
python evaluation/generate_ground_truth.py --mode manual
```

**Ưu điểm:** Chính xác nhất
**Nhược điểm:** Tốn thời gian

## 📝 Custom Queries

Tạo file `my_queries.json`:

```json
[
  "triệu chứng suy thận",
  "cách điều trị tiểu đường",
  "paracetamol có tác dụng phụ gì"
]
```

Chạy:
```bash
python evaluation/generate_ground_truth.py --queries-file my_queries.json
```

## ⚙️ Advanced Options

```bash
# Retrieve nhiều docs hơn (default: 20)
python evaluation/generate_ground_truth.py --top-k 30

# Custom output file
python evaluation/generate_ground_truth.py --output my_test_dataset.json

# Kết hợp tất cả
python evaluation/generate_ground_truth.py \
  --mode hybrid \
  --top-k 30 \
  --queries-file my_queries.json \
  --output my_test_dataset.json
```

## 📊 Output Format

File `test_dataset.json`:

```json
[
  {
    "query": "triệu chứng suy thận",
    "relevant_doc_ids": [3, 7, 15],
    "total_retrieved": 20,
    "num_relevant": 3,
    "doc_details": [
      {
        "doc_id": 3,
        "rank": 2,
        "reasoning": "Document chứa thông tin chi tiết về các triệu chứng suy thận cấp và mãn tính",
        "content_preview": "Suy thận là tình trạng..."
      }
    ]
  }
]
```

## 💡 Tips

### 1. Bắt đầu với queries dễ
- Queries có exact match keywords
- Ví dụ: "triệu chứng suy thận" thay vì "tôi bị đau lưng có phải suy thận không?"

### 2. Đa dạng hóa queries
- Symptoms: "triệu chứng X"
- Treatment: "cách điều trị X"
- Medication: "thuốc X có tác dụng phụ gì"
- Diet: "chế độ ăn cho người X"

### 3. Review LLM judgment
- LLM thường đúng ~85-90%
- Cần review kỹ với:
  - Medical terminology phức tạp
  - Queries애매 (ambiguous)
  - Documents ngắn

### 4. Incremental saving
Script tự động lưu `test_dataset_temp.json` sau mỗi query → Không sợ mất dữ liệu nếu bị gián đoạn

## 🔍 Ví dụ thực tế

```bash
$ python evaluation/generate_ground_truth.py --mode hybrid

================================================================================
🚀 GROUND TRUTH GENERATION
================================================================================
Mode: hybrid
Queries: 15
Top-K: 20
Output: test_dataset.json
================================================================================

🔀 Hybrid mode: LLM judges first, then you can override
   Type 'y' to confirm, 'n' to reject, or press Enter to accept LLM judgment

Press Enter to start...

################################################################################
# Query 1/15
################################################################################

================================================================================
Query: triệu chứng suy thận
================================================================================

────────────────────────────────────────────────────────────────────────────────
📄 Document #1 (ID: 3)
────────────────────────────────────────────────────────────────────────────────
Suy thận mãn tính là tình trạng thận mất dần chức năng lọc máu...
Các triệu chứng thường gặp:
- Tiểu ít hoặc tiểu đêm nhiều lần
- Mệt mỏi, chán ăn
- Buồn nôn, nôn
...
────────────────────────────────────────────────────────────────────────────────

🤖 LLM Judge: ✅ RELEVANT
   Reasoning: Document chứa thông tin chi tiết về triệu chứng suy thận mãn tính, 
   trả lời trực tiếp câu hỏi của user.

👤 Your judgment:
   Is this document relevant? (y/n/skip): y

[✅ Marked as RELEVANT]

...

================================================================================
✅ Found 3 relevant documents
   IDs: [3, 7, 15]
================================================================================
```

## 🎓 Best Practices

1. **Start small**: Tạo 10-15 queries trước, test evaluation
2. **Iterate**: Dựa trên kết quả để thêm queries khó hơn
3. **Balance**: Mix queries dễ, trung bình, khó
4. **Document**: Ghi chú lại reasoning cho các edge cases
5. **Review**: Sau khi tạo xong, review lại toàn bộ dataset

## ⚠️ Lưu ý

- Script cần kết nối Pinecone và Gemini API
- Đảm bảo `.env` đã config đúng
- LLM judgment tốn API quota (nhưng ít hơn nhiều so với manual)
- Với 15 queries × 20 docs = 300 LLM calls ≈ $0.01 - $0.05

## 🔗 Next Steps

Sau khi có `test_dataset.json`:

```bash
# Run evaluation
python evaluation/rag_evaluator.py

# Analyze results
# Cải thiện RAG dựa trên metrics
# Re-run evaluation
```
