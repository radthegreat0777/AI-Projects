from datetime import datetime

from sqlalchemy import String, func, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): #DRY - Dont Repeat yourself
    pass

class User(Base):

    __tablename__ = 'users'

    id : Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)


class Invoice(Base):

    __tablename__ = 'invoices'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(nullable=False)

    amount: Mapped[float]

    description: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at : Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=datetime.now()
    )

class PendingRequest(Base):
    __tablename__ = "pending_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    query: Mapped[str] = mapped_column(String(1000))
    sql: Mapped[str] = mapped_column(Text())
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at : Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=datetime.now()
    )

