#!/usr/bin/env python3
"""Curie SDK Async Example - Fold multiple proteins concurrently"""

import asyncio
import curie

SEQUENCES = [
    "MKTIIALSYIFCLVFA",
    "GSHMKPVAATVPLVPQQ",
    "LTEEQIAEFKEAFSLFD",
]


async def fold_all():
    """Fold multiple sequences concurrently."""
    async with curie.Client() as client:
        # Launch all fold operations concurrently
        tasks = [client.afold(seq) for seq in SEQUENCES]
        results = await asyncio.gather(*tasks)

        print(f"Folded {len(results)} proteins:\n")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result.length}aa → {result.confidence:.1f}% confidence ({result.latency_ms}ms)")

        total_latency = sum(r.latency_ms for r in results)
        print(f"\nTotal latency: {total_latency}ms (would be {sum(r.latency_ms for r in results)}ms serial)")


if __name__ == "__main__":
    asyncio.run(fold_all())
