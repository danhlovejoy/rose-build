#!/usr/bin/env python3
"""
build_quiz.py — Quiz IMSCC Package Generator

Reads a quiz definition JSON file and produces a Canvas-compatible IMSCC
package (Common Cartridge 1.1.0 with QTI 1.2 assessment).

Usage:
    python3 build_quiz.py <quiz.json>
    python3 build_quiz.py <quiz.json> --output-dir /path/to/dir
    python3 build_quiz.py quizzes/               # batch: all .json in dir
    python3 build_quiz.py quizzes/ --output-dir build/output

Input format:
    See quizzes/aiml2003-module2-reading-quiz.json for a complete example.

    {
      "course": "aiml2003",          // course directory name
      "module": 2,                   // module number (or "final" for exams)
      "title": "Module 2 ...",       // quiz title shown in Canvas
      "description": "...",          // HTML description
      "allowed_attempts": 2,         // number of attempts
      "scoring_policy": "keep_highest",
      "shuffle_answers": true,
      "show_correct_answers_last_attempt": true,
      "points_per_question": 2,      // default points for MC questions
      "questions": [
        {
          "id": "unique_ident",      // unique identifier (alphanumeric + underscore)
          "type": "multiple_choice", // "multiple_choice" (default) or "essay"
          "title": "Display Title",  // shown in Canvas question bank
          "stem": "Question text?",  // the question (plain text or HTML)
          "choices": ["A", "B", "C", "D"],  // MC only: 4 answer choices
          "correct": 0,             // MC only: 0-indexed correct answer
          "correct_feedback": "...", // MC only (optional): shown when correct
          "incorrect_feedback": "..."// MC only (optional): shown when incorrect
          // Essay questions use "points": 15 for per-question point value
        }
      ]
    }

Output:
    <course>-module<N>-reading-quiz.imscc or <course>-final-exam.imscc
    (written to --output-dir, or to the current working directory by
    default; use quizzes/ as output-dir to keep JSON and IMSCC together)

Deterministic. No LLM. No external dependencies. Python 3.8+ stdlib only.
"""

import json
import os
import sys
import zipfile
from html import escape
from xml.sax.saxutils import escape as xml_escape


# ──────────────────────────────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────────────────────────────

MANIFEST_TEMPLATE = """\
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
    <resource identifier="{quiz_id}" type="imsqti_xmlv1p2/imscc_xmlv1p1/assessment" href="quizzes/{quiz_filename}">
      <file href="quizzes/{quiz_filename}"/>
      <dependency identifierref="{quiz_id}_meta"/>
    </resource>
    <resource identifier="{quiz_id}_meta" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="assessment_meta/{meta_filename}">
      <file href="assessment_meta/{meta_filename}"/>
    </resource>
  </resources>
  <organizations>
    <organization identifier="org_1" structure="rooted-hierarchy">
      <title>{title}</title>
      <item identifier="module_quiz">
        <title>{title}</title>
        <item identifier="item_quiz" identifierref="{quiz_id}">
          <title>{title}</title>
        </item>
      </item>
    </organization>
  </organizations>
</manifest>
"""

META_TEMPLATE = """\
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

QTI_HEADER = """\
<?xml version="1.0" encoding="UTF-8"?>
<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd">
  <assessment ident="{quiz_id}" title="{title}">
    <qtimetadata>
      <qtimetadatafield>
        <fieldlabel>cc_maxattempts</fieldlabel>
        <fieldentry>{allowed_attempts}</fieldentry>
      </qtimetadatafield>
    </qtimetadata>
    <section ident="root_section">
"""

QTI_FOOTER = """\
    </section>
  </assessment>
</questestinterop>
"""

CHOICE_LABELS = ["a", "b", "c", "d", "e", "f", "g", "h"]


# ──────────────────────────────────────────────────────────────────────
# QTI item builder
# ──────────────────────────────────────────────────────────────────────

def build_item_xml(q, points_per_question):
    """Build QTI XML for a single multiple-choice question."""
    qid = q["id"]
    correct_idx = q["correct"]
    correct_label = f"{qid}_{CHOICE_LABELS[correct_idx]}"

    lines = []
    lines.append(f'      <item ident="{xml_escape(qid)}" title="{xml_escape(q["title"])}">')
    lines.append('        <itemmetadata>')
    lines.append('          <qtimetadata>')
    lines.append('            <qtimetadatafield>')
    lines.append('              <fieldlabel>question_type</fieldlabel>')
    lines.append('              <fieldentry>multiple_choice_question</fieldentry>')
    lines.append('            </qtimetadatafield>')
    lines.append('            <qtimetadatafield>')
    lines.append('              <fieldlabel>points_possible</fieldlabel>')
    lines.append(f'              <fieldentry>{points_per_question}</fieldentry>')
    lines.append('            </qtimetadatafield>')
    lines.append('          </qtimetadata>')
    lines.append('        </itemmetadata>')

    # Presentation: stem + choices
    lines.append('        <presentation>')
    lines.append(f'          <material><mattext texttype="text/html"><![CDATA[<p>{q["stem"]}</p>]]></mattext></material>')
    lines.append('          <response_lid ident="response1" rcardinality="Single">')
    lines.append('            <render_choice>')
    for i, choice in enumerate(q["choices"]):
        label = f"{qid}_{CHOICE_LABELS[i]}"
        lines.append(f'              <response_label ident="{label}">'
                     f'<material><mattext texttype="text/plain">{xml_escape(choice)}</mattext></material>'
                     f'</response_label>')
    lines.append('            </render_choice>')
    lines.append('          </response_lid>')
    lines.append('        </presentation>')

    # Response processing
    lines.append('        <resprocessing>')
    lines.append('          <outcomes><decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/></outcomes>')
    lines.append('          <respcondition continue="No">')
    lines.append(f'            <conditionvar><varequal respident="response1">{correct_label}</varequal></conditionvar>')
    lines.append('            <setvar action="Set" varname="SCORE">100</setvar>')
    lines.append('          </respcondition>')
    lines.append('        </resprocessing>')

    # Feedback (only if present in the source JSON)
    if "correct_feedback" in q:
        lines.append(f'        <itemfeedback ident="{qid}_correct_fb">')
        lines.append(f'          <flow_mat><material><mattext texttype="text/html">'
                     f'<![CDATA[<p>{q["correct_feedback"]}</p>]]>'
                     f'</mattext></material></flow_mat>')
        lines.append('        </itemfeedback>')
    if "incorrect_feedback" in q:
        lines.append(f'        <itemfeedback ident="{qid}_incorrect_fb">')
        lines.append(f'          <flow_mat><material><mattext texttype="text/html">'
                     f'<![CDATA[<p>{q["incorrect_feedback"]}</p>]]>'
                     f'</mattext></material></flow_mat>')
        lines.append('        </itemfeedback>')

    lines.append('      </item>')
    return "\n".join(lines)


def build_essay_item_xml(q):
    """Build QTI XML for a single essay question."""
    qid = q["id"]
    points = q["points"]

    lines = []
    lines.append(f'      <item ident="{xml_escape(qid)}" title="{xml_escape(q["title"])}">')
    lines.append('        <itemmetadata>')
    lines.append('          <qtimetadata>')
    lines.append('            <qtimetadatafield>')
    lines.append('              <fieldlabel>question_type</fieldlabel>')
    lines.append('              <fieldentry>essay_question</fieldentry>')
    lines.append('            </qtimetadatafield>')
    lines.append('            <qtimetadatafield>')
    lines.append('              <fieldlabel>points_possible</fieldlabel>')
    lines.append(f'              <fieldentry>{points}</fieldentry>')
    lines.append('            </qtimetadatafield>')
    lines.append('          </qtimetadata>')
    lines.append('        </itemmetadata>')

    # Presentation: stem + text response area
    lines.append('        <presentation>')
    lines.append(f'          <material><mattext texttype="text/html"><![CDATA[<p>{q["stem"]}</p>]]></mattext></material>')
    lines.append('          <response_str ident="response1" rcardinality="Single">')
    lines.append('            <render_fib>')
    lines.append('              <response_label ident="answer1" rshuffle="No"/>')
    lines.append('            </render_fib>')
    lines.append('          </response_str>')
    lines.append('        </presentation>')

    # Response processing (no auto-grading for essays)
    lines.append('        <resprocessing>')
    lines.append('          <outcomes><decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/></outcomes>')
    lines.append('        </resprocessing>')

    lines.append('      </item>')
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# Package builder
# ──────────────────────────────────────────────────────────────────────

def build_quiz_package(quiz_data, output_dir):
    """Generate an IMSCC zip from a quiz definition dict."""
    course = quiz_data["course"]
    module_num = quiz_data["module"]  # int for reading quizzes, "final" for exams
    title = quiz_data["title"]
    description = quiz_data["description"]
    questions = quiz_data["questions"]
    points_per_q = quiz_data.get("points_per_question", 2)
    allowed_attempts = quiz_data.get("allowed_attempts", 2)
    scoring_policy = quiz_data.get("scoring_policy", "keep_highest")
    shuffle = "true" if quiz_data.get("shuffle_answers", True) else "false"
    show_last = "true" if quiz_data.get("show_correct_answers_last_attempt", True) else "false"

    # Compute total points: MC uses points_per_question, essays use per-question points field
    total_points = 0
    for q in questions:
        q_type = q.get("type", "multiple_choice")
        if q_type == "essay":
            total_points += q["points"]
        else:
            total_points += points_per_q

    # Derive identifiers — handle module="final" vs module=2
    course_prefix = "nlp" if "2003" in course else "cv"
    is_final = str(module_num) == "final"
    if is_final:
        quiz_id = f"{course_prefix}_final_exam"
        manifest_id = f"{course}_final_exam"
        quiz_filename = "final_exam.xml"
        meta_filename = "final_exam_meta.xml"
        output_filename = f"{course}-final-exam.imscc"
    else:
        quiz_id = f"{course_prefix}_module{module_num}_reading_quiz"
        manifest_id = f"{course}_module{module_num}_reading_quiz"
        quiz_filename = f"module{module_num}_reading_quiz.xml"
        meta_filename = f"module{module_num}_reading_quiz_meta.xml"
        output_filename = f"{course}-module{module_num}-reading-quiz.imscc"
    lom_title = f"{course.upper()} - {title}"

    # Build QTI assessment XML
    qti_xml = QTI_HEADER.format(
        quiz_id=quiz_id,
        title=xml_escape(title),
        allowed_attempts=allowed_attempts,
    )
    for q in questions:
        q_type = q.get("type", "multiple_choice")
        if q_type == "essay":
            qti_xml += "\n" + build_essay_item_xml(q) + "\n"
        else:
            qti_xml += "\n" + build_item_xml(q, points_per_q) + "\n"
    qti_xml += QTI_FOOTER

    # Build metadata XML
    meta_xml = META_TEMPLATE.format(
        quiz_id=quiz_id,
        title=xml_escape(title),
        description=description,
        shuffle=shuffle,
        scoring_policy=scoring_policy,
        points_possible=total_points,
        show_last=show_last,
        allowed_attempts=allowed_attempts,
    )

    # Build manifest XML
    manifest_xml = MANIFEST_TEMPLATE.format(
        manifest_id=manifest_id,
        lom_title=xml_escape(lom_title),
        quiz_id=quiz_id,
        quiz_filename=quiz_filename,
        meta_filename=meta_filename,
        title=xml_escape(title),
    )

    # Write IMSCC zip
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("imsmanifest.xml", manifest_xml)
        zf.writestr(f"quizzes/{quiz_filename}", qti_xml)
        zf.writestr(f"assessment_meta/{meta_filename}", meta_xml)

    return output_path


# ──────────────────────────────────────────────────────────────────────
# Validation
# ──────────────────────────────────────────────────────────────────────

def validate_quiz(data, filepath):
    """Check required fields and constraints. Returns list of error strings."""
    errors = []
    required_top = ["course", "module", "title", "description", "questions"]
    for field in required_top:
        if field not in data:
            errors.append(f"Missing top-level field: {field}")

    if "questions" in data:
        if len(data["questions"]) == 0:
            errors.append("Quiz has no questions")
        for i, q in enumerate(data["questions"]):
            prefix = f"Question {i + 1}"
            q_type = q.get("type", "multiple_choice")

            # Fields required for all question types
            for field in ["id", "title", "stem"]:
                if field not in q:
                    errors.append(f"{prefix}: missing field '{field}'")

            if q_type == "essay":
                # Essay questions need a points field
                if "points" not in q:
                    errors.append(f"{prefix} (essay): missing field 'points'")
            else:
                # MC questions need choices and correct index
                for field in ["choices", "correct"]:
                    if field not in q:
                        errors.append(f"{prefix}: missing field '{field}'")
                if "choices" in q:
                    if len(q["choices"]) < 2:
                        errors.append(f"{prefix}: needs at least 2 choices")
                    if len(q["choices"]) > 8:
                        errors.append(f"{prefix}: max 8 choices supported")
                if "correct" in q and "choices" in q:
                    if q["correct"] < 0 or q["correct"] >= len(q["choices"]):
                        errors.append(f"{prefix}: correct index {q['correct']} "
                                      f"out of range (0–{len(q['choices']) - 1})")

    if errors:
        print(f"\nValidation failed for {filepath}:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
    return errors


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 build_quiz.py <quiz.json|directory> [--output-dir DIR]")
        print()
        print("  <quiz.json>     Single quiz JSON file")
        print("  <directory>     Process all .json files in the directory")
        print("  --output-dir    Where to write .imscc files (default: project root)")
        print()
        print("Example:")
        print("  python3 build/build_quiz.py quizzes/aiml2003-module2-reading-quiz.json")
        print("  python3 build/build_quiz.py quizzes/")
        print("  python3 build/build_quiz.py quizzes/ --output-dir build/output")
        sys.exit(1)

    target = sys.argv[1]
    output_dir = "."

    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
        else:
            print("Error: --output-dir requires a path", file=sys.stderr)
            sys.exit(1)

    # Collect input files
    if os.path.isdir(target):
        json_files = sorted(
            os.path.join(target, f)
            for f in os.listdir(target)
            if f.endswith(".json")
        )
        if not json_files:
            print(f"No .json files found in {target}", file=sys.stderr)
            sys.exit(1)
    elif os.path.isfile(target):
        json_files = [target]
    else:
        print(f"Not found: {target}", file=sys.stderr)
        sys.exit(1)

    # Process each file
    had_errors = False
    for filepath in json_files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        errors = validate_quiz(data, filepath)
        if errors:
            had_errors = True
            continue

        output_path = build_quiz_package(data, output_dir)

        # Verify the package
        with zipfile.ZipFile(output_path, "r") as zf:
            names = zf.namelist()
            assert names[0] == "imsmanifest.xml", \
                f"imsmanifest.xml not first entry in {output_path}"

        n_questions = len(data["questions"])
        points_per_q = data.get("points_per_question", 2)
        total_pts = 0
        for q in data["questions"]:
            q_type = q.get("type", "multiple_choice")
            if q_type == "essay":
                total_pts += q["points"]
            else:
                total_pts += points_per_q
        print(f"  {output_path}  ({n_questions} questions, {total_pts} pts)")

    if had_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
