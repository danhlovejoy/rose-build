#!/usr/bin/env python3
"""
Split Szeliski's "Computer Vision: Algorithms and Applications" (2nd Ed.)
into one PDF per second-level section (e.g., 5.1, 5.2, 5.3).

Requires PyMuPDF: pip install pymupdf

Usage:
  python3 scripts/split_szeliski.py                          # default paths
  python3 scripts/split_szeliski.py input.pdf output_dir/    # custom paths
"""

import os
import re
import sys

import fitz  # PyMuPDF


def slugify(text):
    """Convert a title to a filename-safe kebab-case slug."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def identify_chapters_and_sections(toc):
    """
    Walk the TOC and assign chapter/section numbers.

    Returns a list of dicts for each L2 (section-level) entry:
      { 'chapter_num': int, 'section_num': int, 'title': str,
        'start_page': int, 'chapter_title': str }
    Plus a flat list of all entries with page numbers for computing end pages.
    """
    # Front matter L1 entries that are not numbered chapters
    skip_titles = {
        'preface', 'contents', 'references', 'index',
    }

    # Identify numbered chapters (L1 entries that are real chapters)
    chapters = []  # (toc_index, title, page)
    for i, (level, title, page) in enumerate(toc):
        if level == 1 and title.lower().strip() not in skip_titles:
            chapters.append((i, title, page))

    # For each chapter, collect its L2 children and number them
    sections = []
    for ch_idx, (toc_i, ch_title, ch_page) in enumerate(chapters):
        ch_num = ch_idx + 1  # 1-based chapter numbering

        # Find L2 entries that belong to this chapter (between this L1 and next L1)
        next_l1_toc_i = None
        for j in range(toc_i + 1, len(toc)):
            if toc[j][0] == 1:
                next_l1_toc_i = j
                break

        sec_num = 0
        for j in range(toc_i + 1, next_l1_toc_i if next_l1_toc_i else len(toc)):
            level, title, page = toc[j]
            if level == 2:
                sec_num += 1
                sections.append({
                    'chapter_num': ch_num,
                    'section_num': sec_num,
                    'title': title,
                    'start_page': page,  # 1-based PDF page
                    'chapter_title': ch_title,
                })

    return sections


def compute_page_ranges(sections, total_pages):
    """
    Compute end pages for each section.
    Each section runs from its start page to the page before the next section starts.
    """
    for i, sec in enumerate(sections):
        if i + 1 < len(sections):
            sec['end_page'] = sections[i + 1]['start_page'] - 1
        else:
            sec['end_page'] = total_pages

    return sections


def split_pdf(input_path, output_dir):
    """Split the PDF into per-section files."""
    doc = fitz.open(input_path)
    toc = doc.get_toc()

    sections = identify_chapters_and_sections(toc)
    sections = compute_page_ranges(sections, doc.page_count)

    os.makedirs(output_dir, exist_ok=True)

    created = 0
    for sec in sections:
        label = f"{sec['chapter_num']}.{sec['section_num']}"
        slug = slugify(sec['title'])
        filename = f"szeliski-{label}-{slug}.pdf"
        filepath = os.path.join(output_dir, filename)

        # fitz uses 0-based page indices
        start = sec['start_page'] - 1
        end = sec['end_page'] - 1

        # Extract pages
        out_doc = fitz.open()
        out_doc.insert_pdf(doc, from_page=start, to_page=end)
        out_doc.save(filepath)
        out_doc.close()

        page_count = end - start + 1
        print(f"  {filename}  ({page_count} pages, p{sec['start_page']}–{sec['end_page']})")
        created += 1

    doc.close()
    print(f"\n  {created} files written to {output_dir}/")


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if len(sys.argv) >= 3:
        input_path = sys.argv[1]
        output_dir = sys.argv[2]
    elif len(sys.argv) == 2:
        input_path = sys.argv[1]
        output_dir = os.path.join(project_root, 'readings', 'szeliski')
    else:
        input_path = os.path.join(project_root, 'Szeliski_CVAABook_2ndEd.pdf')
        output_dir = os.path.join(project_root, 'readings', 'szeliski')

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return 1

    print(f"Splitting: {os.path.basename(input_path)}")
    print(f"Output:    {output_dir}/\n")

    split_pdf(input_path, output_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main())
