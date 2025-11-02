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
            # Default to BAAI reranker
            self.reranker = FlagReranker(model_name, use_fp16=True)
            self.backend = "baai"

    def rerank(self, query: str, passages: list[str]) -> list[str]:
        """
        Rerank retrieved documents by semantic relevance.

        Args:
            query (str): The user question or symptom description.
            passages (list[str]): List of retrieved medical passages.

        Returns:
            list[str]: Passages reordered by relevance score.
        """
        if not passages:
            return []

        if self.backend == "cohere":
            results = self.reranker.rerank(
                query=query,
                documents=passages,
                top_n=min(self.top_n, len(passages)),
                model="rerank-multilingual-v3.0"
            ).results
            reranked_passages = [passages[result.index] for result in results]
            scores = [result.relevance_score for result in results]

        else:  # BAAI reranker
            scores = self.reranker.compute_score(
                [[query, passage] for passage in passages],
                normalize=True
            )
            # Sort descending by score
            reranked_pairs = sorted(zip(scores, passages), key=lambda x: x[0], reverse=True)
            reranked_passages = [p for _, p in reranked_pairs[:self.top_n]]

        print(f"[RERANK] Query: {query}")
        print(f"[RERANK] Scores: {scores[:self.top_n]}")
        return reranked_passages


# if __name__ == "__main__":
#     # Example test run
#     query = "Tôi bị đau đầu, chóng mặt, và buồn nôn, có thể là bệnh gì?"
#     passages = [
#         "Đau đầu có thể liên quan đến tăng huyết áp hoặc căng thẳng.",
#         "Triệu chứng buồn nôn và chóng mặt thường gặp ở người bị rối loạn tiền đình.",
#         "Sốt nhẹ và ho là dấu hiệu thường thấy của cảm cúm."
#     ]

#     # Test Cohere reranker
#     cohere_rerank = Rerank(model_name="cohere", top_n=2)
#     print("Cohere:", cohere_rerank.rerank(query, passages))

#     # Test BAAI reranker
#     baai_rerank = Rerank(model_name="BAAI/bge-reranker-v2-m3", top_n=2)
#     print("BAAI:", baai_rerank.rerank(query, passages))
