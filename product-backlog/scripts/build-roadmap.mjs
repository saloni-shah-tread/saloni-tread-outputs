name: Refresh roadmap from Linear

on:
  schedule:
    - cron: "0 * * * *"      # hourly (UTC)
  workflow_dispatch:          # lets you run it manually from the Actions tab

permissions:
  contents: write

concurrency:
  group: refresh-roadmap
  cancel-in-progress: true

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Build data.json from Linear
        env:
          LINEAR_API_KEY: ${{ secrets.LINEAR_API_KEY }}
        run: node scripts/build-roadmap.mjs

      - name: Commit if changed
        run: |
          git config user.name  "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add product-backlog/data.json
          if git diff --staged --quiet; then
            echo "No changes."
          else
            git commit -m "Refresh roadmap data ($(date -u +%FT%TZ))"
            git push
          fi
