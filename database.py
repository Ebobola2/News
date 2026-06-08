"""
database.py — Модуль работы с SQLite базой данных.
Создаёт таблицы, вставляет и возвращает статьи.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "news.db")


def get_connection() -> sqlite3.Connection:
    """Возвращает соединение с базой данных SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Создаёт таблицу articles, если она ещё не существует."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT    NOT NULL,
            url       TEXT    NOT NULL UNIQUE,
            summary   TEXT,
            source    TEXT,
            category  TEXT    DEFAULT 'general',
            published TEXT,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def insert_article(title: str, url: str, summary: str,
                   source: str, category: str, published: str) -> bool:
    """
    Вставляет статью в базу данных.
    Возвращает True при успешной вставке, False при дублировании.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO articles (title, url, summary, source, category, published)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, url, summary, source, category, published))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Дубликат по UNIQUE url
    finally:
        conn.close()


def get_articles(category: str = None, keyword: str = None,
                 limit: int = 50) -> list:
    """
    Возвращает список статей с фильтрацией по категории и ключевому слову.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM articles WHERE 1=1"
    params = []

    if category and category != "all":
        query += " AND category = ?"
        params.append(category)

    if keyword:
        query += " AND (title LIKE ? OR summary LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    query += " ORDER BY scraped_at DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_categories() -> list:
    """Возвращает список всех уникальных категорий из базы."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM articles ORDER BY category")
    rows = cursor.fetchall()
    conn.close()
    return [row["category"] for row in rows]


def count_articles() -> int:
    """Возвращает общее количество статей в базе."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM articles")
    row = cursor.fetchone()
    conn.close()
    return row["cnt"]
