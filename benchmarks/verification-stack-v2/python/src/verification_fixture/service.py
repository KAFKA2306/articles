from __future__ import annotations


async def fetch_count() -> int:
    return 1


def calculate_total(amount: float, rate: float) -> float:
    return amount * (1.0 + rate)


def render_total(total: float) -> str:
    return f"{total:.2f}"


def increment(count: int) -> int:
    return count + 1


async def next_count() -> int:
    count = await fetch_count()
    return count + 1


EXAMPLE_TOTAL = calculate_total(100.0, 0.2)
