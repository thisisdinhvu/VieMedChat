import os
import time
import argparse
from tqdm import tqdm
from typing import List, Dict, Any
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

import google.generativeai as genai
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.embeddings.base import Embeddings

try:
    from utils import load_corpus
except ImportError:
    try:
        from .utils import load_corpus
    except ImportError:
        print("⚠️ Warning: load_corpus not available")
        load_corpus = None

load_dotenv()


# ==========================================
# ✅ Custom Google Embeddings Class
# ==========================================
class GoogleGenAIEmbeddings(Embeddings):
    """
    Custom wrapper for Google Generative AI Embeddings
    Supports multilingual embedding with task-specific optimization
    """
    
    def __init__(self, api_key: str, model: str = "models/text-multilingual-embedding-002"):
        """
        Initialize Google GenAI Embeddings
        
        Args:
            api_key: Google API key
            model: Embedding model name (default: text-multilingual-embedding-002)
        """
        genai.configure(api_key=api_key)
        self.model = model
        print(f"✅ Initialized Google GenAI Embeddings with model: {model}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed search documents
        
        Args:
            texts: List of documents to embed
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            try:
                result = genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result["embedding"])
            except Exception as e:
                print(f"⚠️ Error embedding document: {str(e)[:100]}")
                embeddings.append([0.0] * 768)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed query text
        
        Args:
            text: Query text to embed
        
        Returns:
            Embedding vector
        """
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_query"
            )
            return result["embedding"]
        except Exception as e:
            print(f"⚠️ Error embedding query: {str(e)}")
            return [0.0] * 768


# ==========================================
# 🎯 Embedding Dimension Mapping
# ==========================================
def get_embedding_dimension(model_name):
    """
    Get embedding dimension based on model name
    
    Args:
        model_name: Name of embedding model
    
    Returns:
        int: Embedding dimension
    """
    dimensions = {
        "google": 768,
        "openai": 3072,
        "BAAI/bge-m3": 1024,
        "bkai-foundation-models/vietnamese-bi-encoder": 768,
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 384,
    }
    return dimensions.get(model_name, 768)


# ==========================================
# 📦 Main Embedding Class (Pure Pinecone API)
# ==========================================
class Embedding:
    """
    Unified embedding class using ONLY Pinecone API (no LangChain dependencies)
    
    Supports:
    - Google Generative AI Embeddings
    - SentenceTransformers (HuggingFace models)
    - Direct Pinecone API for all operations
    """
    
    def __init__(self, model_name=None, device="cpu", cache_dir=None,
                 index_name="medical-chatbot", google_api_key=None, pinecone_api_key=None):
        """
        Initialize embedding model and Pinecone
        
        Args:
            model_name: Embedding model name ("google" or HuggingFace model)
            device: "cpu" or "cuda"
            cache_dir: Cache directory for local models
            index_name: Pinecone index name
            google_api_key: Google API key (if model_name="google")
            pinecone_api_key: Pinecone API key (required)
        """
        self.model_name = model_name or "BAAI/bge-m3"
        self.device = device
        self.cache_dir = cache_dir
        self.index_name = index_name
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")

        # Validate pipecone API key
        if not self.pinecone_api_key:
            raise ValueError("❌ PINECONE_API_KEY is required!")
        
        # Initialize pipecone
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.index = None
        
        # Initialize embedding model
        self._initialize_embedding_model()
        
        print(f"✅ Embedding class initialized")
        print(f"   Model: {self.model_name}")
        print(f"   Index: {self.index_name}")
        print(f"   Device: {self.device}")
    
    def _initialize_embedding_model(self):
        """Initialize embedding model based on model_name"""
        if self.model_name == "google":
            if not self.google_api_key:
                raise ValueError("❌ GOOGLE_API_KEY is required for model='google'!")
            
            print("🔹 Using Google Generative AI Embeddings...")
            self.embed_model = GoogleGenAIEmbeddings(
                api_key=self.google_api_key,
                model="models/text-multilingual-embedding-002"
            )
        else:
            print(f"🔹 Using SentenceTransformer model: {self.model_name}")
            self.embed_model = SentenceTransformerEmbeddings(
                model_name=self.model_name,
                model_kwargs={'device': self.device},
                cache_folder=self.cache_dir,
                encode_kwargs={'batch_size': 32, "normalize_embeddings": True}
            )
    
    def create_index(self, dimension=None, metric="cosine"):
        """
        Create Pinecone index if not exists
        
        Args:
            dimension: Embedding dimension (auto-detected if None)
            metric: Similarity metric (cosine, euclidean, dotproduct)
        """
        if dimension is None:
            dimension = get_embedding_dimension(self.model_name)
        
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"📦 Creating new Pinecone index: {self.index_name}")
            print(f"📊 Dimension: {dimension}, Metric: {metric}")
            
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            print("⏳ Waiting for index to be ready...")
            time.sleep(10)
            print(f"✅ Index '{self.index_name}' created!")
        else:
            print(f"ℹ️ Index '{self.index_name}' already exists.")
        
        self.index = self.pc.Index(self.index_name)
        return self

    def create_embedding(self, splits, batch_size=100, namespace=""):
        """
        Create embeddings and upload to Pinecone using direct API
        
        Args:
            splits: List of documents
            batch_size: Batch size for uploading
            namespace: Pinecone namespace (optional)
        
        Returns:
            self (for chaining)
        """
        if not self.index:
            self.index = self.pc.Index(self.index_name)
        
        print(f"\n{'='*60}")
        print(f"🔄 Starting embedding process...")
        print(f"📊 Total chunks: {len(splits)}")
        print(f"📦 Batch size: {batch_size}")
        print(f"{'='*60}\n")
        
        total_batches = (len(splits) + batch_size - 1) // batch_size
        successful_batches = 0
        failed_batches = 0
        
        for i in tqdm(range(0, len(splits), batch_size), 
                      desc="🚀 Uploading to Pinecone",
                      total=total_batches,
                      unit="batch"):
            batch = splits[i:i+batch_size]
            
            try:
                texts = [doc.page_content for doc in batch]
                metadatas = [doc.metadata for doc in batch]
                
                # Embed documents
                embeddings = self.embed_model.embed_documents(texts)
                
                # Create vectors
                vectors = []
                for j, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
                    vector_id = f"doc_{i+j}"
                    vectors.append({
                        "id": vector_id,
                        "values": embedding,
                        "metadata": {
                            "text": text[:1000],
                            **metadata
                        }
                    })
                
                # Upload to Pinecone
                if namespace:
                    self.index.upsert(vectors=vectors, namespace=namespace)
                else:
                    self.index.upsert(vectors=vectors)
                
                successful_batches += 1
                time.sleep(0.5)
                
            except Exception as e:
                failed_batches += 1
                print(f"\n❌ Error at batch {i//batch_size + 1}: {str(e)[:200]}")
                print("⏭️  Skipping and continuing...")
                time.sleep(2)
        
        stats = self.index.describe_index_stats()
        print(f"\n{'='*60}")
        print(f"✅ Upload completed!")
        print(f"📊 Successful: {successful_batches}/{total_batches}")
        print(f"❌ Failed: {failed_batches}/{total_batches}")
        print(f"📊 Total vectors: {stats['total_vector_count']}")
        print(f"{'='*60}\n")
        
        return self
    
    def load_embedding(self):
        """
        Load existing Pinecone index (for querying existing data)
        
        Returns:
            self (for chaining)
        """
        if not self.index:
            print(f"📦 Connecting to existing Pinecone index: {self.index_name}")
            self.index = self.pc.Index(self.index_name)
            
            # Verify index exists and get stats
            try:
                stats = self.index.describe_index_stats()
                print(f"✅ Index connected!")
                print(f"   Total vectors: {stats['total_vector_count']}")
                print(f"   Dimension: {stats.get('dimension', 'unknown')}")
            except Exception as e:
                print(f"⚠️ Warning: Could not get index stats: {e}")
        
        return self

    def similarity_search(self, query, k=5, namespace="") -> List[Dict[str, Any]]:
        """
        Perform similarity search using direct Pinecone API
        
        Args:
            query: Search query
            k: Number of results
            namespace: Pinecone namespace
        
        Returns:
            List of dicts with 'text', 'score', 'metadata'
        """
        if not self.index:
            self.index = self.pc.Index(self.index_name)
        
        print(f"🔎 Searching top-{k} docs for: '{query[:50]}...'")
        
        # Embed query
        query_embedding = self.embed_model.embed_query(query)
        
        # Search params
        search_params = {
            "vector": query_embedding,
            "top_k": k,
            "include_metadata": True
        }
        if namespace:
            search_params["namespace"] = namespace
        
        results = self.index.query(**search_params)
        
        # Format results
        docs = []
        for match in results['matches']:
            docs.append({
                'text': match['metadata'].get('text', ''),
                'score': match['score'],
                'metadata': match['metadata'],
                'id': match['id']
            })
        
        return docs

    def similarity_search_with_score(self, query, k=5, namespace=""):
        """Alias for similarity_search (returns same format)"""
        return self.similarity_search(query, k, namespace)

    def add_documents(self, new_splits, namespace=""):
        """
        Add new documents to existing index
        
        Args:
            new_splits: New documents to add
            namespace: Pinecone namespace
        """
        print(f"➕ Adding {len(new_splits)} new documents...")
        return self.create_embedding(new_splits, namespace=namespace)

    def delete_index(self):
        """Delete Pinecone index"""
        print(f"🗑️ Deleting index '{self.index_name}'...")
        self.pc.delete_index(self.index_name)
        print("✅ Index deleted!")
    
    def get_stats(self):
        """Get index statistics"""
        if not self.index:
            self.index = self.pc.Index(self.index_name)
        return self.index.describe_index_stats()


# ==========================================
# 🧪 CLI Interface
# ==========================================
def parse_args():
    parser = argparse.ArgumentParser(description="Pinecone Embedding Manager")
    parser.add_argument("--model_name", type=str, default="BAAI/bge-m3")
    parser.add_argument("--cache_dir", type=str, default="cache/")
    parser.add_argument("--index_name", type=str, default="medical-chatbot")
    parser.add_argument("--corpus_path", type=str, default="text_corpus")
    parser.add_argument("--dimension", type=int, default=None)
    parser.add_argument("--action", type=str, default="create",
                       choices=["create", "search", "stats", "delete"])
    parser.add_argument("--query", type=str, default="")
    return parser.parse_args()
