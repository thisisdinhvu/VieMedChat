import os
from dotenv import load_dotenv
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

load_dotenv(".env")

class Searching:
    def __init__(self, k1, k2, vectorstore, splits):
        """
        Hybrid search with Pinecone vector store and BM25
        :param k1: number of results for vector search
        :param k2: number of results for BM25 search
        :param vectorstore: PineconeVectorStore instance
        :param splits: document splits for BM25
        """
        self.k1 = k1
        self.k2 = k2
        
        # self.vectorstore = vectorstore
        
        # Pinecone retriever
        self.retriever = vectorstore.as_retriever(search_kwargs={"k": k1})
        
        # BM25 retriever
        self.bm25_retriever = BM25Retriever.from_documents(splits)
        self.bm25_retriever.k = k2
        
        # Ensemble retriever (hybrid search)
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.bm25_retriever, self.retriever],
            weights=[0.7, 0.3]  # 70% BM25, 30% vector search
        )

    def hybrid_search(self, query):
        """
        Perform hybrid search (BM25 + Vector)
        """
        print(f"🔍 Hybrid search for: {query}")
        ensemble_docs = self.ensemble_retriever.invoke(query)
        return ensemble_docs

    def bm25_search(self, query):
        """
        Perform BM25 keyword search only
        """
        print(f"🔍 BM25 search for: {query}")
        bm25_docs = self.bm25_retriever.invoke(query)
        return bm25_docs

    def vector_search(self, query):
        """
        Perform vector semantic search only (via Pinecone)
        """
        print(f"🔍 Vector search for: {query}")
        vector_docs = self.retriever.invoke(query)
        return vector_docs

    def get_context(self, docs):
        """
        Extract text content from retrieved documents
        """
        context = []
        for doc in docs:
            context.append(doc.page_content)
        return context

    def search_with_score(self, query, k=5):
        """
        Perform similarity search with relevance scores
        """
        print(f"🔍 Searching with scores for: {query}")
        
        try:
            # Method 1: Dùng similarity_search_with_score (nếu có)
            results = self.retriever.vectorstore.similarity_search_with_score(query, k=k)
            return results
        except AttributeError:
            # Method 2: Fallback nếu không có method trên
            print("⚠️ similarity_search_with_score not available, using similarity_search")
            docs = self.retriever.vectorstore.similarity_search(query, k=k)
            # Return docs without scores
            return [(doc, None) for doc in docs]


# Example usage
if __name__ == "__main__":
    from embedding import Embedding
    from utils import load_corpus

    # Load corpus
    _, splits = load_corpus("backend/database/text_corpus")

    # Initialize Pinecone embedding
    embedding = Embedding(
        model_name="BAAI/bge-m3",
        index_name='vie-med-chat',
        pinecone_api_key=os.getenv("PINECONE_API_KEY")
    )

    # Load existing vector store
    vectorstore = embedding.load_embedding()

    # Initialize search
    search = Searching(k1=5, k2=5, vectorstore=vectorstore, splits=splits)

    # Test query
    query = "Tôi bị đau đầu và chóng mặt, có thể là bệnh gì?"
    
    # Hybrid search
    results = search.hybrid_search(query)
    context = search.get_context(results)
    
    print("\n📄 Search Results:")
    for i, ctx in enumerate(context, 1):
        print(f"\n{i}. {ctx[:200]}...")