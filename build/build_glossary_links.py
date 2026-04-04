#!/usr/bin/env python3
"""
build_glossary_links.py — Auto-link glossary terms in built HTML output.

Runs AFTER CSS inlining. Scans build/output/ HTML files and wraps the
first occurrence of each glossary term per page with a linked anchor that:
  - Links to the course glossary page with a #slug fragment
  - Carries a title= attribute for native browser tooltip (no JS needed)
  - Has class="glossary-link" for the dotted-underline CSS styling

Produces:
  <a href="{canvas_url}#{slug}" title="{definition}" class="glossary-link">term</a>

Skip rules:
  - Content inside <code>, <pre>, <a>, <h1>–<h6>, <script>, <style>
  - Content inside any element with data-no-glossary attribute
  - All occurrences after the first per page (one link per term per page)
  - The glossary page itself (glossary.html) is never processed

Usage:
    python3 build_glossary_links.py <project_root>
    python3 build_glossary_links.py <project_root> aiml2003/module2

Deterministic. No LLM. No external dependencies. Python 3.8+ stdlib only.
"""

import json
import os
import re
import sys


# Tags whose text content should never be linked
SKIP_TAGS = frozenset({
    'code', 'pre', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'script', 'style'
})

# HTML void elements (never have closing tags)
VOID_TAGS = frozenset({
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
})


def load_config(root_dir):
    path = os.path.join(root_dir, 'build', 'course-config.json')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_glossary(root_dir):
    path = os.path.join(root_dir, 'glossary.json')
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    # Skip schema/comment entries
    return [t for t in data['terms'] if 'term' in t and 'definition' in t]


def term_slug(term_str):
    """Convert a term string to a URL-safe slug."""
    return re.sub(r'[^a-z0-9]+', '-', term_str.lower()).strip('-')


def prepare_terms(all_terms, glossary_filter, canvas_url):
    """
    Filter terms for a course, build match patterns, sort longest-first.

    Longest-first ensures "cosine similarity" is matched before "cosine",
    and "TF-IDF" before "TF" if both were in the glossary.
    """
    result = []
    for t in all_terms:
        if glossary_filter not in t.get('courses', []):
            continue
        slug = term_slug(t['term'])
        # Word-boundary lookaround: avoids matching "token" inside "tokenization",
        # "kernel" inside "kernels" is fine (plural) — we use \b-style via lookaround
        # that respects hyphens (TF-IDF should not match "TF-IDF-like")
        escaped = re.escape(t['term'])
        pattern = re.compile(
            r'(?<![a-zA-Z0-9\-])' + escaped + r'(?![a-zA-Z0-9\-])',
            re.IGNORECASE
        )
        result.append({
            'term':       t['term'],
            'pattern':    pattern,
            'definition': t['definition'],
            'slug':       slug,
            'canvas_url': canvas_url,
        })
    # Sort longest first to prevent partial matches
    result.sort(key=lambda x: len(x['term']), reverse=True)
    return result


GLOSSARY_LINK_STYLE = (
    "color: inherit; "
    "text-decoration: none; "
    "border-bottom: 1px dashed currentColor; "
    "opacity: 0.75; "
    "cursor: help;"
)


def make_link(matched_text, defn, canvas_url, slug):
    """Build the replacement <a> tag string.

    Inline styles are applied directly because the glossary linker runs
    after CSS inlining — Canvas strips external stylesheets, so the
    class alone would have no effect. The class is retained for local
    preview rendering (where course-styles.css is loaded normally).
    """
    href = f"{canvas_url}#{slug}"
    # Escape definition for use in an HTML attribute.
    # & must be first to avoid double-encoding entities.
    # Then encode every remaining non-ASCII character as a numeric XML
    # character reference so the title= attribute is pure ASCII.
    safe_def = (defn
        .replace('&', '&amp;')
        .replace('"', '&quot;')
        .replace("'", '&#39;'))
    safe_def = safe_def.encode('ascii', 'xmlcharrefreplace').decode('ascii')
    return (
        f'<a href="{href}" title="{safe_def}" '
        f'class="glossary-link" style="{GLOSSARY_LINK_STYLE}">'
        f'{matched_text}</a>'
    )


def apply_links_to_text(text, terms, linked):
    """
    Scan a single text node, match unlinked terms, and insert link HTML.

    Multiple terms can match in one text node (e.g. "cosine similarity and
    logistic regression"). They are replaced right-to-left so character
    positions remain valid.

    linked: set of term strings already linked on this page (mutated in place)
    """
    if not text.strip():
        return text

    matches = []
    for t in terms:
        if t['term'] in linked:
            continue
        m = t['pattern'].search(text)
        if m:
            matches.append((m.start(), m.end(), t, m.group(0)))

    if not matches:
        return text

    # Sort descending by start position for right-to-left replacement
    matches.sort(key=lambda x: x[0], reverse=True)

    # Remove overlapping matches (keep rightmost when iterating right-to-left,
    # which corresponds to leftmost in reading order — first occurrence wins)
    filtered = []
    last_start = len(text) + 1
    for start, end, t, matched in matches:
        if end <= last_start:
            filtered.append((start, end, t, matched))
            last_start = start

    for start, end, t, matched in filtered:
        replacement = make_link(matched, t['definition'], t['canvas_url'], t['slug'])
        text = text[:start] + replacement + text[end:]
        linked.add(t['term'])

    return text


def process_html(html_content, terms):
    """
    Walk the HTML as a token stream (alternating text nodes and tags).
    Apply glossary links to text nodes while respecting skip rules.

    Uses a simple stack to track whether we're inside a skip element
    or an element with data-no-glossary. No external HTML parser needed.
    """
    linked = set()  # terms already linked on this page

    # Split into alternating text / tag tokens.
    # Tags are everything from < to the next >; text is everything between.
    tokens = re.split(r'(<[^>]+>)', html_content)

    skip_stack = []         # stack of tag names currently suppressing linking
    no_glossary_stack = []  # stack of tag names with data-no-glossary attr

    result = []

    for token in tokens:
        if not token.startswith('<'):
            # ── Text node ──────────────────────────────────────────────────
            if skip_stack or no_glossary_stack:
                result.append(token)
            else:
                result.append(apply_links_to_text(token, terms, linked))
            continue

        # ── Tag token ──────────────────────────────────────────────────────
        result.append(token)

        # Parse: closing tag?
        close_m = re.match(r'<\s*/\s*(\w+)', token)
        if close_m:
            name = close_m.group(1).lower()
            if skip_stack and skip_stack[-1] == name:
                skip_stack.pop()
            if no_glossary_stack and no_glossary_stack[-1] == name:
                no_glossary_stack.pop()
            continue

        # Parse: opening (or self-closing) tag
        open_m = re.match(r'<\s*(\w+)([^>]*?)\s*(/\s*)?>$', token)
        if open_m:
            name = open_m.group(1).lower()
            attrs = open_m.group(2) or ''
            is_self_close = bool(open_m.group(3)) or name in VOID_TAGS
            if not is_self_close:
                if name in SKIP_TAGS:
                    skip_stack.append(name)
                if 'data-no-glossary' in attrs:
                    no_glossary_stack.append(name)

    return ''.join(result)


def process_file(filepath, terms):
    """Read, process, and overwrite one HTML file. Returns True if changed."""
    with open(filepath, encoding='utf-8') as f:
        original = f.read()

    processed = process_html(original, terms)

    if processed != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(processed)
        return True
    return False


def collect_html_files(directory, exclude_names=None):
    """Walk a directory and return all .html file paths."""
    exclude_names = exclude_names or set()
    found = []
    for dirpath, _, filenames in os.walk(directory):
        for fname in filenames:
            if fname.endswith('.html') and fname not in exclude_names:
                found.append(os.path.join(dirpath, fname))
    return found


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 build_glossary_links.py <project_root> [target]")
        print("  target: optional path relative to project root to limit processing")
        sys.exit(1)

    root = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else None

    config = load_config(root)
    all_terms = load_glossary(root)

    for course_key, course_cfg in config['courses'].items():
        canvas_url = course_cfg['glossary_canvas_url']
        glossary_filter = course_cfg['glossary_filter']
        build_output_dir = os.path.join(root, course_cfg['build_output_dir'])

        if not os.path.isdir(build_output_dir):
            print(f"  SKIP {course_key}: output dir not found ({build_output_dir})")
            continue

        terms = prepare_terms(all_terms, glossary_filter, canvas_url)

        # Collect files, excluding the glossary page itself
        all_files = collect_html_files(build_output_dir, exclude_names={'glossary.html'})

        # If a target was specified, limit to files under that path
        if target:
            target_abs = os.path.normpath(os.path.join(root, 'build', 'output', target))
            all_files = [f for f in all_files if os.path.normpath(f).startswith(target_abs)]

        changed = 0
        for filepath in sorted(all_files):
            if process_file(filepath, terms):
                rel = os.path.relpath(filepath, root)
                print(f"    linked  {rel}")
                changed += 1

        total = len(all_files)
        print(f"  {course_key}: {changed} of {total} files updated with glossary links")


if __name__ == '__main__':
    main()
