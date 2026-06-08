
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ─── Три новостных источника ───────────────────────────────────────────────
SOURCES = [
    {
        "name": "BBC News",
        "url": "https://feeds.bbci.co.uk/news/rss.xml",
        "type": "rss",
    },
    {
        "name": "Hacker News",
        "url": "https://hnrss.org/frontpage",
        "type": "rss",
    },
    {
    "name": "The Verge",
    "url": "https://www.theverge.com/rss/index.xml",
    "type": "rss",
     },
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


def clean_html(text: str) -> str:
    """Удаляет HTML-теги из строки с помощью BeautifulSoup."""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ").strip()


def parse_date(entry) -> str:
    """Извлекает дату публикации из записи RSS."""
    if hasattr(entry, "published"):
        return entry.published
    if hasattr(entry, "updated"):
        return entry.updated
    return datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")


def scrape_rss(source: dict) -> list:
    """
    Скрапит RSS-ленту и возвращает список словарей с полями:
    title, url, summary, source, published.
    """
    articles = []
    logger.info(f"Скрапинг: {source['name']} ({source['url']})")

    try:
        feed = feedparser.parse(source["url"])
        entries = feed.entries[:30]  # Берём максимум 30 статей

        for entry in entries:
            title = clean_html(getattr(entry, "title", ""))
            url = getattr(entry, "link", "")
            summary = clean_html(
                getattr(entry, "summary", "") or
                getattr(entry, "description", "")
            )
            published = parse_date(entry)

            if title and url:
                articles.append({
                    "title": title,
                    "url": url,
                    "summary": summary[:500],  # Ограничиваем длину
                    "source": source["name"],
                    "published": published,
                })

        logger.info(f"  → Получено {len(articles)} статей")
    except Exception as e:
        logger.error(f"Ошибка при скрапинге {source['name']}: {e}")

    return articles


def scrape_all_sources() -> list:
    """
    Запускает скрапинг всех источников и возвращает
    объединённый список статей.
    """
    all_articles = []

    for source in SOURCES:
        articles = scrape_rss(source)
        all_articles.extend(articles)
        time.sleep(1)  # Задержка между запросами

    logger.info(f"Итого собрано статей: {len(all_articles)}")
    return all_articles


if __name__ == "__main__":
    articles = scrape_all_sources()
    for a in articles[:5]:
        print(f"[{a['source']}] {a['title'][:80]}")
        print(f"  URL: {a['url']}")
        print()
