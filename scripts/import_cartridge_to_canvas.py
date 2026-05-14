#!/usr/bin/env python3
"""
import_cartridge_to_canvas.py — Import the Canvas cartridge bundle into a course.

Modes:
    Single-cartridge:
        python3 scripts/import_cartridge_to_canvas.py <cartridge.imscc> <course_id>

    Full course bundle (cartridges + quizzes + assignment shells + rubrics):
        python3 scripts/import_cartridge_to_canvas.py --bundle <course> <course_id> \\
            [--start-date YYYY-MM-DD] [--source-course <id>]

In --bundle mode, the script:
    1. Imports the master cartridge (pages, modules, graded ethics discussions).
    2. Imports each per-module reading quiz IMSCC.
    3. Imports the final exam IMSCC.
    4. Places quizzes into their target modules via the Canvas API and removes
       the leftover "Misc Module" Canvas auto-creates.
    5. Clones the three deliverable rubrics (Presentation, Demo, Repo) from the
       source course (26943 for aiml2003, 26944 for aiml2013, or --source-course)
       into the target course.
    6. Creates per-module assignment shells: Participation (80 pts; 100 for
       Module 6), Presentation or Demo (100 pts, rubric attached), GitHub Repo
       (100 pts, rubric attached). Sets due dates from --start-date (default
       2026-03-31, the source semester's first Tuesday) walking forward by week.
    7. Backfills due dates on the Phase-2 graded ethics discussions.

The script splits cartridge imports because Canvas's CC importer fails on
cartridges that contain more than one standalone QTI quiz resource.

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


# ──────────────────────────────────────────────────────────────────────
# Phase 3: rubric cloning + assignment shells
# ──────────────────────────────────────────────────────────────────────

# Rubric IDs that live in the live courses. Future instructors can override
# --source-course to point at their own backup course.
RUBRIC_SOURCE = {
    "aiml2003": {
        "course_id": 26943,
        "rubrics": {"Presentation": 65800, "Demo": 65794, "Repo": 66034},
    },
    "aiml2013": {
        "course_id": 26944,
        "rubrics": {"Presentation": 66062, "Demo": 66063, "Repo": 66064},
    },
}

# Deliverable type by course / module
DELIVERABLE_BY_MODULE = {
    "aiml2003": {1: "Presentation", 2: "Presentation", 3: "Demo", 4: "Demo",
                  5: "Presentation", 6: "Demo", 7: "Final Portfolio"},
    "aiml2013": {1: "Presentation", 2: "Presentation", 3: "Demo", 4: "Demo",
                  5: "Demo", 6: "Presentation", 7: "Final Portfolio"},
}

# Source semester class times (ISO 8601 with CDT offset)
CLASS_TIME = {"aiml2003": "17:30:00-05:00", "aiml2013": "19:00:00-05:00"}
DEFAULT_START_DATE = "2026-03-31"  # Module 1 Tuesday, Spring 2026 2nd 8 weeks


def module_due_at(course, module_num, start_date_str):
    """Return ISO 8601 due_at string for a module, walking forward by 1 week from Module 1."""
    from datetime import datetime, timedelta
    base = datetime.strptime(start_date_str, "%Y-%m-%d")
    due_day = base + timedelta(days=(module_num - 1) * 7)
    return f"{due_day.strftime('%Y-%m-%d')}T{CLASS_TIME[course]}"


def fetch_rubric_data(course_id, rubric_id, token):
    """Get a rubric (with criteria + ratings) from a source course."""
    return api_request(
        f"{CANVAS_BASE}/api/v1/courses/{course_id}/rubrics/{rubric_id}",
        token=token,
    )


def post_rubric_to_course(target_course_id, rubric, token):
    """Create a rubric in target course based on a source rubric dict.

    Returns the new rubric id. Canvas requires form-encoded nested params and
    a rubric_association payload for the rubric to attach to the course.
    """
    fields = {
        "rubric[title]": rubric["title"],
        "rubric[free_form_criterion_comments]":
            "1" if rubric.get("free_form_criterion_comments") else "0",
        "rubric_association[association_id]": str(target_course_id),
        "rubric_association[association_type]": "Course",
        "rubric_association[use_for_grading]": "0",
        "rubric_association[purpose]": "bookmark",
    }
    for i, crit in enumerate(rubric.get("data", [])):
        fields[f"rubric[criteria][{i}][description]"] = crit.get("description", "")
        fields[f"rubric[criteria][{i}][long_description]"] = crit.get("long_description", "") or ""
        fields[f"rubric[criteria][{i}][points]"] = str(crit.get("points", 0))
        for j, rating in enumerate(crit.get("ratings", [])):
            fields[f"rubric[criteria][{i}][ratings][{j}][description]"] = rating.get("description", "")
            fields[f"rubric[criteria][{i}][ratings][{j}][long_description]"] = rating.get("long_description", "") or ""
            fields[f"rubric[criteria][{i}][ratings][{j}][points]"] = str(rating.get("points", 0))

    result = api_request(
        f"{CANVAS_BASE}/api/v1/courses/{target_course_id}/rubrics",
        method="POST", token=token, data=fields,
    )
    # Canvas returns {"rubric": {...}, "rubric_association": {...}}
    inner = result.get("rubric") or result
    return inner.get("id")


def clone_rubrics_to_course(course, target_course_id, token, source_course_id=None):
    """Clone the three deliverable rubrics from source to target. Returns name → id map.

    Reuses existing rubrics in the target if a same-titled rubric is already there
    (e.g., on a re-run of the bundle import).
    """
    source = RUBRIC_SOURCE[course]
    if source_course_id is None:
        source_course_id = source["course_id"]

    existing = api_fetch_all(
        f"{CANVAS_BASE}/api/v1/courses/{target_course_id}/rubrics?per_page=50",
        token,
    )
    by_title = {r["title"]: r["id"] for r in existing}

    mapping = {}
    for name, src_rubric_id in source["rubrics"].items():
        if name in by_title:
            mapping[name] = by_title[name]
            print(f"    {name}: reusing existing rubric in target (id {by_title[name]})")
            continue
        print(f"    {name}: cloning from course {source_course_id} (src id {src_rubric_id})...")
        rubric_data = fetch_rubric_data(source_course_id, src_rubric_id, token)
        new_id = post_rubric_to_course(target_course_id, rubric_data, token)
        mapping[name] = new_id
        print(f"      → new id {new_id}")
    return mapping


def find_assignment_groups(course_id, token):
    groups = api_request(
        f"{CANVAS_BASE}/api/v1/courses/{course_id}/assignment_groups?per_page=50",
        token=token,
    )
    return {g["name"]: g["id"] for g in groups}


def find_module_by_number(modules, num):
    for m in modules:
        if m["name"].strip().lower() == "misc module":
            continue
        if re.search(rf"\bmodule\s+{num}\b", m["name"], re.I):
            return m
    return None


def create_assignment(course_id, name, points, group_id, submission_type, due_at, token):
    """Create an unpublished assignment via API. Returns its id."""
    r = api_request(
        f"{CANVAS_BASE}/api/v1/courses/{course_id}/assignments",
        method="POST", token=token,
        data={
            "assignment[name]": name,
            "assignment[points_possible]": str(points),
            "assignment[assignment_group_id]": str(group_id),
            "assignment[submission_types][]": submission_type,
            "assignment[due_at]": due_at,
            "assignment[published]": "false",
        },
    )
    return r["id"]


def attach_rubric_to_assignment(course_id, assignment_id, rubric_id, token):
    """Attach a rubric to an assignment for grading."""
    if not rubric_id:
        return
    api_request(
        f"{CANVAS_BASE}/api/v1/courses/{course_id}/rubric_associations",
        method="POST", token=token,
        data={
            "rubric_association[rubric_id]": str(rubric_id),
            "rubric_association[association_id]": str(assignment_id),
            "rubric_association[association_type]": "Assignment",
            "rubric_association[use_for_grading]": "1",
            "rubric_association[purpose]": "grading",
        },
    )


def add_module_item(course_id, module_id, title, item_type, content_id, token):
    api_request(
        f"{CANVAS_BASE}/api/v1/courses/{course_id}/modules/{module_id}/items",
        method="POST", token=token,
        data={
            "module_item[title]": title,
            "module_item[type]": item_type,
            "module_item[content_id]": str(content_id),
        },
    )


def create_assignment_shells(course, target_course_id, rubric_map, start_date, token):
    """Per-module: Participation + Presentation/Demo + GitHub Repo. Ethics already
    created by Phase 2 as a graded discussion; we backfill its due date here."""
    groups = find_assignment_groups(target_course_id, token)

    def gid(fragment):
        for k, v in groups.items():
            if fragment.lower() in k.lower():
                return v
        raise SystemExit(f"No assignment group matching '{fragment}' in target course")

    grp_part = gid("Participation")
    grp_repo = gid("Repos")
    grp_pres = gid("Presentation")
    grp_demo = gid("Demos")
    grp_portfolio = None
    grp_reflection = None
    for k, v in groups.items():
        if "Final Portfolio" in k:
            grp_portfolio = v
        if "Final Reflection" in k:
            grp_reflection = v

    modules = api_fetch_all(
        f"{CANVAS_BASE}/api/v1/courses/{target_course_id}/modules?per_page=100",
        token,
    )

    for mod_num in range(1, 8):
        module = find_module_by_number(modules, mod_num)
        if not module:
            print(f"    Module {mod_num}: not found in target, skipping")
            continue

        deliverable = DELIVERABLE_BY_MODULE[course][mod_num]
        due_at = module_due_at(course, mod_num, start_date)
        is_module6 = (mod_num == 6)
        label = f"Module {mod_num}"

        # 1. Participation (100 pts for Module 6, otherwise 80)
        part_pts = 100 if is_module6 else 80
        part_id = create_assignment(
            target_course_id, f"{label} Participation", part_pts, grp_part,
            "none", due_at, token,
        )
        add_module_item(
            target_course_id, module["id"], f"{label} Participation",
            "Assignment", part_id, token,
        )

        # 2. Presentation / Demo / Final Portfolio (with rubric)
        if deliverable == "Final Portfolio":
            deliv_group = grp_portfolio or grp_pres
            deliv_rubric_key = "Presentation"
        elif deliverable == "Presentation":
            deliv_group = grp_pres
            deliv_rubric_key = "Presentation"
        else:  # Demo
            deliv_group = grp_demo
            deliv_rubric_key = "Demo"

        deliv_id = create_assignment(
            target_course_id, f"{label} {deliverable}", 100, deliv_group,
            "on_paper", due_at, token,
        )
        attach_rubric_to_assignment(
            target_course_id, deliv_id, rubric_map.get(deliv_rubric_key), token,
        )
        add_module_item(
            target_course_id, module["id"], f"{label} {deliverable}",
            "Assignment", deliv_id, token,
        )

        # 3. GitHub Repo (with rubric)
        repo_id = create_assignment(
            target_course_id, f"{label} GitHub Repo", 100, grp_repo,
            "online_url", due_at, token,
        )
        attach_rubric_to_assignment(
            target_course_id, repo_id, rubric_map.get("Repo"), token,
        )
        add_module_item(
            target_course_id, module["id"], f"{label} GitHub Repo",
            "Assignment", repo_id, token,
        )

        print(f"    Module {mod_num}: Participation ({part_pts} pts), "
              f"{deliverable} (100 pts), GitHub Repo (100 pts)")


def backfill_ethics_due_dates(course, target_course_id, start_date, token):
    """Phase 2 created ethics discussions but didn't set due_at. Add it now."""
    discussions = api_fetch_all(
        f"{CANVAS_BASE}/api/v1/courses/{target_course_id}/discussion_topics?per_page=100",
        token,
    )
    updated = 0
    for d in discussions:
        title = d.get("title", "")
        m = re.match(r"Module\s+(\d+)\s+Ethics", title, re.I)
        if not m:
            continue
        mod_num = int(m.group(1))
        assignment_id = d.get("assignment_id")
        if not assignment_id:
            continue
        due_at = module_due_at(course, mod_num, start_date)
        api_request(
            f"{CANVAS_BASE}/api/v1/courses/{target_course_id}/assignments/{assignment_id}",
            method="PUT", token=token,
            data={"assignment[due_at]": due_at},
        )
        updated += 1
    print(f"    Set due dates on {updated} ethics discussion(s).")


def import_full_bundle(course, course_id, token, start_date=None, source_course_id=None):
    """Master cartridge + quizzes + assignment shells + rubrics."""
    master = os.path.join(ROOT, "dist", f"{course}-canvas-import.imscc")
    quizzes_dir = os.path.join(ROOT, "quizzes")
    final_exam_dir = os.path.join(ROOT, "final-exam")
    start_date = start_date or DEFAULT_START_DATE

    print(f"Target:     {CANVAS_BASE}/courses/{course_id}")
    print(f"Start date: {start_date}  (Module 1 Tuesday; later modules walk forward by 1 week)")
    if source_course_id:
        print(f"Rubric src: course {source_course_id}")

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

    print(f"\n[5] Cloning deliverable rubrics:")
    rubric_map = clone_rubrics_to_course(course, course_id, token, source_course_id)

    print(f"\n[6] Creating per-module assignment shells:")
    create_assignment_shells(course, course_id, rubric_map, start_date, token)

    print(f"\n[7] Backfilling ethics-discussion due dates:")
    backfill_ethics_due_dates(course, course_id, start_date, token)

    print(f"\nDone. View at {CANVAS_BASE}/courses/{course_id}")


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    token = load_token()

    # Pull out optional flags
    start_date = None
    source_course_id = None
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--start-date" and i + 1 < len(args):
            start_date = args[i + 1]
            i += 2
        elif args[i] == "--source-course" and i + 1 < len(args):
            source_course_id = args[i + 1]
            i += 2
        else:
            positional.append(args[i])
            i += 1

    if positional[:1] == ["--bundle"] and len(positional) == 3:
        _, course, course_id = positional
        if course not in {"aiml2003", "aiml2013"}:
            raise SystemExit("Course must be aiml2003 or aiml2013")
        import_full_bundle(course, course_id, token,
                           start_date=start_date, source_course_id=source_course_id)
        return

    if len(positional) == 2:
        cartridge_path, course_id = positional
        print(f"Target: {CANVAS_BASE}/courses/{course_id}")
        import_cartridge(cartridge_path, course_id, token)
        print(f"View at {CANVAS_BASE}/courses/{course_id}")
        return

    print(__doc__.strip())
    sys.exit(1)


if __name__ == "__main__":
    main()
