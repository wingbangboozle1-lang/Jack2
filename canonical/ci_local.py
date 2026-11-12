#!/usr/bin/env python3
"""Run the steps of .github/workflows/verify.yml locally, in order, exactly as written.

Usage:
    python3 canonical/ci_local.py            # run every step, stop at the first failure
    python3 canonical/ci_local.py --list     # list the steps
    python3 canonical/ci_local.py --until N  # run steps 1..N only (used to refresh generated files)

The workflow file is the single source of truth: this script reads the `run:` blocks from it,
so a step added by any session is picked up automatically.
"""
import os
import re
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(REPO, ".github", "workflows", "verify.yml")


def steps():
    out, name, block, indent = [], None, None, None
    with open(WORKFLOW, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^\s*- name:\s*(.+?)\s*$", line)
        if m:
            name = m.group(1)
        m = re.match(r"^(\s*)run:\s*(.*)$", line)
        if m and name:
            if m.group(2).strip() in ("|", "|-", ">"):
                base = len(m.group(1))
                body = []
                i += 1
                while i < len(lines) and (lines[i].strip() == "" or len(lines[i]) - len(lines[i].lstrip()) > base):
                    body.append(lines[i])
                    i += 1
                pad = min((len(b) - len(b.lstrip()) for b in body if b.strip()), default=0)
                out.append((name, "\n".join(b[pad:] for b in body)))
                name = None
                continue
            out.append((name, m.group(2)))
            name = None
        i += 1
    return out


def main():
    todo = steps()
    if "--list" in sys.argv:
        for n, (name, _) in enumerate(todo, 1):
            print(f"{n:2d}. {name}")
        return 0
    limit = len(todo)
    if "--until" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--until") + 1])
    quiet = "--quiet" in sys.argv
    for n, (name, script) in enumerate(todo[:limit], 1):
        t0 = time.time()
        proc = subprocess.run(["bash", "-eo", "pipefail", "-c", script], cwd=REPO,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        status = "ok" if proc.returncode == 0 else "FAILED"
        print(f"[{n:2d}/{len(todo)}] {status:6s} {time.time() - t0:5.1f}s  {name}", flush=True)
        if proc.returncode != 0:
            print(proc.stdout[-4000:])
            return 1
        if not quiet and "--verbose" in sys.argv:
            print(proc.stdout[-800:])
    print("all %d step(s) passed" % limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
