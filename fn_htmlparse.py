from bs4 import BeautifulSoup

def inspect_html(path: str = r"data/raw/AAPL_10K_2025-09-27.html", keyword: str = "Item 1A", context_chars: int = 150):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    print(find_keyword_positions(text, "Item 1A"))
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
inspect_html()

