import argparse
import asyncio
import time
from typing import List

import httpx


def build_job_payload(provider: str, model: str | None, count: int) -> dict:
    return {
        "test_case_id": f"load-{int(time.time() * 1000)}",
        "prompt_template": "Return JSON with key 'message' using input: {{input}}",
        "json_schema": {
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": ["message"],
        },
        "test_inputs": [{"input": f"test-{i}"} for i in range(count)],
        "provider": provider,
        "model": model,
    }


async def worker(
    client: httpx.AsyncClient,
    url: str,
    payload: dict,
    total: int,
    results: List[float],
    sem: asyncio.Semaphore,
) -> None:
    for _ in range(total):
        async with sem:
            start = time.time()
            try:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
            except Exception:
                results.append(-1.0)
                continue
            results.append((time.time() - start) * 1000)


async def run(args: argparse.Namespace) -> None:
    payload = build_job_payload(args.provider, args.model, args.test_inputs)
    total_per_worker = args.requests // args.concurrency
    remainder = args.requests % args.concurrency
    sem = asyncio.Semaphore(args.concurrency)
    results: List[float] = []
    async with httpx.AsyncClient(timeout=args.timeout) as client:
        tasks = []
        for i in range(args.concurrency):
            count = total_per_worker + (1 if i < remainder else 0)
            if count == 0:
                continue
            tasks.append(
                worker(client, args.endpoint, payload, count, results, sem)
            )
        await asyncio.gather(*tasks)

    latencies = [r for r in results if r >= 0]
    failed = len(results) - len(latencies)
    if not latencies:
        print("All requests failed.")
        return
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.5)]
    p95 = latencies[int(len(latencies) * 0.95) - 1]
    avg = sum(latencies) / len(latencies)
    print(f"requests={len(results)} failed={failed}")
    print(f"avg_ms={avg:.2f} p50_ms={p50:.2f} p95_ms={p95:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="http://localhost:8001/api/v1/validate")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--provider", default="openai")
    parser.add_argument("--model", default=None)
    parser.add_argument("--test-inputs", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
