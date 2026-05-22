# saloni-tread-outputs

Static dashboards published to GitHub Pages.

## Tread Product Release Dashboard

Live URL: **https://saloni-shah-tread.github.io/saloni-tread-outputs/release-dashboard/**

Source data: Saloni's "Release Notes" thread replies in the Tread `#shipit` Slack channel.

Republished automatically every day at 8am ET by a Cowork scheduled task that:
1. Fetches the latest release notes from Slack
2. Generates monthly themes for any new month
3. Regenerates the static HTML and pushes here

To regenerate manually, run the scheduled task in Cowork.

Last generated: see the "Generated" timestamp in the top right of the dashboard.
