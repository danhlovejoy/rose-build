#!/usr/bin/env python3
"""
check_links.py — Dead link checker for source HTML files.

Scans all source HTML files under aiml2003/ and aiml2013/ for href and src
attributes, resolves relative paths, and reports any targets that don't exist
on disk. Skips external URLs, Canvas paths, and anchor-only links.

Usage:
    python3 build/check_links.py                  # check everything
    python3 build/check_links.py aiml2003/module2 # check one directory

Exit code 0 if no dead links, 1 if any found.
Stdlib only — no external dependencies.
"""

import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Attributes that contain link targets
LINK_ATTRS = {'href', 'src'}

# Prefixes to skip (not local file references)
SKIP_PREFIXES = (
    'http://', 'https://', 'mailto:', 'tel:', 'data:',
    '#',           # same-page anchor
    '/courses/',   # Canvas-internal path
    '/api/',       # Canvas API
    '{{',          # template placeholder
)


class LinkExtractor(HTMLParser):
    """Extract (attr, url, line) tuples from an HTML file."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for attr_name, attr_value in attrs:
            if attr_name in LINK_ATTRS and attr_value:
                self.links.append((attr_name, attr_value, self.getpos()[0]))


def extract_links(filepath):
    """Return list of (attr, url, lineno) from an HTML file."""
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    parser = LinkExtractor()
    parser.feed(content)
    return parser.links


def resolve_link(source_file, url):
    """Resolve a relative URL against the source file's directory.

    Returns the absolute path the link points to, or None if the URL
    should be skipped (external, anchor-only, etc.).
    """
    # Strip fragment
    url_no_fragment = url.split('#')[0]
    if not url_no_fragment:
        return None  # anchor-only

    # Skip non-file URLs
    for prefix in SKIP_PREFIXES:
        if url_no_fragment.startswith(prefix):
            return None

    source_dir = os.path.dirname(source_file)
    return os.path.normpath(os.path.join(source_dir, url_no_fragment))


def find_html_files(target):
    """Find all .html files under the target directory."""
    target_path = os.path.join(ROOT, target) if target else ROOT
    html_files = []
    for dirpath, _dirnames, filenames in os.walk(target_path):
        # Skip build output, templates, and hidden dirs
        rel = os.path.relpath(dirpath, ROOT)
        if rel.startswith('build') or rel.startswith('.') or rel.startswith('templates'):
            continue
        for fname in sorted(filenames):
            if fname.endswith('.html'):
                html_files.append(os.path.join(dirpath, fname))
    return html_files


def check_links(target=None):
    """Check all internal links. Returns list of (file, line, attr, url, resolved) tuples."""
    html_files = find_html_files(target)
    dead = []

    for filepath in html_files:
        rel_file = os.path.relpath(filepath, ROOT)
        links = extract_links(filepath)
        for attr, url, lineno in links:
            resolved = resolve_link(filepath, url)
            if resolved is None:
                continue
            if not os.path.exists(resolved):
                dead.append((rel_file, lineno, attr, url, resolved))

    return dead


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None

    # Validate target
    if target:
        target_path = os.path.join(ROOT, target)
        if not os.path.isdir(target_path):
            print(f"ERROR: directory not found: {target}")
            sys.exit(2)

    dead = check_links(target)

    if not dead:
        scope = target or 'all courses'
        print(f"No dead links found ({scope}).")
        sys.exit(0)

    # Group by file for readability
    current_file = None
    for rel_file, lineno, attr, url, resolved in dead:
        if rel_file != current_file:
            current_file = rel_file
            print(f"\n\033[1m{rel_file}\033[0m")
        rel_target = os.path.relpath(resolved, ROOT)
        print(f"  line {lineno}: {attr}=\"{url}\" → {rel_target} (not found)")

    print(f"\n\033[31m{len(dead)} dead link(s) found.\033[0m")
    sys.exit(1)


if __name__ == '__main__':
    main()
