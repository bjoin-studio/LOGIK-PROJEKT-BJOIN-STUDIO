"""Set R3D debayer to 16-bit float on a freshly created projekt.

WHY THIS IS A HOOK
    A new projekt is born with `debayerDepth` = 16 ("12bit integer"). Every R3D
    imported before somebody remembers to change it decodes at 12-bit and has to
    be reimported. On LC-26_678 this was caught by hand, with Flame closed,
    minutes before the first ingest -- exactly the kind of step that eventually
    gets missed. Creation time is the only moment it is guaranteed safe to do:
    Flame is not running yet, so nothing will rewrite the file underneath us.

THE FILE
    <setups>/media_import/pref/R3D_<n>.fmt  -- this is the one that takes effect.
    NOT setups/mediaImport/Project_Settings.R3D_*.rule; on LC-26_677 the working
    16-bit-float configuration has the .rule still reading "12bit integer", so
    the .rule is not the lever despite its name.

    Two <debayerDepth> elements exist. The one in <options> is the setting; the
    one in <categories> is a bitmask and MUST NOT be touched. They are told
    apart by value -- options is 16, categories is 8 -- so matching on the exact
    element text is unambiguous.

IRON LAW 4: this is a MediaHub IMPORT setting applied at decode time. It is not
clip.reformat() and it re-encodes nothing.
"""

from __future__ import annotations

import glob
import logging
import os
import shutil
import time
from typing import Dict

logger = logging.getLogger(__name__)

OPTIONS_12BIT = '<debayerDepth type="uint">16</debayerDepth>'
OPTIONS_16FP = '<debayerDepth type="uint" label="16bit float">1</debayerDepth>'
CATEGORIES_MASK = '<debayerDepth type="uint">8</debayerDepth>'


def _patch(path: str, res: Dict) -> bool:
    body = open(path, encoding="utf-8").read()
    if OPTIONS_16FP in body:
        res.setdefault("already", []).append(os.path.basename(path))
        return False
    n = body.count(OPTIONS_12BIT)
    if n != 1:
        res.setdefault("skipped", []).append(
            "%s: %d matches for the options value, expected 1" % (os.path.basename(path), n))
        return False
    bak = "%s.bak-%s" % (path, time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(path, bak)
    out = body.replace(OPTIONS_12BIT, OPTIONS_16FP)
    if CATEGORIES_MASK not in out:          # refuse to write if the mask moved
        res.setdefault("skipped", []).append(
            "%s: categories mask missing after patch - NOT written" % os.path.basename(path))
        return False
    open(path, "w", encoding="utf-8").write(out)
    res.setdefault("patched", []).append(os.path.basename(path))
    res.setdefault("backups", []).append(bak)
    return True


def run(ctx: Dict) -> Dict:
    res: Dict = {"ok": False}
    setups = ctx.get("flame_projekt_setups_dir") or ""
    if not setups:
        res.update(ok=True, skipped="no setups dir in context")
        return res
    pref = os.path.join(setups, "media_import", "pref")
    files = sorted(glob.glob(os.path.join(pref, "R3D_*.fmt")))
    if not files:
        res.update(ok=True, skipped="no R3D_*.fmt under %s" % pref)
        return res
    for f in files:
        try:
            _patch(f, res)
        except Exception as exc:
            res.setdefault("errors", []).append("%s: %s" % (os.path.basename(f), exc))
    res["ok"] = not res.get("errors")
    res["summary"] = "16bit float: %d patched, %d already, %d skipped" % (
        len(res.get("patched", [])), len(res.get("already", [])), len(res.get("skipped", [])))
    return res
