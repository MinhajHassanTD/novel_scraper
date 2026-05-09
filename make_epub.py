from ebooklib import epub
from html import escape

def build_epub(title: str, author: str, chapters: list[tuple[str, list[str]]], filename: str | None = None, cover: bytes | None = None) -> str:
    book = epub.EpubBook()
    book.set_title(title)
    book.add_author(author)
    book.set_language('en')
    if cover:
        book.set_cover("cover.jpg", cover)

    epub_chapters: list[epub.EpubHtml] = []
    for i, (chapter_title, paragraphs) in enumerate(chapters):
        toc_title = chapter_title
        content = f'<h2>{escape(chapter_title)}</h2>' + ''.join(f'<p>{escape(p)}</p>' for p in paragraphs)
        chap = epub.EpubHtml(title=toc_title, file_name=f'chap_{i+1}.xhtml', lang='en')
        chap.content = content
        book.add_item(chap)
        epub_chapters.append(chap)

    book.toc = tuple(epub.Link(c.file_name, c.title, c.id) for c in epub_chapters)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + epub_chapters

    output = filename or f"{title.replace(' ', '_')}.epub"
    epub.write_epub(output, book)
    return output
