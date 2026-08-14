export async function fetchCount(): Promise<number> {
  return 1;
}

export function calculateTotal(amount: number, rate: number): number {
  return amount * (1 + rate);
}

export function renderTotal(total: number): string {
  return total.toFixed(2);
}

export function increment(count: number): number {
  return count + 1;
}

export async function nextCount(): Promise<number> {
  const count = await fetchCount();
  return count + 1;
}

export const exampleTotal = calculateTotal(100, 0.2);
