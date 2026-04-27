"""Pydantic-схемы для валидации входных данных (Pydantic V2)"""
from pydantic import BaseModel, Field, field_validator


class ReviewCreate(BaseModel):
    """Схема для создания отзыва"""
    product_id: int = Field(..., gt=0, description="ID товара в Django")
    user_id: str = Field(..., min_length=1, max_length=100, description="ID пользователя")
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    comment: str = Field(..., min_length=1, max_length=1000, description="Текст отзыва")

    @field_validator('comment')
    @classmethod
    def validate_comment(cls, v: str) -> str:
        """Защита от пустых значений"""
        if not v or not v.strip():
            raise ValueError('Комментарий не может быть пустым')
        return v.strip()


class ReviewResponse(BaseModel):
    """Схема для ответа с отзывом"""
    id: int
    product_id: int
    user_id: str
    rating: int
    comment: str
    status: str
    created_at: str


class ReviewUpdateStatus(BaseModel):
    """Схема для обновления статуса отзыва (для администратора)"""
    status: str

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ('active', 'hidden', 'pending'):
            raise ValueError('status должен быть: active, hidden или pending')
        return v


class ErrorResponse(BaseModel):
    """Единый формат ошибок"""
    success: bool = False
    error: dict