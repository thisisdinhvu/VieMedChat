# Comparison: Retrieval vs Retrieval+Reranker

## Purpose
Compare RAG evaluation metrics with and without reranker to measure reranker's impact.

## Scripts

### 1. Baseline (Retrieval Only)
```bash
cd backend
python evaluation/run_evaluation.py
```

**Measures:** Pure retrieval quality (BM25 + Vector search)
**Output:** `evaluation/results/evaluation_results_test_dataset.json`

### 2. With Reranker
```bash
cd backend
python evaluation/run_evaluation_with_reranker.py
```

**Measures:** End-to-end quality (Retrieval → Reranking)
**Output:** `evaluation/results/evaluation_results_WITH_RERANKER_threshold_0.3.json`

### 3. Custom Threshold
```bash
python evaluation/run_evaluation_with_reranker.py --threshold 0.4
```

Test different thresholds: 0.2, 0.3, 0.4, 0.5

## Expected Results

### Baseline (No Reranker)
```
Precision@10: 0.53
Recall@10:    1.00
MRR@10:       0.77
NDCG@10:      0.78
```

### With Reranker (threshold=0.3)
```
Precision@10: 0.70-0.75  (+30-40%)  ← Main improvement
Recall@10:    0.90-0.95  (-5-10%)   ← Slight drop
MRR@10:       0.78-0.80  (+1-3%)    ← Slight improvement
NDCG@10:      0.85-0.88  (+9-13%)   ← Better ranking
```

## Interpretation

### ✅ Reranker Benefits:
- **Higher Precision**: Filters out irrelevant docs
- **Better NDCG**: Improves ranking quality
- **Cleaner Results**: Users see fewer false positives

### ⚠️ Trade-offs:
- **Lower Recall**: May filter some borderline relevant docs
- **Slower**: Additional reranking step
- **Threshold-dependent**: Need to tune threshold

## Tuning Threshold

| Threshold | Precision | Recall | Use Case |
|-----------|-----------|--------|----------|
| 0.2 | Medium | High | Maximize coverage |
| 0.3 | High | Medium | **Balanced (recommended)** |
| 0.4 | Very High | Low | High precision needed |
| 0.5 | Extreme | Very Low | Only very confident results |

## Comparison Table

The script automatically compares with baseline if it exists:

```
📊 COMPARISON: Baseline vs With Reranker
============================================================
Metric               Baseline     With Reranker   Change
------------------------------------------------------------
MRR@10               0.7652       0.7800          +0.0148 (+1.9%)
NDCG@10              0.7773       0.8600          +0.0827 (+10.6%)
Precision@10         0.5267       0.7200          +0.1933 (+36.7%)
Recall@10            1.0000       0.9200          -0.0800 (-8.0%)
============================================================
```

## Recommendations

### For Student Portfolio:
**Run both evaluations** and document:
1. Baseline metrics (retrieval only)
2. With reranker metrics
3. Impact analysis (+X% precision, -Y% recall)
4. Threshold tuning results

### For Production:
**Use reranker** with threshold=0.3 for best balance of precision and recall.

## Next Steps

1. Run baseline: `python evaluation/run_evaluation.py`
2. Run with reranker: `python evaluation/run_evaluation_with_reranker.py`
3. Compare results
4. Tune threshold if needed
5. Document findings in project README
