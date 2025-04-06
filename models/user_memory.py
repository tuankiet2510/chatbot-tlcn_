from enum import Enum
import uuid
from pydantic import BaseModel, ConfigDict
from .base import Base
from datetime import datetime, timezone
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Float, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID


class UserDemand(str, Enum): # Kế thừa từ str và Enum, tạo ra 1 enum mà các giá trị vừa là chuỗi vừa là enum, ensure các giá trị trong enum là cố định không thay đổi
    MOBILE_PHONE = "mobile phone"
    LAPTOP = "laptop" # Thêm một giá trị mới vào enum
    ANOTHER_PRODUCT = "another product"


class PriceRequirement(BaseModel): #pydantic model để validate input data cho khoảng giá
    # properties
    min_price: int | None = None
    max_price: int | None = None

    # constructor
    def __init__(
        self,
        approximate_price: int | None,
        min_price: int | None,
        max_price: int | None,
        diff: int = 500000,
    ):
        # Khi ghi đè __init__ method trong subclass Pydantic model, cần gọi __init__ của BaseModel để đảm bảo các thuộc tính được khởi tạo đúng cách
        #Nếu không gọi, các cơ chế của BaseModel như validate data hoặc thiết lập thuộc tính sẽ bị bỏ qua, có thể dẫn đến lỗi hoặc hành vi không mong muốn.
        BaseModel.__init__(self) # ensure any logic defined in BaseModel __init__ is executed when creating an instance of PriceRequirement, duy trì tính toàn vẹn của lớp cha khi ghi đè __init__ method trong lớp con
        # super().__init__() # tự động xác định lớp cha trực tiếp của lớp hiện tại, không cần chỉ định tên lớp cha cụ thể (như BaseModel).
        if approximate_price: # tạo khoảng giá xung quanh giá ước lượng
            self.min_price = approximate_price - diff
            self.max_price = approximate_price + diff
        else: # dùng khoảng giá được chỉ định
            self.min_price = min_price
            self.max_price = max_price

# lưu trữ context của conversation
class UserMemory(Base):
    __tablename__ = "user_memory"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), # SQLAlchemy tự động chuyển đổi UUID value từ cơ sở dữ liệu thành 1 uuid.UUID object , nếu as_uuid=False sẽ chuyển thành 1 chuỗi.
        primary_key=True, 
        nullable=False, 
        default=uuid.uuid4 # tự động tạo id mới dạng UUID like 123e4567-e89b-12d3-a456-426614174000
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    thread_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_demand: Mapped[UserDemand | None] = mapped_column(Text, nullable=True)
    product_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_type: Mapped[str | None] = mapped_column(Text, nullable=True) # Laptop, Mobile phone, etc
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )


class CreateUserMemoryModel(BaseModel):
    user_id: uuid.UUID
    thread_id: uuid.UUID


class UserMemoryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    thread_id: uuid.UUID
    user_demand: UserDemand | None
    product_name: str | None
    brand: str | None
    min_price: int | None
    max_price: float | None
    phone_number: str | None
    email: str | None
    created_at: datetime
    updated_at: datetime
    product_type: str | None

    def has_contact_info(self) -> bool:
        return self.phone_number is not None
        # return self.phone_number is not None or self.email is not None
