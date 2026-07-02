import os
import chromadb
from chromadb.config import Settings
from tools import read_document_content

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_data", "chroma")

def get_chroma_client():
    if not os.path.exists(os.path.dirname(DB_DIR)):
        os.makedirs(os.path.dirname(DB_DIR))
    return chromadb.PersistentClient(path=DB_DIR)

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
    """Chunks text into sections, prioritizing paragraph breaks."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        para_len = len(para)
        
        # If a single paragraph is too large, split it by sentences
        if para_len > chunk_size:
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                if current_length + len(sentence) > chunk_size:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [sentence]
                    current_length = len(sentence)
                else:
                    current_chunk.append(sentence)
                    current_length += len(sentence)
        else:
            if current_length + para_len > chunk_size:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_length = para_len
            else:
                current_chunk.append(para)
                current_length += para_len
                
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks

import re

def ingest(file_path: str) -> str:
    """Ingests a document into the ChromaDB vector database."""
    try:
        content = read_document_content(file_path)
        if content.startswith("Error:"):
            return content
            
        chunks = chunk_text(content)
        if not chunks:
            return f"No readable content found in {file_path} to ingest."
            
        client = get_chroma_client()
        # Default collection creation
        collection = client.get_or_create_collection(name="course_materials")
        
        documents = []
        metadatas = []
        ids = []
        
        base_name = os.path.basename(file_path)
        
        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "source": base_name,
                "chunk_id": idx,
                "length": len(chunk)
            })
            ids.append(f"{base_name}_chunk_{idx}")
            
        # Add to collection
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return f"Successfully ingested '{base_name}' into vector store. {len(chunks)} chunks created."
    except Exception as e:
        return f"Error during document ingestion: {str(e)}"
