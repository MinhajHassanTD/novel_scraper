# Novel Scraper

A Python desktop app that scrapes novels from novelbin.com and saves them as EPUB files, complete with a chapter table of contents and optional cover art.

## Features

- Dark charcoal + amber GUI built with tkinter
- Scrapes chapters sequentially with configurable start/end range
- Auto-fills title, author, and cover art from the novel's info page
- Live progress log with ETA and average time per chapter
- Cancel mid-scrape — partial EPUB is saved automatically
- Configurable request delay to avoid rate limiting
- Opens the EPUB in your default reader when done

## Usage

```bash
python gui.py
```

Enter the first chapter URL, click **Auto-fill** to populate the title and author, set your chapter range, and click **Start Scraping**.

The EPUB is saved as `Novel Title (start-end).epub` in the chosen directory.

## Requirements

```
beautifulsoup4
cloudscraper
ebooklib
```
