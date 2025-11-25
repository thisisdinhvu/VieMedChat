"""
Synthetic Data Generator for Reranker Fine-tuning
Generates (Query, Positive, Hard Negative) triplets from the corpus.

Features:
1. Smart Filtering: Skips short/low-quality chunks.
2. Synthetic Query Generation: Uses LLM to create questions for chunks.
3. Hard Negative Mining: Retrieves similar docs.
4. LLM Verification: Ensures Negatives are truly irrelevant (denoising).

Usage:
    python evaluation/generate_synthetic_data.py --output triplets_synthetic.jsonl --limit 500
"""

import json
import os
import sys
import random
import time
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.routes.rag.search import Searching
from backend.routes.rag.embedding import Embedding
from backend.routes.rag.utils import load_corpus
from backend.utils.logger import setup_logger
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document

load_dotenv()
logger = setup_logger(__name__)


@dataclass
class Triplet:
    query: str
    positive: str
    negative: str


class SyntheticDataGenerator:
    def __init__(self, search_engine: Searching):
        self.search_engine = search_engine
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # Fast and cheap
            temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
        self.judge_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # Fast judge
            temperature=0.0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )

    def is_high_quality_chunk(self, text: str) -> bool:
        """Filter out low quality chunks."""
        if len(text) < 100:
            return False

        # Skip navigational/meta text
        skip_keywords = ["Trang chủ", "Liên hệ", "Bản quyền", "Copyright", "Menu"]
        if any(k in text for k in skip_keywords):
            return False

        return True

    def generate_question(self, chunk_text: str) -> Optional[str]:
        """Generate a question that the chunk answers."""
        prompt = f"""Bạn là chuyên gia y tế. Hãy đặt MỘT câu hỏi tiếng Việt ngắn gọn, tự nhiên mà đoạn văn dưới đây có thể trả lời.
        
        Đoạn văn:
        \"\"\"
        {chunk_text[:1000]}
        \"\"\"
        
        Yêu cầu:
        - Câu hỏi phải cụ thể, không chung chung.
        - Chỉ trả về nội dung câu hỏi, không thêm dẫn dắt.
        """
        try:
            response = self.llm.invoke(prompt).content.strip()
            return response
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            return None

    def verify_negative(self, query: str, doc_content: str) -> bool:
        """
        Verify if a document is truly irrelevant (Negative) to the query.
        Returns True if it is a valid Negative (Irrelevant).
        Returns False if it is actually Relevant (False Negative).
        """
        prompt = f"""Query: "{query}"
        
        Document:
        \"\"\"
        {doc_content[:1000]}
        \"\"\"
        
        Document này có trả lời được Query không?
        Trả lời YES nếu có, NO nếu không.
        """
        try:
            response = self.judge_llm.invoke(prompt).content.strip().upper()
            # If LLM says YES (Relevant), then it's NOT a valid Negative.
            # We want valid Negatives (NO).
            return "NO" in response
        except Exception as e:
            logger.error(f"Error verifying negative: {e}")
            return True  # Assume it's negative if error, to be safe? Or skip? Let's keep it.

    def generate_triplets(
        self, corpus_texts: List[Document], limit: int = 500
    ) -> List[Triplet]:
        triplets = []

        # Shuffle corpus to get random sample
        shuffled_docs = list(corpus_texts)
        random.shuffle(shuffled_docs)

        pbar = tqdm(total=limit, desc="Generating Triplets")

        for doc in shuffled_docs:
            if len(triplets) >= limit:
                break

            chunk_text = doc.page_content

            # 1. Smart Filter
            if not self.is_high_quality_chunk(chunk_text):
                continue

            # 2. Generate Question
            question = self.generate_question(chunk_text)
            if not question:
                continue

            # 3. Mine Hard Negatives
            # Search for similar docs
            retrieved_docs = self.search_engine.hybrid_search(question)

            hard_negatives = []
            for ret_doc in retrieved_docs:
                # Skip if it's the same doc (Positive)
                # We use simple string matching or ID check if available
                # Here we assume content overlap means same doc
                if (
                    chunk_text in ret_doc.page_content
                    or ret_doc.page_content in chunk_text
                ):
                    continue

                # 4. LLM Verification (Denoising)
                # Only keep if it's TRULY irrelevant
                if self.verify_negative(question, ret_doc.page_content):
                    hard_negatives.append(ret_doc.page_content)
                    if len(hard_negatives) >= 1:  # Just need 1-2 good negatives
                        break

            if not hard_negatives:
                continue

            # Create Triplet
            triplet = Triplet(
                query=question,
                positive=chunk_text,
                negative=hard_negatives[0],  # Take the top verified hard negative
            )
            triplets.append(triplet)
            pbar.update(1)

            # Sleep briefly to avoid rate limits
            time.sleep(0.5)

        pbar.close()
        return triplets

    def save_triplets(self, triplets: List[Triplet], output_file: str):
        output_path = Path(__file__).parent / output_file
        with open(output_path, "w", encoding="utf-8") as f:
            for t in triplets:
                data = {
                    "query": t.query,
                    "positive": t.positive,
                    "negative": t.negative,
                }
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        logger.info(f"Saved {len(triplets)} triplets to {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="triplets_synthetic.jsonl")
    parser.add_argument("--limit", type=int, default=10)  # Start small for testing
    args = parser.parse_args()

    # Init RAG
    embedding = Embedding(
        model_name="BAAI/bge-m3",
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    )
    vectorstore = embedding.load_embedding()
    corpus_path = os.getenv("CORPUS_PATH")
    _, texts = load_corpus(corpus_path)  # Load chunks

    search_engine = Searching(
        k1=10, k2=10, embedding_instance=vectorstore, splits=texts
    )

    generator = SyntheticDataGenerator(search_engine)
    triplets = generator.generate_triplets(texts, limit=args.limit)
    generator.save_triplets(triplets, args.output)


if __name__ == "__main__":
    main()
