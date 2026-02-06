from cloudscraper import CloudScraper
from requests.models import Response
import cloudscraper
from get_text import extract_chapter_text
from get_next import get_next_chapter_url
from typing import Any  # pyright: ignore[reportUnusedImport]
import time

def search_novel(responses: list[tuple[Response, str]], Novel_Name: str,scraper: CloudScraper, urls: list[str]) -> str:
    for r in responses:
        search_url: str = r[1]
        if search_url == urls[0]:
            search_url += f"search?keyword={Novel_Name}&type=title"
        elif search_url  == urls[1]:
            search_url += f"?search={Novel_Name}"
        elif search_url  == urls[2]:
            search_url += f"search?keyword={Novel_Name}"
            
        response : Response = scraper.get(url=search_url)
        print(response.status_code)
        print(search_url)
        
        safe_filename: str = r[1].replace("https://", "").replace("/", "_").replace(":", "__").replace(".", "-")
        with open(file=f"{safe_filename}.html", mode="w", encoding="utf-8") as f:
            _ = f.write(response.text)
    
    return "done"

def safe_string(String : str)->str:
    String = String.replace(" ","+")
    String = String.lower()
    return String

def fetch() -> int:
    scraper: CloudScraper = cloudscraper.create_scraper()  # pyright: ignore[reportUnknownMemberType]
    
    urls: list[str] = []
    urls.append("https://novelfire.net/") #Has search?keyword=[string]&type=title to get names
    urls.append("https://novels.pl/") #has ?search=[string] to get queried names
    urls.append("https://novelbin.com/") #has search?keyword=[string] to get queried names
    
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
    
    
    novel_url: str = search_novel(responses=responses, Novel_Name=safe_string(String="Shadow Slave"),scraper=scraper, urls= urls)
    print(novel_url)
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