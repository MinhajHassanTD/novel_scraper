from bs4 import BeautifulSoup, Tag

def get_next_chapter_url(html_file_path: str): 
    with open(file=html_file_path, mode="r", encoding="utf-8") as f:
        soup: BeautifulSoup = BeautifulSoup(markup=f.read(), features='html.parser')
    
    next_link: Tag | None = soup.find(id='next_chap')
    
    if next_link:
        return next_link.get(key='href')
    return None

if __name__ == "__main__":
    get_next_chapter_url(html_file_path="chapter.html")
