#!/usr/bin/env python3
"""
clean_sandbox.py — Wipe the Rose State Canvas Sandbox so a fresh upload
can be tested.

HARDCODED to course 20338 (the Sandbox). Before deleting anything, the
script fetches the course and aborts unless its name contains "sandbox"
(case-insensitive). There is no CLI flag to target a different course.

Deletes, in order:
    1. Module items + modules
    2. Assignments (covers quizzes and graded discussions)
    3. Quizzes (classic, anything not already removed)
    4. Discussion topics (ungraded)
    5. Wiki pages
    6. Files
    7. Folders (best-effort; non-root folders only)

Run with --dry-run to list what would be deleted without touching Canvas.
Run with --yes to actually delete. Without either flag, prints a summary
and exits.
"""

import json
import os
import sys
import time
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CANVAS_BASE = "https://rose.instructure.com"
SANDBOX_COURSE_ID = 20338
SANDBOX_NAME_MARKER = "sandbox"   # course name must contain this (case-insensitive)


# ── Token loading ───────────────────────────────────────────────────────────

def load_token():
    env_path = os.path.join(ROOT, '.env')
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                if key.strip() in ('CANVAS_TOKEN', 'TOKEN'):
                    return val.strip()
                # fall back to first token-looking line
                return val.strip()
    raise RuntimeError(".env file found but no token detected")


# ── Canvas API helpers ──────────────────────────────────────────────────────

def api_request(method, url, token, payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
    req = Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    if data:
        req.add_header('Content-Type', 'application/json')
    resp = urlopen(req)
    body = resp.read().decode('utf-8', errors='replace')
    link = resp.headers.get('Link', '')
    return resp.status, body, link


def parse_next_link(link_header):
    """Pull the rel=next URL out of a Canvas Link header."""
    if not link_header:
        return None
    for part in link_header.split(','):
        segs = part.strip().split(';')
        if len(segs) < 2:
            continue
        url_part = segs[0].strip()
        rel_part = ';'.join(segs[1:]).strip()
        if 'rel="next"' in rel_part and url_part.startswith('<') and url_part.endswith('>'):
            return url_part[1:-1]
    return None


def paged_get(path, token):
    """Yield items from a paginated Canvas GET endpoint."""
    url = f"{CANVAS_BASE}{path}"
    if '?' in url:
        url += '&per_page=100'
    else:
        url += '?per_page=100'
    while url:
        status, body, link = api_request('GET', url, token)
        items = json.loads(body)
        if not isinstance(items, list):
            raise RuntimeError(f"Expected list from {url}, got: {body[:200]}")
        for item in items:
            yield item
        url = parse_next_link(link)


def safe_delete(url, token, label):
    """DELETE with friendly error handling. Returns True on success."""
    try:
        api_request('DELETE', url, token)
        return True
    except HTTPError as e:
        detail = e.read().decode('utf-8', errors='replace')[:200]
        print(f"    FAIL {label}  ({e.code}: {detail})")
        return False


# ── Safety check ────────────────────────────────────────────────────────────

def verify_sandbox(token):
    url = f"{CANVAS_BASE}/api/v1/courses/{SANDBOX_COURSE_ID}"
    status, body, _ = api_request('GET', url, token)
    course = json.loads(body)
    name = course.get('name', '')
    print(f"  Course {SANDBOX_COURSE_ID}: {name!r}")
    if SANDBOX_NAME_MARKER not in name.lower():
        raise RuntimeError(
            f"REFUSING TO DELETE: course {SANDBOX_COURSE_ID} name {name!r} "
            f"does not contain {SANDBOX_NAME_MARKER!r}. Aborting."
        )
    return name


# ── Collectors ──────────────────────────────────────────────────────────────

def collect_targets(token):
    """Gather everything we plan to delete. Returns dict of lists."""
    cid = SANDBOX_COURSE_ID
    targets = {}

    targets['modules'] = list(paged_get(
        f"/api/v1/courses/{cid}/modules", token))

    targets['assignments'] = list(paged_get(
        f"/api/v1/courses/{cid}/assignments", token))

    targets['quizzes'] = list(paged_get(
        f"/api/v1/courses/{cid}/quizzes", token))

    targets['discussions'] = list(paged_get(
        f"/api/v1/courses/{cid}/discussion_topics", token))

    targets['pages'] = list(paged_get(
        f"/api/v1/courses/{cid}/pages", token))

    targets['files'] = list(paged_get(
        f"/api/v1/courses/{cid}/files", token))

    targets['folders'] = list(paged_get(
        f"/api/v1/courses/{cid}/folders", token))

    return targets


# ── Deleters ────────────────────────────────────────────────────────────────

def delete_modules(modules, token):
    cid = SANDBOX_COURSE_ID
    print(f"\n  Deleting {len(modules)} module(s)...")
    n = 0
    for m in modules:
        mid = m['id']
        label = f"module {mid} {m.get('name','')!r}"
        if safe_delete(f"{CANVAS_BASE}/api/v1/courses/{cid}/modules/{mid}", token, label):
            print(f"    OK   {label}")
            n += 1
        time.sleep(0.1)
    return n


def delete_assignments(assignments, token):
    cid = SANDBOX_COURSE_ID
    print(f"\n  Deleting {len(assignments)} assignment(s)...")
    n = 0
    for a in assignments:
        aid = a['id']
        label = f"assignment {aid} {a.get('name','')!r}"
        if safe_delete(f"{CANVAS_BASE}/api/v1/courses/{cid}/assignments/{aid}", token, label):
            print(f"    OK   {label}")
            n += 1
        time.sleep(0.1)
    return n


def delete_quizzes(quizzes, token):
    cid = SANDBOX_COURSE_ID
    print(f"\n  Deleting {len(quizzes)} quiz(zes)...")
    n = 0
    for q in quizzes:
        qid = q['id']
        label = f"quiz {qid} {q.get('title','')!r}"
        if safe_delete(f"{CANVAS_BASE}/api/v1/courses/{cid}/quizzes/{qid}", token, label):
            print(f"    OK   {label}")
            n += 1
        time.sleep(0.1)
    return n


def delete_discussions(discussions, token):
    cid = SANDBOX_COURSE_ID
    print(f"\n  Deleting {len(discussions)} discussion(s)...")
    n = 0
    for d in discussions:
        did = d['id']
        label = f"discussion {did} {d.get('title','')!r}"
        if safe_delete(f"{CANVAS_BASE}/api/v1/courses/{cid}/discussion_topics/{did}", token, label):
            print(f"    OK   {label}")
            n += 1
        time.sleep(0.1)
    return n


def delete_pages(pages, token):
    cid = SANDBOX_COURSE_ID
    print(f"\n  Deleting {len(pages)} page(s)...")

    # Canvas refuses to delete the course front page. Unset any page flagged
    # as front_page before the delete loop runs.
    for p in pages:
        if p.get('front_page'):
            slug = p['url']
            print(f"    note unsetting front_page on {slug!r}")
            try:
                api_request(
                    'PUT',
                    f"{CANVAS_BASE}/api/v1/courses/{cid}/pages/{slug}",
                    token,
                    payload={'wiki_page': {'front_page': False}},
                )
            except HTTPError as e:
                detail = e.read().decode('utf-8', errors='replace')[:200]
                print(f"    FAIL unset front_page on {slug!r}  ({e.code}: {detail})")

    n = 0
    for p in pages:
        slug = p['url']
        label = f"page {slug!r} ({p.get('title','')!r})"
        if safe_delete(f"{CANVAS_BASE}/api/v1/courses/{cid}/pages/{slug}", token, label):
            print(f"    OK   {label}")
            n += 1
        time.sleep(0.1)
    return n


def delete_files(files, token):
    print(f"\n  Deleting {len(files)} file(s)...")
    n = 0
    for f in files:
        fid = f['id']
        label = f"file {fid} {f.get('display_name','')!r}"
        if safe_delete(f"{CANVAS_BASE}/api/v1/files/{fid}", token, label):
            print(f"    OK   {label}")
            n += 1
        time.sleep(0.1)
    return n


def delete_folders(folders, token):
    """Delete non-root folders. force=true wipes their contents too."""
    deletable = [f for f in folders if f.get('parent_folder_id') is not None]
    print(f"\n  Deleting {len(deletable)} folder(s) (skipping root)...")
    n = 0
    for f in deletable:
        fid = f['id']
        label = f"folder {fid} {f.get('full_name','')!r}"
        url = f"{CANVAS_BASE}/api/v1/folders/{fid}?force=true"
        if safe_delete(url, token, label):
            print(f"    OK   {label}")
            n += 1
        time.sleep(0.1)
    return n


# ── Main ────────────────────────────────────────────────────────────────────

def summarize(targets):
    print()
    print("  Found:")
    print(f"    {len(targets['modules']):>4}  modules")
    print(f"    {len(targets['assignments']):>4}  assignments")
    print(f"    {len(targets['quizzes']):>4}  quizzes")
    print(f"    {len(targets['discussions']):>4}  discussions")
    print(f"    {len(targets['pages']):>4}  pages")
    print(f"    {len(targets['files']):>4}  files")
    non_root_folders = [f for f in targets['folders'] if f.get('parent_folder_id') is not None]
    print(f"    {len(non_root_folders):>4}  folders (excluding root)")


def main():
    args = sys.argv[1:]
    do_delete = '--yes' in args
    dry_run = '--dry-run' in args or not do_delete

    print("=" * 60)
    print(f"Canvas Sandbox cleanup — course {SANDBOX_COURSE_ID}")
    print("=" * 60)

    token = load_token()

    name = verify_sandbox(token)
    print(f"  Confirmed sandbox: {name}")

    print("\n  Scanning course contents...")
    targets = collect_targets(token)
    summarize(targets)

    if dry_run:
        print("\n  Dry run — no deletions performed.")
        print("  Re-run with --yes to actually delete the items above.")
        return

    print("\n  --yes flag set. Deleting...")

    totals = {}
    totals['modules']     = delete_modules(targets['modules'], token)
    totals['assignments'] = delete_assignments(targets['assignments'], token)
    totals['quizzes']     = delete_quizzes(targets['quizzes'], token)
    totals['discussions'] = delete_discussions(targets['discussions'], token)
    totals['pages']       = delete_pages(targets['pages'], token)
    totals['files']       = delete_files(targets['files'], token)
    totals['folders']     = delete_folders(targets['folders'], token)

    print()
    print("=" * 60)
    print("Cleanup complete.")
    for k, v in totals.items():
        print(f"  Deleted {v} {k}")
    print("=" * 60)
    print()
    print(f"Sandbox course {SANDBOX_COURSE_ID} is ready for a fresh upload.")


if __name__ == '__main__':
    main()
