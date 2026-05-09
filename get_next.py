from bs4 import BeautifulSoup, Tag

def get_next_url(html: str) -> str | None:
    soup: BeautifulSoup = BeautifulSoup(markup=html, features='html.parser')
    next_link: Tag | None = soup.find(id='next_chap')
    if next_link:
        href = next_link.get('href')
        return str(href) if href else None
    return None
