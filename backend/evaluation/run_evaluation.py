"""
Fixed RAG Evaluator - Loads real test_dataset.json

IMPORTANT: Must run from backend/ directory:
    cd backend
    python evaluation/run_evaluation.py
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
from utils.logger import setup_logger
from evaluation.rag_evaluator import RAGEvaluator

load_dotenv()
logger = setup_logger(__name__)


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Evaluate RAG retrieval quality")
    parser.add_argument(
        "--test-file",
        type=str,
        default="test_dataset.json",
        help="Path to test dataset JSON file (default: test_dataset.json)",
    )
    parser.add_argument(
        "--k-values",
        type=int,
        nargs="+",
        default=[5, 10, 20],
        help="K values for metrics (default: 5 10 20)",
    )

    args = parser.parse_args()

    # Initialize components
    logger.info("Initializing RAG components...")

    # Load embedding
    embedding = Embedding(
        model_name="BAAI/bge-m3",
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    )
    vectorstore = embedding.load_embedding()

    # Fix corpus path (remove "backend" prefix if present)
    corpus_path = os.getenv("CORPUS_PATH")
    if corpus_path and corpus_path.startswith("backend"):
        corpus_path = corpus_path.replace("backend\\", "").replace("backend/", "")

    logger.info(f"Loading corpus from: {corpus_path}")
    _, splits = load_corpus(corpus_path)

    # Create search engine with TUNED parameters
    search_engine = Searching(
        k1=10,  # ✅ TUNED: Reduced from 10 to 5 for better precision
        k2=10,  # ✅ TUNED: Reduced from 10 to 5 for better precision
        embedding_instance=vectorstore,
        splits=splits,
    )

    # Create evaluator
    evaluator = RAGEvaluator(search_engine)

    # Load test dataset from file
    test_file_path = Path("evaluation") / args.test_file
    logger.info(f"Loading test dataset from: {test_file_path}")

    if not test_file_path.exists():
        logger.error(f"Test file not found: {test_file_path}")
        logger.error("Please run: python evaluation/generate_ground_truth.py first")
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
    print(f"{'='*60}\n")

    # Evaluate
    logger.info(f"Evaluating with k_values: {args.k_values}")
    metrics = evaluator.evaluate_all_metrics(test_queries, k_values=args.k_values)

    # Print results
    evaluator.print_metrics_table(metrics)

    # Save results
    results_dir = Path("evaluation/results")
    results_dir.mkdir(exist_ok=True)

    timestamp = Path(args.test_file).stem
    results_file = results_dir / f"evaluation_results_{timestamp}.json"

    # Save both metrics and dataset info
    full_results = {
        "test_file": args.test_file,
        "num_queries": len(test_queries),
        "total_relevant_docs": total_relevant,
        "avg_relevant_per_query": avg_relevant,
        "k_values": args.k_values,
        "metrics": metrics,
    }

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Results saved to {results_file}")
