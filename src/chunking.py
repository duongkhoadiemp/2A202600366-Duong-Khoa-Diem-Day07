from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        chunks = []
        for i in range(0, len(sentences), self.max_sentences_per_chunk):
            chunk = " ".join(sentences[i:i + self.max_sentences_per_chunk])
            chunks.append(chunk)
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        return self._split(text, self.separators)

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        if len(current_text) <= self.chunk_size:
            return [current_text]
        
        if not remaining_separators:
            return [current_text[i:i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]
        
        separator = remaining_separators[0]
        next_separators = remaining_separators[1:]
        
        if separator == "":
            return [current_text[i:i + self.chunk_size] for i in range(0, len(current_text), self.chunk_size)]
            
        splits = current_text.split(separator)
        chunks = []
        current_chunk = ""
        
        for idx, s in enumerate(splits):
            part = s + (separator if idx < len(splits) - 1 else "")
            
            if len(part) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                chunks.extend(self._split(part, next_separators))
            elif len(current_chunk) + len(part) <= self.chunk_size:
                current_chunk += part
            else:
                chunks.append(current_chunk)
                current_chunk = part
                
        if current_chunk:
            chunks.append(current_chunk)
            
        return [c.strip() for c in chunks if c.strip()]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b:
        return 0.0
        
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
        
    return dot_product / (mag_a * mag_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        results = {}
        
        fixed_chunks = FixedSizeChunker(chunk_size=chunk_size).chunk(text)
        results['fixed_size'] = {
            'count': len(fixed_chunks),
            'avg_length': sum(len(c) for c in fixed_chunks) / len(fixed_chunks) if fixed_chunks else 0,
            'chunks': fixed_chunks
        }
        
        sentence_chunks = SentenceChunker().chunk(text)
        results['by_sentences'] = {
            'count': len(sentence_chunks),
            'avg_length': sum(len(c) for c in sentence_chunks) / len(sentence_chunks) if sentence_chunks else 0,
            'chunks': sentence_chunks
        }
        
        recursive_chunks = RecursiveChunker(chunk_size=chunk_size).chunk(text)
        results['recursive'] = {
            'count': len(recursive_chunks),
            'avg_length': sum(len(c) for c in recursive_chunks) / len(recursive_chunks) if recursive_chunks else 0,
            'chunks': recursive_chunks
        }
        
        return results
