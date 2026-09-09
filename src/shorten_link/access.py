from .database import SessionLocal
from .models import AccessLog, Link


def record_access(code: str) -> None:
    """리다이렉트 1회에 대해 hit_count 증가 + 접속 로그 1건 기록."""
    session = SessionLocal()
    try:
        link = session.query(Link).filter_by(code=code).one_or_none()
        if link is None:
            return
        link.hit_count += 1
        session.add(AccessLog(link_id=link.id))
        session.commit()
    finally:
        session.close()
