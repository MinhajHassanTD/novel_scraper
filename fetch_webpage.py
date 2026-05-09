import re
import time
import threading
import cloudscraper
from cloudscraper import CloudScraper
from urllib.parse import urlparse
from typing import Callable
from bs4 import BeautifulSoup
import os
import socket
from get_text import extract_chapter
from get_next import get_next_url
from make_epub import build_epub

_MAX_RETRIES = 3
_RETRY_BACKOFF = 2.0  # seconds, doubles each attempt


def _get_with_retry(scraper: CloudScraper, url: str, log: Callable[[str], None]) -> str:
    last_exc: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            resp = scraper.get(url=url, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            last_exc = exc
            is_dns = isinstance(exc.__cause__, socket.gaierror) or "NameResolutionError" in type(exc).__name__ or "getaddrinfo" in str(exc)
            if is_dns:
                log(f"  DNS error — cannot reach {urlparse(url).netloc}. Check your internet connection.")
                raise
            if attempt < _MAX_RETRIES:
                wait = _RETRY_BACKOFF * (2 ** (attempt - 1))
                log(f"  Request failed (attempt {attempt}/{_MAX_RETRIES}), retrying in {wait:.0f}s…")
                time.sleep(wait)
    raise RuntimeError(f"Failed after {_MAX_RETRIES} attempts: {last_exc}") from last_exc


def _meta(soup: BeautifulSoup, prop: str) -> str:
    tag = soup.find("meta", property=prop)
    return tag["content"].strip() if tag and tag.get("content") else ""  # type: ignore[index]


def _book_url(chapter_url: str) -> str:
    parsed = urlparse(chapter_url)
    base_path = parsed.path.rstrip("/").rsplit("/", 1)[0]
    return f"{parsed.scheme}://{parsed.netloc}{base_path}"


def _chapter_count(soup: BeautifulSoup) -> int | None:
    # Extract chapter number from the latest-chapter meta URL (most reliable)
    for prop in ("og:novel:latest_chapter_link", "og:novel:latest_chapter_url"):
        url = _meta(soup, prop)
        if url:
            m = re.search(r"/chapter-(\d+)", url)
            if m:
                return int(m.group(1))

    # Fall back to DOM selectors
    for sel in (".chapter-count", ".total-chapter", "[class*='chapter-count']", "[class*='total-chapter']"):
        tag = soup.select_one(sel)
        if tag:
            m = re.search(r"\d+", tag.get_text())
            if m:
                return int(m.group())

    m = re.search(r"(\d+)\s+[Cc]hapters?", soup.get_text())
    return int(m.group(1)) if m else None


def fetch_metadata(chapter_url: str, scraper: CloudScraper) -> tuple[str, str, bytes | None]:
    base_url = _book_url(chapter_url)
    soup = BeautifulSoup(_get_with_retry(scraper, base_url, print), "html.parser")

    title  = _meta(soup, "og:novel:novel_name") or _meta(soup, "og:title")
    author = _meta(soup, "og:novel:author")
    cover_url = _meta(soup, "og:image")

    cover_bytes: bytes | None = None
    if cover_url:
        try:
            resp = scraper.get(cover_url, timeout=30)
            resp.raise_for_status()
            cover_bytes = resp.content
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

    try:
        book_soup = BeautifulSoup(_get_with_retry(scraper, _book_url(start_url), log), "html.parser")
        total = _chapter_count(book_soup)
        log(f"Total chapters available: {total}" if total else "Total chapters: unknown")
    except Exception:
        log("Total chapters: unknown")

    current_url = start_url
    chapters: list[tuple[str, list[str]]] = []

    while True:
        if cancel_event and cancel_event.is_set():
            log("Cancelled.")
            break

        chapter_num = start_chapter + len(chapters)
        log(f"Fetching chapter {chapter_num}...")
        t0 = time.monotonic()
        try:
            html: str = _get_with_retry(scraper, current_url, log)
        except Exception as exc:
            log(f"  Failed to fetch chapter {chapter_num}: {exc}")
            break

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
