export interface ExternalPayloadShape {
  count: number;
  label: string;
}

export function acceptUnknownPayload(value: unknown): unknown {
  return value;
}
