#!/usr/bin/env python3
"""
Lint interactive demos in slides/.

Checks:
  1. assert: comments — verifies math claims (dot products, cosine comparisons)
  2. Anti-patterns from DEMO-STANDARDS.md:
     - Plotly.newPlot (should be Plotly.react)
     - SVG via innerHTML
     - CSS vars in JS-generated inline styles
     - Missing required CSS variables
     - Bare h2 selectors

Usage:
  python3 build/lint_demos.py              # lint all demos
  python3 build/lint_demos.py slides/foo.html  # lint one file
"""

import glob
import math
import os
import re
import sys

# ── Required CSS variables (from DEMO-STANDARDS.md) ──

REQUIRED_CSS_VARS = {
    '--primary', '--primary-light', '--accent', '--light-bg', '--border',
    '--text', '--muted', '--neg', '--neg-bg', '--pos', '--pos-bg',
    '--purple', '--purple-bg', '--orange',
}

# ── Assertion parser ──

def parse_dot(expr):
    """Parse dot(a,b, c,d) or dot(a,b,c,..., e,f,g,...) and compute."""
    m = re.match(r'dot\(([^)]+)\)', expr.strip())
    if not m:
        return None
    nums = [float(x.strip()) for x in m.group(1).split(',')]
    if len(nums) % 2 != 0:
        return None
    half = len(nums) // 2
    vec_a = nums[:half]
    vec_b = nums[half:]
    return sum(a * b for a, b in zip(vec_a, vec_b))


def parse_cosine(expr, vectors):
    """Parse cosine(name1, name2) and compute from extracted vectors."""
    m = re.match(r'cosine\((\w+),\s*(\w+)\)', expr.strip())
    if not m:
        return None
    name1, name2 = m.group(1).lower(), m.group(2).lower()
    v1 = vectors.get(name1)
    v2 = vectors.get(name2)
    if v1 is None or v2 is None:
        return None
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 < 1e-12 or mag2 < 1e-12:
        return 0.0
    return dot / (mag1 * mag2)


def check_assertion(assertion_text, vectors):
    """
    Parse and verify a single assertion.
    Returns (passed: bool, message: str) or None if unparseable.

    Supported forms:
      assert: dot(a,b, c,d) = 0
      assert: dot(a,b, c,d) = 0 (perpendicular)
      assert: cosine(king, queen) > 0.6
      assert: cosine(king, queen) > 0.6 (most similar pair)
    """
    # Strip the "assert:" prefix and any trailing parenthetical
    text = assertion_text.strip()
    if text.lower().startswith('assert:'):
        text = text[7:].strip()

    # Remove trailing parenthetical comment: "(perpendicular)" etc.
    text = re.sub(r'\s*\([^)]*\)\s*$', '', text)

    # Try: expr = number
    m = re.match(r'(.+?)\s*=\s*(-?[\d.]+)\s*$', text)
    if m:
        expr, expected = m.group(1), float(m.group(2))
        actual = None
        if expr.strip().startswith('dot('):
            actual = parse_dot(expr)
        elif expr.strip().startswith('cosine('):
            actual = parse_cosine(expr, vectors)
        if actual is not None:
            passed = abs(actual - expected) < 0.01
            return (passed, f"{expr.strip()} = {actual:.4f} (expected {expected})")

    # Try: expr > number
    m = re.match(r'(.+?)\s*>\s*(-?[\d.]+)\s*$', text)
    if m:
        expr, threshold = m.group(1), float(m.group(2))
        actual = None
        if expr.strip().startswith('cosine('):
            actual = parse_cosine(expr, vectors)
        elif expr.strip().startswith('dot('):
            actual = parse_dot(expr)
        if actual is not None:
            passed = actual > threshold
            return (passed, f"{expr.strip()} = {actual:.4f} (expected > {threshold})")

    # Try: expr < number
    m = re.match(r'(.+?)\s*<\s*(-?[\d.]+)\s*$', text)
    if m:
        expr, threshold = m.group(1), float(m.group(2))
        actual = None
        if expr.strip().startswith('cosine('):
            actual = parse_cosine(expr, vectors)
        elif expr.strip().startswith('dot('):
            actual = parse_dot(expr)
        if actual is not None:
            passed = actual < threshold
            return (passed, f"{expr.strip()} = {actual:.4f} (expected < {threshold})")

    return None  # Unparseable


def extract_vectors(content):
    """Extract named vector data from JS objects like REAL_EMBEDDINGS, WORDS_S1, etc."""
    vectors = {}
    # Match patterns like: 'king': [0.1, 0.2, ...],
    for m in re.finditer(r"'(\w+)'\s*:\s*\[([^\]]+)\]", content):
        name = m.group(1).lower()
        try:
            vals = [float(x.strip()) for x in m.group(2).split(',')]
            vectors[name] = vals
        except ValueError:
            continue
    return vectors


# ── Anti-pattern checks ──

def check_antipatterns(filepath, content, lines):
    """Check for known anti-patterns. Returns list of (line_num, message)."""
    issues = []

    in_script = False
    in_style = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip().lower()

        # Track whether we're in <script> or <style>
        if '<script' in stripped and 'src=' not in stripped:
            in_script = True
        if '</script>' in stripped:
            in_script = False
        if '<style' in stripped:
            in_style = True
        if '</style>' in stripped:
            in_style = False

        # Plotly.newPlot
        if in_script and 'plotly.newplot' in stripped:
            issues.append((i, "Plotly.newPlot — use Plotly.react instead"))

        # SVG via innerHTML
        if in_script and 'innerhtml' in stripped and '<svg' in stripped.lower():
            issues.append((i, "SVG created via innerHTML — use Canvas or createElementNS"))

        # CSS vars in JS string literals (template literals or string concat)
        if in_script and 'var(--' in line:
            # Allow if it's in a CSS comment or actual <style> context
            if not in_style:
                issues.append((i, "CSS variable in JS context — hardcode hex value or use getComputedStyle"))

        # Bare h2 selector in CSS
        if in_style and re.match(r'\s*h2\s*\{', line):
            issues.append((i, "Bare h2 selector — scope to .stage-line h2"))

    return issues


def check_css_vars(content):
    """Check that all required CSS variables are defined in :root."""
    # Extract :root block
    m = re.search(r':root\s*\{([^}]+)\}', content)
    if not m:
        return ['No :root CSS block found']

    root_block = m.group(1)
    defined = set(re.findall(r'(--[\w-]+)\s*:', root_block))
    missing = REQUIRED_CSS_VARS - defined

    if missing:
        return [f"Missing required CSS variable: {v}" for v in sorted(missing)]
    return []


# ── Main lint logic ──

def lint_file(filepath):
    """Lint a single demo file. Returns (errors, warnings, info)."""
    errors = []
    warnings = []
    info = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    basename = os.path.basename(filepath)

    # 1. Extract vectors for cosine assertions
    vectors = extract_vectors(content)

    # 2. Find and verify assert: comments
    assert_count = 0
    for i, line in enumerate(lines, 1):
        # HTML comment assertions: <!-- assert: ... -->
        for m in re.finditer(r'<!--\s*assert:\s*(.+?)\s*-->', line):
            assert_count += 1
            result = check_assertion(m.group(1), vectors)
            if result is None:
                warnings.append(f"  line {i}: could not parse assertion: {m.group(1)}")
            elif not result[0]:
                errors.append(f"  line {i}: FAILED — {result[1]}")
            else:
                info.append(f"  line {i}: passed — {result[1]}")

        # JS comment assertions: // assert: ...
        js_assert = re.search(r'//\s*assert:\s*(.+)$', line)
        if js_assert:
            assert_count += 1
            result = check_assertion(js_assert.group(1), vectors)
            if result is None:
                warnings.append(f"  line {i}: could not parse assertion: {js_assert.group(1)}")
            elif not result[0]:
                errors.append(f"  line {i}: FAILED — {result[1]}")
            else:
                info.append(f"  line {i}: passed — {result[1]}")

    # 3. Anti-pattern checks
    for line_num, msg in check_antipatterns(filepath, content, lines):
        warnings.append(f"  line {line_num}: {msg}")

    # 4. CSS variable completeness
    for msg in check_css_vars(content):
        warnings.append(f"  {msg}")

    # 5. Note if no assertions found
    if assert_count == 0:
        info.append("  no assert: comments found")

    return errors, warnings, info


def main():
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        files = sorted(glob.glob(os.path.join(project_root, 'slides', '*-demo.html')))

    if not files:
        print("No demo files found.")
        return 1

    total_errors = 0
    total_warnings = 0
    total_assertions = 0

    for filepath in files:
        basename = os.path.basename(filepath)
        errors, warnings, info = lint_file(filepath)

        total_errors += len(errors)
        total_warnings += len(warnings)

        # Count passed assertions from info
        passed = sum(1 for i in info if 'passed' in i)
        total_assertions += passed + len(errors)  # errors are failed assertions

        # Print results
        status = "FAIL" if errors else ("WARN" if warnings else "OK")
        print(f"\n{'='*60}")
        print(f"  {basename}  [{status}]")
        print(f"{'='*60}")

        for e in errors:
            print(f"  ERROR {e}")
        for w in warnings:
            print(f"  WARN  {w}")
        for i in info:
            print(f"  INFO  {i}")

    # Summary
    print(f"\n{'─'*60}")
    print(f"  {len(files)} files scanned")
    print(f"  {total_assertions} assertions checked ({total_assertions - total_errors} passed, {total_errors} failed)")
    print(f"  {total_warnings} warnings")
    print(f"{'─'*60}")

    return 1 if total_errors > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
