# Windows guide

Auto Zoom Leaver for Windows is distributed as an unsigned executable. It
uses Zoom's Microsoft UI Automation controls to read participant counts and
select the exact `Leave Meeting` action.

## Download and install

1. Open the successful `Windows application` GitHub Actions run for the
   repository's commit. The workflow is linked from [the Windows workflow](../.github/workflows/windows.yml).
2. Download the `AutoZoomLeaver-windows` artifact and extract it.
3. Keep `AutoZoomLeaver.exe` in a folder you control. No Python, Git, or
   repository checkout is required.

The executable is unsigned, so Windows SmartScreen may warn before it opens.
Continue only after checking that the file came from the repository's own
`Windows application` Actions run and that you downloaded it from GitHub.

## First run and configuration

Open PowerShell in the extracted folder and run:

```powershell
.\AutoZoomLeaver.exe --self-test
.\AutoZoomLeaver.exe
```

The self-test checks configuration access and the Windows UI Automation
backend. The normal program opens a menu where you can set the participant
threshold, polling interval, auto-start, and activity logging.

The program stores its settings at:

```text
%LOCALAPPDATA%\AutoZoomLeaver\config.json
```

## Test detection

Use a disposable Zoom meeting. Start the program and choose `Test Zoom
participant detection`. The participant count should appear when Zoom's
participant panel is available. Start monitoring and confirm that the program
does nothing while the count is above the configured threshold.

When the count reaches or falls below the threshold, verify that the program
opens Zoom's leave prompt and invokes `Leave Meeting`. It must never invoke
`End Meeting for All`. Test with Zoom minimized and with the participant panel
open and closed. The [Windows diagnostic guide](WINDOWS_DIAGNOSTIC.md) explains
how to inspect a Zoom accessibility tree without clicking any controls.

## Logs

When activity logging is enabled, the log is written to:

```text
%LOCALAPPDATA%\AutoZoomLeaver\activity.log
```

## Troubleshooting

- If `--self-test` fails, confirm that you are running the executable on
  Windows and that Zoom is installed. The program needs the Windows UI
  Automation backend.
- If the participant count is unavailable, open Zoom's participant panel and
  confirm that Zoom is using its English interface.
- If leaving is cancelled, the app fails closed when it cannot find exactly
  one enabled `Leave Meeting` button. Check the log and leave the meeting
  manually.
- If SmartScreen warns, do not bypass it for a file from an unknown source.
  Re-download the artifact from the repository's own Actions run.

## Removal

Exit the program, delete `AutoZoomLeaver.exe`, then delete
`%LOCALAPPDATA%\AutoZoomLeaver` if you also want to remove its settings and
logs.

## Current limitations

- Windows 10 and 11 are the target platforms, but live Zoom checks still need
  a Windows machine and a disposable meeting.
- The current selectors support Zoom's English desktop interface. Zoom web
  meetings and other languages are not supported.
- The executable is unsigned. There is no installer, tray UI, auto-update, or
  code-signing step.

See the [project status](../PROJECT_STATUS.md) and the [main README](../README.md)
for the rest of the project.
