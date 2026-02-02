import random

from sqlalchemy import Column, Integer, DateTime, Boolean, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timezone, timedelta

Base = declarative_base()
engine = create_engine('sqlite:///users.db', echo=False)
SessionLocal = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    tg_id = Column(Integer, unique=True, nullable=False)
    join_date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    scheduled_time = Column(DateTime)
    sent_delayed = Column(Boolean, default=False)
    utm_mark = Column(String(100), nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def add_user_with_schedule(tg_id: int, utm_mark: str):
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.tg_id == tg_id).first()

        if not user:
            now = datetime.now(timezone.utc)
            tomorrow = now + timedelta(days=1)
            scheduled = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
            random_delay = random.randint(0, 180)
            final_time = scheduled + timedelta(minutes=random_delay)

            new_user = User(
                tg_id=tg_id,
                scheduled_time=final_time,
                utm_mark=utm_mark
            )
            session.add(new_user)
            session.commit()
    finally:
        session.close()


