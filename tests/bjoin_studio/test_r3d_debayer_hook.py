"""hook_20_r3d_debayer against real .fmt fixtures. Nothing here touches a projekt."""
import os, sys, tempfile, shutil
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
from bjoin_studio.hooks import hook_20_r3d_debayer as H

fails = []
def ck(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)

HEAD = '<options><customPDLogWhitePoint type="int">685</customPDLogWhitePoint>'
TAIL = '<denoise type="int" label="Off">0</denoise></options><categories>'
MASK = '<debayerDepth type="uint">8</debayerDepth></categories>'

def mk(tmp, opts_value):
    d = os.path.join(tmp, "setups", "media_import", "pref")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "R3D_20.fmt")
    open(p, "w").write(HEAD + opts_value + TAIL + MASK)
    return p

tmp = tempfile.mkdtemp()
p = mk(tmp, H.OPTIONS_12BIT)
r = H.run({"flame_projekt_setups_dir": os.path.join(tmp, "setups")})
body = open(p).read()
ck(r["ok"] and r.get("patched"), "patches a fresh 12-bit projekt")
ck(H.OPTIONS_16FP in body, "options element becomes 16bit float / value 1")
ck(H.CATEGORIES_MASK in body, "categories MASK left at 8 (must never change)")
ck(body.count("<debayerDepth") == 2, "still exactly two debayerDepth ELEMENTS (open tags)")
ck(os.path.isfile(r["backups"][0]), "backup written before the edit")

r2 = H.run({"flame_projekt_setups_dir": os.path.join(tmp, "setups")})
ck(r2["ok"] and r2.get("already") and not r2.get("patched"), "IDEMPOTENT on re-run")

# a file that does not match the expected shape must be refused, not guessed at
tmp2 = tempfile.mkdtemp()
p2 = mk(tmp2, '<debayerDepth type="uint">99</debayerDepth>')
r3 = H.run({"flame_projekt_setups_dir": os.path.join(tmp2, "setups")})
ck(r3.get("skipped") and not r3.get("patched"), "unexpected value -> skipped, not guessed")
ck('99' in open(p2).read(), "unexpected file left untouched")

# missing dirs are reported, never invented
r4 = H.run({"flame_projekt_setups_dir": os.path.join(tmp2, "nope")})
ck(r4["ok"] and "skipped" in r4, "missing pref dir -> reports, stays ok (never fatal)")
ck(H.run({})["ok"], "empty context -> ok, no crash")

shutil.rmtree(tmp, ignore_errors=True); shutil.rmtree(tmp2, ignore_errors=True)
print("\n" + ("ALL PASS" if not fails else "FAILURES: %s" % fails))
sys.exit(1 if fails else 0)
