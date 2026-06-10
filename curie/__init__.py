# curie/__init__.py
"""Curie Python SDK

Inference infrastructure for scientific AI.

Run biology, chemistry, and physics AI models through one unified API.

Quick start:
    import curie

    client = curie.Client(api_key="sk-...")

    # Predict protein structure
    result = client.fold("MKTIIALSYIFCLVFA...")
    print(f"Confidence: {result.confidence:.1f}%")
    result.save_pdb("my_protein.pdb")

    # Generate embeddings
    embedding = client.embed("MKTIIALSYIFCLVFA...")
    vector = embedding.to_numpy()

    # Design sequences for a backbone
    design = client.design(result.pdb, num_sequences=3)
    print(design.best.sequence)

Docs: https://curie.sh/dashboard/docs
"""

from .client import Curie, Client
from .exceptions import (
    CurieError,
    AuthenticationError,
    ModelNotFoundError,
    InferenceError,
    RateLimitError,
    ValidationError,
    TimeoutError,
)
from .types import FoldResult, DesignResult, DesignedSequence, EmbeddingResult

__version__ = "0.1.0"
__all__ = [
    "Curie",
    "Client",
    "CurieError",
    "AuthenticationError",
    "ModelNotFoundError",
    "InferenceError",
    "RateLimitError",
    "ValidationError",
    "TimeoutError",
    "FoldResult",
    "DesignResult",
    "DesignedSequence",
    "EmbeddingResult",
]
