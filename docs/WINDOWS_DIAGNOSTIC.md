# Windows Zoom diagnostic

The diagnostic reads Zoom's Microsoft UI Automation tree. It does not send
keyboard input, click controls, invoke buttons, or modify Zoom.

## Get the executable

Open the successful `Windows Zoom diagnostic` GitHub Actions run and download
the `AutoZoomLeaverDiagnostic-windows` artifact. Extract the executable on the
Windows laptop. Git, Python, and a repository checkout are not required.

## Perform the captures

Use disposable meetings and keep the Zoom window visible.

1. Start a meeting as a participant. Open the participant panel, leave the
   meeting state visible, and choose the participant meeting capture.
2. As a participant, manually press `Alt+Q` in Zoom. Leave the prompt visible,
   do not click a button, and choose the participant leave-prompt capture.
3. Start a disposable meeting as host. Manually press `Alt+Q` in Zoom. Leave
   the prompt visible, do not click a button, and choose the host leave-prompt
   capture.

The executable asks for each capture in order. Press Enter in its console only
when the requested Zoom state is ready. The executable never presses Enter in
Zoom.

## Return the report

After all three captures succeed, the executable writes one sanitized file at
`%LOCALAPPDATA%\AutoZoomLeaver\report.json`. Send that `report.json` file to
Aki. If Zoom is missing or its UI Automation tree cannot be read, the program
prints an actionable error and writes no report.

The report includes process name, control type, class name, automation ID,
control hierarchy, and normalized participant-count or leave-action labels.
Participant names, email addresses, meeting IDs, meeting topics, and unknown
text become `<redacted>` before the report is written.

The returned report's selector findings are recorded in
`docs/WINDOWS_ZOOM_SELECTORS.md`, with a sanitized fixture at
`tests/fixtures/windows_zoom_report.json`.
