from bs4 import BeautifulSoup

def extract_chapter_text(html_file_path, output_txt_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    title = soup.find('h4')
    title_text = title.get_text(strip=True) if title else "No Title"
    
    paragraphs = soup.find_all('p')
    
    chapter_text = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and not text.startswith("Total Response"):
            chapter_text.append(text)
    
    with open(output_txt_path, "a", encoding="utf-8") as output:
        output.write(title_text + "\n\n")
        output.write("\n\n".join(chapter_text))
        output.write("\n\n\n")
    
    return len(chapter_text)

if __name__ == "__main__":
    extract_chapter_text("chapter.html", "chapter.txt")