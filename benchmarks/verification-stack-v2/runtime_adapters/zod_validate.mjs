import fs from "node:fs";
import { z } from "zod";

const schema = z.object({
  count: z.number().int().positive(),
  label: z.string(),
});

const raw = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const result = schema.safeParse(raw);
if (!result.success) {
  console.error(result.error.issues);
  process.exit(2);
}
