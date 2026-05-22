#!/usr/bin/env python3
"""Render release-dashboard/index.html in-place using marker-delimited blocks.

Inputs (paths relative to this script's directory):
  - index.html        — has marker pairs: BEGIN/END DATA: releases | themes | generated_at
  - releases.json     — { "releases": [ {ts, version, releaseDate, isMobile, permalink, content}, ... ],
                          "themes":   { "YYYY-MM": { label, narrative, themes, heroFeatures, inProgress }, ... } }

Output: index.html updated in-place, with the three marker blocks replaced.

Usage:
    python3 render.py releases.json index.html
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def js_template_literal_escape(s: str) -> str:
    """Escape a string for safe inclusion inside a JS template literal (backticks)."""
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def js_dq_string_escape(s: str) -> str:
    """Escape a string for a double-quoted JS string."""
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def build_prebaked_js(releases):
    """Return the JS source for the PREBAKED array (no const declaration)."""
    releases_sorted = sorted(
        releases,
        key=lambda r: (r["releaseDate"], float(r.get("ts") or 0)),
        reverse=True,
    )
    lines = ["const PREBAKED = ["]
    for i, r in enumerate(releases_sorted):
        ts = js_dq_string_escape(str(r.get("ts", "")))
        version = js_dq_string_escape(r["version"])
        date = js_dq_string_escape(r["releaseDate"])
        is_mobile = "true" if r.get("isMobile") else "false"
        permalink = js_dq_string_escape(r.get("permalink", ""))
        content = js_template_literal_escape(r["content"])
        suffix = "," if i < len(releases_sorted) - 1 else ""
        lines.append(
            "  {ts:\"" + ts + "\","
            "version:\"" + version + "\","
            "releaseDate:\"" + date + "\","
            "isMobile:" + is_mobile + ","
            "permalink:\"" + permalink + "\","
            "content:`" + content + "`}" + suffix
        )
    lines.append("];")
    return "\n".join(lines)


def build_themes_js(themes):
    """Return the JS source for the MONTHLY_THEMES object."""
    body = json.dumps(themes, indent=2, ensure_ascii=False)
    return "const MONTHLY_THEMES = " + body + ";"


def build_generated_at_js(iso_ts):
    return 'const GENERATED_AT = "' + js_dq_string_escape(iso_ts) + '";'


def replace_marker_block(html: str, marker: str, new_content: str) -> str:
    """Replace content between // === BEGIN DATA: <marker> === and // === END DATA: <marker> ===."""
    pattern = re.compile(
        r"(// === BEGIN DATA: "
        + re.escape(marker)
        + r" ===\n)([\s\S]*?)(\n// === END DATA: "
        + re.escape(marker)
        + r" ===)"
    )
    match = pattern.search(html)
    if not match:
        raise SystemExit(f"Could not find marker block for: {marker}")
    return pattern.sub(lambda m: m.group(1) + new_content + m.group(3), html, count=1)


def main():
    if len(sys.argv) < 3:
        print("Usage: render.py <releases.json> <index.html>", file=sys.stderr)
        sys.exit(2)
    releases_json_path = Path(sys.argv[1])
    html_path = Path(sys.argv[2])

    data = json.loads(releases_json_path.read_text())
    releases = data.get("releases", [])
    themes = data.get("themes", {})

    html = html_path.read_text()
    html = replace_marker_block(html, "releases", build_prebaked_js(releases))
    html = replace_marker_block(html, "themes", build_themes_js(themes))
    iso_ts = datetime.now(timezone.utc).isoformat()
    html = replace_marker_block(
        html,
        "generated_at",
        "// GENERATED_AT is replaced at publish time by the scheduled task.\n"
        + build_generated_at_js(iso_ts),
    )

    html_path.write_text(html)
    print(
        f"Rendered: {len(releases)} releases, themes for {len(themes)} months, "
        f"generated_at={iso_ts}"
    )


if __name__ == "__main__":
    main()
