from bs4 import BeautifulSoup, Tag

# Ordered from most-specific to most-general; stops at first non-empty match.
_TITLE_SELECTORS = [
    ".chr-title",
    ".chapter-title",
    "[class*='chapter-title']",
    "[class*='chapter_title']",
    "h1.title",
    "h2.title",
    "h1",
    "h2",
    "h3",
]

# Divs that wrap only the chapter body text (excludes comments, sidebar, etc.).
_CONTENT_SELECTORS = [
    "#chr-content",
    ".chr-content",
    "#chapter-content",
    ".chapter-content",
    "[class*='chapter-c']",
    "article",
]


def extract_chapter(html: str) -> tuple[str, list[str]]:
    soup = BeautifulSoup(html, "html.parser")

    # --- title ---
    title_text = "Untitled"
    for sel in _TITLE_SELECTORS:
        tag = soup.select_one(sel)
        if tag:
            text = tag.get_text(strip=True)
            if text:
                title_text = text
                break

    # Fall back to <title> tag ("Chapter X - Novel Name" → take the left part)
    if title_text == "Untitled":
        page_title = soup.find("title")
        if page_title:
            title_text = page_title.get_text(strip=True).split(" - ")[0].strip()

    # --- paragraphs (prefer scoped content div to avoid comments noise) ---
    content_root: Tag | BeautifulSoup = soup
    for sel in _CONTENT_SELECTORS:
        node = soup.select_one(sel)
        if node:
            content_root = node
            break

    paragraphs: list[str] = [
        p.get_text(strip=True)
        for p in content_root.find_all("p")
        if p.get_text(strip=True) and not p.get_text(strip=True).startswith("Total Response")
    ]
    return title_text, paragraphs
