from typing import Optional

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, PrimaryKeyConstraint, String
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy.sql.sqltypes import BigInteger
from app.models.base import Base

class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['status_id'], ['status.id'], name='users_status_fk'),
        PrimaryKeyConstraint('id', name='users_pk'),
        Index('idx_users_email', 'email', unique=True),
        Index('idx_users_username', 'username', unique=True)
    )

    id = mapped_column(BigInteger)
    username = mapped_column(String(255), nullable=False)
    email = mapped_column(String(255), nullable=False)
    password_hash = mapped_column(String(255), nullable=False)
    role = mapped_column(String(50), nullable=False)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))

    status: Mapped[Optional['Status']] = relationship('Status', back_populates='users')
