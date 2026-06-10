# curie/types/protein.py
from pydantic import BaseModel
from typing import Optional


class FoldResult(BaseModel):
    """Result from a protein structure prediction (ESMFold, Boltz-2)."""
    job_id: str
    model: str
    pdb: str
    plddt: float
    length: int
    latency_ms: int
    cost_usd: float

    @property
    def confidence(self) -> float:
        """pLDDT confidence score as percentage (0-100)."""
        return self.plddt * 100

    @property
    def is_high_confidence(self) -> bool:
        """True if mean pLDDT > 70 (generally reliable structure)."""
        return self.plddt > 0.7

    def save_pdb(self, path: str) -> None:
        """Save the PDB structure to a file."""
        with open(path, 'w') as f:
            f.write(self.pdb)
        print(f"Structure saved to {path}")


class DesignedSequence(BaseModel):
    """A single sequence designed by ProteinMPNN."""
    sequence: str
    score: float
    recovery: float


class DesignResult(BaseModel):
    """Result from protein sequence design (ProteinMPNN)."""
    job_id: str
    model: str
    sequences: list[DesignedSequence]
    latency_ms: int
    cost_usd: float

    @property
    def best(self) -> DesignedSequence:
        """Returns the highest-scoring designed sequence."""
        return min(self.sequences, key=lambda s: s.score)

    def save_fasta(self, path: str) -> None:
        """Save all designed sequences to a FASTA file."""
        with open(path, 'w') as f:
            for i, seq in enumerate(self.sequences):
                f.write(f">designed_sequence_{i+1} score={seq.score:.4f} recovery={seq.recovery:.4f}\n")
                f.write(f"{seq.sequence}\n")
        print(f"{len(self.sequences)} sequences saved to {path}")
