"""
app.py — Flask-приложение новостного агрегатора NewsFlow.
Маршруты: главная, поиск, фильтр по категориям, REST API, ручное обновление.
"""

import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for

from database import init_db, get_articles, get_categories, count_articles
from scheduler import create_scheduler, fetch_and_save

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ─── Запуск базы и планировщика ───────────────────────────────────────────
init_db()
scheduler = create_scheduler()
scheduler.start()
logger.info("APScheduler запущен — обновление каждый час")


# ─── Маршруты ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Главная страница — список новостей с поиском и фильтром."""
    keyword  = request.args.get("q", "").strip()
    category = request.args.get("category", "all").strip()

    articles   = get_articles(category=category, keyword=keyword, limit=60)
    categories = get_categories()
    total      = count_articles()

    return render_template(
        "index.html",
        articles=articles,
        categories=categories,
        current_category=category,
        keyword=keyword,
        total=total,
    )


@app.route("/refresh", methods=["POST"])
def refresh():
    """Ручной запуск скрапинга через кнопку на странице."""
    result = fetch_and_save()
    logger.info(f"Ручное обновление: {result}")
    return redirect(url_for("index"))


@app.route("/api/articles")
def api_articles():
    """
    REST API endpoint.
    GET /api/articles?category=технологии&q=AI&limit=20
    """
    keyword  = request.args.get("q", "").strip()
    category = request.args.get("category", "all").strip()
    limit    = min(int(request.args.get("limit", 20)), 100)

    articles = get_articles(category=category, keyword=keyword, limit=limit)
    return jsonify({
        "count": len(articles),
        "articles": articles,
    })


@app.route("/api/stats")
def api_stats():
    """REST API — статистика базы данных."""
    categories = get_categories()
    total      = count_articles()
    return jsonify({
        "total_articles": total,
        "categories": categories,
        "sources": ["BBC News", "Hacker News", "Reuters"],
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
