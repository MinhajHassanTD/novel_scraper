from bs4 import BeautifulSoup, Tag

def get_next_url(html: str) -> str | None:
    soup: BeautifulSoup = BeautifulSoup(markup=html, features='html.parser')
    next_link: Tag | None = soup.find(id='next_chap')
    if next_link:
        return str(next_link.get(key='href'))
    return None
