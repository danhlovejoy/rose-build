#!/usr/bin/env python3
"""
create_module_assignments.py

Creates Canvas assignments, discussions, and module structure for any module
in either AIML 2003 (NLP) or AIML 2013 (CV).

Usage:
    python3 create_module_assignments.py <course> <module_num> <due_date>

Arguments:
    course       aiml2003 or aiml2013
    module_num   integer (1, 2, 3, …)
    due_date     ISO 8601 with offset, e.g. "2026-04-07T17:30:00-05:00"
                 AIML 2003 class time = 17:30  (5:30 PM CDT)
                 AIML 2013 class time = 19:00  (7:00 PM CDT)

What it does:
    1. Resolves the deliverable type for the module (Presentation, Demo, or
       Final Portfolio) from the course/module combination.
    2. Looks up Canvas assignment group IDs via API (no hard-coding needed).
    3. Creates four Canvas artifacts:
         - Module N Participation   (Assignment, 80 pts, No Submission)
         - Module N Ethics Discussion (Discussion, 20 pts)
         - Module N Presentation/Demo (Assignment, 100 pts, On Paper, rubric attached)
         - Module N GitHub Repo     (Assignment, 100 pts, Online URL, rubric attached)
    4. Finds the existing Canvas module by name pattern, removes any stale
       assignment/discussion items, and adds the new items in order.
    5. Publishes the module and all its items.

Week → Module mapping
    Module 1 spans Weeks 1-2. Module N (N≥2) = Week N+1.

Deliverable type by module:
    Module   NLP (2003)        CV (2013)
    -------  ----------------  ----------------
    1        Presentation      Presentation
    2        Presentation      Presentation
    3        Demo              Demo
    4        Demo              Demo
    5        Presentation      Demo
    6        Demo              Presentation
    7        Final Portfolio   Final Portfolio

Rubric IDs (fixed):
    NLP: Presentation=65800  Demo=65794  Repo=66034
    CV:  Presentation=66062  Demo=66063  Repo=66064
"""

import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://rose.instructure.com"

# ── Course config ──────────────────────────────────────────────────────────────

COURSES = {
    'aiml2003': {
        'course_id': 26943,
        'name':      'AIML 2003 — NLP',
        'rubrics': {
            'Presentation':     65800,
            'Demo':             65794,
            'Repo':             66034,
            'Final Portfolio':  65800,   # uses Presentation rubric
        },
    },
    'aiml2013': {
        'course_id': 26944,
        'name':      'AIML 2013 — CV',
        'rubrics': {
            'Presentation':     66062,
            'Demo':             66063,
            'Repo':             66064,
            'Final Portfolio':  66062,   # uses Presentation rubric
        },
    },
}

# Deliverable type per module per course (1-indexed)
DELIVERABLE = {
    'aiml2003': {
        1: 'Presentation',
        2: 'Presentation',
        3: 'Demo',
        4: 'Demo',
        5: 'Presentation',
        6: 'Demo',
        7: 'Final Portfolio',
    },
    'aiml2013': {
        1: 'Presentation',
        2: 'Presentation',
        3: 'Demo',
        4: 'Demo',
        5: 'Demo',
        6: 'Presentation',
        7: 'Final Portfolio',
    },
}


# ── Helpers ────────────────────────────────────────────────────────────────────

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
        print(f"  HTTP {e.code} on {method} {path}")
        print(f"  {detail[:400]}")
        raise


def get_assignment_groups(course_id, token):
    """Return dict: group_name → group_id"""
    req = Request(f"{BASE}/api/v1/courses/{course_id}/assignment_groups?per_page=50")
    req.add_header('Authorization', f'Bearer {token}')
    resp = urlopen(req)
    groups = json.loads(resp.read())
    return {g['name']: g['id'] for g in groups}


def find_canvas_module(course_id, module_num, token):
    """Return (module_id, module_name) for the module whose name contains
    'Module {module_num}' (case-insensitive). Raises if not found."""
    req = Request(f"{BASE}/api/v1/courses/{course_id}/modules?per_page=50")
    req.add_header('Authorization', f'Bearer {token}')
    resp = urlopen(req)
    modules = json.loads(resp.read())
    needle = f"module {module_num}".lower()
    for m in modules:
        if needle in m['name'].lower():
            return m['id'], m['name']
    names = [m['name'] for m in modules]
    raise RuntimeError(
        f"No Canvas module found matching 'Module {module_num}'. "
        f"Existing modules: {names}"
    )


def get_module_items(course_id, module_id, token):
    req = Request(
        f"{BASE}/api/v1/courses/{course_id}/modules/{module_id}/items?per_page=50"
    )
    req.add_header('Authorization', f'Bearer {token}')
    resp = urlopen(req)
    return json.loads(resp.read())


def remove_assignment_items(course_id, module_id, items, token):
    """Remove Assignment and Discussion items from the module (leaves Pages)."""
    removed = []
    for item in items:
        if item['type'] in ('Assignment', 'Discussion'):
            try:
                api('DELETE',
                    f'/courses/{course_id}/modules/{module_id}/items/{item["id"]}',
                    token=token)
                removed.append(item)
                print(f"   Removed module item: {item['title']} (id {item['id']})")
            except HTTPError:
                print(f"   Could not remove item {item['id']} — skipping")
    return removed


def delete_canvas_artifact(course_id, item, token):
    """Delete the Canvas assignment or discussion that backed a module item."""
    content_id = item.get('content_id')
    if not content_id:
        return
    try:
        if item['type'] == 'Assignment':
            api('DELETE', f'/courses/{course_id}/assignments/{content_id}', token=token)
            print(f"   Deleted assignment {content_id}: {item['title']}")
        elif item['type'] == 'Discussion':
            api('DELETE', f'/courses/{course_id}/discussion_topics/{content_id}',
                token=token)
            print(f"   Deleted discussion {content_id}: {item['title']}")
    except HTTPError:
        print(f"   Could not delete {item['type']} {content_id} — may already be gone")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 create_module_assignments.py <course> <module_num> <due_date>")
        print("  course     : aiml2003 or aiml2013")
        print("  module_num : 1-7")
        print("  due_date   : e.g. 2026-04-07T17:30:00-05:00")
        print()
        print("Examples:")
        print("  python3 create_module_assignments.py aiml2003 2 2026-04-07T17:30:00-05:00")
        print("  python3 create_module_assignments.py aiml2013 3 2026-04-14T19:00:00-05:00")
        sys.exit(1)

    course_key = sys.argv[1].lower()
    module_num = int(sys.argv[2])
    due_date   = sys.argv[3]

    if course_key not in COURSES:
        print(f"Unknown course '{course_key}'. Use aiml2003 or aiml2013.")
        sys.exit(1)
    if module_num not in DELIVERABLE[course_key]:
        print(f"Module {module_num} not in deliverable table for {course_key}.")
        sys.exit(1)

    cfg          = COURSES[course_key]
    course_id    = cfg['course_id']
    deliverable  = DELIVERABLE[course_key][module_num]
    rubrics      = cfg['rubrics']
    label        = f"Module {module_num}"
    token        = load_token()

    print(f"\n{'='*60}")
    print(f"Course      : {course_key} (id {course_id})")
    print(f"Module      : {label}")
    print(f"Deliverable : {deliverable}")
    print(f"Due         : {due_date}")
    print(f"{'='*60}\n")

    # ── Resolve assignment group IDs via API ──────────────────────────────────
    print("Resolving assignment groups…")
    groups = get_assignment_groups(course_id, token)
    print(f"  Found: {list(groups.keys())}")

    # Flexible group name lookup (Canvas group names differ slightly per course)
    def group_id(name_fragment):
        for k, v in groups.items():
            if name_fragment.lower() in k.lower():
                return v
        raise RuntimeError(f"No assignment group matching '{name_fragment}'")

    grp_participation = group_id('participation')
    grp_repos         = group_id('repo')
    grp_presentations = group_id('presentation')
    grp_demos         = group_id('demo')

    if deliverable in ('Presentation', 'Final Portfolio'):
        grp_deliverable = grp_presentations
    else:
        grp_deliverable = grp_demos

    rubric_deliverable = rubrics[deliverable]
    rubric_repo        = rubrics['Repo']

    # ── Find the Canvas module ────────────────────────────────────────────────
    print(f"\nFinding Canvas module for Module {module_num}…")
    module_id, module_name = find_canvas_module(course_id, module_num, token)
    print(f"  Found: '{module_name}' (id {module_id})")

    # ── Remove stale assignment/discussion items ───────────────────────────────
    print("\nRemoving any existing assignment/discussion items from module…")
    existing_items = get_module_items(course_id, module_id, token)
    removed = remove_assignment_items(course_id, module_id, existing_items, token)
    if not removed:
        print("  (none to remove)")

    print("\nDeleting the stale Canvas artifacts…")
    for item in removed:
        delete_canvas_artifact(course_id, item, token)

    # ── Create four new Canvas artifacts ──────────────────────────────────────
    print(f"\nCreating {label} artifacts…")
    created = []

    # 1. Participation
    print(f"  1. {label} Participation (80 pts, No Submission)…")
    r = api('POST', f'/courses/{course_id}/assignments', {
        'assignment': {
            'name':                  f'{label} Participation',
            'points_possible':       80,
            'assignment_group_id':   grp_participation,
            'submission_types':      ['none'],
            'due_at':                due_date,
            'published':             False,
        }
    }, token)
    print(f"     OK  id={r['id']}")
    created.append({'title': f'{label} Participation', 'type': 'Assignment',
                    'content_id': r['id']})

    # 2. Ethics Discussion
    print(f"  2. {label} Ethics Discussion (20 pts)…")
    r = api('POST', f'/courses/{course_id}/discussion_topics', {
        'title':           f'{label} Ethics Discussion',
        'discussion_type': 'threaded',
        'assignment': {
            'points_possible':    20,
            'assignment_group_id': grp_participation,
            'due_at':             due_date,
            'submission_types':   ['discussion_topic'],
            'published':          False,
        },
        'published': False,
    }, token)
    print(f"     OK  id={r['id']}")
    created.append({'title': f'{label} Ethics Discussion', 'type': 'Discussion',
                    'content_id': r['id']})

    # 3. Presentation / Demo / Final Portfolio
    print(f"  3. {label} {deliverable} (100 pts, On Paper, rubric {rubric_deliverable})…")
    r = api('POST', f'/courses/{course_id}/assignments', {
        'assignment': {
            'name':                  f'{label} {deliverable}',
            'points_possible':       100,
            'assignment_group_id':   grp_deliverable,
            'submission_types':      ['on_paper'],
            'due_at':                due_date,
            'published':             False,
            'rubric':                {'id': str(rubric_deliverable)},
            'rubric_settings': {
                'point_deductions':              False,
                'free_form_criterion_comments':  True,
            },
            'use_rubric_for_grading': True,
        }
    }, token)
    print(f"     OK  id={r['id']}")
    created.append({'title': f'{label} {deliverable}', 'type': 'Assignment',
                    'content_id': r['id']})

    # 4. GitHub Repo
    print(f"  4. {label} GitHub Repo (100 pts, Online URL, rubric {rubric_repo})…")
    r = api('POST', f'/courses/{course_id}/assignments', {
        'assignment': {
            'name':                  f'{label} GitHub Repo',
            'points_possible':       100,
            'assignment_group_id':   grp_repos,
            'submission_types':      ['online_url'],
            'due_at':                due_date,
            'published':             False,
            'rubric':                {'id': str(rubric_repo)},
            'rubric_settings': {
                'point_deductions':              False,
                'free_form_criterion_comments':  True,
            },
            'use_rubric_for_grading': True,
        }
    }, token)
    print(f"     OK  id={r['id']}")
    created.append({'title': f'{label} GitHub Repo', 'type': 'Assignment',
                    'content_id': r['id']})

    # ── Add items to module ────────────────────────────────────────────────────
    print(f"\nAdding items to Canvas module '{module_name}'…")
    for item in created:
        r = api('POST', f'/courses/{course_id}/modules/{module_id}/items',
                {'module_item': item}, token)
        print(f"  Added: {r['title']}  (item id {r['id']}, position {r['position']})")

    # ── Publish module + all items ─────────────────────────────────────────────
    print("\nPublishing module and all items…")
    api('PUT', f'/courses/{course_id}/modules/{module_id}',
        {'module': {'published': True}}, token)

    all_items = get_module_items(course_id, module_id, token)
    for item in all_items:
        api('PUT', f'/courses/{course_id}/modules/{module_id}/items/{item["id"]}',
            {'module_item': {'published': True}}, token)
        print(f"  Published: {item['title']}")

    # ── Final summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"DONE — {label} ({course_key})")
    print()
    all_items = get_module_items(course_id, module_id, token)
    for item in all_items:
        print(f"  {item['position']:2d}  {item['type']:12s}  {item['title']}")
    print()
    print("Next steps:")
    print("  1. Verify rubrics attached correctly in Canvas UI")
    print("  2. Run: python3 upload_to_canvas.py (if pages not yet uploaded)")
    print("  3. Update welcome page (Monday night / Tuesday before class only)")


if __name__ == '__main__':
    main()
