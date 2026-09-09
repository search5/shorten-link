from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # id를 base62로 인코딩한 뒤 채워지므로, insert 시점(flush)에는 잠시 비어 있다.
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=True, index=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    hit_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    accesses: Mapped[list["AccessLog"]] = relationship(
        back_populates="link", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "url": self.url,
            "created_at": self.created_at.isoformat(),
            "hit_count": self.hit_count,
        }


class AccessLog(Base):
    __tablename__ = "access_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    link_id: Mapped[int] = mapped_column(ForeignKey("links.id"), nullable=False)
    accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)

    link: Mapped["Link"] = relationship(back_populates="accesses")
