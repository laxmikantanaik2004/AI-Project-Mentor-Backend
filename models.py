from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Project(Base):
    __tablename__ = "projects"

    project_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    technology_stack: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )
