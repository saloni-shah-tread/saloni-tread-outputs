#!/usr/bin/env python3
"""Renders the CUS Backlog Dashboard HTML from data.json.
Usage: python3 render.py [data.json] [index.html]
"""
import sys, json, datetime, os

def main():
    data_path = sys.argv[1] if len(sys.argv) > 1 else 'data.json'
    out_path  = sys.argv[2] if len(sys.argv) > 2 else 'index.html'
    with open(data_path) as f:
        data_json_str = f.read()
    generated_at = datetime.datetime.now().strftime("%B %d, %Y")
    template = TEMPLATE
    html = template.replace("__DATA__", data_json_str).replace("__GENERATED__", generated_at)
    with open(out_path, 'w') as f:
        f.write(html)
    print(f"Wrote {out_path} ({len(html)} chars)")

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Tread Customer Backlog Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root { color-scheme: light; }
* { box-sizing: border-box; }
html, body {
  margin: 0; padding: 0;
  background: #f7f8fa;
  color: #1a1d29;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 14px; line-height: 1.5;
}
.wrap { max-width: 1280px; margin: 0 auto; padding: 24px 20px 60px; }

/* Header */
.header { display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 12px; margin-bottom: 24px; }
.brand-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.brand-mark { display: block; }
.brand-name { font-size: 12px; font-weight: 800; letter-spacing: 0.16em; color: #0a1929; }
.title { font-size: 32px; font-weight: 800; color: #0a1929; letter-spacing: -0.02em; margin: 0 0 6px; line-height: 1.1; }
.subtitle { color: #6a7280; font-size: 13px; margin: 0; }
.refresh-meta { font-size: 12px; color: #8a93a4; }

/* Stats */
.stats { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 24px; }
.stat { background: #fff; border: 1px solid #e7eaf1; border-radius: 10px; padding: 14px 16px; }
.stat-label { color: #6a7280; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.stat-value { font-size: 24px; font-weight: 700; color: #0a1929; margin-top: 4px; line-height: 1.1; }
.stat-sub { font-size: 11px; color: #8a93a4; margin-top: 2px; }
.stat.accent { border-left: 3px solid #FFD400; }
.stat.bug .stat-value { color: #b5325b; }
.stat.feature .stat-value { color: #1d5fb3; }
.stat.urgent .stat-value { color: #b5710a; }

/* Tabs */
.tabs { display: inline-flex; background: #fff; border: 1px solid #e7eaf1; border-radius: 10px; padding: 4px; gap: 2px; margin-bottom: 18px; flex-wrap: wrap; }
.tab { background: transparent; border: 0; padding: 9px 14px; border-radius: 7px; font-size: 13px; font-weight: 700; color: #4b5161; cursor: pointer; letter-spacing: 0.01em; }
.tab:hover { color: #0a1929; }
.tab.active { background: #0a1929; color: #fff; box-shadow: inset 0 -3px 0 #FFD400; }
.tab .count { opacity: 0.6; font-weight: 500; margin-left: 5px; font-size: 11px; }
.tab.active .count { opacity: 0.85; }

/* Filters */
.filters { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 14px; padding: 14px 16px; background: #fff; border: 1px solid #e7eaf1; border-radius: 10px; }
.filters .search { flex: 1; min-width: 220px; }
.filters input, .filters select { width: 100%; padding: 8px 11px; border: 1px solid #d6dbe6; border-radius: 7px; background: #fff; font-size: 13px; color: #1a1d29; outline: none; font-family: inherit; }
.filters input:focus, .filters select:focus { border-color: #FFD400; box-shadow: 0 0 0 3px rgba(255, 212, 0, 0.25); }
.filters select { width: auto; min-width: 130px; cursor: pointer; }
.filters .reset { background: #f4f5f9; border: 1px solid #d6dbe6; padding: 7px 12px; border-radius: 7px; cursor: pointer; font-size: 13px; color: #4b5161; font-weight: 500; }
.filters .reset:hover { background: #e7eaf1; color: #0a1929; }
.filters .count-readout { margin-left: auto; font-size: 12px; color: #8a93a4; font-weight: 500; }

/* Table */
.table-wrap { background: #fff; border: 1px solid #e7eaf1; border-radius: 10px; overflow-x: auto; -webkit-overflow-scrolling: touch; }
table { width: 100%; border-collapse: collapse; font-size: 13px; min-width: 1100px; }
thead th { text-align: left; padding: 11px 12px; background: #fafbfd; border-bottom: 1px solid #e7eaf1; font-weight: 700; font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.08em; color: #6a7280; white-space: nowrap; cursor: pointer; user-select: none; }
thead th:hover { color: #0a1929; background: #f4f5f9; }
thead th.sorted-asc::after { content: " ↑"; color: #FFD400; }
thead th.sorted-desc::after { content: " ↓"; color: #FFD400; }
tbody tr { border-bottom: 1px solid #f0f2f7; transition: background 0.1s; }
tbody tr:last-child { border-bottom: 0; }
tbody tr:hover { background: #fafbfd; }
tbody td { padding: 12px; vertical-align: top; }
tbody tr.row-done { opacity: 0.55; }

.id-cell { white-space: nowrap; }
.id-link { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; font-weight: 700; color: #0a1929; text-decoration: none; }
.id-link:hover { color: #FFD400; }
.item-num { font-size: 10.5px; color: #8a93a4; margin-top: 2px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-weight: 600; }
.unparsed-tag { font-size: 9.5px; color: #b5710a; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 3px; }

.title-cell { max-width: 360px; }
.title-cell .title-txt { color: #0a1929; font-weight: 600; line-height: 1.4; font-size: 13.5px; }
.title-cell .parent { color: #8a93a4; font-size: 11.5px; margin-top: 4px; line-height: 1.35; }
.customer { font-weight: 600; color: #1a1d29; white-space: nowrap; font-size: 13px; }
.customer.none { color: #c8cdd8; font-weight: 400; font-style: italic; }
.requester { color: #4b5161; white-space: nowrap; font-size: 12.5px; }
.requester.none { color: #c8cdd8; font-style: italic; }

.chip { display: inline-block; font-size: 10px; padding: 3px 8px; border-radius: 999px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; white-space: nowrap; }
.chip-bug { background: #fdebef; color: #b5325b; }
.chip-feature { background: #eef7ff; color: #1d5fb3; }
.chip-needs { background: #FFF8C2; color: #0a1929; }
.chip-other { background: #f4ecff; color: #6c3fb8; }
.chip-unknown { background: #f4f5f9; color: #6a7280; }

.prio { display: inline-block; padding: 3px 8px; border-radius: 999px; font-size: 10.5px; font-weight: 700; white-space: nowrap; }
.prio-1 { background: #fdebef; color: #b5325b; }
.prio-2 { background: #fff7e6; color: #b5710a; }
.prio-3 { background: #FFF8C2; color: #8a6f00; }
.prio-4 { background: #eef7ff; color: #1d5fb3; }
.prio-0 { background: #f4f5f9; color: #8a93a4; }
.prio-blank { color: #c8cdd8; font-style: italic; font-size: 12px; }

.status { display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 10.5px; font-weight: 600; white-space: nowrap; }
.status-backlog { background: #f4f5f9; color: #4b5161; }
.status-unstarted { background: #f4ecff; color: #6c3fb8; }
.status-started { background: #eef7ff; color: #1d5fb3; }
.status-completed { background: #d1fae5; color: #065f46; }
.status-canceled { background: #f4f5f9; color: #8a93a4; text-decoration: line-through; }
.status-duplicate { background: #f4f5f9; color: #8a93a4; }
.status-triage { background: #fff7e6; color: #b5710a; }
.status-unknown { background: #f4f5f9; color: #c8cdd8; }

.eng-cell { max-width: 220px; }
.eng-item { display: flex; gap: 6px; align-items: center; line-height: 1.3; flex-wrap: wrap; }
.eng-item a { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px; color: #0a1929; text-decoration: none; flex-shrink: 0; font-weight: 600; }
.eng-item a:hover { color: #FFD400; }
.eng-item .status { font-size: 9.5px; padding: 2px 6px; }
.eng-item .eng-title { color: #8a93a4; font-size: 11px; flex: 1 1 100%; padding-left: 4px; line-height: 1.3; }
.eng-none { color: #c8cdd8; font-style: italic; font-size: 12px; }

.date-cell { color: #6a7280; font-size: 12px; white-space: nowrap; font-weight: 500; }

.empty { padding: 40px; text-align: center; color: #8a93a4; background: #fff; border: 1px dashed #d6dbe6; border-radius: 10px; }
.footer-note { margin-top: 24px; padding: 14px 16px; background: #fff; border: 1px solid #e7eaf1; border-radius: 10px; color: #6a7280; font-size: 12px; line-height: 1.6; }
.footer-note b { color: #0a1929; }

@media (max-width: 960px) {
  .stats { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 640px) {
  .stats { grid-template-columns: repeat(2, 1fr); }
  .filters select { width: 100%; min-width: 0; }
  thead th { font-size: 9.5px; padding: 8px; }
  tbody td { padding: 9px 8px; }
}
</style>
</head>
<body>
<div class="wrap">

  <div class="header">
    <div>
      <div class="brand-row">
        <svg class="brand-mark" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <path d="M2 22 L12 4 L22 22 Z" fill="#0a1929"/>
          <path d="M9 22 L12 16 L15 22 Z" fill="#FFD400"/>
        </svg>
        <span class="brand-name">TREAD</span>
      </div>
      <h1 class="title">Customer Backlog Dashboard</h1>
      <p class="subtitle">Bugs and feature requests parsed from Customer Success (CUS) ticket auto-triage analyses</p>
    </div>
    <div class="refresh-meta">Generated __GENERATED__</div>
  </div>

  <div class="stats" id="stats"></div>
  <div class="tabs" id="tabs"></div>

  <div class="filters">
    <div class="search"><input type="text" id="search" placeholder="Search title, CUS ID, customer, or requester…"></div>
    <select id="customerFilter"><option value="">All customers</option></select>
    <select id="requesterFilter"><option value="">All requesters</option></select>
    <select id="priorityFilter">
      <option value="">All priorities</option>
      <option value="1">Urgent / P0 / P1</option>
      <option value="2">High</option>
      <option value="3">Medium / P2 / P3</option>
      <option value="4">Low / P4</option>
      <option value="-1">Not stated</option>
    </select>
    <select id="statusFilter">
      <option value="open">Open only</option>
      <option value="all">All statuses</option>
      <option value="done">Done / Closed only</option>
    </select>
    <select id="engFilter">
      <option value="">Any eng state</option>
      <option value="linked">Has linked TRE</option>
      <option value="none">No eng ticket</option>
    </select>
    <button class="reset" id="resetBtn">Reset</button>
    <span class="count-readout" id="resultCount"></span>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th data-sort="rowId">Item</th>
          <th data-sort="classification">Type</th>
          <th data-sort="itemTitle" class="title-cell">Title</th>
          <th data-sort="customer">Customer</th>
          <th data-sort="priorityValue">Priority</th>
          <th data-sort="cusStatus">CUS Status</th>
          <th>Linked Eng</th>
          <th data-sort="requester">Requester</th>
          <th data-sort="createdAt">Created</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
    </table>
    <div id="empty" class="empty" style="display:none;">No items match the current filters.</div>
  </div>

  <div class="footer-note" id="footer"></div>
</div>

<script>
const RAW_DATA = __DATA__;

document.getElementById('footer').innerHTML = `<b>${RAW_DATA.length} action items</b> parsed from auto-triage comments. Items are extracted per-bug/per-feature from the triage analysis; tickets without a structured triage appear as a single row. Priority is shown only when set on the CUS ticket, on a P-label, or stated in the triage. Row open/done reflects the CUS ticket's status. Data refreshes daily at 8:15 AM PT via a scheduled task.`;

const state = { classification: 'all', search: '', customer: '', requester: '', priority: '', statusGroup: 'open', eng: '', sortKey: 'priorityValue', sortDir: 'desc' };

function priorityRank(v) { if (v === -1) return -1; if (v === 0) return 0; return 5 - v; }
function isOpen(t) { return t.rowOpen; }
function fmtDate(s) { if (!s) return ''; const d = new Date(s); const m = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getMonth()]; return `${m} ${d.getDate()}`; }
function esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function classChip(c) {
  if (c === 'Bug') return '<span class="chip chip-bug">Bug</span>';
  if (c === 'Feature Request') return '<span class="chip chip-feature">Feature</span>';
  if (c === 'Needs More Info') return '<span class="chip chip-needs">Needs Info</span>';
  if (c === 'Other' || c === 'Mixed') return '<span class="chip chip-other">Other</span>';
  return '<span class="chip chip-unknown">Unclassified</span>';
}
function prioBadge(p, v) { if (v === -1) return '<span class="prio-blank">—</span>'; return `<span class="prio prio-${v}">${esc(p)}</span>`; }
function statusBadge(s, t) { return `<span class="status status-${t || 'unknown'}">${esc(s || '—')}</span>`; }

function buildOptions(selectId, values) { const sel = document.getElementById(selectId); values.forEach(v => { const o = document.createElement('option'); o.value = v; o.textContent = v; sel.appendChild(o); }); }
function buildFilters() {
  const customers = [...new Set(RAW_DATA.map(t => t.customer).filter(Boolean))].sort();
  const requesters = [...new Set(RAW_DATA.map(t => t.requester).filter(Boolean))].sort();
  buildOptions('customerFilter', customers); buildOptions('requesterFilter', requesters);
}

function getFiltered() {
  let list = RAW_DATA.slice();
  if (state.classification !== 'all') list = list.filter(t => t.classification === state.classification);
  if (state.statusGroup === 'open') list = list.filter(isOpen);
  else if (state.statusGroup === 'done') list = list.filter(t => !isOpen(t));
  if (state.customer) list = list.filter(t => t.customer === state.customer);
  if (state.requester) list = list.filter(t => t.requester === state.requester);
  if (state.priority !== '') { const v = parseInt(state.priority); list = list.filter(t => t.priorityValue === v); }
  if (state.eng === 'linked') list = list.filter(t => t.linkedTre);
  else if (state.eng === 'none') list = list.filter(t => !t.linkedTre);
  if (state.search) {
    const q = state.search.toLowerCase();
    list = list.filter(t => t.cusId.toLowerCase().includes(q) || (t.itemTitle || '').toLowerCase().includes(q) || (t.cusTitle || '').toLowerCase().includes(q) || (t.customer || '').toLowerCase().includes(q) || (t.requester || '').toLowerCase().includes(q));
  }
  const key = state.sortKey, dir = state.sortDir === 'asc' ? 1 : -1;
  list.sort((a, b) => {
    let av, bv;
    if (key === 'priorityValue') { av = priorityRank(a.priorityValue); bv = priorityRank(b.priorityValue); }
    else if (key === 'rowId' || key === 'cusId') { const an = parseInt(a.cusId.split('-')[1]||0), bn = parseInt(b.cusId.split('-')[1]||0); av = an*100 + a.itemNum; bv = bn*100 + b.itemNum; }
    else if (key === 'createdAt') { av = new Date(a.createdAt).getTime(); bv = new Date(b.createdAt).getTime(); }
    else { av = (a[key] || '').toString().toLowerCase(); bv = (b[key] || '').toString().toLowerCase(); }
    if (av < bv) return -1 * dir; if (av > bv) return 1 * dir; return 0;
  });
  return list;
}

function renderStats() {
  const open = RAW_DATA.filter(isOpen);
  const cards = [
    {label: 'Total open', value: open.length, sub: `${RAW_DATA.length} action items`, cls: 'accent'},
    {label: 'Open bugs', value: open.filter(t => t.classification === 'Bug').length, sub: '', cls: 'bug'},
    {label: 'Open features', value: open.filter(t => t.classification === 'Feature Request').length, sub: '', cls: 'feature'},
    {label: 'Urgent / P0', value: open.filter(t => t.priorityValue === 1).length, sub: 'priority', cls: 'urgent'},
    {label: 'Eng tracked', value: open.filter(t => t.linkedTre).length, sub: 'linked TRE'},
    {label: 'No eng ticket', value: open.filter(t => !t.linkedTre).length, sub: 'not yet filed'},
  ];
  document.getElementById('stats').innerHTML = cards.map(c => `<div class="stat ${c.cls || ''}"><div class="stat-label">${esc(c.label)}</div><div class="stat-value">${esc(c.value)}</div><div class="stat-sub">${esc(c.sub)}</div></div>`).join('');
}

function renderTabs() {
  const open = RAW_DATA.filter(isOpen);
  const tabs = [{key:'all',label:'All Open'},{key:'Bug',label:'Bugs'},{key:'Feature Request',label:'Feature Requests'},{key:'Needs More Info',label:'Needs Info'},{key:'Other',label:'Other'},{key:'Unknown',label:'Unclassified'}];
  const counts = { all: open.length, Bug: open.filter(t => t.classification === 'Bug').length, 'Feature Request': open.filter(t => t.classification === 'Feature Request').length, 'Needs More Info': open.filter(t => t.classification === 'Needs More Info').length, Other: open.filter(t => t.classification === 'Other' || t.classification === 'Mixed').length, Unknown: open.filter(t => t.classification === 'Unknown').length };
  const c = document.getElementById('tabs');
  c.innerHTML = tabs.map(t => `<button class="tab ${state.classification===t.key?'active':''}" data-key="${t.key}">${esc(t.label)}<span class="count">${counts[t.key]}</span></button>`).join('');
  c.querySelectorAll('.tab').forEach(btn => btn.addEventListener('click', () => { state.classification = btn.dataset.key; renderTabs(); renderTable(); }));
}

function renderTable() {
  const list = getFiltered();
  document.getElementById('resultCount').textContent = `${list.length} item${list.length===1?'':'s'}`;
  const tbody = document.getElementById('tbody'); const empty = document.getElementById('empty');
  if (list.length === 0) { tbody.innerHTML = ''; empty.style.display = 'block'; } else {
    empty.style.display = 'none';
    tbody.innerHTML = list.map(t => {
      const engHtml = !t.linkedTre ? '<span class="eng-none">— no eng ticket</span>' : `<div class="eng-item"><a href="${esc(t.linkedTreUrl)}" target="_blank" rel="noopener">${esc(t.linkedTre)}</a>${statusBadge(t.linkedTreStatus, t.linkedTreStatusType)}${t.linkedTreTitle ? `<div class="eng-title">${esc(t.linkedTreTitle)}</div>` : ''}</div>`;
      const isDone = !isOpen(t);
      const parentBlock = t.itemTitle !== t.cusTitle ? `<div class="parent">↳ from ${esc(t.cusTitle)}</div>` : '';
      const unparsedTag = t.isUnparsed ? `<div class="unparsed-tag">unparsed</div>` : '';
      return `<tr class="${isDone?'row-done':''}"><td class="id-cell"><a href="${esc(t.cusUrl)}" target="_blank" rel="noopener" class="id-link">${esc(t.cusId)}</a>${t.showItemNum ? `<div class="item-num">#${t.itemNum}</div>` : ''}${unparsedTag}</td><td>${classChip(t.classification)}</td><td class="title-cell"><div class="title-txt">${esc(t.itemTitle)}</div>${parentBlock}</td><td><span class="customer ${t.customer?'':'none'}">${esc(t.customer || '—')}</span></td><td>${prioBadge(t.priority, t.priorityValue)}</td><td>${statusBadge(t.cusStatus, t.cusStatusType)}</td><td class="eng-cell">${engHtml}</td><td><span class="requester ${t.requester?'':'none'}">${esc(t.requester || '—')}</span></td><td class="date-cell">${fmtDate(t.createdAt)}</td></tr>`;
    }).join('');
  }
  document.querySelectorAll('thead th').forEach(th => { th.classList.remove('sorted-asc','sorted-desc'); if (th.dataset.sort === state.sortKey) th.classList.add(state.sortDir === 'asc' ? 'sorted-asc' : 'sorted-desc'); });
}

document.querySelectorAll('thead th[data-sort]').forEach(th => { th.addEventListener('click', () => { const k = th.dataset.sort; if (state.sortKey === k) state.sortDir = state.sortDir === 'asc' ? 'desc' : 'asc'; else { state.sortKey = k; state.sortDir = k === 'priorityValue' ? 'desc' : 'asc'; } renderTable(); }); });
document.getElementById('search').addEventListener('input', e => { state.search = e.target.value; renderTable(); });
document.getElementById('customerFilter').addEventListener('change', e => { state.customer = e.target.value; renderTable(); });
document.getElementById('requesterFilter').addEventListener('change', e => { state.requester = e.target.value; renderTable(); });
document.getElementById('priorityFilter').addEventListener('change', e => { state.priority = e.target.value; renderTable(); });
document.getElementById('statusFilter').addEventListener('change', e => { state.statusGroup = e.target.value; renderTable(); });
document.getElementById('engFilter').addEventListener('change', e => { state.eng = e.target.value; renderTable(); });
document.getElementById('resetBtn').addEventListener('click', () => { state.search = ''; state.customer = ''; state.requester = ''; state.priority = ''; state.statusGroup = 'open'; state.eng = ''; document.getElementById('search').value = ''; document.getElementById('customerFilter').value = ''; document.getElementById('requesterFilter').value = ''; document.getElementById('priorityFilter').value = ''; document.getElementById('statusFilter').value = 'open'; document.getElementById('engFilter').value = ''; renderTable(); });

buildFilters(); renderStats(); renderTabs(); renderTable();
</script>
</body>
</html>
"""

if __name__ == '__main__':
    main()
