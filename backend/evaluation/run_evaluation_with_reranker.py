"""
RAG Evaluation WITH Reranker
Evaluates end-to-end RAG pipeline including reranking step

Usage:
    cd backend
    python evaluation/run_evaluation_with_reranker.py

This will show the impact of reranker on retrieval metrics.
"""

import json
import numpy as np
from typing import List, Dict
from pathlib import Path
import sys
import os
import argparse
from dotenv import load_dotenv

# CRITICAL: Add backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

# Now imports will work
from routes.rag.search import Searching
from routes.rag.embedding import Embedding
from routes.rag.utils import load_corpus
from routes.rag.reranker import Reranker
from utils.logger import setup_logger
from evaluation.rag_evaluator import RAGEvaluator

load_dotenv()
logger = setup_logger(__name__)


class RAGEvaluatorWithReranker(RAGEvaluator):
    """
    Extended evaluator that includes reranking step.
    Measures end-to-end performance: Retrieval → Reranking → Metrics
    """

    def __init__(
        self,
        search_engine: Searching,
        reranker: Reranker,
        rerank_threshold: float = 0.3,
    ):
        """
        Initialize evaluator with reranker.

        Args:
            search_engine: Configured search engine
            reranker: Configured reranker
            rerank_threshold: Score threshold for filtering (default: 0.3)
        """
        super().__init__(search_engine)
        self.reranker = reranker
        self.rerank_threshold = rerank_threshold
        logger.info(
            f"RAG Evaluator WITH Reranker initialized (threshold={rerank_threshold})"
        )

    def evaluate_all_metrics(
        self, test_queries: List[Dict], k_values: List[int] = [5, 10, 20]
    ) -> Dict:
        """
        Evaluate all metrics with reranking step.

        Args:
            test_queries: List of test cases
            k_values: List of k values to evaluate

        Returns:
            Dictionary of all metrics
        """
        logger.info(f"Evaluating {len(test_queries)} test queries WITH RERANKER...")

        # Retrieve and rerank documents for all queries
        all_results = []
        all_relevant = []

        for test_case in test_queries:
            query = test_case["query"]
            relevant_ids = test_case["relevant_doc_ids"]

            # Step 1: Perform retrieval (with tuned parameters)
            docs = self.search_engine.hybrid_search(
                query, vector_weight=0.6, bm25_weight=0.4  # ✅ TUNED  # ✅ TUNED
            )

            # Step 2: Extract content for reranking
            context_candidates = self.search_engine.get_context(docs)

            # Step 3: Rerank with threshold filtering
            try:
                reranked_context = self.reranker.rerank(
                    query, context_candidates, threshold=self.rerank_threshold
                )

                # Map reranked context back to doc IDs
                # Find which docs match the reranked context
                reranked_doc_ids = []
                for reranked_text in reranked_context:
                    for i, doc in enumerate(docs):
                        if doc.page_content == reranked_text:
                            doc_id = doc.metadata.get("doc_id", i)
                            if doc_id not in reranked_doc_ids:
                                reranked_doc_ids.append(doc_id)
                            break

                retrieved_ids = reranked_doc_ids

            except Exception as e:
                logger.warning(f"Reranking failed for query '{query[:30]}...': {e}")
                # Fallback to original retrieval
                retrieved_ids = [
                    doc.metadata.get("doc_id", i) for i, doc in enumerate(docs)
                ]

            all_results.append(retrieved_ids)
            all_relevant.append(relevant_ids)

        # Calculate metrics for each k
        metrics = {}
        for k in k_values:
            logger.info(f"\n--- Metrics @{k} (WITH RERANKER) ---")
            metrics[f"MRR@{k}"] = self.calculate_mrr(all_results, all_relevant, k)
            metrics[f"Recall@{k}"] = self.calculate_recall_at_k(
                all_results, all_relevant, k
            )
            metrics[f"Precision@{k}"] = self.calculate_precision_at_k(
                all_results, all_relevant, k
            )
            metrics[f"NDCG@{k}"] = self.calculate_ndcg_at_k(
                all_results, all_relevant, k
            )
            metrics[f"HitRate@{k}"] = self.calculate_hit_rate_at_k(
                all_results, all_relevant, k
            )

        return metrics


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Evaluate RAG with reranker")
    parser.add_argument(
        "--test-file",
        type=str,
        default="test_dataset.json",
        help="Path to test dataset JSON file",
    )
    parser.add_argument(
        "--k-values",
        type=int,
        nargs="+",
        default=[5, 10, 20],
        help="K values for metrics",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.2,
        help="Reranker score threshold (default: 0.2)",
    )

    args = parser.parse_args()

    # Initialize components
    logger.info("Initializing RAG components WITH RERANKER...")

    # Load embedding
    embedding = Embedding(
        model_name="BAAI/bge-m3",
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    )
    vectorstore = embedding.load_embedding()

    # Fix corpus path
    corpus_path = os.getenv("CORPUS_PATH")
    if corpus_path and corpus_path.startswith("backend"):
        corpus_path = corpus_path.replace("backend\\", "").replace("backend/", "")

    logger.info(f"Loading corpus from: {corpus_path}")
    _, splits = load_corpus(corpus_path)

    # Create search engine with TUNED parameters
    search_engine = Searching(
        k1=10,  # ✅ TUNED
        k2=10,  # ✅ TUNED
        embedding_instance=vectorstore,
        splits=splits,
    )

    # Create reranker
    logger.info("Initializing reranker...")
    reranker = Reranker(
        model_name="BAAI/bge-reranker-v2-m3",
        top_n=10,  # Allow up to 10 docs after reranking
    )

    # Create evaluator WITH reranker
    evaluator = RAGEvaluatorWithReranker(
        search_engine, reranker, rerank_threshold=args.threshold
    )

    # Load test dataset
    test_file_path = Path("evaluation") / args.test_file
    logger.info(f"Loading test dataset from: {test_file_path}")

    if not test_file_path.exists():
        logger.error(f"Test file not found: {test_file_path}")
        sys.exit(1)

    with open(test_file_path, "r", encoding="utf-8") as f:
        test_queries = json.load(f)

    logger.info(f"✅ Loaded {len(test_queries)} test queries")

    # Print dataset info
    total_relevant = sum(len(q.get("relevant_doc_ids", [])) for q in test_queries)
    avg_relevant = total_relevant / len(test_queries) if test_queries else 0

    print(f"\n{'='*60}")
    print(f"TEST DATASET INFO")
    print(f"{'='*60}")
    print(f"Total queries: {len(test_queries)}")
    print(f"Total relevant docs: {total_relevant}")
    print(f"Avg relevant per query: {avg_relevant:.2f}")
    print(f"Reranker threshold: {args.threshold}")
    print(f"{'='*60}\n")

    # Evaluate WITH reranker
    logger.info(f"Evaluating with k_values: {args.k_values}")
    metrics_with_reranker = evaluator.evaluate_all_metrics(
        test_queries, k_values=args.k_values
    )

    # Print results
    evaluator.print_metrics_table(metrics_with_reranker)

    # Save results
    results_dir = Path("evaluation/results")
    results_dir.mkdir(exist_ok=True)

    results_file = (
        results_dir
        / f"evaluation_results_WITH_RERANKER_threshold_{args.threshold}.json"
    )

    full_results = {
        "test_file": args.test_file,
        "num_queries": len(test_queries),
        "total_relevant_docs": total_relevant,
        "avg_relevant_per_query": avg_relevant,
        "k_values": args.k_values,
        "reranker_enabled": True,
        "reranker_threshold": args.threshold,
        "metrics": metrics_with_reranker,
    }

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Results saved to {results_file}")

    # Compare with baseline (if exists)
    baseline_file = results_dir / "evaluation_results_test_dataset.json"
    if baseline_file.exists():
        print(f"\n{'='*60}")
        print(f"📊 COMPARISON: Baseline vs With Reranker")
        print(f"{'='*60}")

        with open(baseline_file, "r", encoding="utf-8") as f:
            baseline_results = json.load(f)

        baseline_metrics = baseline_results.get("metrics", {})

        print(f"{'Metric':<20} {'Baseline':<12} {'With Reranker':<15} {'Change':<10}")
        print(f"{'-'*60}")

        for metric_name in sorted(metrics_with_reranker.keys()):
            baseline_score = baseline_metrics.get(metric_name, 0.0)
            reranker_score = metrics_with_reranker[metric_name]
            change = reranker_score - baseline_score
            change_pct = (change / baseline_score * 100) if baseline_score > 0 else 0

            change_str = f"{change:+.4f} ({change_pct:+.1f}%)"
            print(
                f"{metric_name:<20} {baseline_score:<12.4f} {reranker_score:<15.4f} {change_str:<10}"
            )

        print(f"{'='*60}\n")
