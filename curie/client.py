# curie/client.py
import os
from typing import Optional, Union
from ._http import HttpClient
from .exceptions import AuthenticationError
from .types import FoldResult, DesignResult, EmbeddingResult

DEFAULT_BASE_URL = "https://api.curie.sh"
DEFAULT_TIMEOUT = 120
DEFAULT_MAX_RETRIES = 2


class Curie:
    """
    The official Curie Python client.

    Usage:
        import curie

        client = curie.Client(api_key="sk-...")

        # Fold a protein
        result = client.fold("MKTIIALSYIFCLVFA...")
        print(result.pdb)

        # Or use the generic run method
        result = client.run("esm/esmfold-v1", sequence="MKTIIALSYIFCLVFA...")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        resolved_key = api_key or os.environ.get("CURIE_API_KEY")
        if not resolved_key:
            raise AuthenticationError(
                "No API key provided. Pass api_key='sk-...' or set the "
                "CURIE_API_KEY environment variable."
            )

        self._http = HttpClient(
            api_key=resolved_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

    # ── High-level methods ────────────────────────────────────────────

    def fold(
        self,
        sequence: str,
        model: str = "esm/esmfold-v1",
    ) -> FoldResult:
        """
        Predict the 3D structure of a protein sequence.

        Args:
            sequence: Amino acid sequence (single-letter codes, e.g. "MKTII...")
            model: Model to use. Default: "esm/esmfold-v1"

        Returns:
            FoldResult with .pdb, .plddt, .confidence, .is_high_confidence

        Example:
            result = client.fold("MKTIIALSYIFCLVFA...")
            result.save_pdb("my_protein.pdb")
            print(f"Confidence: {result.confidence:.1f}%")
        """
        data = self._http.post("/v1/run", {"model": model, "sequence": sequence})
        return FoldResult(**data)

    async def afold(
        self,
        sequence: str,
        model: str = "esm/esmfold-v1",
    ) -> FoldResult:
        """Async version of fold()."""
        data = await self._http.apost("/v1/run", {"model": model, "sequence": sequence})
        return FoldResult(**data)

    def embed(
        self,
        sequence: str,
        model: str = "meta/esm2-650m",
        return_per_residue: bool = False,
    ) -> EmbeddingResult:
        """
        Generate protein language model embeddings.

        Args:
            sequence: Amino acid sequence
            model: Embedding model. Default: "meta/esm2-650m"
            return_per_residue: If True, return per-residue embeddings

        Returns:
            EmbeddingResult with .embedding (1280-dim), .dim, .to_numpy(), .to_tensor()

        Example:
            result = client.embed("MKTIIALSYIFCLVFA...")
            vector = result.to_numpy()  # shape: (1280,)
        """
        data = self._http.post("/v1/run", {
            "model": model,
            "sequence": sequence,
            "return_per_residue": str(return_per_residue).lower(),
        })
        return EmbeddingResult(**data)

    async def aembed(
        self,
        sequence: str,
        model: str = "meta/esm2-650m",
        return_per_residue: bool = False,
    ) -> EmbeddingResult:
        """Async version of embed()."""
        data = await self._http.apost("/v1/run", {
            "model": model,
            "sequence": sequence,
            "return_per_residue": str(return_per_residue).lower(),
        })
        return EmbeddingResult(**data)

    def design(
        self,
        pdb: str,
        num_sequences: int = 1,
        temperature: float = 0.1,
        model: str = "bakerlab/proteinmpnn",
    ) -> DesignResult:
        """
        Design protein sequences for a given backbone structure.

        Args:
            pdb: PDB file content as string (from fold() result)
            num_sequences: Number of sequences to generate (1-10)
            temperature: Sampling temperature (0.1 = conservative, 1.0 = diverse)
            model: Design model. Default: "bakerlab/proteinmpnn"

        Returns:
            DesignResult with .sequences, .best (highest scoring sequence)

        Example:
            # First fold a protein
            fold_result = client.fold("MKTIIALSYIFCLVFA...")
            # Then design sequences for that backbone
            design_result = client.design(fold_result.pdb, num_sequences=5)
            print(design_result.best.sequence)
        """
        data = self._http.post("/v1/run", {
            "model": model,
            "pdb": pdb,
            "num_sequences": str(num_sequences),
            "temperature": str(temperature),
        })
        return DesignResult(**data)

    async def adesign(
        self,
        pdb: str,
        num_sequences: int = 1,
        temperature: float = 0.1,
        model: str = "bakerlab/proteinmpnn",
    ) -> DesignResult:
        """Async version of design()."""
        data = await self._http.apost("/v1/run", {
            "model": model,
            "pdb": pdb,
            "num_sequences": str(num_sequences),
            "temperature": str(temperature),
        })
        return DesignResult(**data)

    # ── Generic run method ────────────────────────────────────────────

    def run(self, model: str, **kwargs) -> dict:
        """
        Generic method to run any Curie model.

        Args:
            model: Model slug (e.g. "esm/esmfold-v1")
            **kwargs: Model-specific parameters

        Returns:
            Raw dict response from the API

        Example:
            result = client.run("esm/esmfold-v1", sequence="MKTII...", return_per_residue="false")
        """
        return self._http.post("/v1/run", {"model": model, **kwargs})

    async def arun(self, model: str, **kwargs) -> dict:
        """Async version of run()."""
        return await self._http.apost("/v1/run", {"model": model, **kwargs})

    def models(self) -> list[dict]:
        """List all available models."""
        import httpx
        response = httpx.get(
            f"{self._http.base_url}/v1/run",
            headers={"Authorization": f"Bearer {self._http.api_key}"},
        )
        data = response.json()
        return data.get("models", [])

    # ── Context manager support ───────────────────────────────────────

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._http.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._http.aclose()


# Convenience alias
Client = Curie
