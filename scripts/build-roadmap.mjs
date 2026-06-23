// Builds product-backlog/data.json from Linear for the TREAD workflow roadmap.
// Runs in GitHub Actions. Requires env LINEAR_API_KEY (a Linear personal API key).
import { writeFileSync, mkdirSync } from "node:fs";

const API = "https://api.linear.app/graphql";
const KEY = process.env.LINEAR_API_KEY;
if (!KEY) { console.error("Missing LINEAR_API_KEY env var"); process.exit(1); }

// Workflow labels in display order (these are project labels in Linear).
const WORKFLOWS = ["Onboarding","Dispatch Management","Rate Set Up","Data Input","Approvals","Connected Customer Ecosystem","Parent Co View","Exporting","Advanced Billing"];
const IMPACT = { "High Impact":"High", "Medium Impact":"Medium", "Low Impact":"Low" };
const EFFORT = { "High Effort":"High", "Medium Effort":"Medium", "Low Effort":"Low" };
// Sort order within a workflow (by Linear status type), then alphabetical by item.
const STATUS_RANK = { started:0, planned:1, triage:1, backlog:2, paused:3, completed:4, canceled:5 };

async function gql(query, variables) {
  const res = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": KEY },
    body: JSON.stringify({ query, variables }),
  });
  const json = await res.json();
  if (json.errors) throw new Error("GraphQL: " + JSON.stringify(json.errors));
  return json.data;
}

async function paged(field, selection, pageSize = 50) {
  const out = []; let after = null;
  do {
    const data = await gql(
      `query($after:String){ ${field}(first:${pageSize}, after:$after){ pageInfo{ hasNextPage endCursor } nodes{ ${selection} } } }`,
      { after }
    );
    const conn = data[field];
    out.push(...conn.nodes);
    after = conn.pageInfo.hasNextPage ? conn.pageInfo.endCursor : null;
  } while (after);
  return out;
}

function fmtRevenue(r) {
  if (r == null) return "";
  const n = Number(r); if (!n) return "";
  return n >= 1000 ? ` ($${Math.round(n / 1000)}K)` : ` ($${n})`;
}

const projects = await paged("projects",
  "id name url lead{ name } status{ name type } labels{ nodes{ name } } teams{ nodes{ key } }", 50);
const customers = await paged("customers",
  "name revenue needs{ project{ id } }", 40);

// projectId -> ["Customer ($ACV)", ...]
const projCustomers = {};
for (const cu of customers) {
  const tag = cu.name + fmtRevenue(cu.revenue);
  for (const need of (cu.needs || [])) {
    const pid = need.project?.id; if (!pid) continue;
    (projCustomers[pid] ||= []);
    if (!projCustomers[pid].includes(tag)) projCustomers[pid].push(tag);
  }
}

const rows = [];
for (const p of projects) {
  const labels = (p.labels?.nodes || []).map(l => l.name);
  const wf = labels.find(l => WORKFLOWS.includes(l));
  if (!wf) continue; // only include projects tagged with a workflow label
  const keys = (p.teams?.nodes || []).map(t => t.key);
  const platform = [keys.includes("TRE") && "Web", keys.includes("MBL") && "Mobile"].filter(Boolean).join(" + ");
  const flags = [labels.includes("At Risk") && "At Risk", labels.includes("Pause") && "Paused"].filter(Boolean).join(" · ");
  rows.push({
    "Workflow": wf,
    "Item": p.name,
    "Platform": platform,
    "Customers (ACV)": (projCustomers[p.id] || []).join(", "),
    "Impact": labels.map(l => IMPACT[l]).find(Boolean) || "TBD",
    "Effort": labels.map(l => EFFORT[l]).find(Boolean) || "TBD",
    "Vibeable?": labels.includes("Vibeable") ? "Yes" : "TBD",
    "Status": p.status?.name || "",
    "Product Owner": p.lead?.name || "",
    "Notes": flags,
    "PRD Brief Link": p.url || "",
    "_rank": STATUS_RANK[p.status?.type] ?? 9,
  });
}

rows.sort((a, b) => {
  const w = WORKFLOWS.indexOf(a.Workflow) - WORKFLOWS.indexOf(b.Workflow);
  if (w) return w;
  if (a._rank !== b._rank) return a._rank - b._rank;            // by status
  if (a.Status !== b.Status) return a.Status.localeCompare(b.Status);
  return a.Item.localeCompare(b.Item);                          // then A–Z
});
rows.forEach(r => delete r._rank);

mkdirSync("product-backlog", { recursive: true });
writeFileSync("product-backlog/data.json", JSON.stringify({ generatedAt: new Date().toISOString(), rows }, null, 2));
console.log(`Wrote product-backlog/data.json — ${rows.length} roadmap projects.`);
