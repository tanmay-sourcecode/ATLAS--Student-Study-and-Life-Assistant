import os
import json
import chromadb
from rag.ingest import DB_DIR, get_chroma_client

def retrieve(query: str, top_k: int = 3) -> str:
    """
    Retrieves the top_k most relevant chunks from ChromaDB for a given query.
    Returns a formatted string containing the text and metadata for citation.
    """
    try:
        if not os.path.exists(DB_DIR):
            return "No documents have been ingested yet. Please ingest some course materials first."
            
        client = get_chroma_client()
        # Retrieve the collection
        collection = client.get_or_create_collection(name="course_materials")
        
        # Check if collection is empty
        if collection.count() == 0:
            return "No documents found in the database. Please ingest some syllabus or lecture files."
            
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        formatted_results = []
        
        if results and 'documents' in results and results['documents']:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            
            for doc, meta in zip(docs, metas):
                source = meta.get("source", "unknown")
                chunk_id = meta.get("chunk_id", 0)
                formatted_results.append({
                    "content": doc,
                    "source": source,
                    "chunk": chunk_id
                })
                
        if not formatted_results:
            return "No relevant information found in the local documents."
            
        return json.dumps(formatted_results, indent=2)
    except Exception as e:
        return f"Error retrieving documents: {str(e)}"
