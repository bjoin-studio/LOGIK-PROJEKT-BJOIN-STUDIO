import os, sys, tempfile, shutil
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)   # repo root, where bjoin_studio/ lives
from bjoin_studio.hooks import hook_10_iteration_mirror as H

fails = []
def ck(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)

tmp = tempfile.mkdtemp()
mac = os.path.join(tmp, "iteration-mirror.macos.conf")
lin = os.path.join(tmp, "lsyncd.conf.lua")
open(mac, "w").write("# header\n/x/LC-26_677/iterations\t/PROJEKTS/LC-26_677/flame/iterations\n")
open(lin, "w").write('sync {\n  pushLayer("LC-26_677"),\n  source = "/x/",\n  target = "/y/",\n}\n')
H.MACOS_CONF, H.LINUX_CONF = mac, lin
H.LAUNCHD_LABEL = "com.bjoin.doesnotexist.test"   # keep the real agent untouched

ctx = {"iterations_local": "/local/LC-26_678_2026_2_1_mercury/setups/batch/flame/iterations",
       "iterations_pool": "/PROJEKTS/LC-26_678/flame/iterations",
       "project_short": "LC-26_678", "os": "Darwin"}

r1 = H.run(ctx)
ck(r1.get("appended") is True, "macOS: appended new project")
body = open(mac).read()
ck("/local/LC-26_678_2026_2_1_mercury/setups/batch/flame/iterations\t/PROJEKTS/LC-26_678/flame/iterations" in body,
   "macOS: line is TAB-separated local<TAB>pool")
ck(os.path.isfile(r1.get("backup") or ""), "macOS: backup written before edit")
ck("LC-26_677" in body, "macOS: existing project preserved")
r2 = H.run(ctx)
ck(r2.get("already_present") is True and not r2.get("appended"), "macOS: IDEMPOTENT on re-run")
ck(open(mac).read() == body, "macOS: re-run wrote nothing")

ctx["os"] = "Linux"
r3 = H.run(ctx)
lbody = open(lin).read()
ck(r3.get("appended") is True, "linux: appended new project")
ck('pushLayer("LC-26_678")' in lbody, "linux: pushLayer block present")
ck(lbody.count("sync {") == 2, "linux: exactly one new sync block")
ck(lbody.rstrip().endswith("}"), "linux: file still ends on a closed block")
ck(r3.get("reloaded") is False and "restart_required" in r3, "linux: reports restart pending, does NOT bounce lsyncd")
r4 = H.run(ctx)
ck(r4.get("already_present") is True, "linux: IDEMPOTENT on re-run")

# missing conf = report, never invent one
H.MACOS_CONF = os.path.join(tmp, "nope.conf"); ctx["os"] = "Darwin"
r5 = H.run(ctx)
ck("skipped" in r5 and not os.path.exists(H.MACOS_CONF), "missing conf: skipped, no file invented")

shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("ALL PASS" if not fails else "FAILURES: %s" % fails))
sys.exit(1 if fails else 0)
