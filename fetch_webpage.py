import time
import threading
import cloudscraper
from cloudscraper import CloudScraper
from urllib.parse import urlparse
from typing import Callable
from bs4 import BeautifulSoup
import os
from get_text import extract_chapter
from get_next import get_next_url
from make_epub import build_epub


def fetch_metadata(chapter_url: str, scraper: CloudScraper) -> tuple[str, str, bytes | None]:
    parsed = urlparse(chapter_url)
    base_path = parsed.path.rstrip("/").rsplit("/", 1)[0]
    base_url = f"{parsed.scheme}://{parsed.netloc}{base_path}"

    soup = BeautifulSoup(scraper.get(base_url).text, "html.parser")

    title_tag = soup.select_one("h3.title") or soup.select_one(".book-name") or soup.find("h3")
    author_tag = soup.select_one("a[href*='author']") or soup.select_one(".author")
    cover_tag = soup.select_one(".book img") or soup.select_one("img.cover") or soup.select_one(".cover img")

    title = title_tag.get_text(strip=True) if title_tag else ""
    author = author_tag.get_text(strip=True) if author_tag else ""

    cover_bytes: bytes | None = None
    if cover_tag:
        src = cover_tag.get("src") or cover_tag.get("data-src")
        if src:
            try:
                cover_bytes = scraper.get(str(src)).content
            except Exception:
                pass

    return title, author, cover_bytes


def fetch(
    start_url: str,
    title: str,
    author: str = "Unknown",
    start_chapter: int = 1,
    end_chapter: int = 0,
    delay: float = 1.0,
    save_dir: str = ".",
    cover: bytes | None = None,
    cancel_event: threading.Event | None = None,
    progress_callback: Callable[[str], None] | None = None,
    on_chapter_done: Callable[[int, float], None] | None = None,
) -> str:
    def log(msg: str) -> None:
        if progress_callback:
            progress_callback(msg)
        else:
            print(msg)

    max_chapters = (end_chapter - start_chapter + 1) if end_chapter > 0 else 0

    scraper: CloudScraper = cloudscraper.create_scraper()  # pyright: ignore[reportUnknownMemberType]
    current_url = start_url
    chapters: list[tuple[str, list[str]]] = []

    while True:
        if cancel_event and cancel_event.is_set():
            log("Cancelled.")
            break

        chapter_num = start_chapter + len(chapters)
        log(f"Fetching chapter {chapter_num}...")
        t0 = time.monotonic()
        html: str = scraper.get(url=current_url).text

        chapter_title, paragraphs = extract_chapter(html)
        chapters.append((chapter_title, paragraphs))
        elapsed = time.monotonic() - t0
        log(f"  {chapter_title} ({len(paragraphs)} paragraphs)")

        if on_chapter_done:
            on_chapter_done(len(chapters), elapsed)

        if max_chapters and len(chapters) >= max_chapters:
            break

        next_url: str | None = get_next_url(html)
        if not next_url:
            break

        if next_url.startswith('/'):
            parsed = urlparse(current_url)
            current_url = f"{parsed.scheme}://{parsed.netloc}{next_url}"
        else:
            current_url = next_url

        if delay > 0:
            time.sleep(delay)

    if not chapters:
        raise RuntimeError("No chapters were fetched.")

    end_ch = start_chapter + len(chapters) - 1
    filename = f"{title} ({start_chapter}-{end_ch}).epub"
    output_path = os.path.join(save_dir, filename)
    build_epub(title=title, author=author, chapters=chapters, filename=output_path, cover=cover)
    log(f"Saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    fetch(
        start_url="https://novelbin.com/b/shadow-slave/chapter-1-nightmare-begins",
        title="Shadow Slave",
        author="Guiltythree",
        end_chapter=10,
    )
