import matrix from "../docs/tools/search_matrix/bundle.json";
import llmsTxt from "../docs/tools/search_matrix/llms.txt";
import schema from "../docs/tools/search_matrix/schema.json";
import updatedMeta from "../docs/tools/search_matrix/updated.json";
import changelog from "../docs/tools/search_matrix/changelog.json";

const CANONICAL_ORIGIN = "https://compare-anysearch.ainorthstar.tech";
const GITHUB_REPO = "https://github.com/dhruv-anand-aintech/anysearch";
const DEPLOYMENT_MARKER = "octen-p50-2026-07-28";
const PWA = {
  name: "Anysearch Compare",
  shortName: "Anysearch",
  themeColor: "#176b5b",
  backgroundColor: "#f6f4ee",
  label: "AS",
};

const columns = Object.entries(schema.properties)
  .filter(([key]) => !["links", "notes"].includes(key))
  .map(([key, value]) => {
    const parts = (value.$comment || "").split("|").map(p => p.trim());
    return { key, group: parts[0] || "Other", label: parts[1] || key, description: parts[2] || "" };
  });

const groups = [...new Set(columns.map(c => c.group))];

function htmlEscape(v) { return String(v ?? "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;"); }

function agentDomain(agent) {
  const u = agent.links.website || agent.links.docs || "";
  try { return new URL(u).hostname.replace(/^www\./, ""); } catch { return ""; }
}

const FAVICON_OVERRIDES = {};

function metaTags() {
  const desc = `Compare ${matrix.length} web search APIs for AI agents by features, pricing, SDK support, search modes, and provider capabilities.`;
  return `
    <meta name="description" content="${htmlEscape(desc)}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="${CANONICAL_ORIGIN}/">
    <meta property="og:title" content="Compare Web Search APIs for AI Agents | anysearch">
    <meta property="og:description" content="${htmlEscape(desc)}">
    <meta property="og:url" content="${CANONICAL_ORIGIN}/">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Compare Web Search APIs for AI Agents | anysearch">
    <meta name="twitter:description" content="${htmlEscape(desc)}">`;
}

function feedbackIssueUrl() {
  const body = [
    "## What should be fixed?",
    "",
    "<!-- Describe the wrong/missing matrix value, broken link, or UX issue. -->",
    "",
    "## Matrix location",
    "",
    "- Provider:",
    "- Capability row:",
    "- Current value:",
    "- Expected value:",
    "",
    "## Source or evidence",
    "",
    "<!-- Paste the official docs/source link that supports the correction. -->",
    "",
    "## Extra context",
    "",
    "<!-- Screenshots, notes, or reproduction steps. -->",
  ].join("\n");
  const params = new URLSearchParams({
    title: "Matrix feedback: ",
    body,
    labels: "matrix,feedback",
  });
  return `${GITHUB_REPO}/issues/new?${params.toString()}`;
}

function formatUpdatedLabel(iso) {
  const then = Date.parse(iso);
  if (!then) return "Updated recently";
  const diff = Math.max(0, Date.now() - then);
  const minute = 60 * 1000;
  const hour = 60 * minute;
  const day = 24 * hour;
  if (diff < minute) return "Updated now";
  if (diff < hour) return `Updated ${Math.floor(diff / minute)} min ago`;
  if (diff < day) {
    const hours = Math.floor(diff / hour);
    return `Updated ${hours} ${hours === 1 ? "hour" : "hours"} ago`;
  }
  if (diff < 60 * day) {
    const days = Math.floor(diff / day);
    return `Updated ${days} ${days === 1 ? "day" : "days"} ago`;
  }
  if (diff < 183 * day) {
    const months = Math.max(2, Math.floor(diff / (30 * day)));
    return `Updated ${months} months ago`;
  }
  return `Updated ${new Intl.DateTimeFormat("en-US", { month: "long", day: "numeric", year: "numeric" }).format(new Date(then))}`;
}

function renderChangelog() {
  const byDate = new Map();
  for (const entry of changelog.entries || []) {
    if (!byDate.has(entry.date)) byDate.set(entry.date, []);
    byDate.get(entry.date).push(...entry.items);
  }
  return [...byDate].map(([date, items]) => `
    <section class="change-group">
      <h2>${htmlEscape(new Intl.DateTimeFormat("en-US", {
        year: "numeric", month: "long", day: "numeric", timeZone: "UTC",
      }).format(new Date(`${date}T12:00:00Z`)))}</h2>
      <ul>${items.map(item => `
        <li><a class="changelog-cell-link" href="#${htmlEscape(item.target)}" data-target-id="${htmlEscape(item.target)}">${htmlEscape(item.summary)}</a></li>
      `).join("")}</ul>
    </section>
  `).join("");
}

function render() {
  const payload = JSON.stringify({ matrix, columns, groups, faviconOverrides: FAVICON_OVERRIDES }).replaceAll("</", "<\\/");
  const updatedAt = updatedMeta.updated_at || new Date().toISOString();
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Compare Web Search APIs for AI Agents | anysearch</title>
${metaTags()}
${pwaHead()}
<style>
:root {
  color-scheme: light; --bg: #f6f4ee; --panel: #fffdf8; --ink: #17130d; --muted: #766f63;
  --line: #ded7c9; --line-strong: #bdb3a2; --accent: #176b5b; --warn: #a35f00; --none: #9a3c32; --unknown: #8a8173;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
* { box-sizing: border-box; }
html, body { height: 100%; }
body {
  margin: 0; height: 100vh; height: 100dvh; display: flex; flex-direction: column; overflow: hidden;
  background: var(--bg); color: var(--ink);
}
a { color: inherit; text-decoration: none; }
.topbar {
  height: 44px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 14px; border-bottom: 1px solid var(--line); background: rgba(255,253,248,.92);
  position: sticky; top: 0; z-index: 30; backdrop-filter: blur(10px);
}
.brand { display: flex; gap: 6px; align-items: center; font-weight: 700; font-size: 13px; }
.brand h1 { margin: 0; font: inherit; }
.mark { width: 20px; height: 20px; border: 1px solid var(--ink); display: grid; place-items: center; font-size: 10px; }
.topnav { display: flex; gap: 8px; align-items: center; }
.view-tabs { display: flex; align-items: center; border: 1px solid var(--line); background: #fff; }
.tab-button {
  appearance: none; border: 0; border-right: 1px solid var(--line); background: transparent;
  color: var(--muted); padding: 4px 9px; font: inherit; font-size: 11px; cursor: pointer;
}
.tab-button:last-child { border-right: 0; }
.tab-button:hover { background: #f0eeeb; color: var(--ink); }
.tab-button[aria-selected="true"] { background: var(--ink); color: var(--panel); }
.gh-btn {
  display: inline-flex; align-items: center; gap: 4px; border: 1px solid var(--line);
  background: #fff; padding: 3px 8px; font-size: 12px; color: var(--ink); white-space: nowrap;
}
.gh-btn:hover { background: #f0eeeb; }
.feedback-btn { border-color: var(--accent); color: var(--accent); font-weight: 650; }
.feedback-btn:hover { background: #e8f1ee; }
.hero { padding: 10px 14px 8px; border-bottom: 1px solid var(--line); background: var(--panel); }
.hero p { margin: 0; color: var(--muted); font-size: 12px; }
.meta-row { margin-top: 6px; display: flex; gap: 6px; flex-wrap: wrap; }
.pill { border: 1px solid var(--line); padding: 3px 7px; background: #fff; font-size: 11px; color: var(--muted); }
.view-panel[hidden] { display: none !important; }
.matrix-view { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; }
.changelog-view { flex: 1 1 auto; min-height: 0; overflow: auto; background: var(--bg); }
.changelog-shell { width: min(860px, calc(100% - 28px)); margin: 0 auto; padding: 28px 0 52px; }
.changelog-head {
  display: flex; align-items: baseline; justify-content: space-between; gap: 16px;
  padding-bottom: 12px; border-bottom: 2px solid var(--ink);
}
.changelog-head h1 { margin: 0; font-size: clamp(24px, 4vw, 42px); letter-spacing: -.04em; }
.changelog-head span { color: var(--muted); font-size: 11px; white-space: nowrap; }
.change-group { display: grid; grid-template-columns: 150px 1fr; gap: 24px; padding: 19px 0; border-bottom: 1px solid var(--line); }
.change-group h2 { margin: 2px 0 0; color: var(--muted); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .06em; }
.change-group ul { margin: 0; padding-left: 18px; }
.change-group li { margin: 0 0 7px; padding-left: 3px; font-size: 13px; line-height: 1.4; }
.change-group li:last-child { margin-bottom: 0; }
.changelog-cell-link { text-decoration: underline; text-decoration-color: var(--line-strong); text-underline-offset: 3px; }
.changelog-cell-link:hover { color: var(--accent); text-decoration-color: var(--accent); }
.table-wrap {
  flex: 1 1 auto; overflow: auto; min-height: 0; position: relative;
}
table {
  border-collapse: separate; border-spacing: 0; background: var(--panel); table-layout: fixed;
  width: 100%; min-width: 100%;
}
thead { position: sticky; top: 0; z-index: 20; }
th {
  background: #eee7d8; color: #2a241b; font-weight: 700; font-size: 10px;
  border-right: 1px solid var(--line); border-bottom: 1px solid var(--line-strong);
  padding: 0; vertical-align: middle; text-align: center; position: relative;
  user-select: none;
}
th.corner { position: sticky; left: 0; z-index: 25; background: #e8decc; min-width: 156px; width: 156px; }
th.agent-col {
  width: var(--agent-col-w, 88px); min-width: var(--agent-col-w, 88px); max-width: var(--agent-col-w, 88px);
  min-height: 64px; height: auto; cursor: grab; transition: opacity .15s;
  padding: 5px 6px 7px; vertical-align: bottom;
}
th.agent-col.hidden-col { cursor: default; }
th.agent-col.dragging { opacity: .4; }
th.agent-col.drag-over { background: #d5cdbb; }
th.agent-col.hidden-col {
  width: var(--agent-col-hidden-w, 36px); min-width: var(--agent-col-hidden-w, 36px);
  max-width: var(--agent-col-hidden-w, 36px); opacity: .35;
}
th.agent-col.hidden-col .agent-name { display: none; }
td.col-hidden-slot {
  width: var(--agent-col-hidden-w, 36px); min-width: var(--agent-col-hidden-w, 36px);
  max-width: var(--agent-col-hidden-w, 36px); padding: 0; opacity: .2;
}
.agent-head {
  display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
  gap: 4px; min-height: 48px; width: 100%;
}
.agent-brand-link {
  display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
  gap: 4px; width: 100%; text-decoration: none; color: inherit; border-radius: 4px;
}
.agent-brand-link:hover { background: rgba(42, 36, 27, 0.06); }
.agent-brand-link:focus-visible { outline: 2px solid var(--accent); outline-offset: 1px; }
a.docs-link { font-weight: 600; color: var(--accent); text-decoration: underline; font-size: 10px; }
a.docs-link:hover { text-decoration: none; }
.agent-head:has(.agent-name-stacked) { min-height: 56px; }
.agent-name {
  width: 100%; box-sizing: border-box; font-weight: 700; line-height: 1.15; color: var(--ink);
  text-align: center;
}
.agent-name-stacked {
  display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
  gap: 1px; overflow: visible; max-height: none;
}
.agent-name-line {
  display: block; width: 100%; max-width: 100%;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.agent-name-via {
  font-weight: 600; font-size: 0.92em; color: var(--muted);
  overflow: visible; text-overflow: clip; flex-shrink: 0;
}
.row-label.dragging { opacity: .4; }
.row-label.drag-over { outline: 2px dashed var(--accent); outline-offset: -2px; }
.fav-box { display: inline-block; background: #fff; border-radius: 6px; line-height: 0; box-shadow: inset 0 0 0 1px var(--line); }
th.agent-col .fav { width: 32px; height: 32px; vertical-align: middle; border-radius: 6px; }
th.agent-col.deprecated-col { opacity: .42; }
th.agent-col.deprecated-col .agent-name::after { content: " (deprecated)"; font-weight: 400; font-size: 8px; }
th.agent-col .eye {
  position: absolute; top: 1px; right: 2px; font-size: 9px; color: var(--muted); opacity: .5;
  pointer-events: auto; cursor: pointer; background: none; border: none; padding: 2px 3px; line-height: 1;
  font: inherit; border-radius: 3px; z-index: 2;
}
th.agent-col .eye:hover { opacity: 1; background: rgba(42, 36, 27, 0.08); }
th.agent-col.hidden-col .eye { opacity: 1; color: var(--none); }
tbody td { padding: 3px 4px; font-size: 11px; text-align: center; vertical-align: middle;
  border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); }
td.cell-wrap { position: relative; cursor: default; }
td.cell-wrap.has-source { cursor: pointer; }
td.cell-wrap:hover { outline: 1.5px solid var(--line-strong); outline-offset: -1px; }
td.cell-wrap .cell-value,
td.cell-wrap .support { position: relative; z-index: 1; pointer-events: none; }
td.cell-wrap .cell-value,
td.cell-wrap .form-tags { position: relative; z-index: 1; }
td.cell-wrap .dot {
  display: inline-flex; align-items: center; justify-content: center;
  width: 16px; height: 16px; border-radius: 50%; color: #fff; font-size: 9px; line-height: 1;
}
.full .dot { background: var(--accent); }
.partial .dot { background: var(--warn); }
.none .dot { background: var(--none); }
.unknown .dot { background: var(--unknown); }
.row-label {
  position: sticky; left: 0; z-index: 5; background: var(--panel);
  text-align: left; font-size: 11px; font-weight: 600; padding: 3px 8px !important;
  min-width: 156px; max-width: 156px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  cursor: pointer; user-select: none;
}
.row-label:hover .row-label-tip { display: block; }
.row-label-tip {
  display: none; position: absolute; left: 8px; top: calc(100% + 4px);
  background: #2a241b; color: #f6f4ee; font-size: 10px; line-height: 1.3; padding: 3px 6px;
  border-radius: 3px; z-index: 50; pointer-events: none; max-width: 240px; white-space: normal;
  outline: 1px solid #555; font-weight: 400;
}
.row-label .arrow { font-size: 8px; margin-right: 3px; color: var(--muted); }
.row-label.filter-active { color: var(--accent); }
.row-label.filter-active .arrow { color: var(--accent); }
.group-head .row-label.group-row-label {
  font-size: 9px; text-transform: uppercase; letter-spacing: .03em;
  color: var(--muted); font-weight: 600; cursor: default; background: #e2d8c5;
}
.group-head .group-spacer {
  background: #e2d8c5; padding: 2px 4px !important; border-bottom: 1px solid var(--line);
}
.cell-tip {
  display: none; position: fixed; left: 0; top: 0; transform: none;
  background: #2a241b; color: #f6f4ee; font-size: 10px; line-height: 1.35; padding: 6px 8px;
  border-radius: 3px; z-index: 60; pointer-events: auto; width: max-content; max-width: min(520px, calc(100vw - 16px)); white-space: normal;
  overflow-wrap: anywhere;
  outline: 1px solid #555; text-align: left; font-weight: 400;
  box-shadow: 0 8px 24px rgba(23, 19, 13, .22);
}
.cell-tip-note { display: block; }
.cell-tip-url {
  display: block; margin-top: 4px; padding-top: 4px; border-top: 1px solid rgba(246,244,238,.22);
  color: #d8d1c4; font-size: 8px; line-height: 1.25;
}
.cell-tip a { color: #fff7d1; text-decoration: underline; text-underline-offset: 2px; }
.cell-tip-links {
  display: grid; grid-template-columns: repeat(2, minmax(0, max-content)); gap: 3px 8px;
  margin-top: 5px; padding-top: 5px; border-top: 1px solid rgba(246,244,238,.22);
}
.cell-tip-link { white-space: nowrap; }
td.value {
  font-size: 9px; color: var(--muted); line-height: 1.35; text-align: left; vertical-align: top;
  width: var(--agent-col-w, 88px); max-width: var(--agent-col-w, 88px); min-width: var(--agent-col-w, 88px);
  white-space: normal; overflow-wrap: anywhere; word-break: break-word; hyphens: auto;
}
td.value .cell-value {
  display: block; max-width: 100%; overflow-wrap: anywhere; word-break: break-word;
}
.form-tags { display: flex; flex-wrap: wrap; gap: 1px; justify-content: center; }
.form-tag { border: 1px solid var(--line); background: #fff; padding: 1px 2px; font-size: 8px; }
.form-tag.deprecated-tag { color: var(--warn); border-color: #d4a574; }
.cell-link {
  position: absolute; inset: 0; z-index: 2;
}
.source-mark {
  position: absolute; top: 0; right: 0; z-index: 3;
  width: 0; height: 0; pointer-events: none;
  border-style: solid; border-width: 0 6px 6px 0;
  border-color: transparent var(--line-strong) transparent transparent;
  opacity: .35;
}
.cell-wrap:hover .source-mark { opacity: 1; }
.cell-anchor-flash { animation: cell-anchor-flash 1.8s ease-out; }
@keyframes cell-anchor-flash {
  0%, 28% { outline: 3px solid var(--accent); outline-offset: -3px; background: #dff2ec; }
  100% { outline-color: transparent; }
}
.hidden { display: none; }
@media (max-width: 680px) {
  .topbar { height: auto; min-height: 44px; flex-wrap: wrap; gap: 6px; padding: 6px 10px; }
  .topnav { width: 100%; justify-content: space-between; flex-wrap: wrap; }
  .change-group { grid-template-columns: 1fr; gap: 8px; }
  .changelog-shell { padding-top: 20px; }
}
</style>
</head>
<body>
<header class="topbar">
  <a class="brand" href="/"><span class="mark">AS</span><h1>Compare Web Search APIs</h1></a>
  <nav class="topnav">
    <div class="view-tabs" role="tablist" aria-label="Matrix views">
      <button type="button" class="tab-button" id="compareTab" role="tab" aria-controls="matrixView" aria-selected="true" onclick="showView('matrix')">Compare</button>
      <button type="button" class="tab-button" id="changelogTab" role="tab" aria-controls="changelogView" aria-selected="false" onclick="showView('changelog')">Changelog</button>
    </div>
    <a href="${htmlEscape(feedbackIssueUrl())}" class="gh-btn feedback-btn" target="_blank" rel="noreferrer">Report fix</a>
    <a href="${GITHUB_REPO}" class="gh-btn" target="_blank" rel="noreferrer">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
      Star
    </a>
  </nav>
</header>
<main id="matrixView" class="view-panel matrix-view">
<section class="hero">
  <p>Compare ${htmlEscape(matrix.length)} web search API providers for AI agents by features, pricing, SDK support, search modes, and unified <strong>anysearch</strong> parameters. <strong>Name or icon</strong> opens the provider site; <strong>⊙</strong> hides or shows a column; drag headers to reorder; use the <strong>API docs</strong> row for official references.</p>
  <div class="meta-row">
    <span class="pill">${htmlEscape(matrix.length)} providers</span>
    <span class="pill"><a href="${GITHUB_REPO}">anysearch SDK</a></span>
    <span class="pill" id="updatedPill" data-updated-at="${htmlEscape(updatedAt)}">${htmlEscape(formatUpdatedLabel(updatedAt))}</span>
  </div>
</section>
<div class="table-wrap">
<table>
<thead><tr id="headerRow"></tr></thead>
<tbody id="tbody"></tbody>
</table>
</div>
</main>
<main id="changelogView" class="view-panel changelog-view" hidden>
  <div class="changelog-shell">
    <header class="changelog-head">
      <h1>Changelog</h1>
      <span>${htmlEscape(changelog.entry_count)} tracked changes</span>
    </header>
    ${renderChangelog()}
  </div>
</main>
<script type="application/json" id="payload">${payload}</script>
<script>
function agentDomain(agent) {
  var u = agent.links.website || agent.links.docs || "";
  try { return new URL(u).hostname.replace(/^www\\./, ""); } catch(e) { return ""; }
}
function agentBrandUrl(agent) {
  var links = agent.links || {};
  return links.website || links.docs || "";
}
function agentBrandHeadHtml(agent, idx) {
  var url = agentBrandUrl(agent);
  var inner = favimg(agent, idx) + formatAgentNameHtml(agent.name);
  if (!url) return '<div class="agent-head">'+inner+'</div>';
  var host = agentDomain(agent);
  var title = host ? ('Open ' + host) : 'Open provider site';
  return '<div class="agent-head"><a class="agent-brand-link" href="'+esc(url)+'" target="_blank" rel="noopener noreferrer" draggable="false" title="'+esc(title)+'">'+inner+'</a></div>';
}
function providerDocsCell(agent) {
  var url = agent.links && agent.links.docs;
  if (!url) return '<td class="cell-wrap value"><span class="cell-value">&mdash;</span></td>';
  return '<td class="cell-wrap value"><a class="docs-link" href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">Docs</a></td>';
}
const { matrix, columns, groups, faviconOverrides } = JSON.parse(document.getElementById('payload').textContent);
function formatUpdatedLabelClient(iso) {
  var then = Date.parse(iso);
  if (!then) return 'Updated recently';
  var diff = Math.max(0, Date.now() - then);
  var minute = 60 * 1000, hour = 60 * minute, day = 24 * hour;
  if (diff < minute) return 'Updated now';
  if (diff < hour) {
    var mins = Math.floor(diff / minute);
    return 'Updated ' + mins + ' min ago';
  }
  if (diff < day) {
    var hours = Math.floor(diff / hour);
    return 'Updated ' + hours + ' ' + (hours === 1 ? 'hour' : 'hours') + ' ago';
  }
  if (diff < 60 * day) {
    var days = Math.floor(diff / day);
    return 'Updated ' + days + ' ' + (days === 1 ? 'day' : 'days') + ' ago';
  }
  if (diff < 183 * day) {
    var months = Math.max(2, Math.floor(diff / (30 * day)));
    return 'Updated ' + months + ' months ago';
  }
  return 'Updated ' + new Intl.DateTimeFormat('en-US', {month:'long', day:'numeric', year:'numeric'}).format(new Date(then));
}
function refreshUpdatedPill() {
  var pill = document.getElementById('updatedPill');
  if (pill) pill.textContent = formatUpdatedLabelClient(pill.dataset.updatedAt);
}
refreshUpdatedPill();
setInterval(refreshUpdatedPill, 60000);
// String/metadata rows in About; feature-shaped rows (e.g. requires_key) stay in featureCols.
const metaCols = new Set(['name','env_keys','python_extra','notes']);
const featureCols = columns.filter(c => !metaCols.has(c.key));
const aboutCols = columns.filter(c => metaCols.has(c.key) && c.key !== 'name' && c.key !== 'notes');
const DATE_SORT_ROWS = new Set([]);
const MONTH_MAP = {Jan:1,Feb:2,Mar:3,Apr:4,May:5,Jun:6,Jul:7,Aug:8,Sep:9,Oct:10,Nov:11,Dec:12};

const COOKIE = 'asmat_state';
let colOrder = [];
let rowOrder = [];
let hidden = new Set();
let rowSort = [];
const SORT_ORDER = { full:0, partial:1, none:2, unknown:3, "":4 };
const FORM_FACTOR_ORDER = ['CLI','IDE','Extension','SDK','Web','Mac App'];
const MODE_ORDER = ['fast','balanced','deep'];
const MULTI_VALUE_COLS = new Set(['form_factor','mode']);
function sortModes(vals) {
  var rank = {};
  MODE_ORDER.forEach(function(v,i){rank[v]=i});
  return vals.slice().sort(function(a,b){
    var ra = rank[a]!==undefined?rank[a]:99, rb = rank[b]!==undefined?rank[b]:99;
    return ra-rb || String(a).localeCompare(String(b));
  });
}
function sortFormFactors(vals) {
  var rank = {};
  FORM_FACTOR_ORDER.forEach(function(v,i){rank[v]=i});
  return vals.slice().sort(function(a,b){
    var ra = rank[a]!==undefined?rank[a]:99, rb = rank[b]!==undefined?rank[b]:99;
    return ra-rb || String(a).localeCompare(String(b));
  });
}
function parseDisplayDate(value) {
  var v = String(value || '').trim();
  if (!v) return 0;
  var m = v.match(/^([A-Za-z]{3})\s*['\u2019](\d{2})$/);
  if (m && MONTH_MAP[m[1]]) return Date.UTC(2000 + parseInt(m[2],10), MONTH_MAP[m[1]] - 1, 1);
  if (/^\d{4}$/.test(v)) return Date.UTC(parseInt(v,10), 0, 1);
  if (/^\d{4}-\d{2}-\d{2}$/.test(v)) return Date.parse(v + 'T12:00:00Z') || 0;
  return 0;
}
function dateSortKey(agent, key) {
  var field = agent[key] || {};
  if (field.sort_date) return Date.parse(field.sort_date + 'T12:00:00Z') || 0;
  return parseDisplayDate(field.value);
}
function sortPriorityNumber(sortEntry) {
  return rowSort.length - rowSort.indexOf(sortEntry);
}
function sortableLabelHtml(label, key) {
  var sortEntry = rowSort.find(function(s){ return s.key === key; });
  var isSort = !!sortEntry;
  var active = isSort ? ' filter-active' : '';
  var arrow = isSort ? sortPriorityNumber(sortEntry) : '&#9654;';
  return '<td class="row-label'+active+'" data-rowkey="'+key+'" onclick="cycleSort('+"'"+key+"'"+')" title="Sort columns by this date"><span class="row-label-tip">'+esc(label)+'</span><span class="arrow">'+arrow+'</span>'+esc(label)+'</td>';
}

// Pinned agents (always at top), then rest sorted by full-feature count
const PINNED = [
  'Octen','Exa','Tavily','Brave','Parallel','Perplexity','Gemini',
  'You','Linkup',
  'Google · SerpApi','Bing · SerpApi','Baidu · SerpApi','Yandex · SerpApi',
  'DuckDuckGo · SerpApi','Yahoo · SerpApi',
];
function faviconSlugForAgent(agent) {
  return agent.links && agent.links.slug;
}
function serpapiPinRank(name) {
  var i = PINNED.indexOf(name);
  return i === -1 ? null : -900 + i;
}
const ALL_FEATS = featureCols.map(function(c){return c.key});
function rankAgent(i) {
  var agent = matrix[i];
  if (agent.deprecated) return 2000 + i;
  var sp = serpapiPinRank(agent.name);
  if (sp !== null) return sp;
  var p = PINNED.indexOf(agent.name);
  if (p !== -1) return -1000 + p;
  var cnt = 0;
  ALL_FEATS.forEach(function(k){if((agent[k]||{}).support==='full')cnt++});
  return -cnt;
}

function loadState() {
  var def = { cols: matrix.map(function(_,i){return i}).sort(function(a,b){return rankAgent(a)-rankAgent(b)}), rows: featureCols.map(function(c){return c.key}) };
  try {
    var c = document.cookie.split('; ').find(r => r.startsWith(COOKIE+'='));
    if (c) { var p = JSON.parse(decodeURIComponent(c.split('=')[1]));
      if (Array.isArray(p.cols) && p.cols.length===matrix.length) def.cols = p.cols;
      if (Array.isArray(p.rows) && p.rows.length===featureCols.length) def.rows = p.rows;
    }
  } catch(e) {}
  return def;
}
function saveState() {
  document.cookie = COOKIE + '=' + encodeURIComponent(JSON.stringify({cols:colOrder, rows:rowOrder})) + ';path=/;max-age=31536000';
}
function esc(v) { return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function slugify(v) { return String(v||'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''); }
function cellId(agent, key) {
  var agentSlug = (agent.links && agent.links.slug) || agent.name;
  return 'cell-' + slugify(agentSlug) + '-' + slugify(key);
}
function rowLabelCell(label, extraClass, extraAttrs) {
  return '<td class="row-label'+extraClass+'"'+extraAttrs+'><span class="row-label-tip">'+esc(label)+'</span>'+esc(label)+'</td>';
}
function cellTipHtml(comment, sourceUrl, links) {
  var linkEntries = links ? Object.entries(links).filter(function(entry){ return entry[1]; }) : [];
  if (!comment && !sourceUrl && !linkEntries.length) return '';
  var html = '<div class="cell-tip">';
  if (comment) html += '<span class="cell-tip-note">'+esc(comment)+'</span>';
  if (linkEntries.length) {
    html += '<span class="cell-tip-links">';
    linkEntries.forEach(function(entry){
      html += '<a class="cell-tip-link" href="'+esc(entry[1])+'" target="_blank" rel="noopener noreferrer">'+esc(entry[0])+'</a>';
    });
    html += '</span>';
  }
  if (sourceUrl) html += '<a class="cell-tip-url" href="'+esc(sourceUrl)+'" target="_blank" rel="noopener noreferrer">Source: '+esc(sourceUrl)+'</a>';
  return html + '</div>';
}
var COLORS = ['#176b5b','#2d4f9e','#9a3c32','#a35f00','#4a6fa5','#7b4f9e','#27ae60','#8e44ad','#d35400','#16a085','#2c3e50','#f39c12','#1abc9c','#34495e','#e74c3c','#2980b9','#c0392b'];
var SERPAPI_VIA_SUFFIX = ' \u00b7 SerpApi';
var NAME_VIA_SEP = ' \u00b7 ';
function splitStackedAgentName(name) {
  if (name.endsWith(SERPAPI_VIA_SUFFIX)) {
    return { top: name.slice(0, -SERPAPI_VIA_SUFFIX.length), bottom: 'SerpApi' };
  }
  var i = name.lastIndexOf(NAME_VIA_SEP);
  if (i > 0) {
    return { top: name.slice(0, i), bottom: name.slice(i + NAME_VIA_SEP.length) };
  }
  return null;
}
function formatAgentNameHtml(name) {
  var parts = splitStackedAgentName(name);
  if (parts) {
    return '<span class="agent-name agent-name-stacked" title="'+esc(name)+'">'+
      '<span class="agent-name-line">'+esc(parts.top)+'</span>'+
      '<span class="agent-name-line agent-name-via">'+esc(parts.bottom)+'</span></span>';
  }
  return '<span class="agent-name" title="'+esc(name)+'">'+
    '<span class="agent-name-line">'+esc(name)+'</span></span>';
}
function agentInitials(name) {
  var parts = splitStackedAgentName(name);
  if (parts) {
    return parts.top.slice(0, 2).toUpperCase();
  }
  var p = name.split(/\s+/);
  return p.length===1 ? name.slice(0,2).toUpperCase() : (p[0][0]+p[1][0]).toUpperCase();
}
function avatarSvg(ini, c, size) {
  var s = size||32, r = Math.round(s/5), fs = Math.round(s*0.44);
  return '<svg width="'+s+'" height="'+s+'" viewBox="0 0 '+s+' '+s+'" xmlns="http://www.w3.org/2000/svg"><rect width="'+s+'" height="'+s+'" rx="'+r+'" fill="'+c+'"/><text x="'+s/2+'" y="'+s/2+'" text-anchor="middle" dominant-baseline="central" fill="white" font-size="'+fs+'" font-weight="700" font-family="Inter,sans-serif">'+ini+'</text></svg>';
}
function favimg(agent, idx) {
  var ini = agentInitials(agent.name), c = COLORS[idx%COLORS.length];
  var fallback = avatarSvg(ini, c, 32);
  var slug = faviconSlugForAgent(agent) || '';
  var src = faviconOverrides[slug] || (function(){
    var d = agentDomain(agent);
    return d ? 'https://www.google.com/s2/favicons?domain='+esc(encodeURIComponent(d))+'&sz=64' : '';
  })();
  if (!src) return '<span class="fav-box">'+fallback+'</span>';
  return '<span class="fav-box" style="position:relative"><img class="fav" src="'+esc(src)+'" alt="" width="32" height="32" loading="lazy" onerror="var p=this.parentElement;this.style.display=\\x27none\\x27;var s=p.querySelector(\\x27.fav-av\\x27);if(s)s.style.display=\\x27inline\\x27"><span class="fav-av" style="display:none">'+fallback+'</span></span>';
}
function cell(agent, col) {
  var v = agent[col.key];
  var idAttr = ' id="'+cellId(agent, col.key)+'"';
  if (!v) return '<td'+idAttr+'>&mdash;</td>';
  if (MULTI_VALUE_COLS.has(col.key)) {
    var sortFn = col.key === 'mode' ? sortModes : sortFormFactors;
    var tags = sortFn((v.values||[v.value]).filter(Boolean));
    var links = v.links || {};
    var tip = cellTipHtml(v.comment, v.source_url, links);
    if (!tags.length) return '<td'+idAttr+' class="cell-wrap value"><span class="cell-value">&mdash;</span>'+tip+'</td>';
    var tagHtml = tags.map(function(x){
      var href = links[x];
      if (href) return '<a class="form-tag" href="'+esc(href)+'" target="_blank" rel="noreferrer">'+esc(x)+'</a>';
      return '<span class="form-tag">'+esc(x)+'</span>';
    }).join('');
    if (agent.deprecated) tagHtml += '<span class="form-tag deprecated-tag">deprecated</span>';
    return '<td'+idAttr+' class="cell-wrap"><div class="form-tags">'+tagHtml+'</div>'+tip+'</td>';
  }
  var tip = cellTipHtml(v.comment, v.source_url);
  var hasSrc = !!v.source_url;
  var link = hasSrc ? '<a class="cell-link" href="'+esc(v.source_url)+'" target="_blank" rel="noreferrer" title="Open source" aria-label="Open source"></a>' : '';
  var mark = hasSrc ? '<span class="source-mark" aria-hidden="true"></span>' : '';
  var wrapCls = 'cell-wrap'+(hasSrc?' has-source':'');
  if (v.value !== undefined) return '<td'+idAttr+' class="'+wrapCls+' value"><span class="cell-value">'+esc(v.value)+'</span>'+link+mark+tip+'</td>';
  if (featureCols.some(function(c){ return c.key===col.key; })) {
    var g = {full:'&#10003;',partial:'&#9678;',none:'&#10005;',unknown:'?','':'—'};
    return '<td'+idAttr+' class="'+wrapCls+'">'+link+'<span class="support '+(v.support||'')+'"><span class="dot">'+(g[v.support||'']||'?')+'</span></span>'+mark+tip+'</td>';
  }
  if (v.support !== undefined) {
    var g = {full:'&#10003;',partial:'&#9678;',none:'&#10005;',unknown:'?','':'—'};
    return '<td'+idAttr+' class="'+wrapCls+'">'+link+'<span class="support '+(v.support||'')+'"><span class="dot">'+(g[v.support||'']||'?')+'</span></span>'+mark+tip+'</td>';
  }
  return '<td'+idAttr+'>&mdash;</td>';
}
function updateColWidths() {
  var wrap = document.querySelector('.table-wrap');
  var corner = 156;
  var minVisible = 80;
  var minHidden = 36;
  var hiddenCount = 0;
  colOrder.forEach(function(i){ if (hidden.has(i)) hiddenCount++; });
  var visibleCount = visibleCols().length || 1;
  var avail = Math.max(0, (wrap ? wrap.clientWidth : window.innerWidth) - corner);
  var hiddenW = hiddenCount * minHidden;
  var w = Math.max(minVisible, Math.floor((avail - hiddenW) / visibleCount));
  document.documentElement.style.setProperty('--agent-col-w', w + 'px');
  document.documentElement.style.setProperty('--agent-col-hidden-w', minHidden + 'px');
}
function fitAgentHeaderNames() {
  document.querySelectorAll('th.agent-col:not(.hidden-col) .agent-name').forEach(function(el) {
    el.style.fontSize = '';
    var box = el.closest('.agent-head');
    if (!box) return;
    var maxW = Math.max(0, box.clientWidth - 2);
    var lines = el.querySelectorAll('.agent-name-line');
    var stacked = el.classList.contains('agent-name-stacked');
    var maxH = stacked ? 42 : 34;
    var fs = 10;
    el.style.fontSize = fs + 'px';
    function overflows() {
      if (el.scrollHeight > maxH + 1) return true;
      for (var li = 0; li < lines.length; li++) {
        var line = lines[li];
        if (line.classList.contains('agent-name-via')) continue;
        if (line.scrollWidth > maxW + 1) return true;
      }
      return false;
    }
    while (fs > 5.5 && overflows()) {
      fs -= 0.5;
      el.style.fontSize = fs + 'px';
    }
  });
}
function scheduleFitAgentHeaderNames() {
  requestAnimationFrame(function() {
    requestAnimationFrame(fitAgentHeaderNames);
  });
}
function renderHeader() {
  document.getElementById('headerRow').innerHTML = '<th class="corner"></th>'+displayColOrder().map(function(i){
    var agent = matrix[i], hc = hidden.has(i)?' hidden-col':'', dep = agent.deprecated?' deprecated-col':'';
    var eyeTitle = hidden.has(i) ? 'Show this provider' : 'Hide this provider';
    return '<th class="agent-col'+hc+dep+'" data-idx="'+i+'" draggable="true">'+
      agentBrandHeadHtml(agent, i)+
      '<button type="button" class="eye" onclick="toggleCol('+i+'); event.stopPropagation();" title="'+esc(eyeTitle)+'" aria-label="'+esc(eyeTitle)+'">'+
      (hidden.has(i)?'&#8855;':'&#9679;')+'</button></th>';
  }).join(''); setupColDrag(); updateColWidths(); scheduleFitAgentHeaderNames();
}
function visibleCols() { return colOrder.filter(function(i){return !hidden.has(i)}); }
function sortVisibleColumnIndices(indices) {
  if (!rowSort.length) return indices.slice();
  var originalRank = {};
  indices.forEach(function(i, idx){ originalRank[i] = idx; });
  var priority = rowSort.slice().reverse();
  return indices.slice().sort(function(a,b){
    for (var p=0; p<priority.length; p++) {
      var key = priority[p].key;
      var va = SORT_ORDER[(matrix[a][key]||{}).support||''];
      var vb = SORT_ORDER[(matrix[b][key]||{}).support||''];
      if (va === undefined) va = 4;
      if (vb === undefined) vb = 4;
      if (va !== vb) return va - vb;
    }
    return originalRank[a] - originalRank[b];
  });
}
function displayColOrder() {
  if (!rowSort.length) return colOrder.slice();
  var sortedVisible = sortVisibleColumnIndices(visibleCols());
  var qi = 0;
  return colOrder.map(function(i) {
    if (hidden.has(i)) return i;
    return sortedVisible[qi++];
  });
}
function colCell(i, col, render) {
  if (hidden.has(i)) return '<td class="col-hidden-slot" aria-hidden="true"></td>';
  return render();
}
function renderBody() {
  var cols = displayColOrder();
  var rows = [];
  rows.push('<tr class="group-head">'+rowLabelCell('About',' group-row-label','')+cols.map(function(i){
    return colCell(i, null, function(){ return '<td class="group-spacer"></td>'; });
  }).join('')+'</tr>');
  rows.push('<tr>'+rowLabelCell('API docs','',' title="Official API documentation for this provider"')+cols.map(function(i){
    return colCell(i, null, function(){ return providerDocsCell(matrix[i]); });
  }).join('')+'</tr>');
  aboutCols.forEach(function(col){
    var label = rowLabelCell(col.label,'','');
    rows.push('<tr>'+label+cols.map(function(i){
      return colCell(i, col, function(){ return cell(matrix[i], col); });
    }).join('')+'</tr>');
  });
  // Feature rows in saved order, grouped
  var used = {};
  rowOrder.forEach(function(key){
    var col = featureCols.find(function(c){return c.key===key});
    if (!col||used[key]) return; used[key]=true;
    var sortEntry = rowSort.find(function(s){ return s.key===key; });
    var isSort = !!sortEntry;
    var active = isSort?' filter-active':'';
    var arrow = isSort ? sortPriorityNumber(sortEntry) : '&#9654;';
    var labelHtml = '<td class="row-label'+active+'" draggable="true" data-rowkey="'+key+'" onclick="cycleSort('+"'"+key+"'"+')" title="Sort columns by this feature"><span class="row-label-tip">'+esc(col.label)+'</span><span class="arrow">'+arrow+'</span>'+esc(col.label)+'</td>';
    var cells = cols.map(function(i){
      return colCell(i, col, function(){ return cell(matrix[i], col); });
    }).join('');
    rows.push('<tr>'+labelHtml+cells+'</tr>');
  });
  document.getElementById('tbody').innerHTML = rows.join('');
  setupRowDrag();
  setupCellTips();
}
function toggleCol(i) { hidden.has(i)?hidden.delete(i):hidden.add(i); renderHeader(); renderBody(); updateColWidths(); scheduleFitAgentHeaderNames(); }
function cycleSort(key) {
  if (DATE_SORT_ROWS.has(key)) return;
  var idx = rowSort.findIndex(function(s){ return s.key === key; });
  if (idx !== -1) rowSort.splice(idx, 1);
  else rowSort.push({key:key});
  renderHeader();
  renderBody();
  updateColWidths();
}
function setupColDrag() {
  document.querySelectorAll('th.agent-col').forEach(function(th){
    th.addEventListener('dragstart',function(e){
      if (e.target.closest('.agent-brand-link')) { e.preventDefault(); return; }
      this.classList.add('dragging');e.dataTransfer.setData('text/col',this.dataset.idx);
    });
    th.addEventListener('dragend',function(){this.classList.remove('dragging')});
    th.addEventListener('dragover',function(e){e.preventDefault();this.classList.add('drag-over')});
    th.addEventListener('dragleave',function(){this.classList.remove('drag-over')});
    th.addEventListener('drop',function(e){e.preventDefault();this.classList.remove('drag-over');
      var from=parseInt(e.dataTransfer.getData('text/col')),to=parseInt(this.dataset.idx);
      if (isNaN(from)||isNaN(to)||from===to) return;
      var fp=colOrder.indexOf(from),tp=colOrder.indexOf(to);
      if (fp===-1||tp===-1) return;
      colOrder.splice(fp,1);colOrder.splice(tp,0,from);saveState();renderHeader();renderBody();updateColWidths();scheduleFitAgentHeaderNames();
    });
  });
}
function setupRowDrag() {
  document.querySelectorAll('.row-label[draggable]').forEach(function(td){
    td.addEventListener('dragstart',function(e){this.classList.add('dragging');e.dataTransfer.setData('text/row',this.dataset.rowkey)});
    td.addEventListener('dragend',function(){this.classList.remove('dragging')});
    td.addEventListener('dragover',function(e){e.preventDefault();this.classList.add('drag-over')});
    td.addEventListener('dragleave',function(){this.classList.remove('drag-over')});
    td.addEventListener('drop',function(e){e.preventDefault();this.classList.remove('drag-over');
      var from=e.dataTransfer.getData('text/row'),to=this.dataset.rowkey;
      if (!from||!to||from===to) return;
      var fp=rowOrder.indexOf(from),tp=rowOrder.indexOf(to);
      if (fp===-1||tp===-1) return;
      rowOrder.splice(fp,1);rowOrder.splice(tp,0,from);saveState();renderBody();
    });
  });
}
function setupCellTips() {
  document.querySelectorAll('.cell-wrap .cell-tip').forEach(function(tip){
    var cell = tip.closest('.cell-wrap');
    if (!cell) return;
    var hideTimer = null;
    function showTip(){
      if (hideTimer) {
        clearTimeout(hideTimer);
        hideTimer = null;
      }
      tip.style.display = 'block';
      tip.style.visibility = 'hidden';
      tip.style.left = '0px';
      tip.style.top = '0px';
      var cr = cell.getBoundingClientRect();
      var tr = tip.getBoundingClientRect();
      var margin = 8;
      var left = cr.right + 6;
      if (left + tr.width > window.innerWidth - margin) left = cr.left - tr.width - 6;
      left = Math.max(margin, Math.min(left, window.innerWidth - tr.width - margin));
      var top = cr.top;
      if (top + tr.height > window.innerHeight - margin) top = Math.min(window.innerHeight - tr.height - margin, cr.bottom + 6);
      top = Math.max(margin, top);
      tip.style.left = left + 'px';
      tip.style.top = top + 'px';
      tip.style.visibility = 'visible';
    }
    function scheduleHide(){
      if (hideTimer) clearTimeout(hideTimer);
      hideTimer = setTimeout(function(){
        hideTimer = null;
        if (!cell.matches(':hover') && !tip.matches(':hover')) hideTip();
      }, 180);
    }
    function hideTip(){
      tip.style.display = '';
      tip.style.visibility = '';
    }
    cell.addEventListener('mouseenter', showTip);
    cell.addEventListener('mouseleave', scheduleHide);
    tip.addEventListener('mouseenter', showTip);
    tip.addEventListener('mouseleave', scheduleHide);
    tip.addEventListener('click', function(e){ e.stopPropagation(); });
  });
}
function showView(view, updateHash) {
  var isChangelog = view === 'changelog';
  var matrixView = document.getElementById('matrixView');
  var changelogView = document.getElementById('changelogView');
  var compareTab = document.getElementById('compareTab');
  var changelogTab = document.getElementById('changelogTab');
  if (!matrixView || !changelogView) return;
  matrixView.hidden = isChangelog;
  changelogView.hidden = !isChangelog;
  if (compareTab) compareTab.setAttribute('aria-selected', String(!isChangelog));
  if (changelogTab) changelogTab.setAttribute('aria-selected', String(isChangelog));
  if (updateHash !== false && window.history && window.location) {
    var next = isChangelog ? '#changelog' : window.location.pathname + window.location.search;
    window.history.pushState(null, '', next);
  }
}
function revealCell(targetId) {
  var matrixIndex = -1;
  for (var i=0; i<matrix.length; i++) {
    for (var j=0; j<columns.length; j++) {
      if (cellId(matrix[i], columns[j].key) === targetId) { matrixIndex = i; break; }
    }
    if (matrixIndex !== -1) break;
  }
  if (matrixIndex !== -1 && hidden.has(matrixIndex)) {
    hidden.delete(matrixIndex);
    saveState();
    renderHeader();
    renderBody();
    updateColWidths();
  }
  showView('matrix', false);
  var target = document.getElementById(targetId);
  if (!target) return;
  document.querySelectorAll('.cell-anchor-flash').forEach(function(el){el.classList.remove('cell-anchor-flash')});
  target.scrollIntoView({behavior:'smooth', block:'center', inline:'center'});
  target.classList.add('cell-anchor-flash');
  if (window.history) window.history.replaceState(null, '', '#'+targetId);
}
function setupChangelogLinks() {
  document.querySelectorAll('.changelog-cell-link').forEach(function(link){
    link.addEventListener('click', function(event){
      event.preventDefault();
      revealCell(link.dataset.targetId);
    });
  });
}
var state = loadState(); colOrder = state.cols; rowOrder = state.rows;
renderHeader(); renderBody();
setupChangelogLinks();
if (window.location && window.location.hash === '#changelog') showView('changelog', false);
else showView('matrix', false);
if (window.location && window.location.hash.indexOf('#cell-') === 0) {
  setTimeout(function(){ revealCell(window.location.hash.slice(1)); }, 0);
}
window.addEventListener('resize', function(){ updateColWidths(); scheduleFitAgentHeaderNames(); });
</script>
${pwaScript()}
</body>
</html>`;
}

function pwaHead() {
  return `<meta name="theme-color" content="${PWA.themeColor}">
<link rel="manifest" href="/manifest.json">
<link rel="apple-touch-icon" href="/pwa-icon.svg">`;
}

function pwaScript() {
  return `<script>
if ('serviceWorker' in navigator) window.addEventListener('load', function(){ navigator.serviceWorker.register('/sw.js').catch(function(){}); });
</script>`;
}

function pwaManifest() {
  return JSON.stringify({
    name: PWA.name,
    short_name: PWA.shortName,
    start_url: "/",
    scope: "/",
    display: "standalone",
    background_color: PWA.backgroundColor,
    theme_color: PWA.themeColor,
    icons: [{ src: "/pwa-icon.svg", sizes: "any", type: "image/svg+xml", purpose: "any maskable" }],
  });
}

function pwaIcon() {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" rx="96" fill="${PWA.themeColor}"/><text x="256" y="286" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="150" font-weight="800" fill="#fffdf8">${PWA.label}</text></svg>`;
}

function pwaAsset(url) {
  if (url.pathname === "/manifest.json") return new Response(pwaManifest(), {headers: {"content-type":"application/manifest+json; charset=utf-8","cache-control":"public, max-age=300"}});
  if (url.pathname === "/pwa-icon.svg") return new Response(pwaIcon(), {headers: {"content-type":"image/svg+xml; charset=utf-8","cache-control":"public, max-age=86400"}});
  if (url.pathname === "/sw.js") return new Response("self.addEventListener('install',()=>self.skipWaiting());self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));", {headers: {"content-type":"text/javascript; charset=utf-8","cache-control":"no-cache"}});
  return null;
}

function renderRobots() {
  return `User-agent: *\nAllow: /\nSitemap: ${CANONICAL_ORIGIN}/sitemap.xml\n`;
}
function renderSitemap() {
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>${CANONICAL_ORIGIN}/</loc><lastmod>${new Date().toISOString().slice(0,10)}</lastmod><changefreq>weekly</changefreq><priority>1.0</priority></url>
</urlset>`;
}

const bundleJson = JSON.stringify(matrix, null, 2);

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const pwa = pwaAsset(url);
    if (pwa) return pwa;
    if (env.ASSETS) {
      const asset = await env.ASSETS.fetch(request);
      if (asset.status !== 404) return asset;
    }
    if (url.pathname === "/llms.txt") return new Response(llmsTxt, {headers: {"content-type":"text/plain; charset=utf-8","cache-control":"public, max-age=300"}});
    if (url.pathname === "/deployment-info") return Response.json({
      service: "anysearch-matrix",
      buildMarker: DEPLOYMENT_MARKER,
      providerCount: matrix.length,
    }, {headers: {"cache-control":"no-store"}});
    if (url.pathname === "/robots.txt") return new Response(renderRobots(), {headers: {"content-type":"text/plain; charset=utf-8","cache-control":"public, max-age=86400"}});
    if (url.pathname === "/sitemap.xml") return new Response(renderSitemap(), {headers: {"content-type":"application/xml; charset=utf-8","cache-control":"public, max-age=3600"}});
    if (url.pathname === "/bundle.json") return new Response(bundleJson, {headers: {"content-type":"application/json; charset=utf-8","cache-control":"public, max-age=300","access-control-allow-origin":"*"}});
    return new Response(render(), {headers: {"content-type":"text/html; charset=utf-8","cache-control":"public, max-age=300"}});
  },
};
