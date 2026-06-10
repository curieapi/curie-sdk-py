# curie/types/__init__.py
from .protein import FoldResult, DesignResult, DesignedSequence
from .embeddings import EmbeddingResult

__all__ = [
    "FoldResult",
    "DesignResult",
    "DesignedSequence",
    "EmbeddingResult",
]
