from bs4 import BeautifulSoup

def get_next_chapter_url(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    next_link = soup.find(id='next_chap')
    
    if next_link:
        return next_link.get('href')
    return None

if __name__ == "__main__":
    get_next_chapter_url("chapter.html")
