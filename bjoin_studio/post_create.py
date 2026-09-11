"""Run the studio's post-create hooks after LOGIK-PROJEKT builds a projekt.

WHY THIS EXISTS
    Creating a projekt is only half of making it usable here. The station also
    has to register it with the iteration-mirror agent, and (in time) with
    Kitsu, Frame.io, the job config and whatever else the studio runs. Doing
    that by hand is how LC-26_677 ended up with a mirror conf line that was
    added but never activated -- the watcher ran for days on a stale project
    list and nobody knew. Anything a new projekt needs belongs here, where it
    happens every time.

CONTRACT
    A hook is a module in `hooks/` named `hook_NN_<name>.py` exposing
    `run(ctx) -> dict`. Hooks run in filename order, so NN sets the order.

    THE RUNNER NEVER RAISES. A projekt that is created but not registered is
    a nuisance; a projekt creation that dies at step 18.5 because Kitsu was
    unreachable is a disaster on a shoot day. Every hook is isolated, every
    failure is logged, and creation always continues.

    Hooks must be IDEMPOTENT -- re-running on an existing projekt is a
    supported, expected operation (that is how we backfill).
"""

from __future__ import annotations

import importlib
import logging
import os
import pkgutil
import platform
from typing import Dict, List

logger = logging.getLogger(__name__)

HOOK_PREFIX = "hook_"


def build_context(config) -> Dict:
    """Flatten what the hooks need out of ProjektParameters.

    Derived rather than passed so a hook never has to know LOGIK-PROJEKT's
    internals -- and so this keeps working when upstream renames things.
    `iterations_local` / `iterations_pool` mirror exactly what
    `create_flame_symbolic_links.py` builds, and must stay in step with it.
    """
    setups = getattr(config, "flame_projekt_setups_dir", "") or ""
    logik_path = getattr(config, "logik_projekt_path", "") or ""
    ctx = {
        "flame_projekt_name": getattr(config, "flame_projekt_name", "") or "",
        "flame_projekt_nickname": getattr(config, "flame_projekt_nickname", "") or "",
        "logik_projekt_name": getattr(config, "logik_projekt_name", "") or "",
        "logik_projekt_path": logik_path,
        "flame_projekt_setups_dir": setups,
        "workstation": getattr(config, "current_workstation", "") or "",
        "user": getattr(config, "current_user", "") or "",
        "os": platform.system(),               # Darwin | Linux
        "iterations_local": os.path.join(setups, "batch", "flame", "iterations") if setups else "",
        "iterations_pool": os.path.join(logik_path, "flame", "iterations") if logik_path else "",
        # The short name the mirror + batchTracker key on: /PROJEKTS/<SHORT>/...
        "project_short": os.path.basename(logik_path.rstrip(os.sep)) if logik_path else "",
    }
    return ctx


def _discover() -> List[str]:
    from bjoin_studio import hooks as hooks_pkg
    found = [n for _, n, _ in pkgutil.iter_modules(hooks_pkg.__path__)
             if n.startswith(HOOK_PREFIX)]
    return sorted(found)


def run_all(config) -> Dict:
    """Run every post-create hook. Returns a report; never raises."""
    ctx = build_context(config)
    report: Dict = {"context": ctx, "hooks": []}
    logger.info(
        "bjoin_studio: post-create hooks for %s (%s) on %s",
        ctx.get("project_short") or "?", ctx.get("flame_projekt_name") or "?",
        ctx.get("os"),
    )
    try:
        names = _discover()
    except Exception as exc:
        logger.error("bjoin_studio: hook discovery failed: %s", exc)
        return report

    for name in names:
        entry = {"hook": name, "ok": False}
        try:
            mod = importlib.import_module("bjoin_studio.hooks.%s" % name)
            run = getattr(mod, "run", None)
            if run is None:
                entry["error"] = "no run(ctx)"
            else:
                entry.update(run(ctx) or {})
                entry.setdefault("ok", True)
        except Exception as exc:                      # never fatal -- see module docstring
            entry["error"] = "%s: %s" % (type(exc).__name__, exc)
            logger.exception("bjoin_studio: hook %s failed (continuing)", name)
        report["hooks"].append(entry)
        logger.info("bjoin_studio:   %-34s %s%s", name,
                    "ok" if entry.get("ok") else "FAILED",
                    "" if entry.get("ok") else " -- %s" % entry.get("error"))
    return report
