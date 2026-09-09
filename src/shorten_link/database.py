import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

DB_URL = os.environ.get("SHORTEN_LINK_DB_URL", "sqlite:///shorten_link.db")

engine = create_engine(DB_URL, future=True, connect_args={"check_same_thread": False})
SessionLocal = scoped_session(sessionmaker(bind=engine, future=True, expire_on_commit=False))

Base = declarative_base()


def init_db() -> None:
    from . import models  # noqa: F401  (모델 등록을 위한 임포트)

    Base.metadata.create_all(engine)
