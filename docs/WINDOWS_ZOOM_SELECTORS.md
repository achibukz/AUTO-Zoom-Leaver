# Windows Zoom selector notes

These notes come from the sanitized Windows report returned after running the
diagnostic in three disposable meeting states. The checked-in fixture keeps the
selector-relevant records from that report. It does not reproduce every
redacted UI Automation node.

## Observed controls

| State | Observed control | Details |
| --- | --- | --- |
| Participant meeting | Participant count | `Window`, class `ZPlistPopupContainerWndClass`, hierarchy `Window`, label `Participants (2)` |
| Participant leave prompt | Safe leave action | `Button`, hierarchy `Window > Pane > Button`, label `Leave Meeting` |
| Host leave prompt | Safe leave action | `Button`, hierarchy `Window > Pane > Button`, label `Leave Meeting` |
| Host leave prompt | Destructive action | `Button`, hierarchy `Window > Pane > Button`, label `End Meeting for All` |
| Host leave prompt | Participant count | `Window`, class `ZPlistPopupContainerWndClass`, hierarchy `Window`, label `Participants (1)` |

The participant leave prompt also exposed `Participants (2)`. The host prompt
exposed both leave-action labels at the same hierarchy, so control type and
hierarchy alone cannot identify the safe action.

## Selector rules for the next slice

- Inspect every `Zoom.exe` process and its UI Automation windows.
- Parse participant counts from normalized participant labels instead of relying
  on a top-level window title.
- Match the exact accessible label `Leave Meeting` for the safe action.
- Require exactly one matching `Leave Meeting` button before invoking it.
- Fail closed when no safe button or more than one safe button is present.
- Never match or invoke `End Meeting for All`, even when it is a sibling of the
  safe button.

The report contained two `Zoom.exe` process records in each capture. The
participant-meeting, participant-leave-prompt, and host-leave-prompt captures
contained 183, 261, and 252 controls respectively. The button controls had no
stable class name or automation ID, so those fields are not selector inputs for
the leave action.

The captured report used English Zoom labels. Localization and Zoom versions
that expose different UI Automation names remain outside this slice.
