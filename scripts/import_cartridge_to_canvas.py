#!/usr/bin/env python3
"""
import_cartridge_to_canvas.py — Import a .imscc cartridge into a Canvas course via API.

Mirrors the Canvas UI flow (Course Settings → Import Course Content →
Common Cartridge 1.x Package) using the content_migrations API.

Usage:
    python3 scripts/import_cartridge_to_canvas.py <cartridge.imscc> <course_id>

Example:
    python3 scripts/import_cartridge_to_canvas.py dist/aiml2003-canvas-import.imscc 20338

Reads CANVAS_TOKEN from .env. Polls until the migration completes or fails.
Stdlib only.
"""

import json
import mimetypes
import os
import secrets
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

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
    """Send a JSON request to the Canvas API and return the parsed JSON response."""
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


def multipart_upload(url, fields, filepath):
    """POST a file to a Canvas file-upload endpoint using multipart/form-data."""
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


def import_cartridge(cartridge_path, course_id, token):
    if not os.path.exists(cartridge_path):
        raise SystemExit(f"Cartridge not found: {cartridge_path}")
    size = os.path.getsize(cartridge_path)
    print(f"  Cartridge: {cartridge_path} ({size:,} bytes)")
    print(f"  Target:    {CANVAS_BASE}/courses/{course_id}")

    # Step 1 — create the content_migration with a pre_attachment placeholder.
    print("  [1/4] Creating content migration...")
    url = f"{CANVAS_BASE}/api/v1/courses/{course_id}/content_migrations"
    data = {
        "migration_type": "common_cartridge_importer",
        "pre_attachment[name]": os.path.basename(cartridge_path),
        "pre_attachment[size]": size,
    }
    migration = api_request(url, method="POST", token=token, data=data)
    migration_id = migration["id"]
    pre_attachment = migration.get("pre_attachment")
    if not pre_attachment or "upload_url" not in pre_attachment:
        raise SystemExit(
            f"No pre_attachment.upload_url in migration response:\n{json.dumps(migration, indent=2)}"
        )
    upload_url = pre_attachment["upload_url"]
    upload_params = pre_attachment.get("upload_params", {})
    print(f"    migration_id={migration_id}")

    # Step 2 — POST the file to the pre-signed upload URL.
    print("  [2/4] Uploading cartridge...")
    status, body = multipart_upload(upload_url, upload_params, cartridge_path)
    if status not in (200, 201, 301, 302, 303):
        raise SystemExit(f"Upload failed (HTTP {status}):\n{body[:1000]}")
    print(f"    upload returned HTTP {status}")

    # Step 3 — poll the migration progress URL until completion.
    print("  [3/4] Polling migration progress...")
    progress_url = migration.get("progress_url")
    if not progress_url:
        # Fall back to the migration resource itself for status.
        progress_url = f"{CANVAS_BASE}/api/v1/courses/{course_id}/content_migrations/{migration_id}"
    deadline = time.time() + 300  # 5-minute ceiling for the import
    last_state = None
    while time.time() < deadline:
        progress = api_request(progress_url, token=token)
        state = progress.get("workflow_state") or progress.get("workflow_status")
        if state != last_state:
            print(f"    state: {state}")
            last_state = state
        if state in {"completed", "imported"}:
            break
        if state in {"failed", "failed_with_messages"}:
            raise SystemExit(
                f"Migration failed:\n{json.dumps(progress, indent=2)[:2000]}"
            )
        time.sleep(3)
    else:
        raise SystemExit("Migration timed out after 5 minutes")

    # Step 4 — fetch the final migration record to surface any per-item issues.
    print("  [4/4] Checking final migration record...")
    final_url = f"{CANVAS_BASE}/api/v1/courses/{course_id}/content_migrations/{migration_id}"
    final = api_request(final_url, token=token)
    issues = final.get("migration_issues_count")
    print(f"    workflow_state: {final.get('workflow_state')}")
    if issues:
        print(f"    migration issues: {issues}")
        issues_url = f"{final_url}/migration_issues"
        issue_list = api_request(issues_url, token=token)
        for issue in (issue_list if isinstance(issue_list, list) else [])[:10]:
            print(f"      - {issue.get('description')}")
    print(f"  View in Canvas: {CANVAS_BASE}/courses/{course_id}")


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip())
        sys.exit(1)
    cartridge_path, course_id = sys.argv[1], sys.argv[2]
    token = load_token()
    import_cartridge(cartridge_path, course_id, token)


if __name__ == "__main__":
    main()
