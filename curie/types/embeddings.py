# curie/types/embeddings.py
from pydantic import BaseModel
from typing import Optional


class EmbeddingResult(BaseModel):
    """Result from a protein embedding model (ESM-2)."""
    job_id: str
    model: str
    embedding: list[float]
    per_residue: Optional[list[list[float]]] = None
    length: int
    latency_ms: int
    cost_usd: float

    @property
    def dim(self) -> int:
        """Embedding dimensionality."""
        return len(self.embedding)

    def to_numpy(self):
        """Convert embedding to numpy array. Requires numpy."""
        try:
            import numpy as np
            return np.array(self.embedding)
        except ImportError:
            raise ImportError("numpy is required for to_numpy(). Install with: pip install numpy")

    def to_tensor(self):
        """Convert embedding to PyTorch tensor. Requires torch."""
        try:
            import torch
            return torch.tensor(self.embedding)
        except ImportError:
            raise ImportError("torch is required for to_tensor(). Install with: pip install torch")
