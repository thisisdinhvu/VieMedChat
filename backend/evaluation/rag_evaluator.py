"""
RAG Retrieval Evaluation Framework
Evaluates the quality of document retrieval using multiple metrics:
- MRR@K (Mean Reciprocal Rank)
- Recall@K
- NDCG@K (Normalized Discounted Cumulative Gain)
- Hit Rate@K
- Precision@K
"""

import json
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from routes.rag.search import Searching
from routes.rag.embedding import Embedding
from routes.rag.utils import load_corpus
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RAGEvaluator:
    """
    Evaluate RAG retrieval quality using standard IR metrics.
    """

    def __init__(self, search_engine: Searching):
        """
        Initialize evaluator with a search engine.

        Args:
            search_engine: Configured Searching instance
        """
        self.search_engine = search_engine
        logger.info("RAG Evaluator initialized")

    def calculate_mrr(
        self, results: List[List[int]], relevant_docs: List[List[int]], k: int = 10
    ) -> float:
        """
        Calculate Mean Reciprocal Rank@K

        MRR measures how quickly the first relevant document appears.
        Formula: MRR = (1/|Q|) * Σ(1/rank_i)
        where rank_i is the position of the first relevant document for query i

        Args:
            results: List of retrieved document IDs for each query [[doc1, doc2, ...], ...]
            relevant_docs: List of relevant document IDs for each query [[doc1, doc2], ...]
            k: Consider only top-k results

        Returns:
            MRR@K score (0-1, higher is better)
        """
        reciprocal_ranks = []

        for retrieved, relevant in zip(results, relevant_docs):
            # Only consider top-k
            retrieved_k = retrieved[:k]

            # Find position of first relevant doc
            for rank, doc_id in enumerate(retrieved_k, start=1):
                if doc_id in relevant:
                    reciprocal_ranks.append(1.0 / rank)
                    break
            else:
                # No relevant doc found in top-k
                reciprocal_ranks.append(0.0)

        mrr = np.mean(reciprocal_ranks)
        logger.info(f"MRR@{k}: {mrr:.4f}")
        return mrr

    def calculate_recall_at_k(
        self, results: List[List[int]], relevant_docs: List[List[int]], k: int = 10
    ) -> float:
        """
        Calculate Recall@K

        Recall@K = (# relevant docs in top-k) / (total # relevant docs)

        Args:
            results: Retrieved document IDs
            relevant_docs: Ground truth relevant document IDs
            k: Consider only top-k results

        Returns:
            Recall@K score (0-1, higher is better)
        """
        recalls = []

        for retrieved, relevant in zip(results, relevant_docs):
            if len(relevant) == 0:
                continue

            retrieved_k = set(retrieved[:k])
            relevant_set = set(relevant)

            # How many relevant docs were retrieved?
            num_relevant_retrieved = len(retrieved_k & relevant_set)
            recall = num_relevant_retrieved / len(relevant_set)
            recalls.append(recall)

        avg_recall = np.mean(recalls)
        logger.info(f"Recall@{k}: {avg_recall:.4f}")
        return avg_recall

    def calculate_precision_at_k(
        self, results: List[List[int]], relevant_docs: List[List[int]], k: int = 10
    ) -> float:
        """
        Calculate Precision@K

        Precision@K = (# relevant docs in top-k) / k

        Args:
            results: Retrieved document IDs
            relevant_docs: Ground truth relevant document IDs
            k: Consider only top-k results

        Returns:
            Precision@K score (0-1, higher is better)
        """
        precisions = []

        for retrieved, relevant in zip(results, relevant_docs):
            retrieved_k = set(retrieved[:k])
            relevant_set = set(relevant)

            num_relevant_retrieved = len(retrieved_k & relevant_set)
            precision = num_relevant_retrieved / k
            precisions.append(precision)

        avg_precision = np.mean(precisions)
        logger.info(f"Precision@{k}: {avg_precision:.4f}")
        return avg_precision

    def calculate_ndcg_at_k(
        self, results: List[List[int]], relevant_docs: List[List[int]], k: int = 10
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain@K

        NDCG considers both relevance and ranking position.
        DCG = Σ(rel_i / log2(i+1))
        NDCG = DCG / IDCG (ideal DCG)

        Args:
            results: Retrieved document IDs
            relevant_docs: Ground truth relevant document IDs (binary relevance)
            k: Consider only top-k results

        Returns:
            NDCG@K score (0-1, higher is better)
        """
        ndcgs = []

        for retrieved, relevant in zip(results, relevant_docs):
            retrieved_k = retrieved[:k]
            relevant_set = set(relevant)

            # Calculate DCG
            dcg = 0.0
            for i, doc_id in enumerate(retrieved_k, start=1):
                relevance = 1.0 if doc_id in relevant_set else 0.0
                dcg += relevance / np.log2(i + 1)

            # Calculate ideal DCG (all relevant docs at top)
            ideal_ranking = [1.0] * min(len(relevant), k) + [0.0] * max(
                0, k - len(relevant)
            )
            idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_ranking))

            # NDCG
            ndcg = dcg / idcg if idcg > 0 else 0.0
            ndcgs.append(ndcg)

        avg_ndcg = np.mean(ndcgs)
        logger.info(f"NDCG@{k}: {avg_ndcg:.4f}")
        return avg_ndcg

    def calculate_hit_rate_at_k(
        self, results: List[List[int]], relevant_docs: List[List[int]], k: int = 10
    ) -> float:
        """
        Calculate Hit Rate@K

        Hit Rate = (# queries with at least 1 relevant doc in top-k) / (total # queries)

        Args:
            results: Retrieved document IDs
            relevant_docs: Ground truth relevant document IDs
            k: Consider only top-k results

        Returns:
            Hit Rate@K score (0-1, higher is better)
        """
        hits = 0

        for retrieved, relevant in zip(results, relevant_docs):
            retrieved_k = set(retrieved[:k])
            relevant_set = set(relevant)

            # Check if at least one relevant doc is in top-k
            if len(retrieved_k & relevant_set) > 0:
                hits += 1

        hit_rate = hits / len(results) if len(results) > 0 else 0.0
        logger.info(f"Hit Rate@{k}: {hit_rate:.4f}")
        return hit_rate

    def evaluate_all_metrics(
        self, test_queries: List[Dict], k_values: List[int] = [5, 10, 20]
    ) -> Dict:
        """
        Evaluate all metrics for a set of test queries.

        Args:
            test_queries: List of test cases, each with:
                {
                    "query": "user query",
                    "relevant_doc_ids": [1, 5, 10]  # Ground truth
                }
            k_values: List of k values to evaluate

        Returns:
            Dictionary of all metrics
        """
        logger.info(f"Evaluating {len(test_queries)} test queries...")

        # Retrieve documents for all queries
        all_results = []
        all_relevant = []

        for test_case in test_queries:
            query = test_case["query"]
            relevant_ids = test_case["relevant_doc_ids"]

            # Perform retrieval
            docs = self.search_engine.hybrid_search(query)
            retrieved_ids = [
                doc.metadata.get("doc_id", i) for i, doc in enumerate(docs)
            ]

            all_results.append(retrieved_ids)
            all_relevant.append(relevant_ids)

        # Calculate metrics for each k
        metrics = {}
        for k in k_values:
            logger.info(f"\n--- Metrics @{k} ---")
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

    def print_metrics_table(self, metrics: Dict):
        """
        Print metrics in a nice table format.

        Args:
            metrics: Dictionary of metric name -> value
        """
        print("\n" + "=" * 60)
        print("RAG RETRIEVAL EVALUATION RESULTS")
        print("=" * 60)
        print(f"{'Metric':<20} {'Score':<10}")
        print("-" * 60)

        for metric_name, score in sorted(metrics.items()):
            print(f"{metric_name:<20} {score:.4f}")

        print("=" * 60 + "\n")
