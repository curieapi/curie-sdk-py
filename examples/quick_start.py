#!/usr/bin/env python3
"""Curie SDK Quick Start Example"""

import curie

# Initialize the client (reads CURIE_API_KEY from env)
client = curie.Client()

# Example 1: Fold a protein
print("Example 1: Folding a protein...")
result = client.fold("MKTIIALSYIFCLVFADYKDDDDK")
print(f"  Model: {result.model}")
print(f"  Length: {result.length} amino acids")
print(f"  Confidence: {result.confidence:.1f}%")
print(f"  Latency: {result.latency_ms}ms")
print(f"  Cost: ${result.cost_usd}")

# Save the structure
result.save_pdb("/tmp/my_protein.pdb")
print(f"  Saved to /tmp/my_protein.pdb\n")

# Example 2: Check if structure is high confidence
if result.is_high_confidence:
    print("✓ High confidence structure (pLDDT > 70%)\n")
else:
    print("⚠ Low confidence structure (pLDDT < 70%)\n")

# Example 3: Using context manager (auto-closes connection)
print("Example 3: Using context manager...")
with curie.Client() as client:
    result = client.fold("MKTIIALSYIFCLVFA")
    print(f"  Folded {result.length}aa protein in {result.latency_ms}ms\n")

print("✓ All examples completed!")
