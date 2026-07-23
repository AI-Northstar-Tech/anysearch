#!/usr/bin/env node
/**
 * Predeploy smoke test for the search matrix HTML page.
 * Catches client-script ReferenceErrors (e.g. missing helpers) that break the table.
 */
import vm from "node:vm";
import { register } from "node:module";
import { pathToFileURL } from "node:url";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

register(pathToFileURL(join(__dirname, "matrix_import_hooks.mjs")).href);

const REQUIRED_CLIENT_SYMBOLS = [
  "function faviconSlugForAgent",
  "function renderHeader",
  "function renderBody",
  "function favimg",
  "function showView",
  "function revealCell",
  "renderHeader(); renderBody();",
];

function extractClientScript(html) {
  const blocks = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
  const client = blocks.find(
    (b) => b.includes("renderHeader") && b.includes("JSON.parse")
  );
  if (!client) throw new Error("Could not find matrix client script in rendered HTML");
  return client;
}

function runClientScriptSmoke(clientScript, payload) {
  const headerEl = { innerHTML: "" };
  const bodyEl = { innerHTML: "" };
  const pillEl = { textContent: "", dataset: { updatedAt: new Date().toISOString() } };
  const payloadJson = JSON.stringify(payload);

  const tableWrap = { clientWidth: 1200 };
  const document = {
    cookie: "",
    documentElement: { style: { setProperty() {} } },
    getElementById(id) {
      if (id === "headerRow") return headerEl;
      if (id === "tbody") return bodyEl;
      if (id === "updatedPill") return pillEl;
      if (id === "payload") {
        return { textContent: payloadJson };
      }
      return null;
    },
    querySelector(sel) {
      if (sel === ".table-wrap") return tableWrap;
      return null;
    },
    querySelectorAll() {
      return [];
    },
  };

  const window = {
    innerWidth: 1200,
    addEventListener() {},
    requestAnimationFrame(fn) {
      if (typeof fn === "function") fn();
      return 0;
    },
  };

  const sandbox = {
    document,
    window,
    requestAnimationFrame: window.requestAnimationFrame,
    console,
    setInterval() {},
    clearTimeout() {},
    setTimeout(fn) {
      if (typeof fn === "function") fn();
      return 0;
    },
    Intl: globalThis.Intl,
    Date: globalThis.Date,
    Math: globalThis.Math,
    JSON: globalThis.JSON,
    URL: globalThis.URL,
    encodeURIComponent: globalThis.encodeURIComponent,
  };

  vm.runInNewContext(clientScript, sandbox, { timeout: 10_000 });

  if (!headerEl.innerHTML.trim()) {
    throw new Error("renderHeader() produced empty #headerRow");
  }
  if (!bodyEl.innerHTML.trim()) {
    throw new Error("renderBody() produced empty #tbody");
  }
  if (!headerEl.innerHTML.includes("agent-col")) {
    throw new Error("Header row missing agent columns");
  }
  if (!bodyEl.innerHTML.includes("<tr")) {
    throw new Error("Table body missing rows");
  }
}

async function main() {
  const workerUrl = pathToFileURL(join(ROOT, "worker", "matrix.js")).href;
  const worker = await import(workerUrl);
  const res = await worker.default.fetch(new Request("https://matrix.test/"), {});
  if (!res.ok) throw new Error(`Matrix worker returned HTTP ${res.status}`);

  const html = await res.text();
  if (!html.includes('id="headerRow"') || !html.includes('id="tbody"')) {
    throw new Error("Rendered HTML missing table skeleton");
  }
  if (!html.includes('id="changelogView"') || !html.includes("changelog-cell-link")) {
    throw new Error("Rendered HTML missing changelog view or cell links");
  }

  for (const sym of REQUIRED_CLIENT_SYMBOLS) {
    if (!html.includes(sym)) {
      throw new Error(`Rendered HTML missing required client symbol: ${sym}`);
    }
  }

  const payloadMatch = html.match(
    /<script type="application\/json" id="payload">([\s\S]*?)<\/script>/
  );
  if (!payloadMatch) throw new Error("Rendered HTML missing #payload JSON");
  const payload = JSON.parse(payloadMatch[1]);
  const { matrix, columns } = payload;
  if (!Array.isArray(matrix) || matrix.length < 10) {
    throw new Error(`payload.matrix invalid: length ${matrix?.length}`);
  }
  if (!Array.isArray(columns) || !columns.length) {
    throw new Error("payload.columns missing or empty");
  }
  if (!columns.some((column) => column.key === "free_tier_limits")) {
    throw new Error("payload.columns missing free_tier_limits");
  }

  const slugify = (value) =>
    String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const cellTargets = new Set(
    matrix.flatMap((provider) =>
      columns.map((column) => {
        const providerSlug = provider.links?.slug || provider.name;
        return `cell-${slugify(providerSlug)}-${slugify(column.key)}`;
      })
    )
  );
  const changelogTargets = [
    ...html.matchAll(/data-target-id="(cell-[^"]+)"/g),
  ].map((match) => match[1]);
  if (!changelogTargets.length) {
    throw new Error("Changelog has no cell targets");
  }
  const missingTargets = changelogTargets.filter((target) => !cellTargets.has(target));
  if (missingTargets.length) {
    throw new Error(`Changelog targets missing cells: ${missingTargets.slice(0, 3).join(", ")}`);
  }

  const clientScript = extractClientScript(html);
  runClientScriptSmoke(clientScript, payload);

  console.log(
    `matrix page verify: ok (${matrix.length} providers, header and body rendered)`
  );
}

main().catch((err) => {
  console.error("matrix page verify: FAILED");
  console.error(err.message || err);
  process.exit(1);
});
