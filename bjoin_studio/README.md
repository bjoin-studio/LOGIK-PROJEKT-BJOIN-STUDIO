# bjoin_studio — studio additions to LOGIK-PROJEKT

Everything bjoin studio adds to projekt creation, kept in ONE package with ONE
call site (`src/core/projekt_manager/projekt_creator.py`, step 18.5) so that
merging upstream is a re-drop and a one-line re-add, not an archaeology dig.

## Why

Creating a projekt is only half of making it usable. The station must also
register it with the iteration-mirror agent, and in time with Kitsu, Frame.io,
the job config, Dropbox. Doing that by hand is how LC-26_677 got a mirror conf
line that was added but never activated — the watcher ran for days on a stale
project list and nobody noticed.

## Adding a hook

Drop `hooks/hook_NN_<name>.py` exposing `run(ctx) -> dict`. Filename order is
run order. Two rules:

1. **Never raise.** The runner isolates you, but a hook that reliably throws
   still costs a shoot morning of confusion. A projekt that is created but not
   registered is recoverable; a creation that dies at step 18.5 is not.
2. **Be idempotent.** Re-running against an existing projekt is supported and
   is how we backfill projekts made before your hook existed.

`ctx` keys: `flame_projekt_name`, `flame_projekt_nickname`, `logik_projekt_name`,
`logik_projekt_path`, `flame_projekt_setups_dir`, `workstation`, `user`, `os`
(`Darwin`/`Linux`), `iterations_local`, `iterations_pool`, `project_short`.

## Hooks

| Hook | Does |
|---|---|
| `hook_10_iteration_mirror` | Adds the projekt to this station's mirror agent config — TAB conf + `launchctl kickstart` on macOS, `lsyncd.conf.lua` block on Linux (no auto-restart: lsyncd there is hand-started, its unit disabled). |

## Backfill an existing projekt

```python
from bjoin_studio import post_create
from bjoin_studio.hooks import hook_10_iteration_mirror as h
h.run({"iterations_local": "<setups>/batch/flame/iterations",
       "iterations_pool": "/PROJEKTS/<SHORT>/flame/iterations",
       "project_short": "<SHORT>", "os": "Darwin"})
```

## Upstream merge note

`upstream/release-2026.2.1` is a full refactor (239 files). It KEEPS
`create_flame_symbolic_links.py` but MOVES `projekt_roots.json` and DELETES
`modules/functions/link/link_iterations_dir.py`. When merging, re-home the
`iterations_storage` flag and re-add the step-18.5 call; this package itself
should survive untouched.
