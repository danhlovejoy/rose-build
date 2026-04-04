#!/usr/bin/env python3
"""
fix_module2_structure.py

- Removes old "Week 3" assignment module items (positions 9-11)
- Deletes the stale Canvas assignments created in a prior session
- Adds Module 2 Participation, Presentation, GitHub Repo, Ethics Discussion to the module
"""

import json
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT     = os.path.dirname(os.path.abspath(__file__))
BASE     = "https://rose.instructure.com"
COURSE   = 26943
MODULE   = 203477   # Module 2: Hand-Crafted Features — TF-IDF

# Old module item IDs to remove (Week 3 Presentation, GitHub Repo, Ethics Discussion)
OLD_ITEM_IDS = [2226348, 2226349, 2226350]

# Old Canvas assignment/discussion IDs to delete
OLD_ASSIGNMENT_IDS   = [810600, 810601]
OLD_DISCUSSION_IDS   = [356790]

# New Canvas artifact IDs (created this session)
NEW_PARTICIPATION_ID   = 810698   # Assignment
NEW_ETHICS_DISCUSSION  = 356963   # Discussion Topic
NEW_PRESENTATION_ID    = 810700   # Assignment
NEW_REPO_ID            = 810701   # Assignment


def load_token():
    env_path = os.path.join(ROOT, '.env')
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                return line.split('=', 1)[1].strip()
    raise RuntimeError(".env: no token found")


def api(method, path, payload=None, token=None):
    url = f"{BASE}/api/v1{path}"
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    if data:
        req.add_header('Content-Type', 'application/json')
    try:
        resp = urlopen(req)
        body = resp.read()
        return json.loads(body.decode('utf-8')) if body else {}
    except HTTPError as e:
        detail = e.read().decode('utf-8', errors='replace')
        print(f"  HTTP {e.code} on {method} {path}: {detail[:300]}")
        raise


def main():
    token = load_token()

    # ── 1. Delete old module items ─────────────────────────────────────────
    print("1. Removing old module items…")
    for item_id in OLD_ITEM_IDS:
        try:
            api('DELETE', f'/courses/{COURSE}/modules/{MODULE}/items/{item_id}', token=token)
            print(f"   Deleted module item {item_id}")
        except HTTPError:
            print(f"   (item {item_id} already gone or error — skipping)")

    # ── 2. Delete stale assignments ────────────────────────────────────────
    print("2. Deleting stale assignments…")
    for aid in OLD_ASSIGNMENT_IDS:
        try:
            api('DELETE', f'/courses/{COURSE}/assignments/{aid}', token=token)
            print(f"   Deleted assignment {aid}")
        except HTTPError:
            print(f"   (assignment {aid} already gone or error — skipping)")

    print("3. Deleting stale discussions…")
    for did in OLD_DISCUSSION_IDS:
        try:
            api('DELETE', f'/courses/{COURSE}/discussion_topics/{did}', token=token)
            print(f"   Deleted discussion {did}")
        except HTTPError:
            print(f"   (discussion {did} already gone or error — skipping)")

    # ── 4. Add new module items ────────────────────────────────────────────
    print("4. Adding new module items…")

    items_to_add = [
        {
            'title':      'Module 2 Participation',
            'type':       'Assignment',
            'content_id': NEW_PARTICIPATION_ID,
        },
        {
            'title':      'Module 2 Ethics Discussion',
            'type':       'Discussion',
            'content_id': NEW_ETHICS_DISCUSSION,
        },
        {
            'title':      'Module 2 Presentation',
            'type':       'Assignment',
            'content_id': NEW_PRESENTATION_ID,
        },
        {
            'title':      'Module 2 GitHub Repo',
            'type':       'Assignment',
            'content_id': NEW_REPO_ID,
        },
    ]

    for item in items_to_add:
        r = api('POST', f'/courses/{COURSE}/modules/{MODULE}/items',
                {'module_item': item}, token=token)
        print(f"   Added: {r['title']}  (item id {r['id']}, position {r['position']})")

    # ── 5. Verify final state ──────────────────────────────────────────────
    print("\n5. Final module structure:")
    req = Request(f"{BASE}/api/v1/courses/{COURSE}/modules/{MODULE}/items?per_page=50")
    req.add_header('Authorization', f'Bearer {token}')
    resp = urlopen(req)
    items = json.loads(resp.read())
    for i in items:
        print(f"   {i['position']:2d}  {i['type']:12s}  {i['title']}")

    print("\nDone. Next: publish everything, then smoke-check as student.")


if __name__ == '__main__':
    main()
