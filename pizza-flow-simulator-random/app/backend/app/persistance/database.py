import os
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import Session
from contextlib import contextmanager


db_url = os.getenv("DATABASE_URL") or f'postgresql://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}/{os.getenv("DB_NAME")}'
engine = create_engine(db_url, connect_args={})

@contextmanager
def get_db():
    with Session(engine) as session:
        yield session
