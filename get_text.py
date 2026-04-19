from bs4 import BeautifulSoup, Tag

def extract_chapter(html: str) -> tuple[str, list[str]]:
    soup: BeautifulSoup = BeautifulSoup(markup=html, features='html.parser')
    title: Tag | None = soup.find('h4')
    title_text: str = title.get_text(strip=True) if title else "Untitled"
    paragraphs: list[str] = [
        p.get_text(strip=True) for p in soup.find_all('p')
        if p.get_text(strip=True) and not p.get_text(strip=True).startswith("Total Response")
    ]
    return title_text, paragraphs