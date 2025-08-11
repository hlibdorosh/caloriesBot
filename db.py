from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date
from sqlalchemy import UniqueConstraint

engine = create_engine("sqlite:///bot.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Parameters(Base):
    __tablename__ = "parameters"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    sex = Column(String)
    height = Column(Integer)
    weight = Column(Integer)
    age = Column(Integer)
    goal = Column(String)
    daily_calories = Column(Integer)
    consumed_today = Column(Integer, default=0)
    last_meal_date = Column(Date)  # ← добавили



class Intake(Base):
    __tablename__ = "intake"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, index=True)
    date = Column(Date, default=date.today)
    total_calories = Column(Integer, default=0)



# 🔹 Новая таблица суточной статистики
class DailyLog(Base):
    __tablename__ = "daily_log"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, index=True, nullable=False)     # связь по пользователю
    date = Column(Date, nullable=False, default=date.today)       # день
    advised_calories = Column(Integer, nullable=False, default=0) # рекомендовано на день
    consumed_calories = Column(Integer, nullable=False, default=0)# съедено за день



    # один лог на пользователя в день
    __table_args__ = (
        UniqueConstraint("telegram_id", "date", name="uq_user_day"),
    )





def init_db():
    Base.metadata.create_all(bind=engine)
