# Observatory frontend: state, provenance and interaction review

Baseline inspected: `11a561623b7539f1f9bf20f8ef7bc5b9706c10d2`.
Scope: `gobbler-flyte/observatory.js`, `observatory.css` and `index.html`.
The existing X3D artwork, twelve domain stories, original opt-in soundtrack,
archived Atlas bytes and synthetic teaching sequence are preserved.

The useful improvement is an explicit distinction between an intended action,
an asynchronously completed operation, and a claim the page is ready to make.
This is the same distinction needed between a stored graph, a current witness
and a visual depiction of either.

## Findings and implemented responses

| Baseline behavior | Concrete trigger | Implemented response |
| --- | --- | --- |
| Scene loading could wait indefinitely | `browser.loadURL()` or a response body never settles | Header and body waits are bounded; scene startup has a separate 45-second budget. Timeout is an error, not readiness. |
| Pending startup could populate state after leaving | Page closes while the scene Promise is pending | Lifecycle cancellation stops controller waits and rejects late commits. A nonpersisted `pagehide` disposes the controller. |
| Search compared query text only after success | An old failed Atlas request settles after the user clears or changes the query | Each search has an intent revision. Both successful results and errors check it; abandoned failures do not replace the current message or open an error notice. |
| rAF and SAI callbacks had no release path | Repeated navigation or a partially failed initialization | Dispose cancels the controller frame/timer, removes registered listeners and all sensor callbacks, and pauses audio. Partial scene-hookup failure removes already attached callbacks. |
| Audio could finish starting after shutdown | `audio.play()` resolves after `pagehide` or disposal | The completion checks lifecycle state and pauses again; it never labels a disposed player as sounding. |
| Reduced motion was checked once | OS/browser preference changes after startup | A newly enabled reduced-motion preference pauses scene clocks. Disabling the preference does not override the user's pause decision. |
| Tabs supplied ARIA roles without the matching keyboard behavior | Arrow/Home/End navigation of the tablist | The three tabs have controls/panel relationships, a roving tab stop and standard wraparound arrow navigation. |
| Nonfatal errors were console-only | Missing guard report, hash mismatch, rejected playback | A bounded diagnostic list and a visible live-status notice retain the error. The current graph remains unavailable when its bytes fail the expected digest. |
| Guard inspector hardcoded a passing narrative | Loaded saved report contains a failing fixture | Text derives the met-expectation count and overall result from the loaded report. It identifies the JSON as a recorded Python report, not a new execution or freshness certificate. |
| UI cadence could sound like renderer evidence | rAF counter reports a high value | The on-page label explicitly says UI cadence is not GPU timing. Hidden pages stop this controller's cadence sampling. |

The tab header now says **compiled archive / recorded counts**. Loading a
precompiled manifest is not a fresh recount by the browser. Atlas search still
loads the original archive lazily and checks its SHA-256 against the manifest
before returning records. Those matching bytes do not authenticate an author.

The new Intervention lab link opens the separate, substantive experiment page
added by the main integration pass; it does not change the evidence grade of
the existing domain feathers.

## Readiness and diagnostic contract

`window.__flywheel` is retained for diagnostics and native acceptance tools:

| Field | Meaning |
| --- | --- |
| `status` | `loading`, `ready`, `error` or `disposed`; mirrored in `document.body.dataset.state` |
| `ready` | True only after manifest loading, scene loading and the required controller hookups complete |
| `atlasHashVerified` | Set only after an actual lazy Atlas load matches the expected digest; initial readiness does not assert this |
| `errors` | Last forty reported controller errors; an abandoned request's error is suppressed |
| `scene`, `browser` | Current diagnostic references; released from controller state on disposal |
| `paused` | Current explicit clock-pause state |
| `uiHz` | Controller rAF cadence; not GPU frame time, presentation rate or throughput |

A native test should wait for `ready === true` or `status === 'error'`, and
require the former before asserting success. Merely leaving the text “Opening
the loom” also occurs on failure and is insufficient acceptance evidence.

Timeout/cancellation ends this controller's wait and prevents its stale commits.
It does not claim to abort the browser's underlying fetch, destroy the X_ITE
graphics context or cancel a native scene parse already underway. On a browser
back-forward-cache transition, the controller retains its scene, stops cadence
and pauses sound; restoration restarts cadence without autoplaying audio.

## Executed controls

Run:

```bash
node tools/observatory-controls.test.mjs
```

Twelve controls execute the actual controller module using a small DOM, SAI and
media adapter. They test independent task keys, timeout rejection, readiness
after deferred scene completion, disposal of callbacks and frames, late-load
refusal, cancellation without network completion, partial-hookup cleanup,
reduced-motion changes, hidden-page sampling, tab keyboard behavior, stale
search errors, Atlas digest refusal, late playback and report-derived guard
status. Several control rows deliberately combine related assertions.

This is controller evidence. The adapters do not execute native X_ITE field
semantics, browser Workers, a screen reader, an audio device or rendered pixels.
Fresh native browser/picking/mobile acceptance and a listening review remain
separate gates owned by the repository's runtime validation work.

The browser module has no relative JavaScript imports. Its exact three local
fetch call strings, the scene-load statement and existing standalone setup
anchors remain intact so the separate single-file builder can replace owned
resources deterministically. Exports support Node data-URL testing and remain
legal inside the generated inline module. The generated export must still be
rebuilt and checked after changes.

## Next bounded improvements

1. Add native browser fault injection for delayed response bodies, missing
   sensors and context loss; require visible errors and a stopped readiness flag.
2. Exercise keyboard focus and dialog return behavior with a real screen reader
   and mobile browser. The current tab fix is not a complete accessibility audit.
3. Measure parse/commit time and renderer frame timing separately from UI
   cadence, with identical scene detail and camera settings.
4. Give each recorded guard report an explicit source/tool/input freshness check
   before offering a stronger “current execution” label.
5. Add an inspectable relation legend and search facets without treating visual
   prominence, rotation or particle activity as evidence of repository progress.
