# import os
# from FlagEmbedding import FlagReranker
# from dotenv import load_dotenv
# import cohere

# load_dotenv(".env")

# class Reranker:
#     """
#     A unified reranker class supporting both BAAI and Cohere models.
#     Used to reorder retrieved medical passages based on their relevance
#     to the user's symptom-based question or query.
#     """

#     def __init__(self, model_name="BAAI/bge-reranker-v2-m3", top_n=5):
#         self.model_name = model_name
#         self.top_n = top_n

#         cohere_api_key = os.getenv("COHERE_API_KEY")

#         # Initialize reranker based on model type
#         if self.model_name.lower().startswith("cohere"):
#             if not cohere_api_key:
#                 raise ValueError("❌ COHERE_API_KEY not found in .env file.")
#             self.reranker = cohere.Client(cohere_api_key)
#             self.backend = "cohere"
#         else:
#             # Default to BAAI reranker
#             self.reranker = FlagReranker(model_name, use_fp16=True)
#             self.backend = "baai"

#     def rerank(self, query: str, passages: list[str]) -> list[str]:
#         """
#         Rerank retrieved documents by semantic relevance.

#         Args:
#             query (str): The user question or symptom description.
#             passages (list[str]): List of retrieved medical passages.

#         Returns:
#             list[str]: Passages reordered by relevance score.
#         """
#         if not passages:
#             return []

#         if self.backend == "cohere":
#             results = self.reranker.rerank(
#                 query=query,
#                 documents=passages,
#                 top_n=min(self.top_n, len(passages)),
#                 model="rerank-multilingual-v3.0"
#             ).results
#             reranked_passages = [passages[result.index] for result in results]
#             scores = [result.relevance_score for result in results]

#         else:  # BAAI reranker
#             scores = self.reranker.compute_score(
#                 [[query, passage] for passage in passages],
#                 normalize=True
#             )
#             # Sort descending by score
#             reranked_pairs = sorted(zip(scores, passages), key=lambda x: x[0], reverse=True)
#             reranked_passages = [p for _, p in reranked_pairs[:self.top_n]]

#         print(f"[RERANK] Query: {query}")
#         print(f"[RERANK] Scores: {scores[:self.top_n]}")
#         return reranked_passages

import os
from FlagEmbedding import FlagReranker
from dotenv import load_dotenv
import cohere

load_dotenv(".env")


class Reranker:
    """
    A unified reranker class supporting both BAAI and Cohere models.
    Used to reorder retrieved medical passages based on their relevance
    to the user's symptom-based question or query.

    ✅ TUNED: Added threshold filtering for better precision
    """

    def __init__(self, model_name="BAAI/bge-reranker-v2-m3", top_n=5):
        self.model_name = model_name
        self.top_n = top_n

        cohere_api_key = os.getenv("COHERE_API_KEY")

        # Initialize reranker based on model type
        if self.model_name.lower().startswith("cohere"):
            if not cohere_api_key:
                raise ValueError("❌ COHERE_API_KEY not found in .env file.")
            self.reranker = cohere.Client(cohere_api_key)
            self.backend = "cohere"
        else:
            # Default to BAAI reranker with FP16 fallback
            try:
                self.reranker = FlagReranker(model_name, use_fp16=True)
                self.backend = "baai"
            except Exception as e:
                print(f"⚠️ FP16 initialization failed: {e}")
                print("   Falling back to FP32...")
                self.reranker = FlagReranker(model_name, use_fp16=False)
                self.backend = "baai"

    def rerank(
        self, query: str, passages: list[str], threshold: float = 0.3
    ) -> list[str]:
        """
        Rerank retrieved documents by semantic relevance.
        ✅ TUNED: Added threshold filtering to remove low-score docs

        Args:
            query (str): The user question or symptom description.
            passages (list[str]): List of retrieved medical passages.
            threshold (float): Minimum score to keep (default: 0.3)

        Returns:
            list[str]: Passages reordered by relevance score (filtered by threshold).
        """
        if not passages:
            return []

        if self.backend == "cohere":
            results = self.reranker.rerank(
                query=query,
                documents=passages,
                top_n=min(self.top_n, len(passages)),
                model="rerank-multilingual-v3.0",
            ).results

            # ✅ TUNED: Filter by threshold
            filtered_results = [r for r in results if r.relevance_score >= threshold]
            reranked_passages = [passages[result.index] for result in filtered_results]
            scores = [result.relevance_score for result in filtered_results]

        else:  # BAAI reranker
            scores = self.reranker.compute_score(
                [[query, passage] for passage in passages], normalize=True
            )

            # ✅ TUNED: Filter by threshold before sorting
            filtered_pairs = [
                (score, passage)
                for score, passage in zip(scores, passages)
                if score >= threshold
            ]

            # Sort descending by score
            reranked_pairs = sorted(filtered_pairs, key=lambda x: x[0], reverse=True)
            reranked_passages = [p for _, p in reranked_pairs[: self.top_n]]
            scores = [s for s, _ in reranked_pairs[: self.top_n]]

        print(f"[RERANK] Query: {query[:50]}...")
        print(
            f"[RERANK] Filtered: {len(passages)} → {len(reranked_passages)} docs (threshold={threshold})"
        )
        print(f"[RERANK] Scores: {[f'{s:.3f}' for s in scores[:self.top_n]]}")
        return reranked_passages
