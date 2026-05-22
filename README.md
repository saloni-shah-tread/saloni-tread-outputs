# saloni-tread-outputs

Static dashboards published to GitHub Pages.

## Tread Product Release Dashboard

**Live URL:** https://saloni-shah-tread.github.io/saloni-tread-outputs/release-dashboard/

Source data: Saloni's "Release Notes" thread replies in the Tread `#shipit` Slack channel.

### Auto-update

Republished automatically every morning by a Cowork scheduled task that:

1. Pulls the latest `Release Notes` posts from #shipit (last 90 days)
2. Merges them into `release-dashboard/releases.json`
3. Generates monthly themes for any new month via Claude
4. Runs `release-dashboard/render.py` to rewrite `index.html` in-place
5. Commits and pushes here

### Files

- `release-dashboard/index.html` — the published page. Three marker-delimited blocks inside the script tag get auto-overwritten:
  - `BEGIN/END DATA: releases` — the `const PREBAKED = [...]` array
  - `BEGIN/END DATA: themes` — the `const MONTHLY_THEMES = {...}` object
  - `BEGIN/END DATA: generated_at` — the build timestamp shown in the page header
- `release-dashboard/releases.json` — canonical data store (releases + monthly themes)
- `release-dashboard/render.py` — renderer that overwrites the marker blocks
- `.nojekyll` — disables Jekyll so Pages serves the file literally

### Manual regenerate (locally)

```bash
cd release-dashboard
python3 render.py releases.json index.html
```
