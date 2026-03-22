from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, Double, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Text, text, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy_utils import LtreeType

Base = declarative_base()


class CmsNodes(Base):
    __tablename__ = 'cms_nodes'
    __table_args__ = (
        ForeignKeyConstraint(['parent_id'], ['cms_nodes.id'], name='cms_nodes_parent_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='cms_nodes_status_fk'),
        PrimaryKeyConstraint('id', name='cms_nodes_pk'),
        Index('idx_cms_nodes_path', 'path'),
        Index('idx_cms_nodes_sort_order', 'sort_order'),
        Index('idx_cms_nodes_type', 'cms_node_type')
    )

    id = mapped_column(BigInteger)
    parent_id = mapped_column(BigInteger)
    cms_node_type = mapped_column(String(20))
    path = mapped_column(LtreeType)
    sort_order = mapped_column(Integer)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    parent: Mapped[Optional['CmsNodes']] = relationship('CmsNodes', remote_side=[id], back_populates='children')
    children: Mapped[List['CmsNodes']] = relationship('CmsNodes', uselist=True, remote_side=[parent_id], back_populates='parent')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='cms_nodes')

    content: Mapped[List['Content']] = relationship('Content', uselist=True, back_populates='cms_node')
    folders: Mapped[List['Folders']] = relationship('Folders', uselist=True, back_populates='cms_node')


class ContentDefinitions(Base):
    __tablename__ = 'content_definitions'
    __table_args__ = (
        ForeignKeyConstraint(['status_id'], ['status.id'], name='content_definitions_status_fk'),
        PrimaryKeyConstraint('id', name='content_definitions_pk'),
        Index('idx_content_definitions_name', 'name'),
        Index('idx_content_definitions_sort_order', 'sort_order')
    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    description = mapped_column(Text)
    sort_order = mapped_column(Integer)
    container = mapped_column(Boolean)
    comment = mapped_column(Text)
    schema = mapped_column(JSONB)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    status: Mapped[Optional['Status']] = relationship('Status', back_populates='content_definitions')
    allowed_children_child: Mapped[List['AllowedChildren']] = relationship('AllowedChildren', uselist=True, foreign_keys='[AllowedChildren.child_definition_id]', back_populates='child_definition')
    allowed_children_parent: Mapped[List['AllowedChildren']] = relationship('AllowedChildren', uselist=True, foreign_keys='[AllowedChildren.parent_definition_id]', back_populates='parent_definition')
    content: Mapped[List['Content']] = relationship('Content', uselist=True, back_populates='content_definition')
    folder_allowed_children: Mapped[List['FolderAllowedChildren']] = relationship('FolderAllowedChildren', uselist=True, back_populates='allowed_definition')
    content_definition_items: Mapped[List['ContentDefinitionItems']] = relationship('ContentDefinitionItems', uselist=True, back_populates='content_definition')


class ContentGroups(Base):
    __tablename__ = 'content_groups'
    __table_args__ = (
        ForeignKeyConstraint(['status_id'], ['status.id'], name='content_groups_status_fk'),
        PrimaryKeyConstraint('id', name='content_groups_pk'),
        Index('idx_content_groups_name', 'name')
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

    status: Mapped[Optional['Status']] = relationship('Status', back_populates='content_groups')
    content_element_groups: Mapped[List['ContentElementGroups']] = relationship('ContentElementGroups', uselist=True, back_populates='content_group')


class ContentTypes(Base):
    __tablename__ = 'content_types'
    __table_args__ = (
        ForeignKeyConstraint(['status_id'], ['status.id'], name='content_types_status_fk'),
        PrimaryKeyConstraint('id', name='content_types_pk'),
        Index('idx_content_types_name', 'name')
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

    status: Mapped[Optional['Status']] = relationship('Status', back_populates='content_types')


class DataTypesEnum(Enum):
    STRING = 'string'
    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    DATE = 'date'
    DATETIME = 'datetime'
    TIMESTAMPTZ = 'timestamptz'
    DOUBLE = 'double'
    FILE = 'file'
    IMAGE = 'image'

class DataTypes(Base):
    __tablename__ = 'data_types'
    __table_args__ = (
        ForeignKeyConstraint(['status_id'], ['main.status.id'], name='data_types_status_fk'),
        PrimaryKeyConstraint('id', name='data_types_pk'),
        Index('idx_data_types_name', 'name'),
        {'schema': 'main'}
    )

    id = mapped_column(String(50))
    name = mapped_column(String(255))
    description = mapped_column(Text)
    scala = mapped_column(String(255))
    typescript = mapped_column(String(255))
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    status: Mapped[Optional['Status']] = relationship('Status', back_populates='data_types')
    data_fields: Mapped[List['DataFields']] = relationship('DataFields', uselist=True, back_populates='datatype')


class DataFields(Base):
    __tablename__ = 'data_fields'
    __table_args__ = (
        ForeignKeyConstraint(['datatype_id'], ['main.data_types.id'], name='data_fields_data_types_fk'),
        ForeignKeyConstraint(['status_id'], ['main.status.id'], name='data_fields_status_fk'),
        PrimaryKeyConstraint('id', name='data_fields_pk'),
        Index('idx_data_fields_name', 'name'),
        {'schema': 'main'}
    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    description = mapped_column(Text)
    datatype_id = mapped_column(String(50))
    pattern = mapped_column(String(255))
    max_length = mapped_column(Integer)
    min_length = mapped_column(Integer)
    required = mapped_column(Boolean)
    format = mapped_column(String(255))
    schema = mapped_column(JSONB)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    datatype: Mapped[Optional['DataTypes']] = relationship('DataTypes', back_populates='data_fields')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='data_fields')


class AllowedChildren(Base):
    __tablename__ = 'allowed_children'
    __table_args__ = (
        ForeignKeyConstraint(['child_definition_id'], ['content_definitions.id'], name='allowed_children_child_fk'),
        ForeignKeyConstraint(['parent_definition_id'], ['content_definitions.id'], name='allowed_children_parent_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='allowed_children_status_fk'),
        PrimaryKeyConstraint('id', name='allowed_children_pk'),
        Index('idx_allowed_children_sort_order', 'sort_order')
    )

    id = mapped_column(BigInteger)
    parent_definition_id = mapped_column(BigInteger)
    child_definition_id = mapped_column(BigInteger)
    max_count = mapped_column(Integer)
    min_count = mapped_column(Integer)
    sort_order = mapped_column(Integer)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    child_definition: Mapped[Optional['ContentDefinitions']] = relationship('ContentDefinitions', foreign_keys=[child_definition_id], back_populates='allowed_children')
    parent_definition: Mapped[Optional['ContentDefinitions']] = relationship('ContentDefinitions', foreign_keys=[parent_definition_id], back_populates='allowed_children_')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='allowed_children')


class Content(Base):
    __tablename__ = 'content'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.id'], name='content_category_fk'),
        ForeignKeyConstraint(['cms_node_id'], ['cms_nodes.id'], name='content_cms_node_fk'),
        ForeignKeyConstraint(['content_definition_id'], ['content_definitions.id'], name='content_definition_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='content_status_fk'),
        PrimaryKeyConstraint('id', name='content_pk'),
        Index('idx_content_title', 'title')
    )

    id = mapped_column(BigInteger)
    cms_node_id = mapped_column(BigInteger)
    content_definition_id = mapped_column(BigInteger)
    title = mapped_column(String(255))
    description = mapped_column(Text)
    meta_data = mapped_column(JSONB)
    data = mapped_column(JSONB)
    category_id = mapped_column(BigInteger)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    category: Mapped[Optional['Categories']] = relationship('Categories', back_populates='content')
    cms_node: Mapped[Optional['CmsNodes']] = relationship('CmsNodes', back_populates='content')
    content_definition: Mapped[Optional['ContentDefinitions']] = relationship('ContentDefinitions', back_populates='content')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='content')
    content_tags: Mapped[List['ContentTags']] = relationship('ContentTags', uselist=True, back_populates='content')


class ContentElements(Base):
    __tablename__ = 'content_elements'
    __table_args__ = (
        ForeignKeyConstraint(['field_id'], ['data_fields.id'], name='content_elements_data_fields_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='content_elements_status_fk'),
        PrimaryKeyConstraint('id', name='content_elements_pk'),
        Index('idx_content_elements_control_name', 'control_name'),
        Index('idx_content_elements_name', 'name'),
        Index('idx_content_elements_sort_order', 'sort_order')
    )

    id = mapped_column(Integer)
    control_name = mapped_column(String(255), nullable=False)
    name = mapped_column(String(255))
    description = mapped_column(Text)
    sort_order = mapped_column(Integer)
    field_id = mapped_column(BigInteger)
    schema = mapped_column(JSONB)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    field: Mapped[Optional['DataFields']] = relationship('DataFields', back_populates='content_elements')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='content_elements')
    content_element_groups: Mapped[List['ContentElementGroups']] = relationship('ContentElementGroups', uselist=True, back_populates='content_element')
    content_definition_items: Mapped[List['ContentDefinitionItems']] = relationship('ContentDefinitionItems', uselist=True, back_populates='content_element')


class FolderAllowedChildren(Base):
    __tablename__ = 'folder_allowed_children'
    __table_args__ = (
        ForeignKeyConstraint(['allowed_definition_id'], ['content_definitions.id'], name='folder_allowed_children_definition_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='folder_allowed_children_status_fk'),
        PrimaryKeyConstraint('id', name='folder_allowed_children_pk'),
        Index('idx_folder_allowed_children_allow_all_content', 'allow_all_content'),
        Index('idx_folder_allowed_children_allow_folders', 'allow_folders')
    )

    id = mapped_column(BigInteger)
    allowed_definition_id = mapped_column(BigInteger)
    allow_folders = mapped_column(Boolean)
    allow_all_content = mapped_column(Boolean)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    allowed_definition: Mapped[Optional['ContentDefinitions']] = relationship('ContentDefinitions', back_populates='folder_allowed_children')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='folder_allowed_children')


class Folders(Base):
    __tablename__ = 'folders'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.id'], name='folders_category_fk'),
        ForeignKeyConstraint(['cms_node_id'], ['cms_nodes.id'], name='folders_cms_node_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='folders_status_fk'),
        PrimaryKeyConstraint('id', name='folders_pk'),
        Index('idx_folders_name', 'name')
    )

    id = mapped_column(BigInteger)
    cms_node_id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    description = mapped_column(Text)
    meta_data = mapped_column(JSONB)
    icon = mapped_column(String(255))
    category_id = mapped_column(BigInteger)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    category: Mapped[Optional['Categories']] = relationship('Categories', back_populates='folders')
    cms_node: Mapped[Optional['CmsNodes']] = relationship('CmsNodes', back_populates='folders')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='folders')


class ContentElementGroups(Base):
    __tablename__ = 'content_element_groups'
    __table_args__ = (
        ForeignKeyConstraint(['content_element_id'], ['content_elements.id'], name='content_element_groups_content_elements_fk'),
        ForeignKeyConstraint(['content_group_id'], ['content_groups.id'], name='content_element_groups_content_groups_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='content_element_groups_status_fk'),
        PrimaryKeyConstraint('id', name='content_element_groups_pk'),
        Index('idx_content_element_groups_element', 'content_element_id'),
        Index('idx_content_element_groups_name', 'name')
    )

    id = mapped_column(BigInteger)
    content_element_id = mapped_column(BigInteger)
    content_group_id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    sort_order = mapped_column(Integer)
    schema = mapped_column(JSONB)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    content_element: Mapped[Optional['ContentElements']] = relationship('ContentElements', back_populates='content_element_groups')
    content_group: Mapped[Optional['ContentGroups']] = relationship('ContentGroups', back_populates='content_element_groups')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='content_element_groups')
    content_definition_items: Mapped[List['ContentDefinitionItems']] = relationship('ContentDefinitionItems', uselist=True, back_populates='content_element_group')


class ContentDefinitionItems(Base):
    __tablename__ = 'content_definition_items'
    __table_args__ = (
        CheckConstraint('content_element_id IS NOT NULL AND content_element_group_id IS NULL OR content_element_id IS NULL AND content_element_group_id IS NOT NULL', name='exactly_one_reference'),
        ForeignKeyConstraint(['content_definition_id'], ['content_definitions.id'], name='content_definition_items_def_fk'),
        ForeignKeyConstraint(['content_element_group_id'], ['content_element_groups.id'], name='content_definition_items_group_fk'),
        ForeignKeyConstraint(['content_element_id'], ['content_elements.id'], name='content_definition_items_element_fk'),
        ForeignKeyConstraint(['status_id'], ['status.id'], name='content_definition_items_status_fk'),
        PrimaryKeyConstraint('id', name='content_definition_items_pk'),
        Index('idx_def_items_definition', 'content_definition_id', 'sort_order')
    )

    id = mapped_column(BigInteger)
    content_definition_id = mapped_column(Integer, nullable=False)
    sort_order = mapped_column(Integer, nullable=False, server_default=text('0'))
    content_element_id = mapped_column(BigInteger)
    content_element_group_id = mapped_column(BigInteger)
    override_schema = mapped_column(JSONB)
    status_id = mapped_column(BigInteger)
    version = mapped_column(BigInteger)
    created_at = mapped_column(DateTime(True))
    updated_at = mapped_column(DateTime(True))
    created_by = mapped_column(String(50))
    updated_by = mapped_column(String(50))

    content_definition: Mapped['ContentDefinitions'] = relationship('ContentDefinitions', back_populates='content_definition_items')
    content_element_group: Mapped[Optional['ContentElementGroups']] = relationship('ContentElementGroups', back_populates='content_definition_items')
    content_element: Mapped[Optional['ContentElements']] = relationship('ContentElements', back_populates='content_definition_items')
    status: Mapped[Optional['Status']] = relationship('Status', back_populates='content_definition_items')
