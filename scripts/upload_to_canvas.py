#!/usr/bin/env python3
"""
upload_to_canvas.py — Upload built HTML pages to Canvas wiki.

Reads course configuration from build/course-config.json and the Canvas
API token from .env. For each course, iterates the pages mapping and
either creates (POST) or updates (PUT) the Canvas wiki page.

Usage:
    python3 upload_to_canvas.py                # upload everything
    python3 upload_to_canvas.py aiml2003       # one course
    python3 upload_to_canvas.py aiml2003 glossary  # one page

Canvas API docs:
    https://canvas.instructure.com/doc/api/pages.html
"""

import json
import os
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Load config ────────────────────────────────────────────────────────────

def load_config():
    path = os.path.join(ROOT, 'build', 'course-config.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def load_token():
    env_path = os.path.join(ROOT, '.env')
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                return line.split('=', 1)[1].strip()
    raise RuntimeError(".env file found but no token line detected")


# ── Canvas API helpers ──────────────────────────────────────────────────────

def page_exists(canvas_url, course_id, page_slug, token):
    """Return True if the wiki page already exists in Canvas."""
    url = f"{canvas_url}/api/v1/courses/{course_id}/pages/{page_slug}"
    req = Request(url)
    req.add_header('Authorization', f'Bearer {token}')
    try:
        urlopen(req)
        return True
    except HTTPError as e:
        if e.code == 404:
            return False
        raise


def create_page(canvas_url, course_id, page_slug, title, body, token):
    """POST — create a new wiki page."""
    url = f"{canvas_url}/api/v1/courses/{course_id}/pages"
    payload = json.dumps({
        'wiki_page': {
            'title': title,
            'url':   page_slug,
            'body':  body,
            'published': False,
        }
    }).encode('utf-8')
    req = Request(url, data=payload, method='POST')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    resp = urlopen(req)
    return json.loads(resp.read().decode('utf-8'))


def update_page(canvas_url, course_id, page_slug, body, token):
    """PUT — update an existing wiki page body."""
    url = f"{canvas_url}/api/v1/courses/{course_id}/pages/{page_slug}"
    payload = json.dumps({'wiki_page': {'body': body}}).encode('utf-8')
    req = Request(url, data=payload, method='PUT')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Content-Type', 'application/json')
    urlopen(req)


def upsert_page(canvas_url, course_id, page_slug, body, token):
    """Create if missing, update if present. Returns 'created' or 'updated'."""
    if page_exists(canvas_url, course_id, page_slug, token):
        update_page(canvas_url, course_id, page_slug, body, token)
        return 'updated'
    else:
        # Derive a readable title from the slug
        title = page_slug.replace('-', ' ').title()
        create_page(canvas_url, course_id, page_slug, title, body, token)
        return 'created'


# ── Main upload logic ───────────────────────────────────────────────────────

def upload_course(course_key, course_cfg, canvas_base, token,
                  filter_page=None):
    course_id = course_cfg['course_id']
    build_output = os.path.join(ROOT, course_cfg['build_output_dir'])

    print(f"  Course {course_id}  {course_cfg['name']}")
    print(f"  Output dir: {course_cfg['build_output_dir']}")
    print()

    ok = fail = skip = 0

    for page_slug, rel_path in course_cfg['pages'].items():
        # Optional single-page filter
        if filter_page and page_slug != filter_page:
            continue

        filepath = os.path.join(build_output, rel_path)

        if not os.path.exists(filepath):
            print(f"    SKIP  {page_slug}  (file not found: {rel_path})")
            skip += 1
            continue

        with open(filepath, encoding='utf-8') as f:
            body = f.read()

        try:
            action = upsert_page(canvas_base, course_id, page_slug, body, token)
            marker = 'NEW ' if action == 'created' else '    '
            print(f"    {marker}OK  {page_slug}")
            ok += 1
        except HTTPError as e:
            detail = e.read().decode('utf-8', errors='replace')[:200]
            print(f"    FAIL  {page_slug}  ({e.code}: {detail})")
            fail += 1

        time.sleep(0.3)  # polite rate limiting

    return ok, fail, skip


def main():
    config = load_config()
    token = load_token()
    canvas_base = config['canvas_base_url']

    # Parse CLI args: [course_key] [page_slug]
    filter_course = sys.argv[1] if len(sys.argv) > 1 else None
    filter_page   = sys.argv[2] if len(sys.argv) > 2 else None

    total_ok = total_fail = total_skip = 0

    for course_key, course_cfg in config['courses'].items():
        if filter_course and course_key != filter_course:
            continue

        print('=' * 60)
        print(f'{course_key.upper()}')
        print('=' * 60)

        ok, fail, skip = upload_course(
            course_key, course_cfg, canvas_base, token,
            filter_page=filter_page
        )
        total_ok   += ok
        total_fail += fail
        total_skip += skip
        print(f"\n  Result: {ok} ok, {fail} failed, {skip} skipped\n")

    print('=' * 60)
    print(f'TOTAL  {total_ok} ok  |  {total_fail} failed  |  {total_skip} skipped')
    if total_fail == 0:
        print('All pages uploaded successfully.')
    else:
        print('Some pages failed — check output above.')


if __name__ == '__main__':
    main()
