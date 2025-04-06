from .base import Base
from datetime import datetime, timezone
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import DateTime, String
from pydantic import BaseModel, ConfigDict
from pgvector.sqlalchemy import Vector

# SQLAlchemy model mapping to database
class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False) #brand_code
    name: Mapped[str] = mapped_column(String, nullable=False) #brand_name
    embedding: Mapped[list[float]] = mapped_column(Vector, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

# Pydantic model for create new entity
class CreateBrandModel(BaseModel):
    id: str
    name: str
    embedding: list[float]

# pydantic model for validate/serialize
class BrandModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    embedding: list[float]
    created_at: datetime
    updated_at: datetime
