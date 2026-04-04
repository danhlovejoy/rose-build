#!/usr/bin/env python3
"""
strip_concurrent.py — Remove concurrent-only content for standalone delivery.

When both AIML 2003 and AIML 2013 are offered simultaneously, some content
(bridge boxes, combined lab references, combined lab files) only makes sense
for dual-enrolled students. This script strips elements marked with
data-concurrent="true" so a course can be delivered independently.

Two modes of operation:
  1. Element-level stripping: Removes any element with data-concurrent="true"
     from within a page, preserving the rest of the page.
  2. File-level exclusion: If the root content wrapper (first child of <body>,
     or body itself) has data-concurrent="true", the entire file is excluded
     from build output.

Usage:
    python3 strip_concurrent.py <input_file> <output_file>
    python3 strip_concurrent.py --check <input_file>
        (exit 0 if file should be included, exit 1 if file-level concurrent)

Deterministic. No LLM. No external dependencies. Python 3.8+ stdlib only.
"""

import re
import sys


# Pattern to match elements with data-concurrent="true"
# Matches opening tag, content, and closing tag
CONCURRENT_ATTR = r'data-concurrent\s*=\s*["\']true["\']'


def is_file_level_concurrent(html: str) -> bool:
    """Check if the entire file is marked concurrent.

    Returns True if the first substantive element after <body> (or the
    top-level wrapper div) has data-concurrent="true".
    """
    # Check for concurrent marker in a top-level wrapper after <body>
    body_match = re.search(r'<body[^>]*>', html, re.IGNORECASE)
    if body_match:
        after_body = html[body_match.end():].lstrip()
        # Check if the first element after <body> has concurrent attribute
        first_tag = re.match(r'<(\w+)\s[^>]*' + CONCURRENT_ATTR + r'[^>]*>', after_body)
        if first_tag:
            return True

    # Check for concurrent marker on <body> itself
    if re.search(r'<body\s[^>]*' + CONCURRENT_ATTR + r'[^>]*>', html, re.IGNORECASE):
        return True

    # Check for HTML comment marker at the very top (before doctype/html)
    if re.match(r'\s*<!--\s*concurrent-only\b', html):
        return True

    return False


def strip_concurrent_elements(html: str) -> str:
    """Remove all elements with data-concurrent="true" from the HTML.

    Handles nested HTML by tracking tag depth. Works on both self-closing
    tags and container elements.
    """
    result = []
    pos = 0

    while pos < len(html):
        # Find next opening tag with data-concurrent="true"
        match = re.search(
            r'<(\w+)(\s[^>]*' + CONCURRENT_ATTR + r'[^>]*)(/?)>',
            html[pos:]
        )
        if not match:
            result.append(html[pos:])
            break

        # Keep everything before this element
        result.append(html[pos:pos + match.start()])

        tag_name = match.group(1)
        self_closing = match.group(3) == '/'

        if self_closing:
            # Self-closing tag — just skip it
            pos = pos + match.end()
        else:
            # Find the matching closing tag, accounting for nesting
            search_start = pos + match.end()
            depth = 1
            scan_pos = search_start

            while depth > 0 and scan_pos < len(html):
                # Find next opening or closing tag of the same name
                next_tag = re.search(
                    r'<(/?)' + re.escape(tag_name) + r'(?:\s[^>]*)?(/?)>',
                    html[scan_pos:],
                    re.IGNORECASE
                )
                if not next_tag:
                    # No closing tag found — skip to end (malformed HTML)
                    scan_pos = len(html)
                    break

                is_closing = next_tag.group(1) == '/'
                is_self_closing = next_tag.group(2) == '/'

                if is_closing:
                    depth -= 1
                elif not is_self_closing:
                    depth += 1

                scan_pos = scan_pos + next_tag.end()

            pos = scan_pos

        # Clean up: remove blank lines left behind by stripping
        # (collapse runs of 3+ newlines to 2)
        pass  # We'll do this at the end

    output = ''.join(result)

    # Clean up excessive blank lines left behind
    output = re.sub(r'\n{3,}', '\n\n', output)

    return output


def main():
    if len(sys.argv) < 2:
        print("Usage: strip_concurrent.py [--check] <input_file> [<output_file>]",
              file=sys.stderr)
        sys.exit(2)

    check_mode = sys.argv[1] == '--check'

    if check_mode:
        input_file = sys.argv[2]
        with open(input_file, 'r', encoding='utf-8') as f:
            html = f.read()
        sys.exit(1 if is_file_level_concurrent(html) else 0)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()

    if is_file_level_concurrent(html):
        # File-level concurrent: exclude entirely
        print(f"  [skip] {input_file} (file-level concurrent)")
        # Don't write output file — the file is excluded
        sys.exit(0)

    stripped = strip_concurrent_elements(html)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(stripped)
    else:
        sys.stdout.write(stripped)


if __name__ == '__main__':
    main()
