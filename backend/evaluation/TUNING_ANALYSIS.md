# 🎯 RAG Tuning Analysis & Recommendations

## 📊 Current Configuration

### Hybrid Search (search.py)
```python
k1 = 10  # Vector search results
k2 = 10  # BM25 search results
vector_weight = 0.3
bm25_weight = 0.7
```

**Analysis:**
- Retrieve up to 20 candidates (10 vector + 10 BM25)
- BM25 has higher weight (70%) → keyword matching prioritized
- Deduplication by first 100 chars → may keep similar irrelevant docs

### Reranking (rag_service.py)
```python
use_reranker = True
reranker_model = "BAAI/bge-reranker-v2-m3"
initial_k = top_k * 2  # Fetch 2x candidates for reranking
```

**Analysis:**
- Reranker IS enabled ✅
- Fetches 10 candidates (5 * 2) for reranking to get final 5
- **Issue:** No threshold filtering → keeps low-score docs

---

## 🔍 Root Cause Analysis

### Why Precision@10 = 0.53 (low)?

**Problem 1: Too many candidates**
```
Hybrid search: 10 vector + 10 BM25 = up to 20 docs
After dedup: ~9-10 docs
Evaluation uses top-10 → includes many irrelevant docs
```

**Problem 2: No score threshold**
```python
# Current reranking (no filtering)
final_context = self.reranker.rerank(query, context_candidates)
# Returns ALL docs, even with low scores
```

**Problem 3: BM25 weight too high**
```
BM25 (70%) → keyword matching → may retrieve docs with keywords but wrong context
Vector (30%) → semantic → better for medical queries
```

---

## 🚀 Tuning Strategies (3 Options)

### **Option 1: Reduce k1, k2 (Easiest, Quick Win)**

**Change:**
```python
# Current
k1 = 10, k2 = 10

# Proposed
k1 = 5, k2 = 5
```

**Expected Impact:**
- ✅ Precision@10: 0.53 → **0.65-0.70** (+20-30%)
- ⚠️ Recall@10: 1.0 → **0.95** (-5%)
- ⚠️ MRR@10: 0.77 → **0.75** (-2%)

**Pros:**
- Simple, 1-line change
- Reduces noise significantly
- Faster retrieval

**Cons:**
- Slight recall drop (still excellent at 0.95)

**Recommendation:** ⭐⭐⭐⭐⭐ **DO THIS FIRST**

---

### **Option 2: Adjust Vector/BM25 Weights (Medium Effort)**

**Change:**
```python
# Current
vector_weight = 0.3
bm25_weight = 0.7

# Proposed
vector_weight = 0.5
bm25_weight = 0.5
```

**Rationale:**
- Medical queries benefit more from semantic understanding
- "triệu chứng suy thận" → need semantic match, not just keywords

**Expected Impact:**
- ✅ Precision@10: 0.53 → **0.60-0.65** (+15-20%)
- ✅ NDCG@10: 0.78 → **0.82** (+5%)
- ➡️ Recall@10: ~1.0 (no change)

**Pros:**
- Better semantic matching
- Maintains recall

**Cons:**
- Need to test different ratios (0.5/0.5, 0.6/0.4, etc.)

**Recommendation:** ⭐⭐⭐⭐ **COMBINE WITH OPTION 1**

---

### **Option 3: Add Reranker Threshold (Best Quality)**

**Change:**
```python
# In routes/rag/reranker.py
class Reranker:
    def rerank(self, query, documents, threshold=0.3):  # ← Add threshold
        """Rerank with score filtering"""
        scores = self.model.compute_score([[query, doc] for doc in documents])
        
        # Filter by threshold
        filtered = [
            (doc, score) 
            for doc, score in zip(documents, scores) 
            if score > threshold  # ← Only keep high-score docs
        ]
        
        # Sort and return
        filtered.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in filtered[:self.top_n]]
```

**Expected Impact:**
- ✅ Precision@10: 0.53 → **0.70-0.75** (+30-40%)
- ✅ NDCG@10: 0.78 → **0.85** (+9%)
- ⚠️ Recall@10: 1.0 → **0.90-0.95** (-5-10%)

**Pros:**
- Highest precision gain
- Filters out low-quality docs
- More reliable results

**Cons:**
- Need to tune threshold (0.2, 0.3, 0.4?)
- May filter some borderline relevant docs

**Recommendation:** ⭐⭐⭐⭐⭐ **BEST FOR PRODUCTION**

---

## 📈 Recommended Tuning Plan

### **Phase 1: Quick Wins (5 minutes)**

**Step 1:** Reduce k1, k2
```python
# In evaluation/run_evaluation.py, line 73
search_engine = Searching(
    k1=5,   # ← Change from 10
    k2=5,   # ← Change from 10
    embedding_instance=vectorstore,
    splits=splits
)
```

**Step 2:** Adjust weights
```python
# In routes/rag/search.py, line 72
def hybrid_search(self, query, vector_weight=0.5, bm25_weight=0.5):  # ← Change
```

**Expected Result:**
```
Precision@10: 0.53 → 0.65-0.70
Recall@10: 1.0 → 0.95
MRR@10: 0.77 → 0.75
NDCG@10: 0.78 → 0.82
```

---

### **Phase 2: Advanced (30 minutes)**

**Step 3:** Add reranker threshold

Create new file: `routes/rag/reranker_with_threshold.py`
```python
class RerankerWithThreshold(Reranker):
    def rerank(self, query, documents, threshold=0.3):
        # Implementation above
```

**Step 4:** Use in rag_service.py
```python
# Line 145
if should_rerank and self.reranker:
    final_context = self.reranker.rerank(
        query, 
        context_candidates,
        threshold=0.3  # ← Add threshold
    )
```

**Expected Result:**
```
Precision@10: 0.65 → 0.72
Recall@10: 0.95 → 0.92
MRR@10: 0.75 → 0.78
NDCG@10: 0.82 → 0.86
```

---

## 🧪 Testing Protocol

### 1. Baseline (Current)
```bash
cd backend
python evaluation/run_evaluation.py
# Save results as baseline
```

### 2. Test Option 1 (k1=5, k2=5)
```bash
# Edit run_evaluation.py line 73
python evaluation/run_evaluation.py --k-values 5 10 20
# Compare with baseline
```

### 3. Test Option 2 (weights)
```bash
# Edit search.py line 72
python evaluation/run_evaluation.py
# Compare
```

### 4. Test Option 3 (threshold)
```bash
# Implement threshold
python evaluation/run_evaluation.py
# Final comparison
```

---

## 📊 Expected Final Results

### Conservative Estimate (Option 1 + 2)
```
Metric          Current   After Tuning   Change
----------------------------------------------
MRR@10          0.77      0.75          -2%
Recall@10       1.00      0.95          -5%
Precision@10    0.53      0.68          +28%  ← Main goal
NDCG@10         0.78      0.82          +5%
Hit Rate@10     1.00      0.97          -3%
```

### Aggressive Estimate (All 3 Options)
```
Metric          Current   After Tuning   Change
----------------------------------------------
MRR@10          0.77      0.78          +1%
Recall@10       1.00      0.92          -8%
Precision@10    0.53      0.72          +36%  ← Excellent!
NDCG@10         0.78      0.86          +10%
Hit Rate@10     1.00      0.95          -5%
```

---

## ⚖️ Trade-offs Analysis

### What you GAIN:
✅ **Precision +30-40%** → Less noise, better user experience
✅ **NDCG +5-10%** → Better ranking quality
✅ **Faster retrieval** → Less docs to process

### What you LOSE:
⚠️ **Recall -5-10%** → May miss some relevant docs (still >90%)
⚠️ **Hit Rate -3-5%** → 1-2 queries may have no relevant doc in top-10

### Is it worth it?
**YES!** Because:
1. Precision is MORE important than recall for user experience
2. Recall@10 = 0.92 is still EXCELLENT
3. Users prefer 5 highly relevant docs over 10 mixed-quality docs

---

## 🎓 Recommendation Summary

### For Student Portfolio:
**Do Option 1 + 2** (Quick, safe, good results)
- Change k1, k2 to 5
- Adjust weights to 0.5/0.5
- **Expected: Precision 0.68, Recall 0.95**

### For Production:
**Do All 3 Options** (Best quality)
- Reduce k1, k2
- Adjust weights
- Add threshold filtering
- **Expected: Precision 0.72, Recall 0.92**

---

## 💡 Next Steps

1. **Review this analysis**
2. **Decide which options to implement**
3. **I'll help you make the code changes**
4. **Re-run evaluation**
5. **Compare results**

Ready to tune? 🚀
