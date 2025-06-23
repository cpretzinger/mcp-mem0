import os
import uuid
from datetime import datetime
from typing import List

DATABASE_URL = os.getenv("DATABASE_URL", "memory")

try:
    from sqlalchemy import create_engine, Column, DateTime, Text, func
    from sqlalchemy.orm import declarative_base, sessionmaker
    from sqlalchemy.dialects.postgresql import UUID
    from pgvector.sqlalchemy import Vector
except Exception:  # pragma: no cover - optional deps
    create_engine = Column = DateTime = Text = func = None
    declarative_base = lambda: None
    sessionmaker = lambda *a, **k: None
    UUID = Vector = None

Base = declarative_base() if declarative_base else None

if Base:
    class MemoryORM(Base):
        __tablename__ = "memories"
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        text = Column(Text, nullable=False)
        embedding = Column(Vector(1536))
        ts = Column(DateTime(timezone=True), server_default=func.now())

engine = None
SessionLocal = None
_mem_store: List[dict] = []


def init_db() -> None:
    global engine, SessionLocal
    if DATABASE_URL == "memory" or not create_engine:
        engine = None
        SessionLocal = None
    else:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        Base.metadata.create_all(engine)


def save_memory(text: str, embedding: List[float]) -> str:
    text = " ".join(text.split())[:8000]
    if DATABASE_URL == "memory" or not SessionLocal:
        mem_id = str(uuid.uuid4())
        _mem_store.append({"id": mem_id, "text": text, "embedding": embedding, "ts": datetime.utcnow()})
        return mem_id
    with SessionLocal() as session:
        mem = MemoryORM(text=text, embedding=embedding)
        session.add(mem)
        session.commit()
        return str(mem.id)


def search_memories(embedding: List[float], limit: int = 5) -> List[str]:
    if DATABASE_URL == "memory" or not SessionLocal:
        def dot(a, b):
            return sum(x*y for x, y in zip(a, b))
        scored = sorted([(dot(m['embedding'], embedding), m['text']) for m in _mem_store], reverse=True)
        return [t for _, t in scored[:limit]]
    with SessionLocal() as session:
        result = (
            session.query(MemoryORM.text)
            .order_by(MemoryORM.embedding.cosine_distance(embedding))
            .limit(limit)
            .all()
        )
        return [r[0] for r in result]


def get_all_memories() -> List[str]:
    if DATABASE_URL == "memory" or not SessionLocal:
        return [m['text'] for m in _mem_store]
    with SessionLocal() as session:
        result = session.query(MemoryORM.text).order_by(MemoryORM.ts).all()
        return [r[0] for r in result]
