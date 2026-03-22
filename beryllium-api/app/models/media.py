from typing import List, Optional

from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint, BigInteger, String, Text, DateTime, Double, Index, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.models.base import Base


class MimeTypes(Base):
    __tablename__ = 'mime_types'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='mime_types_pk'),
        Index('idx_mime_types_name', 'name'),
        {'schema': 'main'}
    )

    id = mapped_column(String(50))
    name = mapped_column(String(255))
    description = mapped_column(Text)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(255))
    updated_by = mapped_column(String(255))

    media: Mapped[List['Media']] = relationship('Media', uselist=True, back_populates='mime_type_')





class MediaTypes(Base):
    __tablename__ = 'media_types'
    __table_args__ = (
        ForeignKeyConstraint(['status_id'], ['status.id'], name='media_types_status_fk'),
        PrimaryKeyConstraint('id', name='media_types_pk'),
        Index('idx_media_types_name', 'name'),
        {'schema': 'main'}
    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    description = mapped_column(Text)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    status: Mapped[Optional['Status']] = relationship('Status', back_populates='media_types')
    media: Mapped[List['Media']] = relationship('Media', uselist=True, back_populates='media_type')



class Media(Base):
    __tablename__ = 'media'
    __table_args__ = (
        ForeignKeyConstraint(['media_type_id'], ['media_types.id'], name='media_media_type_fk'),
        ForeignKeyConstraint(['mime_type_id'], ['mime_types.id'], name='media_mime_type_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='media_status_fk'),
        PrimaryKeyConstraint('id', name='media_pk'),
        Index('idx_media_name', 'name'),
        {'schema': 'main'}

    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    description = mapped_column(Text)
    media_type_id = mapped_column(BigInteger)
    mime_type_id = mapped_column(String(50))
    original_filename = mapped_column(String(255))
    stored_filename = mapped_column(String(255))
    extension = mapped_column(String(255))
    size_bytes = mapped_column(Integer)
    object_key = mapped_column(String(255))
    checksum_sha256 = mapped_column(String(255))
    url = mapped_column(String(255))
    status_id = mapped_column(Integer)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    media_type: Mapped[Optional['MediaTypes']] = relationship('MediaTypes', back_populates='media')
    mime_type_: Mapped[Optional['MimeTypes']] = relationship('MimeTypes', back_populates='media')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='media')
    media_variant: Mapped[List['MediaVariant']] = relationship('MediaVariant', uselist=True, back_populates='media')


class MediaVariant(Base):
    __tablename__ = 'media_variant'
    __table_args__ = (
        ForeignKeyConstraint(['media_id'], ['media.id'], name='media_variant_media_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='media_variant_status_fk'),
        PrimaryKeyConstraint('id', name='media_variant_pk'),
        {'schema': 'main'}
    )

    id = mapped_column(BigInteger)
    media_id = mapped_column(BigInteger, nullable=False)
    filename = mapped_column(String(255))
    variant_type = mapped_column(String(50))
    mime_type_id = mapped_column(String(50))
    bucket = mapped_column(String(255))
    object_key = mapped_column(String(255))
    aspect_ratio = mapped_column(Double(53))
    width = mapped_column(Integer)
    height = mapped_column(Integer)
    checksum_sha256 = mapped_column(String(255))
    url = mapped_column(String(255))
    status_id = mapped_column(Integer)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    media: Mapped['Media'] = relationship('Media', back_populates='media_variant')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='media_variant')
    media_tags: Mapped[List['MediaTags']] = relationship('MediaTags', uselist=True, back_populates='media_variant')