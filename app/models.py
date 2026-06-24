from sqlalchemy import Column, BigInteger, Text, Numeric, TIMESTAMP, func, Index
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_products_cursor", created_at.desc(), id.desc()),
        Index("idx_products_category_cursor", "category", created_at.desc(), id.desc()),
        Index("idx_products_created_at", "created_at"),
    )
