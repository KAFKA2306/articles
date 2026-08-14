import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const cwd = process.cwd();
const root = path.resolve(cwd, "../..");
const manifest = JSON.parse(fs.readFileSync(path.join(cwd, "package.json"), "utf8"));

function sha256(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function packageLocations() {
  const roots = ["apps", "packages"];
  const map = new Map();
  for (const group of roots) {
    const groupPath = path.join(root, group);
    for (const child of fs.readdirSync(groupPath)) {
      const packagePath = path.join(groupPath, child);
      const packageJson = path.join(packagePath, "package.json");
      if (!fs.existsSync(packageJson)) continue;
      const pkg = JSON.parse(fs.readFileSync(packageJson, "utf8"));
      map.set(pkg.name, packagePath);
    }
  }
  return map;
}

const locations = packageLocations();
const ownSource = fs.readFileSync(path.join(cwd, "src", "value.ts"), "utf8");
const dependencies = Object.keys(manifest.dependencies ?? {}).sort();
const dependencyEvidence = [];

for (const dependency of dependencies) {
  const dependencyRoot = locations.get(dependency);
  if (!dependencyRoot) continue;
  const outputPath = path.join(dependencyRoot, "dist", "out.txt");
  if (!fs.existsSync(outputPath)) {
    throw new Error(`dependency output missing for ${dependency}: ${outputPath}`);
  }
  const output = fs.readFileSync(outputPath, "utf8");
  dependencyEvidence.push(`${dependency}:${sha256(output)}`);
}

const content = [
  `package=${manifest.name}`,
  `source_sha256=${sha256(ownSource)}`,
  ...dependencyEvidence,
  "",
].join("\n");

fs.mkdirSync(path.join(cwd, "dist"), { recursive: true });
fs.writeFileSync(path.join(cwd, "dist", "out.txt"), content, "utf8");
console.log(`EXECUTED ${manifest.name} ${sha256(content)}`);
