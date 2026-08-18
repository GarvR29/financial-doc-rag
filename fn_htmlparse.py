from bs4 import BeautifulSoup
import re

def inspect_html(path: str = r"data/raw/AAPL_10K_2025-09-27.html", keyword: str = "Item 1A", context_chars: int = 150):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    print(find_keyword_positions(text, "Item 1A"))
    print(filter_heading_candidates(text,find_keyword_positions(text, "Item 1A"), "Item 1A", "Risk Factors"))
    candidates = filter_heading_candidates(text, find_keyword_positions(text, "Item 1A"), "Item 1A", "Risk Factors")
    real_headings = []
    for pos in candidates:
        if not is_toc_entry(text, pos, "Item 1A", "Risk Factors"):
            real_headings.append(pos)
    print(real_headings)
    section_text = extract_section_text(text, 37505, "Item 1B")
    section_text = extract_section_text(text, real_headings[0], "Item 1B")
    section_text = clean_text(section_text, "Apple Inc.")
    print(len(section_text))
    print(section_text[:300])
    pos = 0 
    while True:
        pos = text.find(keyword, pos)
        if pos == -1:
            break

        before = text[max(0, pos - context_chars) : pos]
        after = text[pos + len(keyword) : pos + len(keyword) + context_chars]
        pos += 1
        print(before)
        print(after)
    pass

def find_keyword_positions(text: str, keyword: str = "Risk Factors") -> list[int]:
    """Return every starting index where `keyword` appears in `text`."""
    pos = 0
    positions = []
    while True:

        pos = text.find(keyword, pos)
        if pos == -1:
            break

        positions.append(pos)
        pos+=1

    return positions

def filter_heading_candidates(text: str, positions: list[int], keyword: str, section_title: str, gap: int = 20) -> list[int]:
    """
    Keep only the positions where `section_title` appears shortly after
    the keyword ends — filters out cross-references that aren't
    immediately followed by the section title.
    """
    candidates = []
    for pos in positions:

        after = pos + len(keyword)
        gap = 25
        slice_candidates = text[after : after + gap]
        print(pos, repr(slice_candidates)) 
        if section_title in slice_candidates:
            candidates.append(pos)
    return candidates

def is_toc_entry(text: str, pos: int, keyword: str, section_title: str, gap: int = 25) -> bool:
    """
    Check whether a candidate position looks like a Table of Contents
    entry (title immediately followed by a page number) rather than a
    real section heading (title followed by prose).
    """
    window_start = pos + len(keyword)
    window_end = window_start + gap

    # 1. find WHERE "Risk Factors" itself starts, searching only within
    #    the small window right after "Item 1A" ends
    title_start = text.find(section_title, window_start, window_end)

    # 2. figure out where "Risk Factors" ENDS
    title_end = title_start + len(section_title)

    # 3. grab the single character sitting right at that end index
    next_char = text[title_end]

    # 4 & 5. a digit right after the title means this is a TOC page
    #         reference; anything else means real prose follows
    return next_char.isdigit()

def extract_section_text(text: str, start_pos: int, next_keyword: str = "Item 1B") -> str:
    """
    Extract the full text of a section, from its confirmed heading
    position up to wherever the next section begins.
    """
    next_positions = find_keyword_positions(text, next_keyword)

    # "Item 1B" might appear before our section too (e.g. in the TOC),
    # so only keep occurrences that come AFTER our real heading —
    # then take the earliest of those, since that's the next real boundary
    after_start = [p for p in next_positions if p > start_pos]
    end_pos = min(after_start) if after_start else len(text)

    return text[start_pos:end_pos]


def clean_text(text: str, company_name: str = "Apple Inc.") -> str:
    """
    Remove repeated page-footer artifacts like "Apple Inc. | 2025 Form 10-K | 5"
    that get_text() leaves embedded in the middle of the prose — HTML has no
    concept of "this is a page boundary, not real content," so both end up
    concatenated together as plain text.
    """
    footer_pattern = re.escape(company_name) + r"\s*\|\s*\d{4}\s*Form\s*10-K\s*\|\s*\d+"
    return re.sub(footer_pattern, "", text)
inspect_html()

