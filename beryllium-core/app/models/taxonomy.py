from typing import Optional, List

from psycopg2.extensions import JSONB
from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Index, String, Text, BigInteger, DateTime, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models.base import Base


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        ForeignKeyConstraint(['status_id'], ['status.id'], name='categories_status_fk'),
        PrimaryKeyConstraint('id', name='categories_pk'),
        Index('idx_categories_name', 'name'),
        UniqueConstraint(name='uq_categories_name', columns=['name'])

    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    description = mapped_column(Text)
    meta_data = mapped_column(JSONB)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    status: Mapped[Optional['Status']] = relationship('Status', back_populates='categories')
    content: Mapped[List['Content']] = relationship('Content', uselist=True, back_populates='category')
    folders: Mapped[List['Folders']] = relationship('Folders', uselist=True, back_populates='category')



class Tags(Base):
    __tablename__ = 'tags'
    __table_args__ = (
        ForeignKeyConstraint(['status_id'], ['status.id'], name='tags_status_fk'),
        PrimaryKeyConstraint('id', name='tags_pk'),
        Index('idx_tags_name', 'name'),
        UniqueConstraint(name='uq_tags_name', columns=['name'])
    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    status: Mapped[Optional['Status']] = relationship('Status', back_populates='tags')
    content_tags: Mapped[List['ContentTags']] = relationship('ContentTags', uselist=True, back_populates='tag')
    media_tags: Mapped[List['MediaTags']] = relationship('MediaTags', uselist=True, back_populates='tag')


class ContentTags(Base):
    __tablename__ = 'content_tags'
    __table_args__ = (
        ForeignKeyConstraint(['content_id'], ['content.id'], name='content_tags_content_fk'),
        ForeignKeyConstraint(['tag_id'], ['tags.id'], name='content_tags_tag_fk'),
        PrimaryKeyConstraint('id', name='content_tags_pk')
    )

    id = mapped_column(BigInteger)
    content_id = mapped_column(BigInteger)
    tag_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    content: Mapped[Optional['Content']] = relationship('Content', back_populates='content_tags')
    tag: Mapped[Optional['Tags']] = relationship('Tags', back_populates='content_tags')


class MediaTags(Base):
    __tablename__ = 'media_tags'
    __table_args__ = (
        ForeignKeyConstraint(['media_variant_id'], ['media_variant.id'], name='media_tags_media_variant_fk'),
        ForeignKeyConstraint(['tag_id'], ['tags.id'], name='media_tags_tags_fk'),
        PrimaryKeyConstraint('id', name='media_tags_pk')
    )

    id = mapped_column(BigInteger)
    media_variant_id = mapped_column(BigInteger)
    tag_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(255))
    updated_by = mapped_column(String(255))

    media_variant: Mapped[Optional['MediaVariant']] = relationship('MediaVariant', back_populates='media_tags')
    tag: Mapped[Optional['Tags']] = relationship('Tags', back_populates='media_tags')
