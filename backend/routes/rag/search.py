import os
from dotenv import load_dotenv
from langchain_community.retrievers import BM25Retriever

load_dotenv()


class Searching:
    """
    Hybrid search combining Pinecone vector search and BM25
    Pure implementation without LangChain EnsembleRetriever
    """

    def __init__(self, k1, k2, embedding_instance, splits):
        """
        Initialize hybrid search

        Args:
            k1: Number of results for vector search
            k2: Number of results for BM25 search
            embedding_instance: Embedding class instance (with similarity_search method)
            splits: Document splits for BM25
        """
        self.k1 = k1
        self.k2 = k2
        self.embedding = embedding_instance

        # BM25 retriever
        print("🔍 Initializing BM25 retriever...")
        self.bm25_retriever = BM25Retriever.from_documents(splits)
        self.bm25_retriever.k = k2
        print(f"✅ BM25 ready with {len(splits)} documents")

    def vector_search(self, query):
        """
        Perform vector semantic search via Pinecone

        Args:
            query: Search query

        Returns:
            List of search results
        """
        print(f"🔍 Vector search for: {query}")
        results = self.embedding.similarity_search(query, k=self.k1)

        # Convert to LangChain Document format for compatibility
        from langchain_core.documents import Document

        docs = []
        for result in results:
            docs.append(
                Document(
                    page_content=result["text"], metadata=result.get("metadata", {})
                )
            )
        return docs

    def bm25_search(self, query):
        """
        Perform BM25 keyword search

        Args:
            query: Search query

        Returns:
            List of documents
        """
        print(f"🔍 BM25 search for: {query}")
        return self.bm25_retriever.invoke(query)

    def hybrid_search(self, query, vector_weight=0.3, bm25_weight=0.7):
        """
        Perform hybrid search (BM25 + Vector)

        Args:
            query: Search query
            vector_weight: Weight for vector search (default: 0.3)
            bm25_weight: Weight for BM25 search (default: 0.7)

        Returns:
            List of documents (merged and deduplicated)
        """
        print(f"🔍 Hybrid search for: {query}")

        # Get results from both methods
        vector_docs = self.vector_search(query)
        bm25_docs = self.bm25_search(query)

        # Simple merge: combine and deduplicate by content
        seen_content = set()
        merged_docs = []

        # Add BM25 results first (higher weight)
        for doc in bm25_docs[
            : int(self.k2 * bm25_weight / (vector_weight + bm25_weight))
        ]:
            content = doc.page_content[:100]  # Use first 100 chars as key
            if content not in seen_content:
                seen_content.add(content)
                merged_docs.append(doc)

        # Add vector results
        for doc in vector_docs[
            : int(self.k1 * vector_weight / (vector_weight + bm25_weight))
        ]:
            content = doc.page_content[:100]
            if content not in seen_content:
                seen_content.add(content)
                merged_docs.append(doc)

        print(f"✅ Found {len(merged_docs)} unique documents")
        return merged_docs

    def get_context(self, docs):
        """
        Extract text content from retrieved documents

        Args:
            docs: List of documents (either LangChain Documents or dicts)

        Returns:
            List of text strings
        """
        context = []
        for doc in docs:
            if hasattr(doc, "page_content"):
                # LangChain Document
                context.append(doc.page_content)
            elif isinstance(doc, dict) and "text" in doc:
                # Dict format from Pinecone
                context.append(doc["text"])
            elif isinstance(doc, str):
                # Plain string
                context.append(doc)
        return context

    def search_with_score(self, query, k=5):
        """
        Perform vector search with relevance scores

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of dicts with scores
        """
        print(f"🔍 Searching with scores for: {query}")
        return self.embedding.similarity_search(query, k=k)
