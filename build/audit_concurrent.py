#!/usr/bin/env python3
"""
audit_concurrent.py — Report all concurrent-only content across the project.

Scans all source HTML files and reports:
  - File-level concurrent files (entire file excluded in standalone mode)
  - Element-level concurrent blocks (stripped from pages in standalone mode)
  - Bridge boxes without data-concurrent (may need tagging)

Usage:
    python3 audit_concurrent.py [root_dir]

If root_dir is omitted, uses the parent of the directory containing this script.

Deterministic. No external dependencies. Python 3.8+ stdlib only.
"""

import os
import re
import sys


CONCURRENT_ATTR = r'data-concurrent\s*=\s*["\']true["\']'


def find_html_files(root: str) -> list:
    """Find all source HTML files (exclude build/output)."""
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip build output directory
        rel = os.path.relpath(dirpath, root)
        if rel.startswith('build/output') or rel.startswith('build\\output'):
            continue
        if 'output' in dirnames and os.path.basename(dirpath) == 'build':
            dirnames.remove('output')
        for fname in sorted(filenames):
            if fname.endswith('.html'):
                results.append(os.path.join(dirpath, fname))
    return results


def audit_file(filepath: str, root: str) -> dict:
    """Audit a single file for concurrent markers."""
    rel_path = os.path.relpath(filepath, root)

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    html = ''.join(lines)
    result = {
        'path': rel_path,
        'file_level': False,
        'elements': [],
        'untagged_bridge_boxes': [],
    }

    # Check for file-level concurrent marker
    if re.match(r'\s*<!--\s*concurrent-only\b', html):
        result['file_level'] = True
        return result

    body_match = re.search(r'<body\s[^>]*' + CONCURRENT_ATTR + r'[^>]*>', html, re.IGNORECASE)
    if body_match:
        result['file_level'] = True
        return result

    # Scan line by line for element-level markers and untagged bridge boxes
    for i, line in enumerate(lines, 1):
        if re.search(CONCURRENT_ATTR, line):
            # Extract a preview of the element
            preview = line.strip()[:100]
            result['elements'].append({'line': i, 'preview': preview})

        # Check for bridge-box without concurrent marker
        if 'bridge-box' in line and 'data-concurrent' not in line:
            if re.search(r'class\s*=\s*["\'][^"\']*bridge-box', line):
                preview = line.strip()[:100]
                result['untagged_bridge_boxes'].append({'line': i, 'preview': preview})

    return result


def main():
    if len(sys.argv) > 1:
        root = sys.argv[1]
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    html_files = find_html_files(root)

    file_level = []
    element_level = []
    untagged = []

    for filepath in html_files:
        info = audit_file(filepath, root)
        if info['file_level']:
            file_level.append(info)
        if info['elements']:
            element_level.append(info)
        if info['untagged_bridge_boxes']:
            untagged.append(info)

    # Report
    print("=" * 60)
    print("CONCURRENT CONTENT AUDIT")
    print("=" * 60)

    print(f"\n--- File-level concurrent ({len(file_level)} files) ---")
    print("These entire files are excluded in standalone mode.\n")
    if file_level:
        for info in file_level:
            print(f"  {info['path']}")
    else:
        print("  (none)")

    total_elements = sum(len(info['elements']) for info in element_level)
    print(f"\n--- Element-level concurrent ({total_elements} elements in {len(element_level)} files) ---")
    print("These blocks are stripped from their pages in standalone mode.\n")
    if element_level:
        for info in element_level:
            print(f"  {info['path']}:")
            for elem in info['elements']:
                print(f"    line {elem['line']}: {elem['preview']}")
    else:
        print("  (none)")

    total_untagged = sum(len(info['untagged_bridge_boxes']) for info in untagged)
    print(f"\n--- Untagged bridge boxes ({total_untagged} found) ---")
    print("These bridge-box elements do NOT have data-concurrent. Review whether they should.\n")
    if untagged:
        for info in untagged:
            print(f"  {info['path']}:")
            for elem in info['untagged_bridge_boxes']:
                print(f"    line {elem['line']}: {elem['preview']}")
    else:
        print("  (none — all bridge boxes are tagged)")

    print(f"\n{'=' * 60}")
    total = len(file_level) + total_elements
    print(f"Total concurrent items: {total} ({len(file_level)} files + {total_elements} elements)")
    if total_untagged:
        print(f"ACTION NEEDED: {total_untagged} bridge box(es) may need data-concurrent=\"true\"")
    print("=" * 60)


if __name__ == '__main__':
    main()
