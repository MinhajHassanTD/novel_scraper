from bs4 import BeautifulSoup, Tag, ResultSet

def extract_chapter_text(html_file_path: str, output_txt_path: str) -> int:
    with open(file=html_file_path, mode="r", encoding="utf-8") as f:
        soup: BeautifulSoup = BeautifulSoup(markup=f.read(), features='html.parser')
    
    title: Tag | None = soup.find('h4')
    title_text: str = title.get_text(strip=True) if title else "No Title"
    
    paragraphs: ResultSet[Tag] = soup.find_all('p')
    
    chapter_text: list[str] = []
    for p in paragraphs:
        text: str = p.get_text(strip=True)
        if text and not text.startswith("Total Response"):
            chapter_text.append(text)
    
    with open(file=output_txt_path, mode="a", encoding="utf-8") as output:
        _ = output.write(title_text + "\n\n")
        _ = output.write("\n\n".join(chapter_text))
        _ = output.write("\n\n\n")
    
    return len(chapter_text)

if __name__ == "__main__":
    _ = extract_chapter_text(html_file_path="chapter.html", output_txt_path="chapter.txt")