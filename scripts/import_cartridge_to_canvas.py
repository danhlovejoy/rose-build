#!/usr/bin/env python3
"""
import_cartridge_to_canvas.py — Import the Canvas cartridge bundle into a course.

Modes:
    Single-cartridge:
        python3 scripts/import_cartridge_to_canvas.py <cartridge.imscc> <course_id>

    Full course bundle (master cartridge + per-module reading quizzes + final exam):
        python3 scripts/import_cartridge_to_canvas.py --bundle <course> <course_id>

The bundle mode imports the master cartridge first (pages, modules, graded
discussions), then imports each per-quiz IMSCC from quizzes/, then the final
exam from final-exam/. After every cartridge lands, it walks the Canvas module
structure and inserts each quiz as a Module Item under the right module via
the Canvas API.

The split exists because Canvas's CC importer fails on cartridges that contain
more than one standalone QTI quiz resource. Per-quiz cartridges work, hence the
sequential import.

Reads CANVAS_TOKEN from .env. Stdlib only.
"""

import json
import mimetypes
import os
import re
import secrets
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANVAS_BASE = "https://rose.instructure.com"


def load_token():
    env_path = os.path.join(ROOT, ".env")
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("CANVAS_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise SystemExit("CANVAS_TOKEN not found in .env")


def api_request(url, method="GET", token=None, data=None, headers=None):
    body = None
    req_headers = {"Authorization": f"Bearer {token}"}
    if headers:
        req_headers.update(headers)
    if data is not None:
        body = urlencode(data, doseq=True).encode("utf-8")
        req_headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = Request(url, data=body, method=method, headers=req_headers)
    try:
        with urlopen(req) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else {}
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Canvas API error {e.code} on {method} {url}\n{body}")


def api_fetch_all(url, token):
    """Follow Link: rel=\"next\" pagination and return a flat list."""
    out = []
    while url:
        req = Request(url, headers={"Authorization": f"Bearer {token}"})
        with urlopen(req) as resp:
            out.extend(json.loads(resp.read()))
            link = resp.headers.get("Link", "")
            next_url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    next_url = part.split(";")[0].strip().strip("<>")
            url = next_url
    return out


def multipart_upload(url, fields, filepath):
    boundary = "----rose-cartridge-" + secrets.token_hex(16)
    body_chunks = []

    for name, value in fields.items():
        body_chunks.append(f"--{boundary}\r\n".encode())
        body_chunks.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        )
        body_chunks.append(str(value).encode("utf-8"))
        body_chunks.append(b"\r\n")

    filename = os.path.basename(filepath)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    body_chunks.append(f"--{boundary}\r\n".encode())
    body_chunks.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
    )
    body_chunks.append(f"Content-Type: {content_type}\r\n\r\n".encode())
    with open(filepath, "rb") as fh:
        body_chunks.append(fh.read())
    body_chunks.append(b"\r\n")
    body_chunks.append(f"--{boundary}--\r\n".encode())

    body = b"".join(body_chunks)
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body)),
    }
    req = Request(url, data=body, method="POST", headers=headers)
    try:
        with urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def import_cartridge(cartridge_path, course_id, token, verbose=True):
    """Import a single IMSCC cartridge. Returns migration_id."""
    if not os.path.exists(cartridge_path):
        raise SystemExit(f"Cartridge not found: {cartridge_path}")
    size = os.path.getsize(cartridge_path)
    if verbose:
        print(f"  ▸ {os.path.basename(cartridge_path)} ({size:,} bytes)")

    url = f"{CANVAS_BASE}/api/v1/courses/{course_id}/content_migrations"
    migration = api_request(url, method="POST", token=token, data={
        "migration_type": "common_cartridge_importer",
        "pre_attachment[name]": os.path.basename(cartridge_path),
        "pre_attachment[size]": size,
    })
    migration_id = migration["id"]
    pre = migration.get("pre_attachment") or {}
    upload_url = pre.get("upload_url")
    upload_params = pre.get("upload_params", {})
    if not upload_url:
        raise SystemExit(f"No upload_url in migration response:\n{json.dumps(migration, indent=2)}")

    status, body = multipart_upload(upload_url, upload_params, cartridge_path)
    if status not in (200, 201, 301, 302, 303):
        raise SystemExit(f"Upload failed (HTTP {status}):\n{body[:1000]}")

    progress_url = migration.get("progress_url") or (
        f"{CANVAS_BASE}/api/v1/courses/{course_id}/content_migrations/{migration_id}"
    )
    deadline = time.time() + 300
    last_state = None
    while time.time() < deadline:
        progress = api_request(progress_url, token=token)
        state = progress.get("workflow_state") or progress.get("workflow_status")
        if state != last_state:
            if verbose:
                print(f"    state: {state}")
            last_state = state
        if state in {"completed", "imported"}:
            break
        if state in {"failed", "failed_with_messages"}:
            raise SystemExit(f"Migration failed:\n{json.dumps(progress, indent=2)[:2000]}")
        time.sleep(3)
    else:
        raise SystemExit("Migration timed out after 5 minutes")

    final = api_request(
        f"{CANVAS_BASE}/api/v1/courses/{course_id}/content_migrations/{migration_id}",
        token=token,
    )
    issues = final.get("migration_issues_count") or 0
    if verbose and issues:
        print(f"    {issues} warning(s)")
    return migration_id


# ──────────────────────────────────────────────────────────────────────
# Bundle (master + quizzes) import
# ──────────────────────────────────────────────────────────────────────

QUIZ_FILENAME_RE = re.compile(r"(?:^|/)([\w-]+)-module(\d+)-reading-quiz\.imscc$")
FINAL_EXAM_RE = re.compile(r"(?:^|/)([\w-]+)-final-exam\.imscc$")


def quiz_to_module_assignment(course_short, course_id, token):
    """After all imports land, place each quiz under its target module via Canvas API.

    Maps reading quizzes module1-6 to Modules 1-6 and the final exam to Module 7.
    No-ops if a target module isn't found. Each per-quiz cartridge that Canvas
    couldn't merge into an existing module ends up in a leftover "Misc Module";
    we delete those after placement.
    """
    modules = api_fetch_all(
        f"{CANVAS_BASE}/api/v1/courses/{course_id}/modules?per_page=100", token,
    )
    name_to_module = {}
    misc_modules = []
    for m in modules:
        if m["name"].strip().lower() == "misc module":
            misc_modules.append(m)
            continue
        match = re.search(r"Module\s+(\d+)", m["name"])
        if match:
            name_to_module[int(match.group(1))] = m

    quizzes = api_fetch_all(
        f"{CANVAS_BASE}/api/v1/courses/{course_id}/quizzes?per_page=100", token,
    )

    # Find which quizzes are already in a non-Misc module (Canvas merged them
    # there automatically because the quiz cartridge's container module matched
    # by title prefix). We only need to API-add the rest.
    existing_module_quiz_ids = set()
    for m in modules:
        if m["name"].strip().lower() == "misc module":
            continue
        items = api_fetch_all(
            f"{CANVAS_BASE}/api/v1/courses/{course_id}/modules/{m['id']}/items?per_page=100",
            token,
        )
        for it in items:
            if it.get("type") == "Quiz" and it.get("content_id"):
                existing_module_quiz_ids.add(it["content_id"])

    placed = 0
    for q in quizzes:
        title = q.get("title", "")
        m_quiz = re.match(r"Module\s+(\d+)\s+Reading Quiz", title, re.IGNORECASE)
        is_final = "final exam" in title.lower()

        target_num = None
        if m_quiz:
            target_num = int(m_quiz.group(1))
        elif is_final:
            target_num = 7
        if target_num is None:
            continue
        if q["id"] in existing_module_quiz_ids:
            continue  # Canvas already placed it in the right module
        module = name_to_module.get(target_num)
        if not module:
            print(f"    skip: no Module {target_num} to place '{title}'")
            continue

        api_request(
            f"{CANVAS_BASE}/api/v1/courses/{course_id}/modules/{module['id']}/items",
            method="POST", token=token,
            data={
                "module_item[title]": title,
                "module_item[type]": "Quiz",
                "module_item[content_id]": q["id"],
                "module_item[indent]": 0,
            },
        )
        placed += 1
    print(f"  Placed {placed} quiz item(s) into modules.")

    # Drop any leftover "Misc Module" — its quiz items have been duplicated into
    # their proper modules above.
    for m in misc_modules:
        api_request(
            f"{CANVAS_BASE}/api/v1/courses/{course_id}/modules/{m['id']}",
            method="DELETE", token=token,
        )
        print(f"  Removed leftover module: {m['name']}")


def import_full_bundle(course, course_id, token):
    """Master cartridge + per-quiz cartridges + final exam, then arrange in modules."""
    master = os.path.join(ROOT, "dist", f"{course}-canvas-import.imscc")
    quizzes_dir = os.path.join(ROOT, "quizzes")
    final_exam_dir = os.path.join(ROOT, "final-exam")

    print(f"Target: {CANVAS_BASE}/courses/{course_id}")

    print(f"\n[1] Master cartridge:")
    import_cartridge(master, course_id, token)

    print(f"\n[2] Per-module reading quizzes:")
    quiz_paths = sorted(
        os.path.join(quizzes_dir, f)
        for f in os.listdir(quizzes_dir)
        if f.startswith(f"{course}-module") and f.endswith("-reading-quiz.imscc")
    )
    for path in quiz_paths:
        import_cartridge(path, course_id, token)

    print(f"\n[3] Final exam:")
    final_path = os.path.join(final_exam_dir, f"{course}-final-exam.imscc")
    if os.path.exists(final_path):
        import_cartridge(final_path, course_id, token)
    else:
        print("  (no final-exam IMSCC found, skipping)")

    print(f"\n[4] Placing quizzes into modules via Canvas API:")
    quiz_to_module_assignment(course, course_id, token)

    print(f"\nDone. View at {CANVAS_BASE}/courses/{course_id}")


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    token = load_token()

    if args[:1] == ["--bundle"] and len(args) == 3:
        _, course, course_id = args
        if course not in {"aiml2003", "aiml2013"}:
            raise SystemExit("Course must be aiml2003 or aiml2013")
        import_full_bundle(course, course_id, token)
        return

    if len(args) == 2:
        cartridge_path, course_id = args
        print(f"Target: {CANVAS_BASE}/courses/{course_id}")
        import_cartridge(cartridge_path, course_id, token)
        print(f"View at {CANVAS_BASE}/courses/{course_id}")
        return

    print(__doc__.strip())
    sys.exit(1)


if __name__ == "__main__":
    main()
