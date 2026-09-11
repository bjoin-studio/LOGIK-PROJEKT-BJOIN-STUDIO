"""Register a new projekt with this station's iteration-mirror agent.

Iterations are born LOCAL (projekt_roots.json -> iterations_storage: local) so
saves hit fast NVMe instead of NFS. The shared NAS pool is then fed by a
per-station mirror agent, and that agent only mirrors projects listed in its
config. A projekt created without this step saves fine and -- because
batchTracker derives the pool path from the project name -- still pushes on
Save & Sync; what it loses is the safety net for iterations made with Flame's
own native Iterate, which nothing else would ever carry to the pool.

The two stations run different agents, so this writes two different files:

    macOS (mercury)     ~/.config/iteration-mirror/iteration-mirror.macos.conf
                        one TAB-separated "<local>\t<pool>" line per projekt,
                        read by iteration_mirror_watch.sh (fswatch). Reloaded
                        here via launchctl kickstart -- cheap and proven.

    Linux (supercom)    ~/.config/iteration-mirror/lsyncd.conf.lua
                        one `sync { pushLayer("<SHORT>"), source, target }`
                        block per projekt. NOT reloaded automatically: lsyncd
                        is started by hand there (its unit is disabled), so
                        bouncing it would interrupt a syncer we did not start.
                        The hook reports that a restart is pending instead.

Idempotent: if the projekt is already in the file, nothing is written.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from typing import Dict

logger = logging.getLogger(__name__)

MIRROR_DIR = os.path.expanduser("~/.config/iteration-mirror")
MACOS_CONF = os.path.join(MIRROR_DIR, "iteration-mirror.macos.conf")
LINUX_CONF = os.path.join(MIRROR_DIR, "lsyncd.conf.lua")
LAUNCHD_LABEL = "com.bjoin.iteration-mirror"


def _backup(path: str) -> str:
    """Timestamped copy beside the original before we edit it. Config only --
    never secrets; nothing under this hook touches .env."""
    dst = "%s.bak-%s" % (path, time.strftime("%Y%m%d-%H%M%S"))
    try:
        shutil.copy2(path, dst)
        return dst
    except OSError:
        return ""


def _mac_register(ctx: Dict, res: Dict) -> Dict:
    local = ctx["iterations_local"].rstrip(os.sep)
    pool = ctx["iterations_pool"].rstrip(os.sep)
    if not os.path.isfile(MACOS_CONF):
        res["skipped"] = "no %s -- mirror kit not installed here" % MACOS_CONF
        return res
    body = open(MACOS_CONF, encoding="utf-8").read()
    if local in body:
        res["ok"] = True
        res["already_present"] = True
        return res
    res["backup"] = _backup(MACOS_CONF)
    with open(MACOS_CONF, "a", encoding="utf-8") as f:
        if not body.endswith("\n"):
            f.write("\n")
        f.write("\n# %s (added by bjoin_studio post-create)\n" % ctx["project_short"])
        f.write("%s\t%s\n" % (local, pool))
    res["conf"] = MACOS_CONF
    res["appended"] = True

    uid = os.getuid()
    try:
        p = subprocess.run(
            ["launchctl", "kickstart", "-k", "gui/%d/%s" % (uid, LAUNCHD_LABEL)],
            capture_output=True, text=True, timeout=30,
        )
        res["reloaded"] = (p.returncode == 0)
        if p.returncode != 0:
            res["reload_error"] = (p.stderr or p.stdout or "").strip()[:200]
    except Exception as exc:
        res["reloaded"] = False
        res["reload_error"] = str(exc)
    res["ok"] = True
    return res


def _linux_register(ctx: Dict, res: Dict) -> Dict:
    local = ctx["iterations_local"].rstrip(os.sep) + os.sep
    pool = ctx["iterations_pool"].rstrip(os.sep) + os.sep
    short = ctx["project_short"]
    if not os.path.isfile(LINUX_CONF):
        res["skipped"] = "no %s -- mirror kit not installed here" % LINUX_CONF
        return res
    body = open(LINUX_CONF, encoding="utf-8").read()
    if ('pushLayer("%s")' % short) in body or local in body:
        res["ok"] = True
        res["already_present"] = True
        return res
    res["backup"] = _backup(LINUX_CONF)
    block = (
        '\n-- %s (added by bjoin_studio post-create)\n'
        'sync {\n'
        '  pushLayer("%s"),\n'
        '  source = "%s",\n'
        '  target = "%s",\n'
        '}\n' % (short, short, local, pool)
    )
    with open(LINUX_CONF, "a", encoding="utf-8") as f:
        if not body.endswith("\n"):
            f.write("\n")
        f.write(block)
    res["conf"] = LINUX_CONF
    res["appended"] = True
    # Deliberately NOT restarting lsyncd -- see module docstring.
    res["reloaded"] = False
    res["restart_required"] = "lsyncd must be restarted to pick up %s" % short
    res["ok"] = True
    return res


def run(ctx: Dict) -> Dict:
    res: Dict = {"ok": False}
    if not ctx.get("iterations_local") or not ctx.get("iterations_pool"):
        res["skipped"] = "no iterations paths in context"
        res["ok"] = True
        return res
    if ctx.get("os") == "Darwin":
        return _mac_register(ctx, res)
    if ctx.get("os") == "Linux":
        return _linux_register(ctx, res)
    res["skipped"] = "unsupported platform %r" % ctx.get("os")
    res["ok"] = True
    return res
