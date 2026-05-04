"""FastAPI сервис для уведомлений, авторизации и отчётов"""
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import asyncpg
import asyncio

from .auth import (
    create_access_token, get_password_hash, verify_password,
    get_current_user, decode_token
)

from .schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    NotificationRequest, NotificationResponse
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Схема безопасности для JWT
security = HTTPBearer()

db_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global db_pool
    logger.info("FastAPI сервис запускается...")

    # Подключаемся к PostgreSQL
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="shop_user",
        password="python",
        database="shop_db",
        min_size=1,
        max_size=10
    )

    async with db_pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logger.info("Таблица users готова")

    yield

    await db_pool.close()
    logger.info("FastAPI сервис останавливается...")


# Создаём приложение
app = FastAPI(
    title="Notification & Auth Service",
    description="Сервис для авторизации (JWT), уведомлений и отчётов",
    version="1.0.0",
    lifespan=lifespan
)


# Health Check
@app.get("/health")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {"status": "ok", "service": "notification_service"}


# Auth эндпоинты
@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """
    Регистрация нового пользователя.
    Возвращает данные пользователя.
    """
    global db_pool

    async with db_pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE username = $1 OR email = $2",
            user_data.username, user_data.email
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем или email уже существует"
            )

        password_hash = get_password_hash(user_data.password)
        user_id = await conn.fetchval(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            user_data.username, user_data.email, password_hash
        )

    logger.info(f"Зарегистрирован новый пользователь: {user_data.username} (id={user_id})")

    return UserResponse(
        id=user_id,
        username=user_data.username,
        email=user_data.email
    )


@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """
    Логин пользователя.
    Возвращает JWT токен.
    """
    global db_pool

    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, username, password_hash FROM users WHERE username = $1",
            user_data.username
        )
        if not user or not verify_password(user_data.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль"
            )

        user_id = user['id']
        username = user['username']

    access_token = create_access_token(data={"sub": str(user_id), "username": username})
    logger.info(f"Пользователь {username} (id={user_id}) вошёл в систему")

    return TokenResponse(access_token=access_token)


@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Получить информацию о текущем пользователе.
    Требует JWT токен в заголовке Authorization: Bearer <token>
    """
    global db_pool

    user_id = int(current_user['user_id'])

    async with db_pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, username, email, created_at FROM users WHERE id = $1",
            user_id
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

    return {
        "id": user['id'],
        "username": user['username'],
        "email": user['email'],
        "created_at": str(user['created_at'])
    }


async def send_notification_email(user_id: str, message: str):
    """
    Фоновая задача: отправка уведомления.
    """
    logger.info(f"[Фоновая задача] Отправка уведомления пользователю {user_id}")
    logger.info(f"Сообщение: {message}")

    # Имитируем отправку email
    await asyncio.sleep(2)

    logger.info(f"[Фоновая задача] Уведомление для {user_id} успешно отправлено")


@app.post("/notify", response_model=NotificationResponse)
async def send_notification(
        request: NotificationRequest,
        background_tasks: BackgroundTasks,
        current_user: dict = Depends(get_current_user)
):
    """
    Отправить уведомление пользователю.
    Требует JWT токен.
    Уведомление отправляется в фоне.
    """
    background_tasks.add_task(
        send_notification_email,
        request.user_id,
        request.message
    )

    logger.info(f"Пользователь {current_user['username']} запросил уведомление для {request.user_id}")

    return NotificationResponse(
        task_id=f"notify_{request.user_id}_{datetime.now().timestamp()}",
        status="accepted"
    )


@app.get("/reports/orders")
async def get_orders_report(
        current_user: dict = Depends(get_current_user),
        days: int = 7
):
    """
    Асинхронный отчёт по заказам за последние N дней.
    Требует JWT токен.
    """
    logger.info(f"📊 Пользователь {current_user['username']} запросил отчёт за {days} дней")

    # TODO: запрос к Django API или к БД
    return {
        "success": True,
        "user": current_user['username'],
        "period_days": days,
        "report": {
            "total_orders": 42,
            "total_revenue": 250000,
            "average_order_value": 5952,
            "generated_at": datetime.now().isoformat()
        }
    }


@app.post("/auth/verify")
async def verify_token(token_data: dict):
    """
    Эндпоинт для проверки JWT токена другими сервисами (Django, Flask).
    Принимает {"token": "..."}
    """
    token = token_data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token required")

    try:
        payload = decode_token(token)
        return {
            "valid": True,
            "user_id": payload.get("sub"),
            "username": payload.get("username")
        }
    except HTTPException:
        return {"valid": False}


# Обработка ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Единый формат ошибок"""
    return {
        "success": False,
        "error": {
            "code": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    }
