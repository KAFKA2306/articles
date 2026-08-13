const PYODIDE_VERSION = "v314.0.2";
const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/`;

let pyodidePromise = null;

async function getPyodide(packages = []) {
  if (!pyodidePromise) {
    pyodidePromise = import(`${PYODIDE_BASE}pyodide.mjs`).then(({ loadPyodide }) =>
      loadPyodide({ indexURL: PYODIDE_BASE }),
    );
  }
  const pyodide = await pyodidePromise;
  if (packages.length) {
    await pyodide.loadPackage(packages);
  }
  return pyodide;
}

self.addEventListener("message", async (event) => {
  const { id, action, source, input, packages = [] } = event.data ?? {};
  if (action !== "run") return;
  try {
    const pyodide = await getPyodide(packages);
    pyodide.globals.set("DEMO_INPUT", input ?? "");
    const result = await pyodide.runPythonAsync(source);
    self.postMessage({ id, ok: true, result: String(result ?? "") });
  } catch (error) {
    self.postMessage({ id, ok: false, error: String(error?.message ?? error) });
  }
});
