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
                        block per projekt. Reloaded by restarting the
                        lsyncd whose command line names THIS config. If that
                        process belongs to the systemd unit
                        (iteration-mirror.service, Restart=always) we only
                        TERM it and let systemd relaunch it -- respawning it
                        ourselves is how supercomputer ended up running two
                        lsyncds per projekt build (2026-09-12, 09-14). Only a
                        hand-started lsyncd is relaunched with its own argv.

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
    res.update(_linux_reload(short))
    res["ok"] = True
    return res


SYSTEMD_UNIT_CGROUP = "/system.slice/iteration-mirror.service"


def _reload_strategy(cgroup_text: str) -> str:
    """'systemd' if the lsyncd's cgroup shows the iteration-mirror unit owns
    it (systemd will relaunch it after a TERM), else 'respawn'."""
    return "systemd" if SYSTEMD_UNIT_CGROUP in (cgroup_text or "") else "respawn"


def _pid_cgroup(pid: int) -> str:
    try:
        with open("/proc/%d/cgroup" % pid, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def _linux_reload(short: str) -> Dict:
    """Restart the lsyncd that is serving OUR config, so the block we just
    appended is actually live.

    The earlier version only reported "restart required". That is precisely
    the LC-26_677 failure: a config line added and never activated, and nobody
    noticing for days. A registration that needs a human step is a
    registration that eventually does not happen.

    Strictly scoped: we only ever touch a process whose command line names
    THIS config file, and we restart it with the exact invocation it was
    already using. If no such process is running there is nothing to reload
    (lsyncd reads the config at startup, so a later start picks it up).
    """
    out: Dict = {"reloaded": False}
    try:
        ps = subprocess.run(["ps", "-eo", "pid=,args="],
                            capture_output=True, text=True, timeout=20).stdout
    except Exception as exc:
        out["reload_error"] = "could not list processes: %s" % exc
        return out

    target = None
    for line in ps.splitlines():
        if "lsyncd" in line and LINUX_CONF in line:
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[0].isdigit():
                target = (int(parts[0]), parts[1].strip())
                break
    if target is None:
        out["reload_note"] = ("no lsyncd running against %s — it will pick up "
                              "%s when next started" % (LINUX_CONF, short))
        return out

    pid, argv = target
    strategy = _reload_strategy(_pid_cgroup(pid))
    out["strategy"] = strategy
    try:
        subprocess.run(["kill", str(pid)], capture_output=True, timeout=20)
        for _ in range(20):                       # wait for it to actually go
            time.sleep(0.5)
            if subprocess.run(["kill", "-0", str(pid)],
                              capture_output=True).returncode != 0:
                break
        if strategy == "respawn":
            # Hand-started lsyncd: re-launch detached with the SAME argv, so
            # we never invent a new invocation for a service we did not
            # configure.
            subprocess.Popen(["setsid"] + argv.split(),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL, start_new_session=True)
        # systemd (Restart=always) relaunches its own within RestartSec;
        # either way, wait for a NEW lsyncd on this config to show up.
        back = False
        for _ in range(20):
            time.sleep(0.5)
            ps2 = subprocess.run(["ps", "-eo", "pid=,args="],
                                 capture_output=True, text=True, timeout=20).stdout
            if any("lsyncd" in ln and LINUX_CONF in ln
                   and ln.split(None, 1)[0] != str(pid) for ln in ps2.splitlines()):
                back = True
                break
        if back:
            out["reloaded"] = True
            out["reload_note"] = "lsyncd restarted (%s); %s is live" % (strategy, short)
        else:
            out["reload_error"] = ("lsyncd did NOT come back — start it with: "
                                   "%s" % (argv if strategy == "respawn"
                                           else "sudo systemctl restart iteration-mirror"))
    except Exception as exc:
        out["reload_error"] = "%s: %s" % (type(exc).__name__, exc)
    return out


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
