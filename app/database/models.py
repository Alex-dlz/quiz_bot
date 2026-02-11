from sqlalchemy import BigInteger, String, Text, Integer, ForeignKey, Float
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import DateTime
from datetime import datetime

from app.database.core import Base

class UserProfile(Base):
    __tablename__ = "users"
    
    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(64))
    username: Mapped[str] = mapped_column(String(64), nullable=True)
    # Статистика
    total_games: Mapped[int] = mapped_column(Integer, default=0)
    total_correct: Mapped[int] = mapped_column(Integer, default=0)  
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)    
    exp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="Новичок")
    @property
    async def recalc_status(self):
        if self.exp < 500:
            level = 1
            status = "Новичок"
        elif self.exp < 1500:
            level = 2  
            status = "Ученик"
        elif self.exp < 3000:
            level = 3
            status = "Опытный"
        elif self.exp < 5000:
            level = 4
            status = "Эксперт"
        elif self.exp < 10000:
            level = 5
            status = "Мастер"
        else:
            level = 6
            status = "Гуру"
        return level, status
    @property
    async def recalc_accuracy(self) -> float:
        if self.total_games == 0.0:
            return 0.0
        else:
            accuracy = round(((self.total_correct / (self.total_games * 5)) * 100), 2)
        return accuracy
    # Даты и активность
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

class Topic(Base):
    __tablename__ = "topics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name_topic: Mapped[str] = mapped_column(String(108), unique=True)
    description: Mapped[str] = mapped_column(Text)
    
    questions: Mapped[list["Question"]] = relationship(
        "Question",
        back_populates="topic"  
    )

class Question(Base):
    __tablename__ = "questions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    text_question: Mapped[str] = mapped_column(String(256), nullable=False)
    options: Mapped[str] = mapped_column(Text, nullable=False)
    correct_index: Mapped[int] = mapped_column(Integer) 
    file_id: Mapped[str] = mapped_column(Text, nullable=True)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"))
    
    topic: Mapped["Topic"] = relationship(
        "Topic",
        back_populates="questions"
    )

class Statistics(Base):
    __tablename__ = "statistics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime)  
    total_users: Mapped[int]     
    new_users: Mapped[int]                
    active_users: Mapped[int]                 
    games_played: Mapped[int]