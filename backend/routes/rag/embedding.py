import os
import argparse
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

import google.generativeai as genai
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_pinecone import PineconeVectorStore

try:
    from utils import load_corpus
except ImportError:
    from .utils import load_corpus
    
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

class Embedding:
    def __init__(self, model_name=None, device="cuda", cache_dir=None,
                 index_name="medical-chatbot", google_api_key=None, pinecone_api_key=None):
        """
        Pinecone-based embedding class
        :param model_name: embedding model name
        :param device: cpu/cuda
        :param cache_dir: cache directory for local models
        :param index_name: Pinecone index name
        :param google_api_key: Google API key
        :param pinecone_api_key: Pinecone API key
        """
        self.model_name = model_name
        self.device = device
        self.cache_dir = cache_dir
        self.index_name = index_name
        self.pinecone_api_key = pinecone_api_key

        # Initialize Pinecone
        if not pinecone_api_key:
            raise ValueError("PINECONE_API_KEY is required!")
        
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        # Initialize embedding model
        if self.model_name == "google" and google_api_key:
            print("Using Google Generative AI Embeddings...")
            self.embed_model = GoogleGenAIEmbeddings(
                model="models/embedding-001",
                google_api_key=google_api_key
            )
        else:
            print(f"Using SentenceTransformer model: {self.model_name}")
            self.embed_model = SentenceTransformerEmbeddings(
                model_name=model_name,
                model_kwargs={'device': device},
                encode_kwargs={'batch_size': 8, "normalize_embeddings": True}
            )

    def create_index(self, dimension=1024, metric="cosine"):
        """
        Create Pinecone index if not exists
        :param dimension: embedding dimension (e.g., 1024 for bge-m3, 1536 for OpenAI)
        :param metric: similarity metric (cosine, euclidean, dotproduct)
        """
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating new Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'  # Adjust based on your region
                )
            )
            print(f" Index '{self.index_name}' created!")
        else:
            print(f"ℹ Index '{self.index_name}' already exists.")

    def create_embedding(self, splits, batch_size=100, namespace=""):
        """
        Create embeddings and upload to Pinecone
        :param splits: list of documents
        :param batch_size: batch size for uploading
        :param namespace: Pinecone namespace (optional)
        """
        print(f" Start embedding {len(splits)} chunks...")

        vectorstore = PineconeVectorStore.from_documents(
            documents=splits,
            embedding=self.embed_model,
            index_name=self.index_name,
            namespace=namespace
        )

        print(f"\n All embeddings completed and uploaded to Pinecone index '{self.index_name}'")
        return vectorstore

    def load_embedding(self, namespace=""):
        """
        Load existing Pinecone vector store
        :param namespace: Pinecone namespace
        """
        print(f" Loading embeddings from Pinecone index '{self.index_name}'...")
        return PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embed_model,
            namespace=namespace
        )

    def add_embedding(self, vectorstore, new_splits):
        """
        Add new documents to existing Pinecone index
        :param vectorstore: existing PineconeVectorStore
        :param new_splits: new documents to add
        """
        print(f" Adding {len(new_splits)} new chunks...")
        vectorstore.add_documents(new_splits)
        print("✅ New embeddings added!")
        return vectorstore

    def similarity_search(self, vectorstore, query, k=5):
        """
        Perform similarity search
        :param vectorstore: PineconeVectorStore instance
        :param query: search query
        :param k: number of results
        """
        print(f"🔎 Searching top-{k} similar docs for query: {query}")
        return vectorstore.similarity_search(query=query, k=k)

    def delete_index(self):
        """Delete Pinecone index"""
        print(f"🗑️ Deleting index '{self.index_name}'...")
        self.pc.delete_index(self.index_name)
        print("✅ Index deleted!")


def parse_args():
    parser = argparse.ArgumentParser(description="Pinecone Embedding")
    parser.add_argument("--model_name", type=str, default="BAAI/bge-m3")
    parser.add_argument("--cache_dir", type=str, default="cache/")
    parser.add_argument("--index_name", type=str, default="medical-chatbot")
    parser.add_argument("--corpus_path", type=str, default="text_corpus")
    parser.add_argument("--dimension", type=int, default=1024, help="Embedding dimension")
    return parser.parse_args()
