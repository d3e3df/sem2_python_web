"""Модели данных для UGC-сервиса"""
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'dbname': 'shop_db',
    'user': 'shop_user',
    'password': 'python',
    'host': 'localhost',
    'port': '5432'
}


def get_db():
    """Получить соединение с базой данных"""
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    return conn


def init_db():
    """Инициализация базы данных (создание таблиц)"""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    id SERIAL PRIMARY KEY,
                    product_id INTEGER NOT NULL,
                    user_id VARCHAR(100) NOT NULL,
                    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                    comment TEXT NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_reviews_product_id 
                ON reviews(product_id)
            ''')
            cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_reviews_status 
                ON reviews(status)
            ''')
        conn.commit()


init_db()