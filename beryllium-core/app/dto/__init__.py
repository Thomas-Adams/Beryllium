from app.dto.helper import make_create_dto, make_update_dto, make_read_dto, STATUS_FK, MEDIA_FK, MIME_TYPE_FK, MEDIA_TYPE_FK, FIELD_FK, DATA_TYPES_FK, CONTENT_ELEMENT_FK, CONTENT_ELEMENT_GROUP_FK, \
    CONTENT_DEFINITION_FK, ALLOWED_DEFINITION_PARENT_DEFINITION_FK, CONTENT_FK, FOlDERS_ALLOWED_DEFINITION_FK, CMS_NODE_FK, CMS_PARENT_FK, SELF, SELF_LIST, CATEGORY_FK, MEDIA_VARIANT_FK, TAGS_FK
from app.models import ContentTypes
from app.models.content import ContentElements, DataTypes, Content, ContentGroups, ContentElementGroups, ContentDefinitionItems, ContentDefinitions, AllowedChildren, FolderAllowedChildren, Folders, CmsNodes
from app.models.media import MediaTypes, MimeTypes, Media, MediaVariant
from app.models.status import Status
from app.models.user import Users
from app.models.taxonomy import ContentTags, Categories, Tags, MediaTags

StatusCreate = make_create_dto(Status)
StatusUpdate = make_update_dto(Status)
StatusRead = make_read_dto(Status)

ContentTypesCreate = make_create_dto(ContentTypes)
ContentTypesUpdate = make_update_dto(ContentTypes)
ContentTypesRead = make_read_dto(ContentTypes, exclude_fks=STATUS_FK, status=StatusRead)

UserCreate = make_create_dto(Users)
UserUpdate = make_update_dto(Users)
UserRead = make_read_dto(Users, exclude_fks=STATUS_FK, status=StatusRead)

MediaTypesCreate = make_create_dto(MediaTypes)
MediaTypesUpdate = make_update_dto(MediaTypes)
MediaTypesRead = make_read_dto(MediaTypes, exclude_fks=STATUS_FK, status=StatusRead)

MimeTypesCreate = make_create_dto(MimeTypes)
MimeTypesUpdate = make_update_dto(MimeTypes)
MimeTypesRead = make_read_dto(MimeTypes, exclude_fks=STATUS_FK, status=StatusRead)

MediaCreate = make_create_dto(Media)
MediaUpdate = make_update_dto(Media)
MediaRead = make_read_dto(MediaTypes, exclude_fks=STATUS_FK + MIME_TYPE_FK + MEDIA_TYPE_FK, status=StatusRead, mime_type_=MimeTypesRead)

MediaVariantCreate = make_create_dto(MediaVariant)
MediaVariantUpdate = make_update_dto(MediaVariant)
MediaVariantRead = make_read_dto(MediaVariant, exclude_fks=STATUS_FK + MEDIA_FK + MIME_TYPE_FK, status=StatusRead, media=MediaRead)

DataTypesCreate = make_create_dto(DataTypes)
DataTypesUpdate = make_update_dto(DataTypes)
DataTypesRead = make_read_dto(DataTypes, exclude_fks=STATUS_FK, status=StatusRead)

FieldCreate = make_create_dto(DataTypes)
FieldUpdate = make_update_dto(DataTypes)
FieldRead = make_read_dto(DataTypes, exclude_fks=STATUS_FK + DATA_TYPES_FK, status=StatusRead, data_type=DataTypesRead)

ContentElementsCreate = make_create_dto(ContentElements)
ContentElementsUpdate = make_update_dto(ContentElements)
ContentElementsRead = make_read_dto(ContentElements, exclude_fks=STATUS_FK + FIELD_FK, status=StatusRead, field=FieldRead)

ContentGroupsRead = make_read_dto(ContentGroups, exclude_fks=STATUS_FK, status=StatusRead)
ContentGroupsCreate = make_create_dto(ContentGroups)
ContentGroupsUpdate = make_update_dto(ContentGroups)

ContentElementGroupsCreate = make_create_dto(ContentElementGroups)
ContentElementGroupsUpdate = make_update_dto(ContentElementGroups)
ContentElementGroupsRead = make_read_dto(ContentElementGroups, exclude_fks=STATUS_FK + CONTENT_ELEMENT_FK + CONTENT_ELEMENT_GROUP_FK, status=StatusRead, content_element=ContentElementsRead,
                                         content_group=ContentGroupsRead)

ContentDefinitionCreate = make_create_dto(ContentDefinitions)
ContentDefinitionUpdate = make_update_dto(ContentDefinitions)
ContentDefinitionRead = make_read_dto(ContentDefinitions, exclude_fks=STATUS_FK, status=StatusRead)

ContentDefinitionItemsCreate = make_create_dto(ContentDefinitionItems)
ContentDefinitionItemsUpdate = make_update_dto(ContentDefinitionItems)
ContentDefinitionItemsRead = make_read_dto(ContentDefinitionItems, exclude_fks=STATUS_FK + CONTENT_ELEMENT_FK + CONTENT_DEFINITION_FK + CONTENT_ELEMENT_GROUP_FK, status=StatusRead,
                                           content_element_group=ContentElementGroupsRead, content_element=ContentElementsRead, content_definition=ContentDefinitionRead)

AllowedChildrenCreate = make_create_dto(AllowedChildren)
AllowedChildrenUpdate = make_update_dto(AllowedChildren)
AllowedChildrenRead = make_read_dto(AllowedChildren, exclude_fks=STATUS_FK + ALLOWED_DEFINITION_PARENT_DEFINITION_FK + ALLOWED_DEFINITION_PARENT_DEFINITION_FK, status=StatusRead, parent_definition=ContentDefinitionRead, child_definition=ContentDefinitionRead)

FolderAllowedChildrenCreate = make_create_dto(FolderAllowedChildren)
FolderAllowedChildrenUpdate = make_update_dto(FolderAllowedChildren)
FolderAllowedChildrenRead = make_read_dto(FolderAllowedChildren, exclude_fks=STATUS_FK + FOlDERS_ALLOWED_DEFINITION_FK, status=StatusRead, allowed_definition=ContentDefinitionRead)

CmsNodesCreate = make_create_dto(CmsNodes)
CmsNodesUpdate = make_update_dto(CmsNodes)
CmsNodesRead = make_read_dto(CmsNodes, exclude_fks=STATUS_FK + CMS_PARENT_FK, status=StatusRead, parent=SELF, children=SELF_LIST)




TagsCreate = make_create_dto(Tags)
TagsUpdate = make_update_dto(Tags)
TagsRead = make_read_dto(Tags, exclude_fks=STATUS_FK, status=StatusRead)


MediaTagsCreate = make_create_dto(MediaTags)
MediaTagsUpdate = make_update_dto(MediaTags)
MediaTagsRead = make_read_dto(MediaTags, exclude_fks=STATUS_FK + TAGS_FK + MEDIA_VARIANT_FK, status=StatusRead, media_variant=MediaVariantRead, tagss=TagsRead)




FoldersCreate = make_create_dto(Folders)
FoldersUpdate = make_update_dto(Folders)
FoldersRead = make_read_dto(Folders, exclude_fks=STATUS_FK  +CATEGORY_FK + CMS_NODE_FK, status=StatusRead, cms_node=CmsNodesRead, category=CategoryRead)

ContentCreate = make_create_dto(Content)
ContentUpdate= make_update_dto(Content)
ContentRead = make_read_dto(Content, exclude_fks=STATUS_FK + CATEGORY_FK + CMS_NODE_FK + CONTENT_DEFINITION_FK, status=StatusRead, cms_node=CmsNodesRead, category=CategoryRead, content_definition=ContentDefinitionRead)


ContentTagsCreate = make_create_dto(ContentTags)
ContentTagsUpdate = make_update_dto(ContentTags)
ContentTagsRead = make_read_dto(ContentTags, exclude_fks=STATUS_FK + CONTENT_FK + TAGS_FK, status=StatusRead, content=ContentRead, tag=TagsRead)