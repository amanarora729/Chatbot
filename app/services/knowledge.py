import logging
from typing import List, Dict, Any
import os

from agno.knowledge import Knowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.embedder.google import GeminiEmbedder
from agno.knowledge.document import Document

from app.core.config import settings

logger = logging.getLogger(__name__)

class KnowledgeBaseService:
    def __init__(self):
        # Ensure the vector DB directory exists
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        self.vector_db = LanceDb(
            uri=settings.VECTOR_DB_PATH,
            table_name="website_content",
            search_type=SearchType.hybrid,
            embedder=GeminiEmbedder(api_key=settings.GOOGLE_API_KEY)
        )
        
        self.knowledge_base = Knowledge(
            vector_db=self.vector_db,
        )

    def insert_chunks(self, chunks: List[Dict[str, Any]]):
        """
        Converts raw chunks (dicts) into Agno Documents and inserts them.
        """
        documents = []
        for chunk in chunks:
            doc = Document(
                content=chunk["content"],
                meta_data=chunk["meta_data"]
            )
            documents.append(doc)
            
        if documents:
            try:
                 logger.info(f"Inserting {len(documents)} chunks into Vector DB")
                 
                 # Calculate content_hash (using source URL from metadata or random if missing)
                 source = documents[0].meta_data.get("source", "unknown_source")
                 import hashlib
                 content_hash = hashlib.md5(source.encode()).hexdigest()
                 
                 # Insert directly into vector_db
                 self.vector_db.insert(content_hash=content_hash, documents=documents)
                 logger.info("Insertion successful")
            except Exception as e:
                 logger.error(f"Error inserting documents: {e}")
                 raise e

    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        try:
            results = self.knowledge_base.search(query=query, num_documents=num_results)
            return [
                {
                    "content": res.content,
                    "meta_data": res.meta_data,
                    "score": getattr(res, 'score', 0.0)
                }
                for res in results
            ]
        except Exception as e:
            logger.error(f"Error searching knowledge base: {e}")
            return []
