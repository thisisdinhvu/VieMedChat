import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import BeautifulSoup

load_dotenv()


def load_corpus(corpus_path, chunk_size=800, chunk_overlap=200):
    """
    Load toàn bộ text/HTML từ thư mục corpus_path và chia nhỏ thành chunks.
    """
    text_loader_kwargs = {"autodetect_encoding": True}
    loader = DirectoryLoader(
        corpus_path, loader_cls=TextLoader, loader_kwargs=text_loader_kwargs
    )
    docs = loader.load()

    # Làm sạch HTML tags
    for doc in docs:
        soup = BeautifulSoup(doc.page_content, "html.parser")
        doc.page_content = soup.get_text()

    # Chia nhỏ text thành chunks để đưa vào embedding
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=["\n", "."]
    )
    texts = text_splitter.split_documents(docs)
    return docs, texts


def get_text_from_html_file(html_path):
    """
    Đọc file HTML và lấy plain text.
    """
    with open(html_path, "r", encoding="utf-8") as f:
        html_text = f.read()
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text()


def get_text_chunks(raw_text, chunk_size=1000, chunk_overlap=200):
    """
    Chia nhỏ raw text thành các đoạn nhỏ (chunks).
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = text_splitter.split_text(raw_text)
    return chunks


def preprocess_context(context: list):
    """Làm sạch và chuẩn hóa context."""
    if not context:
        return []

    # Làm sạch context
    cleaned_context = []
    for item in context:
        if isinstance(item, str):
            cleaned_item = item.replace("\n", " ").replace("*", "").strip()
            if cleaned_item:
                cleaned_context.append(cleaned_item)
    return cleaned_context


if __name__ == "__main__":
    # Ví dụ test thử
    corpus_path = "corpus_summarize"
    docs, texts = load_corpus(corpus_path)
    print("Số docs:", len(docs))
    print("Số chunks:", len(texts))
    print("Chunk đầu tiên:\n", texts[0])
