import os
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base


@pytest.fixture()
def temp_db():

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    engine = create_engine(
        f"sqlite:///{path}",
        connect_args={"check_same_thread": False},
    )

    TestingSession = sessionmaker(bind=engine)

    Base.metadata.create_all(bind=engine)

    yield TestingSession

    Base.metadata.drop_all(bind=engine)

    # THIS IS THE IMPORTANT PART
    engine.dispose()

    os.remove(path)