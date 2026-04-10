from __future__ import annotations

from typing import Any, Callable

from .chunking import compute_similarity
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self.embedder = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self.data = []

    def add_documents(self, docs: list[Document]) -> None:
        for doc in docs:
            vector = self.embedder(doc.content)
            self.data.append((vector, doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        query_vector = self.embedder(query)
        results = []
        for vector, doc in self.data:
            sim = compute_similarity(query_vector, vector)
            results.append({
                "content": doc.content,
                "metadata": doc.metadata,
                "similarity": sim,
                "score": sim
            })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_collection_size(self) -> int:
        return len(self.data)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        query_vector = self.embedder(query)
        filtered_data = self.data
        if metadata_filter:
            filtered_data = [
                (vec, doc) for vec, doc in self.data
                if all(doc.metadata.get(k) == v for k, v in metadata_filter.items())
            ]
            
        results = []
        for vector, doc in filtered_data:
            sim = compute_similarity(query_vector, vector)
            results.append({
                "content": doc.content,
                "metadata": doc.metadata,
                "similarity": sim,
                "score": sim
            })
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def delete_document(self, doc_id: str) -> bool:
        initial_length = len(self.data)
        self.data = [(vec, doc) for vec, doc in self.data if getattr(doc, "id", doc.metadata.get("doc_id")) != doc_id]
        return len(self.data) < initial_length
