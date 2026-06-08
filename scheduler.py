"""
scheduler.py — APScheduler для автоматического обновления новостей.
Запускает скрапинг каждый час и сохраняет результаты в SQLite.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from scraper import scrape_all_sources
from classifier import load_model, predict_category
from database import insert_article, init_db

logger = logging.getLogger(__name__)

_model = None  # Кэшируем модель, чтобы не загружать при каждом запуске


def fetch_and_save() -> dict:
    """
    Основная функция планировщика:
    1. Скрапит новости из всех источников
    2. Классифицирует каждую статью
    3. Сохраняет новые статьи в SQLite (дубликаты пропускаются)
    Возвращает статистику: новые / дубликаты.
    """
    global _model

    if _model is None:
        _model = load_model()

    logger.info("Запуск сбора новостей...")
    articles = scrape_all_sources()

    new_count = 0
    dup_count = 0

    for article in articles:
        combined_text = f"{article['title']} {article['summary']}"
        category = predict_category(combined_text, _model)
        logger.info(f"[{category}] {article['title'][:60]}")

        inserted = insert_article(
            title=article["title"],
            url=article["url"],
            summary=article["summary"],
            source=article["source"],
            category=category,
            published=article["published"],
        )

        if inserted:
            new_count += 1
        else:
            dup_count += 1

    logger.info(f"Готово: +{new_count} новых, {dup_count} дубликатов пропущено")
    return {"new": new_count, "duplicates": dup_count}


def create_scheduler() -> BackgroundScheduler:
    """
    Создаёт и возвращает настроенный BackgroundScheduler.
    Задание выполняется каждый час.
    """
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        func=fetch_and_save,
        trigger=IntervalTrigger(hours=1),
        id="hourly_scrape",
        name="Hourly news scrape",
        replace_existing=True,
    )
    return scheduler


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    init_db()
    result = fetch_and_save()
    print(f"Результат: {result}")
