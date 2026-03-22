from enum import Enum
from typing import List

from sqlalchemy import PrimaryKeyConstraint, Index, String, Text, BigInteger, DateTime, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.models.base import Base




class StatusEnum(Enum):
    DRAFT = 1
    IN_REVIEW = 2
    PUBLISHED = 3
    ARCHIVED = 4
    BLOCKED = 5


class Status(Base):
    __tablename__ = 'status'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='status_pkey'),
        Index('idx_status_name', 'name', unique=True),
        {'schema': 'main'}
    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    description = mapped_column(Text)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    categories: Mapped[List['Categories']] = relationship('Categories', uselist=True, back_populates='status')
    cms_nodes: Mapped[List['CmsNodes']] = relationship('CmsNodes', uselist=True, back_populates='status')
    content_definitions: Mapped[List['ContentDefinitions']] = relationship('ContentDefinitions', uselist=True, back_populates='status')
    content_groups: Mapped[List['ContentGroups']] = relationship('ContentGroups', uselist=True, back_populates='status')
    content_types: Mapped[List['ContentTypes']] = relationship('ContentTypes', uselist=True, back_populates='status')
    data_fields: Mapped[List['DataFields']] = relationship('DataFields', uselist=True, back_populates='status')
    data_types: Mapped[List['DataTypes']] = relationship('DataTypes', uselist=True, back_populates='status')
    media_types: Mapped[List['MediaTypes']] = relationship('MediaTypes', uselist=True, back_populates='status')
    tags: Mapped[List['Tags']] = relationship('Tags', uselist=True, back_populates='status')
    users: Mapped[List['Users']] = relationship('Users', uselist=True, back_populates='status')
    allowed_children: Mapped[List['AllowedChildren']] = relationship('AllowedChildren', uselist=True, back_populates='status')
    content: Mapped[List['Content']] = relationship('Content', uselist=True, back_populates='status')
    content_elements: Mapped[List['ContentElements']] = relationship('ContentElements', uselist=True, back_populates='status')
    folder_allowed_children: Mapped[List['FolderAllowedChildren']] = relationship('FolderAllowedChildren', uselist=True, back_populates='status')
    folders: Mapped[List['Folders']] = relationship('Folders', uselist=True, back_populates='status')
    media: Mapped[List['Media']] = relationship('Media', uselist=True, back_populates='status')
    content_element_groups: Mapped[List['ContentElementGroups']] = relationship('ContentElementGroups', uselist=True, back_populates='status')
    media_variant: Mapped[List['MediaVariant']] = relationship('MediaVariant', uselist=True, back_populates='status')
    content_definition_items: Mapped[List['ContentDefinitionItems']] = relationship('ContentDefinitionItems', uselist=True, back_populates='status')
