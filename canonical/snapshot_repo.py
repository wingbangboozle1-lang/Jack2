#!/usr/bin/env python3
"""Snapshot of things the build cannot see from a shallow checkout: open pull requests,
branches that never reached main, and a count of commits whose author field carries a
personal-provider e-mail address (the address itself is never read into the output).

Run by hand with network access and full history:  python3 canonical/snapshot_repo.py
The result, canonical/data/archive.json, is committed and rendered by the site build.
"""
import datetime
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "data", "archive.json")
GH = "https://github.com/wingbangboozle1-lang/Jack2"


def sh(*args):
    return subprocess.check_output(args, cwd=REPO, text=True)


def main():
    sh("git", "fetch", "-q", "origin", "+refs/heads/*:refs/remotes/origin/*")
    prs = json.loads(sh("gh", "pr", "list", "--state", "open", "--limit", "100", "--json",
                        "number,title,headRefName,isDraft,createdAt"))
    prs = [{"number": p["number"], "title": p["title"][:140], "branch": p["headRefName"], "draft": p["isDraft"],
            "opened": p["createdAt"][:10], "url": f"{GH}/pull/{p['number']}"} for p in sorted(prs, key=lambda p: p["number"])]
    branches = []
    refs = [r for r in sh("git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin").split()
            if r.startswith("origin/arena/")]
    for ref in sorted(refs):
        name = ref[len("origin/"):]
        if name == "arena/1c30f8e8-jack2":
            continue  # this session's own working branch
        ahead = int(sh("git", "rev-list", "--count", f"origin/main..{ref}").strip())
        if ahead == 0:
            continue
        on_main = set(sh("git", "ls-tree", "-r", "--name-only", "origin/main").split("\n"))
        added = [l for l in sh("git", "diff", "--name-only", "--diff-filter=A", f"origin/main...{ref}").split("\n")
                 if l and l not in on_main]
        tops = sorted({a.split("/")[0] for a in added if "/" in a})
        branches.append({"branch": name, "commits_not_on_main": ahead, "files_not_on_main": len(added),
                         "folders": tops[:6], "last_commit": sh("git", "log", "-1", "--format=%cI", ref).strip()[:10],
                         "url": f"{GH}/tree/{name}"})
    emails = sh("git", "log", "origin/main", "--format=%ae").split()
    personal = sum(1 for e in emails if e.lower().endswith(("@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com", "@icloud.com")))
    distinct = len({e.lower() for e in emails if e.lower().endswith(("@gmail.com", "@yahoo.com", "@outlook.com", "@hotmail.com", "@icloud.com"))})
    out = {"measured": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
           "main_commit": sh("git", "rev-parse", "--short", "origin/main").strip(),
           "open_pull_requests": prs,
           "branches_with_unmerged_work": [b for b in branches if b["files_not_on_main"] > 0],
           "branches_with_only_log_or_claim_commits": len([b for b in branches if b["files_not_on_main"] == 0]),
           "history": {"commits_on_main": len(emails), "commits_with_personal_provider_email": personal,
                       "distinct_personal_provider_addresses": distinct}}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("wrote", os.path.relpath(OUT, REPO), {k: (len(v) if isinstance(v, list) else v) for k, v in out.items() if k != "measured"})


if __name__ == "__main__":
    main()
