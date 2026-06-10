# Curie AI

The official Python SDK for [Curie](https://curie.sh) — inference infrastructure for scientific AI.

Run biology, chemistry, and physics AI models through one unified API.

## Installation

```bash
pip install curieai
```

## Quick start

```python
import curie

client = curie.Client(api_key="sk-...")

# Or set CURIE_API_KEY environment variable and omit api_key

# Predict protein structure
result = client.fold("MKTIIALSYIFCLVFA...")
print(f"Confidence: {result.confidence:.1f}%")
result.save_pdb("my_protein.pdb")

# Generate embeddings
embedding = client.embed("MKTIIALSYIFCLVFA...")
vector = embedding.to_numpy()  # numpy array, shape (1280,)

# Design sequences for a backbone
design = client.design(result.pdb, num_sequences=3)
print(design.best.sequence)
```

## Async support

```python
import asyncio
import curie

async def main():
    async with curie.Client(api_key="sk-...") as client:
        result = await client.afold("MKTIIALSYIFCLVFA...")
        print(f"Confidence: {result.confidence:.1f}%")

asyncio.run(main())
```

## Environment variable

```bash
export CURIE_API_KEY="sk-..."
```

```python
import curie
client = curie.Client()  # reads from CURIE_API_KEY automatically
```

## Models

| Model | Method | Slug |
|-------|--------|------|
| ESMFold v1 | `client.fold()` | `esm/esmfold-v1` |
| ESM-2 650M | `client.embed()` | `meta/esm2-650m` |
| ProteinMPNN | `client.design()` | `bakerlab/proteinmpnn` |

## Docs

Full API reference: [curie.sh/dashboard/docs](https://curie.sh/dashboard/docs)
