from cloudscraper import CloudScraper
from requests.models import Response
import cloudscraper
from get_text import extract_chapter_text
from get_next import get_next_chapter_url
from typing import Any  # pyright: ignore[reportUnusedImport]
import time

def fetch() -> int:
    scraper: CloudScraper = cloudscraper.create_scraper()  # pyright: ignore[reportUnknownMemberType]
    
    urls: list[str] = []
    urls.append("https://novelfire.net/") #Has home? to get queried novel names
    urls.append("https://www.novels.pl/") #has ?search=[string] to get queried names
    urls.append("https://novelbin.com/") #has search?keyword=S[string] to get queried names
    
    responses: list[tuple[Response, str]] = []
    
    for url in urls:
        time.sleep(1)
        response : Response = scraper.get(url = url)
        if (response.status_code == 200):
            print(response.elapsed , url)
            responses.append((response,url))
        else:
            print(f"Error {response.status_code} for {url}")
    
    responses.sort(key=lambda r: r[0].elapsed)
    
    if len(responses) < 1:
        return -1 #means no reachable link.
    
    current_url:str = responses[0][1] #getting from one which has fastest access time.
    
    print(responses)
    return 0
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