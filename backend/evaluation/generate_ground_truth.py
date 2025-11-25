"""
Ground Truth Generator for RAG Evaluation
Combines manual review + LLM-as-Judge to create test dataset

Usage:
    python evaluation/generate_ground_truth.py --mode interactive  # Manual review
    python evaluation/generate_ground_truth.py --mode auto         # LLM-as-Judge
    python evaluation/generate_ground_truth.py --mode hybrid       # Both (recommended)
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.routes.rag.search import Searching
from backend.routes.rag.embedding import Embedding
from backend.routes.rag.utils import load_corpus
from backend.utils.logger import setup_logger
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
logger = setup_logger(__name__)


class GroundTruthGenerator:
    """
    Generate ground truth labels for RAG evaluation.
    """

    def __init__(self, search_engine: Searching, use_llm_judge: bool = True):
        """
        Initialize generator.

        Args:
            search_engine: Configured search engine
            use_llm_judge: Whether to use LLM for automatic relevance judgment
        """
        self.search_engine = search_engine
        self.use_llm_judge = use_llm_judge

        if use_llm_judge:
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.0,  # Deterministic for evaluation
                google_api_key=os.getenv("GOOGLE_API_KEY"),
            )
            logger.info("LLM judge initialized (Gemini 2.5 Flash)")

        logger.info("Ground Truth Generator initialized")

    def llm_judge_relevance(self, query: str, document: str) -> Tuple[bool, str]:
        """
        Use LLM to judge if document is relevant to query.

        Args:
            query: User query
            document: Document content

        Returns:
            (is_relevant, reasoning)
        """
        prompt = f"""Bạn là chuyên gia đánh giá chất lượng tìm kiếm y tế.

Nhiệm vụ: Đánh giá xem document có RELEVANT (liên quan) đến query không.

Query: "{query}"

Document:
\"\"\"
{document[:1000]}  
\"\"\"

Hãy trả lời theo format:

RELEVANT: Yes/No
REASONING: <Giải thích ngắn gọn tại sao relevant hoặc không relevant>

Quy tắc:
- RELEVANT = Yes nếu document chứa thông tin trả lời được query
- RELEVANT = No nếu document không liên quan hoặc chỉ đề cập qua loa
- Với query y tế, chỉ cần document chứa thông tin hữu ích là được, không cần trả lời đầy đủ 100%
"""

        try:
            response = self.llm.invoke(prompt).content

            # Parse response
            is_relevant = (
                "yes" in response.lower().split("relevant:")[1].split("\n")[0].lower()
            )

            # Extract reasoning
            reasoning = ""
            if "reasoning:" in response.lower():
                reasoning = response.split("REASONING:")[-1].strip()

            return is_relevant, reasoning

        except Exception as e:
            logger.error(f"LLM judge error: {e}")
            return False, "Error in LLM judgment"

    def generate_for_query(
        self, query: str, top_k: int = 20, mode: str = "hybrid"
    ) -> Dict:
        """
        Generate ground truth for a single query.

        Args:
            query: User query
            top_k: Number of documents to retrieve
            mode: "manual", "auto", or "hybrid"

        Returns:
            Test case with ground truth labels
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Query: {query}")
        logger.info(f"{'='*80}")

        # Retrieve documents
        docs = self.search_engine.hybrid_search(query)
        top_docs = docs[:top_k]

        relevant_doc_ids = []
        doc_details = []

        # Process each document
        for rank, doc in enumerate(top_docs, start=1):
            doc_id = doc.metadata.get("doc_id", rank - 1)
            content = doc.page_content

            print(f"\n{'─'*80}")
            print(f"📄 Document #{rank} (ID: {doc_id})")
            print(f"{'─'*80}")
            print(f"{content[:500]}...")
            print(f"{'─'*80}")

            is_relevant = False
            reasoning = ""

            # Auto mode: LLM judges
            if mode in ["auto", "hybrid"] and self.use_llm_judge:
                is_relevant, reasoning = self.llm_judge_relevance(query, content)
                print(
                    f"\n🤖 LLM Judge: {'✅ RELEVANT' if is_relevant else '❌ NOT RELEVANT'}"
                )
                print(f"   Reasoning: {reasoning}")

            # Manual mode or hybrid: Ask user
            if mode in ["manual", "hybrid"]:
                print(f"\n👤 Your judgment:")
                user_input = (
                    input(f"   Is this document relevant? (y/n/skip): ").lower().strip()
                )

                if user_input == "skip":
                    continue
                elif user_input == "y":
                    is_relevant = True
                elif user_input == "n":
                    is_relevant = False
                else:
                    # Default to LLM judgment if available
                    if mode == "hybrid":
                        print(f"   Invalid input. Using LLM judgment: {is_relevant}")
                    else:
                        is_relevant = False

            # Record result
            if is_relevant:
                relevant_doc_ids.append(doc_id)
                doc_details.append(
                    {
                        "doc_id": doc_id,
                        "rank": rank,
                        "reasoning": reasoning,
                        "content_preview": content[:200],
                    }
                )

        # Summary
        print(f"\n{'='*80}")
        print(f"✅ Found {len(relevant_doc_ids)} relevant documents")
        print(f"   IDs: {relevant_doc_ids}")
        print(f"{'='*80}\n")

        return {
            "query": query,
            "relevant_doc_ids": relevant_doc_ids,
            "total_retrieved": top_k,
            "num_relevant": len(relevant_doc_ids),
            "doc_details": doc_details,
        }

    def generate_test_dataset(
        self,
        queries: List[str],
        output_file: str = "test_dataset.json",
        mode: str = "hybrid",
        top_k: int = 20,
    ):
        """
        Generate complete test dataset for multiple queries.

        Args:
            queries: List of test queries
            output_file: Output JSON file path
            mode: "manual", "auto", or "hybrid"
            top_k: Number of docs to retrieve per query
        """
        logger.info(f"Generating ground truth for {len(queries)} queries...")
        logger.info(f"Mode: {mode}")

        test_dataset = []

        for i, query in enumerate(queries, start=1):
            print(f"\n\n{'#'*80}")
            print(f"# Query {i}/{len(queries)}")
            print(f"{'#'*80}\n")

            test_case = self.generate_for_query(query, top_k=top_k, mode=mode)
            test_dataset.append(test_case)

            # Save incrementally (in case of interruption)
            temp_file = output_file.replace(".json", "_temp.json")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(test_dataset, f, indent=2, ensure_ascii=False)

        # Save final dataset
        output_path = Path(__file__).parent / output_file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(test_dataset, f, indent=2, ensure_ascii=False)

        logger.info(f"\n✅ Test dataset saved to: {output_path}")

        # Print statistics
        total_relevant = sum(case["num_relevant"] for case in test_dataset)
        avg_relevant = total_relevant / len(test_dataset)

        print(f"\n{'='*80}")
        print(f"📊 DATASET STATISTICS")
        print(f"{'='*80}")
        print(f"Total queries: {len(test_dataset)}")
        print(f"Total relevant docs: {total_relevant}")
        print(f"Avg relevant per query: {avg_relevant:.2f}")
        print(f"{'='*80}\n")

        return test_dataset


def get_sample_queries() -> List[str]:
    """
    Get sample medical queries for testing.
    You should customize this based on your use case.
    """
    return [
        # ========== SYMPTOMS (Easy - Specific) ==========
        "triệu chứng suy thận",
        "dấu hiệu tiểu đường",
        "đau đầu và buồn nôn",
        "ho ra máu",
        "đau ngực trái",
        "triệu chứng nhồi máu cơ tim",
        # ========== SYMPTOMS (Medium - Vague/Ambiguous) ==========
        "bị mệt mỏi kéo dài",
        "chóng mặt và buồn nôn",
        "đau bụng dữ dội",
        "sốt cao không rõ nguyên nhân",
        "khó thở về đêm",
        # ========== TREATMENT (Easy - Specific Disease) ==========
        "cách điều trị cao huyết áp",
        "thuốc gì cho người tiểu đường",
        "điều trị viêm gan B",
        "điều trị viêm phổi",
        "cách chữa đau dạ dày",
        # ========== TREATMENT (Hard - General/Broad) ==========
        "điều trị bệnh mãn tính ở người già",
        "thuốc gì tốt cho tim mạch",
        "cách chữa bệnh tự miễn",
        # ========== MEDICATION (Easy - Specific Drug) ==========
        "paracetamol có tác dụng phụ gì",
        "liều dùng aspirin",
        "metformin dùng như thế nào",
        "amoxicillin uống bao lâu",
        # ========== MEDICATION (Hard - Generic/Class) ==========
        "tác dụng phụ của kháng sinh",
        "thuốc hạ đường huyết nào tốt nhất",
        "thuốc giảm đau an toàn cho bà bầu",
        # ========== DIET & LIFESTYLE (Medium) ==========
        "chế độ ăn cho người suy thận",
        "phòng ngừa đột quỵ",
        "ăn gì tốt cho gan",
        "tập thể dục cho người tiểu đường",
        # ========== DIAGNOSIS & TESTS (Easy) ==========
        "xét nghiệm gì để biết bị tiểu đường",
        "chỉ số đường huyết bao nhiêu là cao",
        "xét nghiệm máu cần lưu ý gì",
        "siêu âm tim phát hiện được gì",
        # ========== COMPLICATIONS (Medium-Hard) ==========
        "biến chứng của tiểu đường",
        "suy thận giai đoạn cuối sống được bao lâu",
        "tai biến mạch máu não nguy hiểm thế nào",
    ]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate ground truth for RAG evaluation"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="hybrid",
        choices=["manual", "auto", "hybrid"],
        help="Labeling mode: manual (you judge), auto (LLM judges), hybrid (both)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=20,
        help="Number of documents to retrieve per query",
    )
    parser.add_argument(
        "--output", type=str, default="test_dataset.json", help="Output file name"
    )
    parser.add_argument(
        "--queries-file",
        type=str,
        default=None,
        help="JSON file with custom queries (optional)",
    )

    args = parser.parse_args()

    # Initialize RAG components
    logger.info("Initializing RAG components...")

    embedding = Embedding(
        model_name="BAAI/bge-m3",
        index_name=os.getenv("PINECONE_INDEX_NAME"),
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
    )
    vectorstore = embedding.load_embedding()

    corpus_path = os.getenv("CORPUS_PATH")
    _, splits = load_corpus(corpus_path)

    search_engine = Searching(
        k1=10, k2=10, embedding_instance=vectorstore, splits=splits
    )

    # Create generator
    use_llm = args.mode in ["auto", "hybrid"]
    generator = GroundTruthGenerator(search_engine, use_llm_judge=use_llm)

    # Get queries
    if args.queries_file:
        with open(args.queries_file, "r", encoding="utf-8") as f:
            queries = json.load(f)
    else:
        queries = get_sample_queries()

    # Generate dataset
    print(f"\n{'='*80}")
    print(f"🚀 GROUND TRUTH GENERATION")
    print(f"{'='*80}")
    print(f"Mode: {args.mode}")
    print(f"Queries: {len(queries)}")
    print(f"Top-K: {args.top_k}")
    print(f"Output: {args.output}")
    print(f"{'='*80}\n")

    if args.mode == "manual":
        print("⚠️  Manual mode: You will review each document")
        print("   Type 'y' for relevant, 'n' for not relevant, 'skip' to skip\n")
    elif args.mode == "auto":
        print("🤖 Auto mode: LLM will judge all documents")
        print("   You can review the results after generation\n")
    else:
        print("🔀 Hybrid mode: LLM judges first, then you can override")
        print(
            "   Type 'y' to confirm, 'n' to reject, or press Enter to accept LLM judgment\n"
        )

    input("Press Enter to start...")

    # Generate
    dataset = generator.generate_test_dataset(
        queries=queries, output_file=args.output, mode=args.mode, top_k=args.top_k
    )

    print("\n✅ Done! You can now run evaluation with:")
    print(f"   python evaluation/rag_evaluator.py --test-file {args.output}")
