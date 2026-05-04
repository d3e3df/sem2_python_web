"""FastAPI сервис для уведомлений, авторизации и отчётов"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer

from .auth import create_access_token,get_current_user
from .schemas import UserRegister, UserLogin, TokenResponse, UserResponse

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Схема безопасности для JWT
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info(" FastAPI сервис запускается...")
    yield
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
    # TODO: сохранить в БД
    logger.info(f"Регистрация пользователя: {user_data.username}")

    # Временная заглушка
    return UserResponse(
        id=1,
        username=user_data.username,
        email=user_data.email
    )


@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """
    Логин пользователя.
    Возвращает JWT токен.
    """
    # TODO: проверить в БД
    logger.info(f"Логин пользователя: {user_data.username}")

    # Временная заглушка
    if user_data.username == "admin" and user_data.password == "admin":
        access_token = create_access_token(data={"sub": user_data.username})
        return TokenResponse(access_token=access_token)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверное имя пользователя или пароль"
    )


@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Получить информацию о текущем пользователе.
    Требует JWT токен в заголовке Authorization: Bearer <token>
    """
    logger.info(f"Запрос информации о пользователе: {current_user}")
    return {"user": current_user}


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
