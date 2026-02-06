from cloudscraper import CloudScraper
from requests.models import Response
import cloudscraper
from get_text import extract_chapter_text
from get_next import get_next_chapter_url

def fetch() -> None:
    scraper: CloudScraper = cloudscraper.create_scraper()  # pyright: ignore[reportUnknownMemberType]
    current_url: str = "https://novelbin.com/b/shadow-slave/chapter-1-nightmare-begins"

    for i in range(10):
        print(f"Chapter {i+1}...")
        
        response: Response = scraper.get(url=current_url)
        
        with open(file="chapter.html", mode="w", encoding="utf-8") as f:
            _ = f.write(response.text)
        
        _ = extract_chapter_text(html_file_path="chapter.html", output_txt_path="novel.txt")
        
        next_url: str | None = get_next_chapter_url(html_file_path="chapter.html")
        if not next_url:
            break
        
        if next_url.startswith('/'):
            current_url = "https://novelbin.com" + next_url
        else:
            current_url = next_url

    print("Done!")
    
if __name__ == "__main__":
    _ = fetch()