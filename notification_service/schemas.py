"""Pydantic схемы для запросов и ответов"""
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """Регистрация пользователя"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    """Логин пользователя"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Ответ с токеном"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Ответ с данными пользователя"""
    id: int
    username: str
    email: str


class NotificationRequest(BaseModel):
    """Запрос на отправку уведомления"""
    user_id: str
    message: str = Field(..., min_length=1, max_length=500)


class NotificationResponse(BaseModel):
    """Ответ об отправке уведомления"""
    task_id: str
    status: str