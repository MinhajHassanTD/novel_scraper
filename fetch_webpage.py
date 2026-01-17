import cloudscraper
from get_text import extract_chapter_text
from get_next import get_next_chapter_url

scraper = cloudscraper.create_scraper()
current_url = "https://novelbin.com/b/shadow-slave/chapter-1-nightmare-begins"

for i in range(10):
    print(f"Chapter {i+1}...")
    
    response = scraper.get(current_url)
    
    with open("chapter.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    
    extract_chapter_text("chapter.html", "novel.txt")
    
    next_url = get_next_chapter_url("chapter.html")
    if not next_url:
        break
    
    if next_url.startswith('/'):
        current_url = "https://novelbin.com" + next_url
    else:
        current_url = next_url

print("Done!")