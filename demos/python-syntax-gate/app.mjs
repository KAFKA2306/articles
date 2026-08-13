const runButton = document.querySelector("#run");
const sourceInput = document.querySelector("#source");
const resultOutput = document.querySelector("#result");
const fixtureSelect = document.querySelector("#fixture");

let manifest = null;
let pythonSource = null;
let worker = null;
let requestId = 0;
const pending = new Map();

async function loadManifest() {
  manifest = await fetch("./demo.json", { cache: "no-store" }).then((response) => {
    if (!response.ok) throw new Error(`manifest HTTP ${response.status}`);
    return response.json();
  });
  pythonSource = await fetch(manifest.python, { cache: "no-store" }).then((response) => {
    if (!response.ok) throw new Error(`python HTTP ${response.status}`);
    return response.text();
  });
  sourceInput.value = manifest.inputs.broken;
}

function getWorker() {
  if (worker) return worker;
  worker = new Worker("../_shared/pyodide-worker.mjs", { type: "module" });
  worker.addEventListener("message", (event) => {
    const resolver = pending.get(event.data?.id);
    if (!resolver) return;
    pending.delete(event.data.id);
    resolver(event.data);
  });
  return worker;
}

function runPython(input) {
  const id = ++requestId;
  const target = getWorker();
  return new Promise((resolve) => {
    pending.set(id, resolve);
    target.postMessage({
      id,
      action: "run",
      source: pythonSource,
      input,
      packages: manifest.packages,
    });
  });
}

fixtureSelect.addEventListener("change", () => {
  sourceInput.value = manifest.inputs[fixtureSelect.value];
});

runButton.addEventListener("click", async () => {
  runButton.disabled = true;
  resultOutput.textContent = "Pythonを読み込んで実行しています…";
  try {
    const response = await runPython(sourceInput.value);
    resultOutput.textContent = response.ok ? response.result : `ERROR: ${response.error}`;
  } catch (error) {
    resultOutput.textContent = `ERROR: ${error.message}`;
  } finally {
    runButton.disabled = false;
  }
});

loadManifest().catch((error) => {
  runButton.disabled = true;
  resultOutput.textContent = `Demo unavailable: ${error.message}`;
});
