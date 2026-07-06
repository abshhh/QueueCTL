from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)

    command = Column(Text, nullable=False)

    state = Column(
        String,
        nullable=False,
        default="pending",
        index=True,
    )

    attempts = Column(
        Integer,
        nullable=False,
        default=0,
    )

    max_retries = Column(
        Integer,
        nullable=False,
        default=3,
    )

    priority = Column(
        Integer,
        nullable=False,
        default=0,
        index=True,
    )

    next_run_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    locked_by = Column(
        String,
        nullable=True,
    )

    output = Column(
        Text,
        nullable=True,
    )

    error = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )   