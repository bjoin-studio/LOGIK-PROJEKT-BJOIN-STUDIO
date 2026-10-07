"""A failed Wiretap register must stop projekt creation (LC-26_679). Nothing here runs wiretap."""
import os, sys, subprocess
from unittest import mock
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
import importlib.util
# load by path: importing the src package pulls in PySide6
_spec = importlib.util.spec_from_file_location(
    "create_flame_wiretap_node",
    os.path.join(_ROOT, "src/core/functions/create/create_flame_wiretap_node.py"))
W = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(W)

fails = []
def ck(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)

class FakePopen:
    def __init__(self, rc, out=b"", err=b""):
        self.returncode, self._o, self._e = rc, out, err
    def communicate(self):
        return self._o, self._e

def raises(fn):
    try:
        fn(); return None
    except RuntimeError as e:
        return str(e)

# create: failure raises with the wiretap message and the hint
with mock.patch.object(W.subprocess, "Popen", lambda *a, **k: FakePopen(1, err=b"Unable to create node: No route to host\n")):
    msg = raises(lambda: W.create_flame_wiretap_node("LC-26_999_x", "p.xml"))
ck(msg is not None, "create: rc=1 raises")
ck(msg and "No route to host" in msg and "LC-26_999_x" in msg, "create: message names the project and the wiretap error")
ck(msg and "sw_ifffs" in msg, "create: message carries the restart hint")

with mock.patch.object(W.subprocess, "Popen", lambda *a, **k: FakePopen(1, err=b"Unable to create node: Project location /x is not empty [File exists]\n")):
    msg = raises(lambda: W.create_flame_wiretap_node("LC-26_999_x", "p.xml"))
ck(msg and "is not empty" in msg, "create: non-empty folder refusal raises too")

# create: success does not raise
with mock.patch.object(W.subprocess, "Popen", lambda *a, **k: FakePopen(0, out=b"Created node '/projects/ABC'.\n")):
    ck(raises(lambda: W.create_flame_wiretap_node("LC-26_999_x", "p.xml")) is None, "create: rc=0 passes")

# preflight
R = subprocess.CompletedProcess
with mock.patch.object(W.subprocess, "run", lambda *a, **k: R(a, 1, b"", b"Unable to retrieve number of children: No route to host\n")):
    msg = raises(W.check_wiretap_projects_reachable)
ck(msg and "Nothing has been created" in msg and "No route to host" in msg, "preflight: dead ifffs raises")
with mock.patch.object(W.subprocess, "run", lambda *a, **k: R(a, 0, b"/projects/ABC\n", b"")):
    ck(raises(W.check_wiretap_projects_reachable) is None, "preflight: live ifffs passes")

# creator: the preflight runs before step 2 touches anything
src = open(os.path.join(_ROOT, "src/core/projekt_manager/projekt_creator.py")).read()
body = src[src.index("def create_projekt(self"):]
ck(0 < body.index("check_wiretap_projects_reachable()") < body.index("export_session_variables("), "creator: preflight precedes step 2")
ck(body.index("create_flame_wiretap_node(") < body.index("create_flame_setup_dirs("), "creator: register precedes setups dir creation")

print("\n%d failure(s)" % len(fails))
sys.exit(1 if fails else 0)
