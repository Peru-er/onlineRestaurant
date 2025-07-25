from sqlalchemy import create_engine, String, Float, Integer, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

import bcrypt


engine = create_engine(f"postgresql+psycopg2://postgres:Nikami10@localhost:5432/cinnamon_chapters", echo=True)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    def create_db(self):
        Base.metadata.create_all(engine)

    def drop_db(self):
        Base.metadata.drop_all(engine)

class Users(Base, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(50), unique=True)

    reservations = relationship("Reservation", foreign_keys="Reservation.user_id", back_populates="user")
    orders = relationship("Orders", foreign_keys="Orders.user_id", back_populates='user')

    def set_password(self, password: str):
        self.password = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(self.password, password)


class Menu(Base):
    __tablename__ = "menu"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    weight: Mapped[float] = mapped_column(Float)
    ingredients: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[float] = mapped_column(Float)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    file_name: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)

class Reservation(Base):
    __tablename__ = "reservation"
    id: Mapped[int] = mapped_column(primary_key=True)
    time_start: Mapped[datetime] = mapped_column(DateTime)
    type_table: Mapped[str] = mapped_column(String(20))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user = relationship("Users", foreign_keys="Reservation.user_id", back_populates="reservations")

class Orders(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_list: Mapped[dict] = mapped_column(JSONB)
    order_time: Mapped[datetime] = mapped_column(DateTime)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    user = relationship("Users", foreign_keys="Orders.user_id", back_populates="orders")


base = Base()
base.create_db()
