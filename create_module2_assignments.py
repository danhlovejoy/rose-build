#!/usr/bin/env python3
"""
create_module2_assignments.py

Creates (or updates) the four Canvas artifacts for AIML 2003 Module 2:
  1. Module 2 Participation  — Assignment, 80 pts, No Submission, Participation group
  2. Module 2 Ethics Discussion — Discussion, 20 pts, Participation group
  3. Module 2 Presentation   — Assignment, 100 pts, On Paper, Presentations group, rubric 65800
  4. Module 2 GitHub Repo    — Assignment, 100 pts, Online URL, GitHub Repos group, rubric 66034

Existing assignment 810698 (Module 2 Participation, wrong due time) is updated in place.
"""

import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

ROOT    = os.path.dirname(os.path.abspath(__file__))
BASE    = "https://rose.instructure.com"
COURSE  = 26943
DUE     = "2026-04-07T17:30:00-05:00"   # Tuesday Apr 7, 5:30 PM CDT (class time)

# Assignment group IDs (verified via API)
GRP_PARTICIPATION = 98579
GRP_REPOS         = 98580
GRP_PRESENTATIONS = 98581

# Rubric IDs (NLP course)
RUBRIC_PRESENTATION = 65800
RUBRIC_REPO         = 66034

# Existing Participation assignment (created via UI — just needs time fix)
EXISTING_PARTICIPATION_ID = 810698


def load_token():
    env_path = os.path.join(ROOT, '.env')
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                return line.split('=', 1)[1].strip()
    raise RuntimeError(".env: no token found")


def api(method, path, payload=None, token=None):
    url = f"{BASE}/api/v1{path}"
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = Request(url, data=data, method=method)
    req.add_header('Authorization', f'Bearer {token}')
    if data:
        req.add_header('Content-Type', 'application/json')
    try:
        resp = urlopen(req)
        return json.loads(resp.read().decode('utf-8'))
    except HTTPError as e:
        detail = e.read().decode('utf-8', errors='replace')
        print(f"  HTTP {e.code} on {method} {path}")
        print(f"  {detail[:400]}")
        raise


def main():
    token = load_token()
    results = []

    # ── 1. Fix the existing Participation assignment (due time was wrong) ──────
    print("1. Updating Module 2 Participation (ID 810698) — fixing due time…")
    r = api('PUT', f'/courses/{COURSE}/assignments/{EXISTING_PARTICIPATION_ID}', {
        'assignment': {
            'due_at': DUE,
        }
    }, token)
    print(f"   OK  due_at={r['due_at']}")
    results.append(('Module 2 Participation', r['id'], 'updated'))

    # ── 2. Module 2 Ethics Discussion ─────────────────────────────────────────
    print("2. Creating Module 2 Ethics Discussion…")
    body = (
        "<p><strong>The Prompt</strong></p>"
        "<p>Your lab this week trains a sentiment classifier on the NLTK movie reviews corpus. "
        "Sentiment is not a fact — it's an interpretation. The same word can mean different things "
        "in different contexts, and the labels in the training data encode the judgments of the "
        "people who wrote them. The model inherits those judgments as ground truth.</p>"
        "<p>In your post, address at least one of the following:</p>"
        "<ul>"
        "<li>The NLTK corpus was labeled by individual reviewers. If those reviewers share similar "
        "demographics or cultural reference points, what assumptions get baked into the model's "
        "definition of &ldquo;positive&rdquo; and &ldquo;negative&rdquo;?</li>"
        "<li>If a word like &ldquo;predictable&rdquo; has a negative coefficient, the model treats "
        "it as evidence of a bad review regardless of context. What does this tell you about the "
        "limits of training on a single labeled dataset?</li>"
        "<li>Sentiment analysis is used at scale: product reviews, social media monitoring, customer "
        "feedback scoring. If the training data reflects one community's language patterns, what "
        "happens when the model is applied to a different community?</li>"
        "<li>You used Gemini to classify the same reviews. Gemini carries its own biases from its "
        "training data. Is one approach more &ldquo;fair&rdquo; than the other, or do they encode "
        "different biases?</li>"
        "</ul>"
        "<p><strong>Requirements:</strong></p>"
        "<ul>"
        "<li><strong>Your post:</strong> 150&ndash;250 words. Take a position. Don't just summarize the question.</li>"
        "<li><strong>Reply to a classmate:</strong> At least one substantive reply. Engage with their reasoning.</li>"
        "<li><strong>Deadline:</strong> Initial post by Tuesday, April 7 (before class). Reply by April 14.</li>"
        "</ul>"
        "<p>Use specificity from the lab: you've seen the coefficients, found the failures, and know "
        "where the training data came from. Connect the ethical question to what you observed.</p>"
        "<p><em>Worth 20% of your Module 2 Participation grade. Required every week, regardless of attendance.</em></p>"
    )
    r = api('POST', f'/courses/{COURSE}/discussion_topics', {
        'title':                  'Module 2 Ethics Discussion',
        'message':                body,
        'discussion_type':        'threaded',
        'assignment': {
            'points_possible':    20,
            'assignment_group_id': GRP_PARTICIPATION,
            'due_at':             DUE,
            'submission_types':   ['discussion_topic'],
            'published':          False,
        },
        'published': False,
    }, token)
    print(f"   OK  id={r['id']}  title={r['title']}")
    results.append(('Module 2 Ethics Discussion', r['id'], 'created'))

    # ── 3. Module 2 Presentation ──────────────────────────────────────────────
    print("3. Creating Module 2 Presentation…")
    r = api('POST', f'/courses/{COURSE}/assignments', {
        'assignment': {
            'name':                  'Module 2 Presentation',
            'points_possible':       100,
            'assignment_group_id':   GRP_PRESENTATIONS,
            'submission_types':      ['on_paper'],
            'due_at':                DUE,
            'published':             False,
            'rubric': {
                'id': str(RUBRIC_PRESENTATION),
            },
            'rubric_settings': {
                'point_deductions': False,
                'free_form_criterion_comments': True,
            },
            'use_rubric_for_grading': True,
        }
    }, token)
    print(f"   OK  id={r['id']}  title={r['name']}")
    results.append(('Module 2 Presentation', r['id'], 'created'))

    # ── 4. Module 2 GitHub Repo ───────────────────────────────────────────────
    print("4. Creating Module 2 GitHub Repo…")
    r = api('POST', f'/courses/{COURSE}/assignments', {
        'assignment': {
            'name':                  'Module 2 GitHub Repo',
            'points_possible':       100,
            'assignment_group_id':   GRP_REPOS,
            'submission_types':      ['online_url'],
            'due_at':                DUE,
            'published':             False,
            'rubric': {
                'id': str(RUBRIC_REPO),
            },
            'rubric_settings': {
                'point_deductions': False,
                'free_form_criterion_comments': True,
            },
            'use_rubric_for_grading': True,
        }
    }, token)
    print(f"   OK  id={r['id']}  title={r['name']}")
    results.append(('Module 2 GitHub Repo', r['id'], 'created'))

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 55)
    print("DONE")
    for name, aid, action in results:
        print(f"  {action:8s}  {name:35s}  id={aid}")
    print()
    print("Next: attach rubrics in Canvas UI if not auto-attached,")
    print("then upload pages and build the module structure.")


if __name__ == '__main__':
    main()
