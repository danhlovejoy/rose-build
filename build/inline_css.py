#!/usr/bin/env python3
"""
inline_css.py — Canvas CSS Inliner (DOM-aware)

Reads HTML source files that reference an external CSS file via <link>,
resolves CSS custom properties (var(--name)), walks the DOM tree to
apply styles with correct specificity and ancestor context, and outputs
Canvas-ready HTML (body content only) with inline style="" attributes.

Usage:
    python3 inline_css.py <input_dir> <output_dir>
    python3 inline_css.py <input_file> <output_file>

Deterministic. No LLM. No external dependencies. Python 3.8+ stdlib only.
"""

import os
import re
import sys
from html.parser import HTMLParser
from xml.etree import ElementTree as ET


# ============================================================
# CSS PARSING
# ============================================================

def parse_css(css_text):
    """Parse CSS into rules and variables."""
    variables = {}
    for root_match in re.finditer(r':root\s*\{([^}]+)\}', css_text):
        for m in re.finditer(r'--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);', root_match.group(1)):
            variables[f'--{m.group(1)}'] = m.group(2).strip()

    # Strip comments and @media blocks
    css_clean = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
    css_clean = re.sub(r'@media[^{]+\{([^{}]*\{[^}]*\})*[^}]*\}', '', css_clean, flags=re.DOTALL)

    rules = []
    for match in re.finditer(r'([^{}@][^{]*?)\s*\{([^}]+)\}', css_clean):
        selector_raw = match.group(1).strip()
        body = match.group(2).strip()
        if selector_raw.startswith(':root') or selector_raw == '*':
            continue

        props = []
        for pm in re.finditer(r'([\w-]+)\s*:\s*([^;]+);', body):
            pname = pm.group(1).strip()
            pval = resolve_vars(pm.group(2).strip(), variables)
            props.append((pname, pval))

        if props:
            for sel in selector_raw.split(','):
                sel = sel.strip()
                if sel:
                    specificity = calc_specificity(sel)
                    rules.append((sel, props, specificity))

    return rules, variables


def resolve_vars(value, variables):
    """Replace var(--name) references."""
    for _ in range(10):
        m = re.search(r'var\((--[a-zA-Z0-9_-]+)\)', value)
        if not m:
            break
        value = value[:m.start()] + variables.get(m.group(1), '') + value[m.end():]
    return value


def calc_specificity(selector):
    """Calculate CSS specificity as a sortable tuple (ids, classes, tags)."""
    ids = len(re.findall(r'#[a-zA-Z]', selector))
    classes = len(re.findall(r'\.[a-zA-Z]', selector))
    tags = len(re.findall(r'(?:^|[\s>+~])([a-zA-Z][a-zA-Z0-9]*)', selector))
    return (ids, classes, tags)


# ============================================================
# SELECTOR MATCHING (DOM-AWARE)
# ============================================================

def element_matches_simple(sel, tag, classes):
    """Match a single simple selector (no spaces/combinators)."""
    sel = sel.strip()
    if not sel:
        return False

    # Skip pseudo selectors
    sel = re.sub(r'::?[\w-]+(\([^)]*\))?', '', sel)
    if not sel:
        return False

    # Tag only
    if re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', sel):
        return sel.lower() == tag.lower()

    # Class only: .foo or .foo.bar
    if sel.startswith('.') and not re.match(r'^[a-zA-Z]', sel):
        required = [c for c in sel.split('.') if c]
        return all(c in classes for c in required)

    # Tag.class: h2.special
    m = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)(\..+)$', sel)
    if m:
        req_tag = m.group(1)
        required = [c for c in m.group(2).split('.') if c]
        return tag.lower() == req_tag.lower() and all(c in classes for c in required)

    return False


def selector_matches_with_ancestors(selector, tag, classes, ancestor_chain):
    """
    Match a CSS selector against an element, considering its ancestor chain.
    ancestor_chain is a list of (tag, classes_set) from root to parent.
    """
    selector = selector.strip()
    if not selector:
        return False

    # Split on descendant/child combinators
    parts = re.split(r'\s+', selector)

    if len(parts) == 1:
        return element_matches_simple(parts[0], tag, classes)

    if len(parts) == 2:
        child_sel = parts[-1]
        parent_sel = parts[0]

        # Child must match current element
        if not element_matches_simple(child_sel, tag, classes):
            return False

        # Parent must match some ancestor
        for anc_tag, anc_classes in ancestor_chain:
            if element_matches_simple(parent_sel, anc_tag, anc_classes):
                return True
        return False

    if len(parts) >= 3:
        # Multi-level: just check last matches current, and each prior matches some ancestor
        if not element_matches_simple(parts[-1], tag, classes):
            return False
        # Check remaining parts match some ancestors (loose)
        for part in parts[:-1]:
            found = False
            for anc_tag, anc_classes in ancestor_chain:
                if element_matches_simple(part, anc_tag, anc_classes):
                    found = True
                    break
            if not found:
                return False
        return True

    return False


# ============================================================
# DOM-AWARE INLINING
# ============================================================

class StyleInliner(HTMLParser):
    """Walk the HTML DOM, track ancestor chain, apply CSS rules inline."""

    def __init__(self, css_rules):
        super().__init__(convert_charrefs=False)
        self.css_rules = css_rules
        self.output = []
        self.ancestor_stack = []  # List of (tag, classes_set)

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        classes = set(attrs_dict.get('class', '').split())

        # Tags that shouldn't get styles
        skip_tags = {'meta', 'link', 'br', 'hr', 'img', 'input', 'html', 'head', 'title', 'script', 'body'}
        if tag.lower() in skip_tags:
            self.output.append(self._rebuild_tag(tag, attrs))
            if tag.lower() not in {'meta', 'link', 'br', 'hr', 'img', 'input'}:
                self.ancestor_stack.append((tag.lower(), classes))
            return

        # Collect matching rules with specificity
        matched = []
        for selector, props, specificity in self.css_rules:
            if selector_matches_with_ancestors(selector, tag, classes, self.ancestor_stack):
                matched.append((specificity, props))

        # Sort by specificity (lower first, so higher specificity wins via override)
        matched.sort(key=lambda x: x[0])

        # Build property dict (later rules override earlier)
        style_props = {}
        for _, props in matched:
            for pname, pval in props:
                style_props[pname] = pval

        # Merge with existing inline style (existing takes precedence)
        existing_style = attrs_dict.get('style', '')
        if existing_style:
            for part in existing_style.split(';'):
                part = part.strip()
                if ':' in part:
                    k, v = part.split(':', 1)
                    style_props[k.strip()] = v.strip()

        # Rebuild tag with inline style
        new_style = '; '.join(f'{k}: {v}' for k, v in style_props.items()) if style_props else ''

        # Rebuild attrs
        new_attrs = []
        style_added = False
        for name, value in attrs:
            if name == 'style':
                new_attrs.append(('style', new_style))
                style_added = True
            else:
                new_attrs.append((name, value))
        if not style_added and new_style:
            new_attrs.append(('style', new_style))

        self.output.append(self._rebuild_tag(tag, new_attrs))
        self.ancestor_stack.append((tag.lower(), classes))

    def handle_endtag(self, tag):
        self.output.append(f'</{tag}>')
        # Pop from ancestor stack
        if self.ancestor_stack and self.ancestor_stack[-1][0] == tag.lower():
            self.ancestor_stack.pop()

    def handle_data(self, data):
        self.output.append(data)

    def handle_entityref(self, name):
        self.output.append(f'&{name};')

    def handle_charref(self, name):
        self.output.append(f'&#{name};')

    def handle_comment(self, data):
        self.output.append(f'<!--{data}-->')

    def handle_decl(self, decl):
        self.output.append(f'<!{decl}>')

    def handle_pi(self, data):
        self.output.append(f'<?{data}>')

    def _rebuild_tag(self, tag, attrs):
        """Rebuild an opening tag from tag name and attribute list."""
        if not attrs:
            return f'<{tag}>'
        attr_strs = []
        for name, value in attrs:
            if value is None:
                attr_strs.append(name)
            else:
                # Escape quotes in value
                escaped = value.replace('&', '&amp;').replace('"', '&quot;')
                attr_strs.append(f'{name}="{escaped}"')
        return f'<{tag} {" ".join(attr_strs)}>'

    def get_result(self):
        return ''.join(self.output)


def inline_styles(html_content, css_rules):
    """Apply CSS rules as inline styles using DOM-aware parsing."""
    inliner = StyleInliner(css_rules)
    inliner.feed(html_content)
    return inliner.get_result()


def extract_body(html):
    """Extract content between <body> and </body>."""
    m = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    return m.group(1).strip() if m else html


def collect_body_styles(css_rules):
    """Collect CSS properties that target the body element."""
    style_props = {}
    for selector, props, specificity in css_rules:
        sel = selector.strip()
        if sel == 'body':
            for pname, pval in props:
                style_props[pname] = pval
    return style_props


def process_file(input_path, output_path, css_rules):
    """Process one HTML file: inline CSS, extract body, write output."""
    with open(input_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Remove <link> to CSS
    html = re.sub(r'<link[^>]*rel="stylesheet"[^>]*>', '', html)

    # Inline styles
    html = inline_styles(html, css_rules)

    # Extract body only
    body = extract_body(html)

    # Wrap in a div with body-level styles (font-family, color, etc.)
    # since Canvas strips <body> and its inherited properties are lost
    body_styles = collect_body_styles(css_rules)
    if body_styles:
        style_str = '; '.join(f'{k}: {v}' for k, v in body_styles.items())
        body = f'<div style="{style_str}">\n{body}\n</div>'

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(body)

    return True


def main():
    # Parse optional flags
    args = sys.argv[1:]
    css_path = None
    override_css_path = None
    no_recurse = False
    if '--css' in args:
        idx = args.index('--css')
        css_path = args[idx + 1]
        args = args[:idx] + args[idx + 2:]
    if '--override-css' in args:
        idx = args.index('--override-css')
        override_css_path = args[idx + 1]
        args = args[:idx] + args[idx + 2:]
    if '--no-recurse' in args:
        args.remove('--no-recurse')
        no_recurse = True

    if len(args) < 2:
        print("Usage: python3 inline_css.py [--css <path>] <input_dir> <output_dir>")
        print("       python3 inline_css.py [--css <path>] <input_file> <output_file>")
        sys.exit(1)

    input_path = args[0]
    output_path = args[1]

    # Find course-styles.css: explicit flag, or walk up from input
    if not css_path:
        search_dir = input_path if os.path.isdir(input_path) else os.path.dirname(os.path.abspath(input_path))
        check = os.path.abspath(search_dir)
        for _ in range(5):
            candidate = os.path.join(check, 'course-styles.css')
            if os.path.exists(candidate):
                css_path = candidate
                break
            check = os.path.dirname(check)

    if not css_path or not os.path.exists(css_path):
        print("ERROR: Could not find course-styles.css")
        print("  Provide --css <path> or place course-styles.css in a parent directory.")
        sys.exit(1)

    print(f"CSS: {css_path}")

    with open(css_path, 'r', encoding='utf-8') as f:
        css_text = f.read()

    if override_css_path and os.path.exists(override_css_path):
        print(f"Override CSS: {override_css_path}")
        with open(override_css_path, 'r', encoding='utf-8') as f:
            css_text += '\n' + f.read()

    css_rules, variables = parse_css(css_text)
    print(f"Parsed {len(css_rules)} rules, {len(variables)} variables")

    if os.path.isfile(input_path):
        process_file(input_path, output_path, css_rules)
        print(f"  {input_path} -> {output_path}")
    else:
        count = 0
        if no_recurse:
            # Only process HTML files directly in input_path (no subdirs)
            fnames = sorted(os.listdir(input_path))
            for fname in fnames:
                if not fname.endswith('.html'):
                    continue
                src = os.path.join(input_path, fname)
                if not os.path.isfile(src):
                    continue
                dst = os.path.join(output_path, fname)
                process_file(src, dst, css_rules)
                print(f"  {fname}")
                count += 1
        else:
            for root, dirs, fnames in os.walk(input_path):
                for fname in sorted(fnames):
                    if not fname.endswith('.html'):
                        continue
                    src = os.path.join(root, fname)
                    rel = os.path.relpath(src, input_path)
                    dst = os.path.join(output_path, rel)
                    process_file(src, dst, css_rules)
                    print(f"  {rel}")
                    count += 1
        print(f"\nProcessed {count} files -> {output_path}")


if __name__ == '__main__':
    main()
