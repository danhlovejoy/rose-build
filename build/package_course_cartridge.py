#!/usr/bin/env python3
"""
package_course_cartridge.py — Build a single Canvas Common Cartridge per course.

Bundles the standalone-build output, ethics discussion topics, reading quizzes,
and final exam into one .imscc that an instructor can drop into a fresh Canvas
shell. Internal page links are rewritten to Canvas's $WIKI_REFERENCE$ form so
they resolve to whatever course ID the importer ends up with.

Usage:
    python3 build/package_course_cartridge.py aiml2003
    python3 build/package_course_cartridge.py aiml2013

Prerequisites:
    bash build/build.sh --standalone <course>   # populates build/<course>/

Output:
    dist/<course>-canvas-import.imscc

Deterministic. Python 3.8+ stdlib only.
"""

import argparse
import html
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

# Reuse QTI builders from build_quiz.py
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from build_quiz import (
    build_item_xml,
    build_essay_item_xml,
    QTI_HEADER,
    QTI_FOOTER,
)

PROJECT_ROOT = SCRIPT_DIR.parent


# ──────────────────────────────────────────────────────────────────────
# Module ordering and page grouping
# ──────────────────────────────────────────────────────────────────────

MODULE_TITLES = {
    "aiml2003": {
        1: "Module 1: From Prompt to Context Engineering",
        2: "Module 2: Hand-Crafted Features (TF-IDF)",
        3: "Module 3: Learned Embeddings",
        4: "Module 4: Basic RAG",
        5: "Module 5: Evaluating LLMs",
        6: "Module 6: Simple Agents",
        7: "Module 7: Portfolio & Future",
    },
    "aiml2013": {
        1: "Module 1: Vision & Images",
        2: "Module 2: Hand-Crafted Features (HOG)",
        3: "Module 3: Learned Embeddings",
        4: "Module 4: Visual Similarity",
        5: "Module 5: CV Metrics & Bias",
        6: "Module 6: Generative Vision",
        7: "Module 7: Portfolio & Future",
    },
}

COURSE_DISPLAY = {
    "aiml2003": ("AIML 2003", "AIML 2003 — Introduction to Natural Language Processing"),
    "aiml2013": ("AIML 2013", "AIML 2013 — Introduction to Computer Vision"),
}

# Module 1 slugs — what the welcome page's "This Week" link points to in a fresh-import cartridge.
MODULE_1_SLUGS = {
    "aiml2003": "welcome-to-aiml-2003",
    "aiml2013": "welcome-to-aiml-2013",
}


def is_ethics_path(rel_path: str) -> bool:
    """Pages whose source file is the ethics prompt — these become discussion topics, not wiki pages."""
    name = os.path.basename(rel_path).lower()
    return "ethics" in name or "discussion-ethics" in name


def module_number(rel_path: str):
    """Return the module number (1-7) for a source path, or None for course-level pages."""
    m = re.match(r"^module(\d+)/", rel_path)
    return int(m.group(1)) if m else None


def page_sort_key(rel_path: str):
    """Sort pages within a module by leading numeric prefix, with lab files last."""
    filename = os.path.basename(rel_path)
    # Lab files: sort after numeric-prefix files
    if filename.startswith("lab"):
        return (1, filename)
    # Numeric prefix like "00-", "03a-", "11-"
    m = re.match(r"^(\d+)([a-z]?)-", filename)
    if m:
        return (0, int(m.group(1)), m.group(2), filename)
    # Everything else (index.html, etc.): last
    return (2, filename)


def slug_from_path(slug_to_path: dict, rel_path: str):
    """Reverse lookup: find the Canvas page slug for a given source path."""
    for slug, path in slug_to_path.items():
        if path == rel_path:
            return slug
    return None


# ──────────────────────────────────────────────────────────────────────
# Wiki page handling
# ──────────────────────────────────────────────────────────────────────

# Match Canvas page URLs like:
#   https://rose.instructure.com/courses/26943/pages/some-slug
#   /courses/26943/pages/some-slug
#   /courses/26944/pages/some-slug#fragment
CANVAS_PAGE_LINK_RE = re.compile(
    r'(href=")(?:https?://[^/"]+)?/courses/\d+/pages/([a-z0-9\-]+)(#[^"]*)?(")',
    re.IGNORECASE,
)


def rewrite_links(html_body: str, known_slugs: set) -> str:
    """Rewrite Canvas page links to $WIKI_REFERENCE$ form. Unknown slugs pass through unchanged."""
    def replace(m):
        prefix, slug, fragment, suffix = m.group(1), m.group(2), m.group(3) or "", m.group(4)
        if slug in known_slugs:
            return f'{prefix}$WIKI_REFERENCE$/pages/{slug}{fragment}{suffix}'
        return m.group(0)
    return CANVAS_PAGE_LINK_RE.sub(replace, html_body)


WELCOME_THIS_WEEK_RE = re.compile(
    r'(<p[^>]*>This Week</p>\s*<p[^>]*><a href=")[^"]*("[^>]*>)[^<]*(</a>)',
    re.DOTALL,
)
WELCOME_PAST_MODULES_RE = re.compile(
    r'(<h3[^>]*>Previous Modules</h3>\s*<ul[^>]*>).*?(</ul>)',
    re.DOTALL,
)


def reset_welcome_to_module_1(body_html: str, module_1_slug: str, module_1_title: str) -> str:
    """Reset the course welcome page to its semester-start state for the cartridge.

    The live welcome page tracks "This Week" as the instructor advances each week. A
    fresh-import cartridge should start at Module 1 with no past modules listed; the
    future instructor advances week-by-week from there using the same workflow.
    """
    body_html = WELCOME_THIS_WEEK_RE.sub(
        lambda m: (
            m.group(1)
            + f"$WIKI_REFERENCE$/pages/{module_1_slug}"
            + m.group(2)
            + f"{module_1_title} &rarr;"
            + m.group(3)
        ),
        body_html,
    )
    body_html = WELCOME_PAST_MODULES_RE.sub(r"\1\2", body_html)
    return body_html


def extract_body(html_text: str) -> str:
    """Return inner-body content of a built HTML page, or the full text if there's no <body>."""
    m = re.search(r"<body[^>]*>(.*)</body>", html_text, re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else html_text.strip()


def page_title_from_source(source_html_path: Path, fallback: str) -> str:
    """Read <title> from the source HTML (build output strips it). Strip the ' | AIML 20XX' suffix.

    Source files have <title>Friendly Page Title | AIML 2003</title>; the build pipeline
    extracts body-only, so titles must come from the source tree.
    """
    if not source_html_path.exists():
        return fallback
    try:
        html_text = source_html_path.read_text(encoding="utf-8")
    except Exception:
        return fallback
    m = re.search(r"<title>(.*?)</title>", html_text, re.DOTALL | re.IGNORECASE)
    if not m:
        return fallback
    title = m.group(1).strip()
    title = re.sub(r"\s*\|\s*AIML\s*20\d\d.*$", "", title).strip()
    return title or fallback


def slug_to_friendly_fallback(slug: str) -> str:
    """Used only when no source <title> is available — e.g., the synthetic Course Setup Notes page."""
    return " ".join(w.capitalize() for w in slug.split("-"))


# ──────────────────────────────────────────────────────────────────────
# Discussion topic builder
# ──────────────────────────────────────────────────────────────────────

DISCUSSION_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<topic xmlns="http://www.imsglobal.org/xsd/imsccv1p1/imsdt_v1p1"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="http://www.imsglobal.org/xsd/imsccv1p1/imsdt_v1p1 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imsdt_v1p1.xsd">
  <title>{title}</title>
  <text texttype="text/html"><![CDATA[{body}]]></text>
</topic>
"""


def build_discussion_xml(title: str, body_html: str) -> str:
    """Wrap an HTML body in the IMS discussion-topic envelope."""
    return DISCUSSION_TEMPLATE.format(title=xml_escape(title), body=body_html)


DISCUSSION_META_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<topicMeta identifier="{meta_id}"
           xmlns="http://canvas.instructure.com/xsd/cccv1p0"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <topic_id>{topic_id}</topic_id>
  <title>{title}</title>
  <type>topic</type>
  <discussion_type>threaded</discussion_type>
  <workflow_state>active</workflow_state>
  <require_initial_post>true</require_initial_post>
  <points_possible>{points}</points_possible>
  <assignment identifier="{assignment_id}">
    <title>{title}</title>
    <workflow_state>published</workflow_state>
    <points_possible>{points}</points_possible>
    <grading_type>points</grading_type>
    <submission_types>discussion_topic</submission_types>
    <assignment_group_identifierref>{group_ref}</assignment_group_identifierref>
    <position>1</position>
  </assignment>
</topicMeta>
"""


def build_discussion_meta_xml(meta_id, topic_id, assignment_id, title, points, group_ref):
    """Canvas-extension metadata that marks a discussion topic as graded.

    Sits alongside the standard IMS topic XML; on import Canvas creates both the
    discussion and a linked Assignment row in the gradebook tied to the chosen
    assignment group.
    """
    return DISCUSSION_META_TEMPLATE.format(
        meta_id=meta_id,
        topic_id=topic_id,
        assignment_id=assignment_id,
        title=xml_escape(title),
        points=points,
        group_ref=group_ref,
    )


# ──────────────────────────────────────────────────────────────────────
# Assignment groups
# ──────────────────────────────────────────────────────────────────────

ASSIGNMENT_GROUPS_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<assignmentGroups xmlns="http://canvas.instructure.com/xsd/cccv1p0"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <assignmentGroup identifier="participation">
    <title>Participation</title>
    <position>1</position>
    <group_weight>20.0</group_weight>
  </assignmentGroup>
  <assignmentGroup identifier="github_repos">
    <title>GitHub Repos</title>
    <position>2</position>
    <group_weight>25.0</group_weight>
  </assignmentGroup>
  <assignmentGroup identifier="presentations">
    <title>Presentations</title>
    <position>3</position>
    <group_weight>15.0</group_weight>
  </assignmentGroup>
  <assignmentGroup identifier="demos">
    <title>Demos</title>
    <position>4</position>
    <group_weight>25.0</group_weight>
  </assignmentGroup>
  <assignmentGroup identifier="final_reflection">
    <title>Final Reflection</title>
    <position>5</position>
    <group_weight>5.0</group_weight>
  </assignmentGroup>
  <assignmentGroup identifier="final_portfolio">
    <title>Final Portfolio</title>
    <position>6</position>
    <group_weight>10.0</group_weight>
  </assignmentGroup>
</assignmentGroups>
"""


# ──────────────────────────────────────────────────────────────────────
# Quiz handling — reuses build_quiz.py
# ──────────────────────────────────────────────────────────────────────

QUIZ_META_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<quiz identifier="{quiz_id}"
      xmlns="http://canvas.instructure.com/xsd/cccv1p0"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <title>{title}</title>
  <description><![CDATA[<p>{description}</p>]]></description>
  <shuffle_answers>{shuffle}</shuffle_answers>
  <scoring_policy>{scoring_policy}</scoring_policy>
  <hide_results></hide_results>
  <quiz_type>assignment</quiz_type>
  <points_possible>{points_possible}</points_possible>
  <require_lockdown_browser>false</require_lockdown_browser>
  <require_lockdown_browser_for_results>false</require_lockdown_browser_for_results>
  <require_lockdown_browser_monitor>false</require_lockdown_browser_monitor>
  <lockdown_browser_monitor_data/>
  <show_correct_answers>true</show_correct_answers>
  <show_correct_answers_last_attempt>{show_last}</show_correct_answers_last_attempt>
  <anonymous_submissions>false</anonymous_submissions>
  <could_be_locked>false</could_be_locked>
  <allowed_attempts>{allowed_attempts}</allowed_attempts>
  <one_question_at_a_time>false</one_question_at_a_time>
  <cant_go_back>false</cant_go_back>
  <available>false</available>
  <one_time_results>false</one_time_results>
  <show_correct_answers_at/>
  <hide_correct_answers_at/>
  <time_limit></time_limit>
  <assignment identifier="{quiz_id}_assignment">
    <title>{title}</title>
    <points_possible>{points_possible}</points_possible>
    <grading_type>points</grading_type>
    <submission_types>online_quiz</submission_types>
    <position>1</position>
  </assignment>
</quiz>
"""


def build_quiz_artifacts(quiz_json: dict, quiz_id: str):
    """Return (qti_xml, meta_xml, total_points) for a quiz definition dict."""
    questions = quiz_json["questions"]
    points_per_q = quiz_json.get("points_per_question", 2)
    allowed_attempts = quiz_json.get("allowed_attempts", 2)
    scoring_policy = quiz_json.get("scoring_policy", "keep_highest")
    shuffle = "true" if quiz_json.get("shuffle_answers", True) else "false"
    show_last = "true" if quiz_json.get("show_correct_answers_last_attempt", True) else "false"

    total_points = 0
    for q in questions:
        if q.get("type") == "essay":
            total_points += q["points"]
        else:
            total_points += points_per_q

    qti_xml = QTI_HEADER.format(
        quiz_id=quiz_id,
        title=xml_escape(quiz_json["title"]),
        allowed_attempts=allowed_attempts,
    )
    for q in questions:
        if q.get("type") == "essay":
            qti_xml += "\n" + build_essay_item_xml(q) + "\n"
        else:
            qti_xml += "\n" + build_item_xml(q, points_per_q) + "\n"
    qti_xml += QTI_FOOTER

    meta_xml = QUIZ_META_TEMPLATE.format(
        quiz_id=quiz_id,
        title=xml_escape(quiz_json["title"]),
        description=quiz_json["description"],
        shuffle=shuffle,
        scoring_policy=scoring_policy,
        points_possible=total_points,
        show_last=show_last,
        allowed_attempts=allowed_attempts,
    )
    return qti_xml, meta_xml, total_points


# ──────────────────────────────────────────────────────────────────────
# Setup-notes page rendering (Markdown → HTML, lightweight)
# ──────────────────────────────────────────────────────────────────────

def render_setup_notes(md_text: str, substitutions: dict) -> str:
    """Render docs/COURSE-SETUP-NOTES.md to HTML. Light Markdown — h1/h2/h3, paragraphs, lists, code, links."""
    # Substitute placeholders first
    for key, value in substitutions.items():
        md_text = md_text.replace(f"{{{{{key}}}}}", value)

    lines = md_text.split("\n")
    out_lines = []
    in_code_block = False
    code_lines = []
    in_list = None  # "ul" or "ol" or None
    in_table = False
    para_lines = []

    def flush_paragraph():
        if para_lines:
            inline = " ".join(para_lines).strip()
            if inline:
                out_lines.append(f"<p>{render_inline(inline)}</p>")
            para_lines.clear()

    def close_list():
        nonlocal in_list
        if in_list:
            out_lines.append(f"</{in_list}>")
            in_list = None

    def close_table():
        nonlocal in_table
        if in_table:
            out_lines.append("</tbody></table>")
            in_table = False

    for line in lines:
        if line.startswith("```"):
            flush_paragraph()
            close_list()
            close_table()
            if in_code_block:
                out_lines.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            continue
        if in_code_block:
            code_lines.append(line)
            continue

        stripped = line.strip()

        # Headers
        if stripped.startswith("### "):
            flush_paragraph()
            close_list()
            close_table()
            out_lines.append(f"<h3>{render_inline(stripped[4:])}</h3>")
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            close_list()
            close_table()
            out_lines.append(f"<h2>{render_inline(stripped[3:])}</h2>")
            continue
        if stripped.startswith("# "):
            flush_paragraph()
            close_list()
            close_table()
            out_lines.append(f"<h1>{render_inline(stripped[2:])}</h1>")
            continue

        # Table rows
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            # Skip separator row (|---|---|)
            if all(re.match(r"^:?-+:?$", c) for c in cells if c):
                continue
            flush_paragraph()
            close_list()
            if not in_table:
                out_lines.append("<table><tbody>")
                in_table = True
            out_lines.append("<tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in cells) + "</tr>")
            continue

        # Lists
        if re.match(r"^\s*[-*]\s+", line):
            flush_paragraph()
            close_table()
            if in_list != "ul":
                close_list()
                out_lines.append("<ul>")
                in_list = "ul"
            content = re.sub(r"^\s*[-*]\s+", "", line)
            out_lines.append(f"<li>{render_inline(content)}</li>")
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            flush_paragraph()
            close_table()
            if in_list != "ol":
                close_list()
                out_lines.append("<ol>")
                in_list = "ol"
            content = re.sub(r"^\s*\d+\.\s+", "", line)
            out_lines.append(f"<li>{render_inline(content)}</li>")
            continue

        # Blank line: paragraph separator
        if not stripped:
            flush_paragraph()
            close_list()
            close_table()
            continue

        # Regular text — accumulate into a paragraph
        para_lines.append(stripped)

    flush_paragraph()
    close_list()
    close_table()
    return "\n".join(out_lines)


INLINE_CODE_RE = re.compile(r"`([^`]+)`")
INLINE_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
INLINE_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def render_inline(text: str) -> str:
    """Render inline Markdown: code spans, links, bold."""
    # Code spans first so we don't escape inside them later
    pieces = []
    last = 0
    for m in INLINE_CODE_RE.finditer(text):
        pieces.append(("text", text[last:m.start()]))
        pieces.append(("code", m.group(1)))
        last = m.end()
    pieces.append(("text", text[last:]))

    out = []
    for kind, content in pieces:
        if kind == "code":
            out.append(f"<code>{html.escape(content)}</code>")
        else:
            escaped = html.escape(content)
            escaped = INLINE_LINK_RE.sub(r'<a href="\2">\1</a>', escaped)
            escaped = INLINE_BOLD_RE.sub(r"<strong>\1</strong>", escaped)
            out.append(escaped)
    return "".join(out)


SETUP_NOTES_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Course Setup Notes</title>
</head>
<body>
{content}
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────────────
# Wiki page envelope (with Canvas-specific meta tags)
# ──────────────────────────────────────────────────────────────────────

def wrap_wiki_page(title: str, body_html: str, resource_id: str, is_front_page: bool = False) -> str:
    """Wrap a page body in a head/body skeleton with Canvas's per-page meta tags.

    The meta tags are what tells Canvas to import the file as a wiki page (not a
    course file). `identifier` must match the manifest resource id so module_meta.xml
    can reference it. `front_page=true` makes Canvas set the page as the course's
    landing page (combined with default_view=wiki in course_settings.xml).
    """
    front_page_meta = '<meta name="front_page" content="true"/>\n' if is_front_page else ""
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/>\n"
        f"<title>{xml_escape(title)}</title>\n"
        f'<meta name="identifier" content="{resource_id}"/>\n'
        '<meta name="editing_roles" content="teachers"/>\n'
        '<meta name="workflow_state" content="active"/>\n'
        f"{front_page_meta}"
        "</head>\n<body>\n"
        + body_html +
        "\n</body>\n</html>\n"
    )


# ──────────────────────────────────────────────────────────────────────
# Canvas-specific course settings files
# ──────────────────────────────────────────────────────────────────────

CANVAS_EXPORT_MARKER = (
    "Q: What did the panda say when forced out of his natural habitat?\n"
    "A: This is BAMBOOzling\n"
)

COURSE_SETTINGS_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<course identifier="rose_course"
        xmlns="http://canvas.instructure.com/xsd/cccv1p0"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
  <title>{title}</title>
  <course_code>{course_code}</course_code>
  <default_view>wiki</default_view>
  <is_public>false</is_public>
  <indexed>false</indexed>
</course>
"""

MODULE_META_HEADER = """\
<?xml version="1.0" encoding="UTF-8"?>
<modules xmlns="http://canvas.instructure.com/xsd/cccv1p0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd">
"""

MODULE_META_FOOTER = "</modules>\n"


def build_module_meta_xml(modules):
    """Build Canvas's course_settings/module_meta.xml from a list of (title, items) pairs.

    Each item is a dict with keys: identifier, identifierref, content_type, title, position.
    """
    out = [MODULE_META_HEADER]
    for mod_idx, (mod_title, items) in enumerate(modules, start=1):
        out.append(f'  <module identifier="module_meta_{mod_idx}">')
        out.append(f"    <title>{xml_escape(mod_title)}</title>")
        out.append("    <workflow_state>active</workflow_state>")
        out.append(f"    <position>{mod_idx}</position>")
        out.append("    <require_sequential_progress>false</require_sequential_progress>")
        out.append("    <items>")
        for item in items:
            out.append(f'      <item identifier="{item["identifier"]}">')
            out.append(f"        <content_type>{item['content_type']}</content_type>")
            out.append(f"        <workflow_state>active</workflow_state>")
            out.append(f"        <title>{xml_escape(item['title'])}</title>")
            out.append(f"        <identifierref>{item['identifierref']}</identifierref>")
            out.append(f"        <position>{item['position']}</position>")
            out.append("        <new_tab>false</new_tab>")
            out.append("        <indent>0</indent>")
            out.append("      </item>")
        out.append("    </items>")
        out.append("  </module>")
    out.append(MODULE_META_FOOTER)
    return "\n".join(out)


# ──────────────────────────────────────────────────────────────────────
# Manifest assembly
# ──────────────────────────────────────────────────────────────────────

MANIFEST_HEADER = """\
<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{manifest_id}"
          xmlns="http://www.imsglobal.org/xsd/imscc/imscp_v1p1"
          xmlns:lom="http://ltsc.ieee.org/xsd/LOM"
          xmlns:lomimscc="http://ltsc.ieee.org/xsd/imscc/lomimscc_v1p0"
          xmlns:canvas="http://canvas.instructure.com/xsd/cccv1p0">
  <metadata>
    <schema>IMS Common Cartridge</schema>
    <schemaversion>1.1.0</schemaversion>
    <lom:lom>
      <lom:general>
        <lom:title>
          <lom:string>{lom_title}</lom:string>
        </lom:title>
      </lom:general>
    </lom:lom>
  </metadata>
  <resources>
"""

MANIFEST_FOOTER = """\
  </resources>
  <organizations>
    <organization identifier="org_1" structure="rooted-hierarchy">
      <title>{course_title}</title>
{organization_items}
    </organization>
  </organizations>
</manifest>
"""


# ──────────────────────────────────────────────────────────────────────
# Cartridge builder
# ──────────────────────────────────────────────────────────────────────

def build_cartridge(course: str):
    short_name, full_name = COURSE_DISPLAY[course]
    output_filename = f"{course}-canvas-import.imscc"
    dist_dir = PROJECT_ROOT / "dist"
    dist_dir.mkdir(exist_ok=True)
    output_path = dist_dir / output_filename

    # Inputs
    build_dir = PROJECT_ROOT / "build" / course
    if not build_dir.exists():
        raise SystemExit(
            f"build/{course}/ not found. Run `bash build/build.sh --standalone {course}` first."
        )

    config_path = PROJECT_ROOT / "build" / "course-config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    course_cfg = config["courses"][course]
    slug_to_path = course_cfg["pages"]
    path_to_slug = {v: k for k, v in slug_to_path.items()}
    known_slugs = set(slug_to_path.keys())

    quizzes_dir = PROJECT_ROOT / "quizzes"
    final_exam_dir = PROJECT_ROOT / "final-exam"

    # Resource accumulator: (identifier, type, href, [extra_dependency_id_or_none])
    resources = []
    # Files to write into the zip: zip_path → content
    zip_contents = {}
    # Module organization: { module_num: [(title, res_id, content_type)] }
    module_items = {}
    # Course-level (non-module) items: [(title, res_id, content_type)]
    course_resource_items = []

    # ── Pages ────────────────────────────────────────────────────────
    # Walk every slug, see if the file exists in the standalone build,
    # decide whether it becomes a wiki page or a discussion topic.

    source_dir = PROJECT_ROOT / course
    for slug, rel_path in slug_to_path.items():
        src_file = build_dir / rel_path
        if not src_file.exists():
            # Likely a concurrent-only file stripped by the standalone build, or a slug
            # for a page that hasn't shipped yet. Skip silently.
            continue

        html_text = src_file.read_text(encoding="utf-8")
        title = page_title_from_source(source_dir / rel_path,
                                       fallback=slug_to_friendly_fallback(slug))
        body = rewrite_links(extract_body(html_text), known_slugs)

        # The course-level "welcome" page tracks the current live week. For a fresh
        # cartridge import we reset it to point at Module 1 with an empty Past Modules list.
        if slug == "welcome":
            body = reset_welcome_to_module_1(
                body,
                module_1_slug=MODULE_1_SLUGS[course],
                module_1_title=MODULE_TITLES[course][1],
            )

        if is_ethics_path(rel_path):
            # Graded discussion: ship the IMS topic XML alongside a Canvas-extension
            # topicMeta sidecar that turns it into a 20-pt graded discussion in the
            # Participation assignment group.
            mod_num = module_number(rel_path)
            res_id = f"disc_{slug.replace('-', '_')}"
            meta_id = f"{res_id}_meta"
            assignment_id = f"{res_id}_assignment"
            disc_path = f"discussions/{slug}.xml"
            meta_path = f"course_settings/{slug}-topic-meta.xml"
            zip_contents[disc_path] = build_discussion_xml(title, body)
            zip_contents[meta_path] = build_discussion_meta_xml(
                meta_id=meta_id,
                topic_id=res_id,
                assignment_id=assignment_id,
                title=title,
                points=20,
                group_ref="participation",
            )
            resources.append((res_id, "imsdt_xmlv1p1", disc_path, meta_id))
            resources.append((
                meta_id,
                "associatedcontent/imscc_xmlv1p1/learning-application-resource",
                meta_path,
                None,
            ))
            if mod_num is not None:
                module_items.setdefault(mod_num, []).append((title, res_id, "DiscussionTopic"))
        else:
            # Wiki page
            res_id = f"page_{slug.replace('-', '_')}"
            wiki_path = f"wiki_content/{slug}.html"
            is_front_page = (slug == "welcome")
            zip_contents[wiki_path] = wrap_wiki_page(title, body, res_id, is_front_page)
            resources.append((res_id, "webcontent", wiki_path, None))
            mod_num = module_number(rel_path)
            if mod_num is not None:
                module_items.setdefault(mod_num, []).append((title, res_id, "WikiPage"))
            else:
                # Course-level page (welcome, glossary, makeup-participation)
                course_resource_items.append((title, res_id, "WikiPage"))

    # Quizzes (reading + final) are NOT bundled into the master cartridge.
    #
    # Canvas's CC importer fails with a generic error when a single cartridge holds
    # more than one standalone QTI quiz resource (`imsqti_xmlv1p2/imscc_xmlv1p1/assessment`).
    # Each per-module quiz JSON in quizzes/ is built into its own single-quiz IMSCC by
    # build_quiz.py, and import_cartridge_to_canvas.py imports them sequentially after
    # the master cartridge. Same goes for the final exam.
    # Tracked as a documented limitation in Setup Notes.

    # ── Setup notes page ─────────────────────────────────────────────
    setup_md_path = PROJECT_ROOT / "docs" / "COURSE-SETUP-NOTES.md"
    if setup_md_path.exists():
        md_text = setup_md_path.read_text(encoding="utf-8")
        substitutions = {
            "COURSE_CODE": short_name,
            "COURSE_NAME": full_name,
            "COURSE_CODE_LOWER": course,
            "CARTRIDGE_FILENAME": output_filename,
        }
        html_body = render_setup_notes(md_text, substitutions)
        setup_res_id = "page_course_setup_notes"
        zip_contents["wiki_content/course-setup-notes.html"] = wrap_wiki_page(
            "Course Setup Notes", html_body, setup_res_id, is_front_page=False,
        )
        resources.append((setup_res_id, "webcontent",
                          "wiki_content/course-setup-notes.html", None))
        # Place it first in Course Resources
        course_resource_items.insert(0, ("Course Setup Notes", setup_res_id, "WikiPage"))

    # Organization tree: Course Resources + Modules 1-7. WikiPages + quizzes.
    #
    # Canvas processes both the IMS organizations tree and course_settings/module_meta.xml.
    # Discussions placed in both ended up duplicated into an auto-created "Misc Module"
    # in earlier testing — so discussions are now only listed in module_meta.xml. Quizzes,
    # by contrast, are only placed correctly when they appear in the IMS organizations
    # tree, so we keep them here.
    IMS_TREE_TYPES = {"WikiPage", "Quizzes::Quiz"}
    org_lines = []

    if course_resource_items:
        org_lines.append('      <item identifier="course_resources">')
        org_lines.append("        <title>Course Resources</title>")
        for idx, (title, res_id, ct) in enumerate(course_resource_items):
            if ct not in IMS_TREE_TYPES:
                continue
            org_lines.append(
                f'        <item identifier="cr_item_{idx + 1}" identifierref="{res_id}">'
            )
            org_lines.append(f"          <title>{xml_escape(title)}</title>")
            org_lines.append("        </item>")
        org_lines.append("      </item>")

    for mod_num in sorted(module_items.keys()):
        mod_title = MODULE_TITLES[course][mod_num]
        org_lines.append(f'      <item identifier="module_{mod_num}">')
        org_lines.append(f"        <title>{xml_escape(mod_title)}</title>")
        for idx, (title, res_id, ct) in enumerate(module_items[mod_num]):
            if ct not in IMS_TREE_TYPES:
                continue
            org_lines.append(
                f'        <item identifier="m{mod_num}_item_{idx + 1}" identifierref="{res_id}">'
            )
            org_lines.append(f"          <title>{xml_escape(title)}</title>")
            org_lines.append("        </item>")
        org_lines.append("      </item>")

    organization_xml = "\n".join(org_lines)

    # ── Canvas-specific course_settings files ────────────────────────
    # These are what makes Canvas import the cartridge as wiki pages + real modules
    # rather than as a flat pile of HTML files.
    # Deliberately omit course_settings/canvas_export.txt: when Canvas sees that
    # marker, it switches the importer into "Canvas-flavored CC" mode and expects
    # quizzes at non_cc_assessments/*.qti rather than standard QTI at quizzes/*.xml.
    # The IMS-standard QTI path works fine, and wiki pages still import correctly
    # because each page has Canvas's `<meta name="identifier"/>` etc. in its head.
    zip_contents["course_settings/course_settings.xml"] = COURSE_SETTINGS_XML.format(
        title=xml_escape(full_name),
        course_code=xml_escape(short_name),
    )
    zip_contents["course_settings/assignment_groups.xml"] = ASSIGNMENT_GROUPS_XML

    # Build module_meta.xml from the same module_items dict the organization tree used.
    canvas_modules = []
    if course_resource_items:
        canvas_modules.append((
            "Course Resources",
            [
                {
                    "identifier": f"meta_cr_item_{idx + 1}",
                    "identifierref": res_id,
                    "content_type": ct,
                    "title": title,
                    "position": idx + 1,
                }
                for idx, (title, res_id, ct) in enumerate(course_resource_items)
            ],
        ))
    for mod_num in sorted(module_items.keys()):
        canvas_modules.append((
            MODULE_TITLES[course][mod_num],
            [
                {
                    "identifier": f"meta_m{mod_num}_item_{idx + 1}",
                    "identifierref": res_id,
                    "content_type": ct,
                    "title": title,
                    "position": idx + 1,
                }
                for idx, (title, res_id, ct) in enumerate(module_items[mod_num])
            ],
        ))
    zip_contents["course_settings/module_meta.xml"] = build_module_meta_xml(canvas_modules)

    # Register course_settings as a single bundled resource in the manifest so Canvas
    # picks it up during import. This resource needs to reference all three settings
    # files via additional <file> entries, which the manifest emitter handles below.
    resources.append((
        "course_settings",
        "associatedcontent/imscc_xmlv1p1/learning-application-resource",
        "course_settings/canvas_export.txt",
        None,
    ))
    # Track files belonging to multi-file resources so the manifest emitter knows to
    # add extra <file> entries.
    extra_files_for_resource = {
        "course_settings": [
            "course_settings/course_settings.xml",
            "course_settings/module_meta.xml",
            "course_settings/assignment_groups.xml",
        ],
    }

    # ── Build the manifest <resources> section ───────────────────────
    def build_resource_xml(res_id, res_type, href, dep_id, extras):
        lines = [f'    <resource identifier="{res_id}" type="{res_type}" href="{href}">']
        lines.append(f'      <file href="{href}"/>')
        for extra in extras:
            lines.append(f'      <file href="{extra}"/>')
        if dep_id:
            lines.append(f'      <dependency identifierref="{dep_id}"/>')
        lines.append("    </resource>")
        return lines

    resource_xml_lines = []
    for res in resources:
        res_id, res_type, href, dep_id = res
        extras = extra_files_for_resource.get(res_id, [])
        resource_xml_lines.extend(build_resource_xml(res_id, res_type, href, dep_id, extras))
    resource_xml = "\n".join(resource_xml_lines)

    manifest_xml = (
        MANIFEST_HEADER.format(manifest_id=f"{course}_canvas_import",
                               lom_title=xml_escape(full_name))
        + resource_xml + "\n"
        + MANIFEST_FOOTER.format(course_title=xml_escape(full_name),
                                 organization_items=organization_xml)
    )

    # ── Write the zip ────────────────────────────────────────────────
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("imsmanifest.xml", manifest_xml)
        for path, content in sorted(zip_contents.items()):
            zf.writestr(path, content)

    # Verify imsmanifest is first
    with zipfile.ZipFile(output_path, "r") as zf:
        first = zf.namelist()[0]
        if first != "imsmanifest.xml":
            raise SystemExit(f"imsmanifest.xml is not the first entry (got: {first})")

    n_pages = sum(1 for r in resources if r[1] == "webcontent")
    n_discussions = sum(1 for r in resources if r[1] == "imsdt_xmlv1p1")
    n_quizzes = sum(1 for r in resources if r[1] == "imsqti_xmlv1p2/imscc_xmlv1p1/assessment")
    print(f"  {output_path}")
    print(f"    pages: {n_pages}, discussions: {n_discussions}, quizzes: {n_quizzes}")
    return output_path


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build a single Canvas Common Cartridge per course."
    )
    parser.add_argument("course", choices=["aiml2003", "aiml2013"],
                        help="Course directory name")
    args = parser.parse_args()
    build_cartridge(args.course)


if __name__ == "__main__":
    main()
