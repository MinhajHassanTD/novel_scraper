from bs4._typing import _AtMostOneTag


from bs4._typing import _SomeTags


from typing import Any


from bs4 import BeautifulSoup

def extract_chapter_text(html_file_path, output_txt_path) -> int:
    with open(file=html_file_path, mode="r", encoding="utf-8") as f:
        soup: BeautifulSoup = BeautifulSoup(markup=f.read(), features='html.parser')
    
    title: _AtMostOneTag = soup.find('h4')
    title_text: str = title.get_text(strip=True) if title else "No Title"
    
    paragraphs: _SomeTags = soup.find_all('p')
    
    chapter_text: list[Any] = []
    for p in paragraphs:
        text: str = p.get_text(strip=True)
        if text and not text.startswith("Total Response"):
            chapter_text.append(text)
    
    with open(file=output_txt_path, mode="a", encoding="utf-8") as output:
        output.write(title_text + "\n\n")
        output.write("\n\n".join(chapter_text))
        output.write("\n\n\n")
    
    return len(chapter_text)

if __name__ == "__main__":
    extract_chapter_text(html_file_path="chapter.html", output_txt_path="chapter.txt")