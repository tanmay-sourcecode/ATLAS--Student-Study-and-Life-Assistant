import os
import pytest
from rag.ingest import chunk_text

def test_text_chunking():
    """Verifies that the text chunker splits paragraph text correctly based on size."""
    sample_text = (
        "This is paragraph one. It contains some basic introductory statements about functional systems.\n\n"
        "This is paragraph two. It deals with tail recursion optimization and how the compiler handles calls.\n\n"
        "This is paragraph three. It talks about mutable vs immutable structures in modern compiler environments."
    )
    
    # Chunk with small size to trigger split
    chunks = chunk_text(sample_text, chunk_size=120)
    assert len(chunks) >= 2
    assert any("paragraph one" in chunk for chunk in chunks)
    assert any("paragraph two" in chunk for chunk in chunks)
    assert any("paragraph three" in chunk for chunk in chunks)
