from pydantic import BaseModel, ConfigDict, field_validator
from models.phone import Phone
from models.laptop import Laptop
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.operators import OperatorType, ge, le, eq
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql._typing import ColumnExpressionArgument
from typing import Any, Generic, TypeVar
from .config import BRAND_DEFAULT

_T = TypeVar("_T") # define Type Variable ,  đảm bảo tính nhất quán về data type giữa cột trong db và giá trị so sánh

# use Generic[_T] ensure type safety
class FilterAtrribute(BaseModel, Generic[_T]): # điều kiện lọc đơn lẻ , Generic[_T] ensure type matching
    model_config = ConfigDict(arbitrary_types_allowed=True)

    column: ColumnElement[_T] # column in db to filter , could be any data type
    operator: Any # compare operator (ge,le,eq..)
    value: _T # value to compare , must be same type with column

    @field_validator("operator")
    def validate_operator(cls, v): # validate operator is a callable function
        if not callable(v): # check if operator is callable (function)
            raise ValueError(
                f"Operator {v} is not callable. It must be a valid SQLAlchemy operator like `ge`, `le`, or `eq`."
            )
        return v

    def condition_expression(self) -> ColumnElement[bool]: # create SQL expression statement
        return self.operator(self.column, self.value)

'''
price_filter = FilterAttribute(
    column = Phone.price,
    operator = ge,
    value = 100000
)
print(price_filter.condition_expression())
# Output: phones.price >= 10000000
'''

class FilterCondition(BaseModel):
    filters: list[FilterAtrribute] # list conditions

    # func to combine a filter condition
    def condition_expression(self) -> ColumnElement[bool] | None:
        if not self.filters or len(self.filters) == 0:
            return None

        # combine conditions by AND expression
        condition = self.filters[0].condition_expression()
        for filter in self.filters[1:]:
            condition = and_(condition, filter.condition_expression())
        return condition

'''
# Lọc điện thoại Samsung giá từ 10-20 triệu
filters = FilterCondition(filters=[
    FilterAtrribute(Phone.brand_code, eq, "SAMSUNG"),
    FilterAtrribute(Phone.price, ge, 10000000),
    FilterAtrribute(Phone.price, le, 20000000)
])

print(filters.condition_expression())
# Output: phones.brand_code = 'SAMSUNG' AND phones.price >= 10000000 AND phones.price <= 20000000
'''

class PhoneFilter(BaseModel):
    # Filter phone by brand_code and price range like "Iphone từ 10 đến 20 triệu"
    # WHERE brand_code = 'APPLE' AND price >= 10000000 AND price <= 20000000
    brand_code: str | None = None
    max_price: float | None = None
    min_price: int | None = None

    def condition_expression(self) -> ColumnElement[bool] | None:
        filters = []

        # filter for min_price
        if self.min_price:
            filters.append(
                FilterAtrribute(
                    column=Phone.price.expression,
                    operator=ge,
                    value=self.min_price,
                )
            )
        # filter for max_price
        if self.max_price:
            filters.append(
                FilterAtrribute(
                    column=Phone.price.expression,
                    operator=le,
                    value=self.max_price,  # type: ignore
                )
            )
        # filter for brand_code
        if self.brand_code:
            filters.append(
                FilterAtrribute(
                    column=Phone.brand_code.expression,
                    operator=eq,
                    value=self.brand_code,
                )
            )
        # combine all filter condition
        return FilterCondition(filters=filters).condition_expression()
    
        '''
        # Lọc iPhone giá dưới 15 triệu
        iphone_filter = PhoneFilter(
            brand_code="APPLE",
            max_price=15_000_000
        )

        print(iphone_filter.condition_expression())
        # Output: phones.brand_code = 'APPLE' AND phones.price <= 15000000
        '''

    def __eq__(self, value: object) -> bool: # magic method compare PhoneFilter object with value object by operator '=='
        if not isinstance(value, PhoneFilter):
            return False

        return (
            self.min_price == value.min_price
            and self.max_price == value.max_price
            and self.brand_code == value.brand_code
        )


class LaptopFilter(BaseModel):
    # Filter laptop by brand_code and price range
    # WHERE brand_code = 'DELL' AND price >= 15000000 AND price <= 30000000
    brand_code: str | None = None
    max_price: float | None = None
    min_price: int | None = None

    def condition_expression(self) -> ColumnElement[bool] | None:
        filters = []

        # filter for min_price
        if self.min_price:
            filters.append(
                FilterAtrribute(
                    column=Laptop.price.expression,
                    operator=ge,
                    value=self.min_price,
                )
            )
        # filter for max_price
        if self.max_price:
            filters.append(
                FilterAtrribute(
                    column=Laptop.price.expression,
                    operator=le,
                    value=self.max_price,  # type: ignore
                )
            )
        # filter for brand_code
        if self.brand_code:
            filters.append(
                FilterAtrribute(
                    column=Laptop.brand_code.expression,
                    operator=eq,
                    value=self.brand_code,
                )
            )
        # combine all filter conditions
        return FilterCondition(filters=filters).condition_expression()

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, LaptopFilter):
            return False

        return (
            self.min_price == value.min_price
            and self.max_price == value.max_price
            and self.brand_code == value.brand_code
        )
