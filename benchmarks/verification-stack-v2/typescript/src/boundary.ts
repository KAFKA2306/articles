import { readFileSync } from "node:fs";

export function loadUnknownPayload(path: string): unknown {
  return JSON.parse(readFileSync(path, "utf8"));
}
