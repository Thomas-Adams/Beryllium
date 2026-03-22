from typing import Any

from pydantic import ConfigDict, BaseModel, Field, create_model
from pydantic_sqlalchemy_2 import sqlalchemy_to_pydantic
from sqlalchemy import String

# Fields that are always auto-generated
AUTO_FIELDS = ["id", "version", "created_at", "updated_at", "created_by", "updated_by"]

# Fields that are FK IDs we want to resolve as nested objects
STATUS_FK = ["status_id"]
DATA_TYPES_FK = ["datatype_id"]
TAGS_FK = ["tag_id"]
PARENT_FK = ["parent_id"]
PARENT_DEFINITION_FK=["parent_definition_id"]
CHILD_DEFINITION_FK=["child_definition_id"]
FIELD_FK =["field_id"]
ALLOWED_DEFINITION_FK=["allowed_definition_id"]
CATEGORY_FK=["category_id"]
CMS_NODE_FK=["cms_node_id"]
CONTENT_DEFINITION_FK=["content_definition_id"]
CONTENT_ELEMENT_FK=["content_element_id"]
CONTENT_GROUP_FK=["content_group_id"]
CONTENT_ELEMENT_GROUP_FK=["content_element_group_id"]
CONTENT_DEFINITION_ITEM_FK=["content_definition_item_id"]
CONTENT_FK=["content_id"]
MEDIA_FK=["media_id"]
MEDIA_TYPE_FK=["media_type_id"]
MEDIA_VARIANT_FK=["media_variant_id"]
MIME_TYPE_FK=["mime_type_id"]
ALLOWED_DEFINITION_PARENT_DEFINITION_FK=["parent_definition_id"]
ALLOWED_DEFINITION_CHILD_DEFINITION_FK=["child_definition_id"]
FOlDERS_ALLOWED_DEFINITION_FK=["allowed_definition_id"]
CMS_PARENT_FK=["parent_id"]


from pydantic import ConfigDict
from sqlalchemy_to_pydantic import sqlalchemy_to_pydantic

# Sentinel to mark "this is a self-reference"
SELF = "SELF"
SELF_LIST = "SELF_LIST"


def sqlalchemy_model_to_validated_pydantic(sa_model: type, exclude_fields=None) -> type[BaseModel]:
    fields: dict[str, tuple[Any, Any]] = {}

    excludes = exclude_fields or []

    for column in sa_model.__table__.columns:
        if excludes and ( column.name in excludes):
            continue
        py_type = getattr(column.type, "python_type", Any)
        field_kwargs = {}

        # String length -> max_length
        if isinstance(column.type, String) and column.type.length:
            field_kwargs["max_length"] = column.type.length

        # nullable=False and no default -> required
        required = (
                not column.nullable
                and column.default is None
                and column.server_default is None
                and not column.primary_key
        )

        default = ... if required else None

        fields[column.name] = (
            py_type,
            Field(default, **field_kwargs),
        )
    return create_model(f"{sa_model.__name__}Schema", **fields)



def make_read_dto(model, exclude_fks=None, **extra_fields):
    """Generate a read DTO, excluding FK IDs that will be replaced with nested objects."""
    exclude = exclude_fks or []
    Base = sqlalchemy_model_to_validated_pydantic(model, exclude_fields=exclude)

    if extra_fields:
        annotations = {}
        defaults = {}
        needs_rebuild = False

        for name, typ in extra_fields.items():
            if typ is SELF:
                # Forward self-reference — will be resolved by model_rebuild()
                annotations[name] = f"{model.__name__}Read | None"
                defaults[name] = None
                needs_rebuild = True
            elif typ is SELF_LIST:
                annotations[name] = f"list[{model.__name__}Read] | None"
                defaults[name] = None
                needs_rebuild = True
            else:
                annotations[name] = typ
                defaults[name] = None

        ReadDto = type(
            f"{model.__name__}Read",
            (Base,),
            {
                "__annotations__": annotations,
                **defaults,
                "model_config": ConfigDict(from_attributes=True),
            },
        )

        if needs_rebuild:
            # Inject the class into its own namespace so forward refs resolve
            ReadDto.model_rebuild(_types_namespace={f"{model.__name__}Read": ReadDto})

        return ReadDto

    Base.model_config = ConfigDict(from_attributes=True)
    return Base


def make_create_dto(model, extra_exclude=None):
    """Generate a create DTO, excluding auto-generated fields."""
    exclude = AUTO_FIELDS + (extra_exclude or [])
    return sqlalchemy_model_to_validated_pydantic(model, exclude_fields=exclude)


def make_update_dto(model, extra_exclude=None):
    """Generate an update DTO, excluding immutable fields."""
    exclude = ["id", "created_at", "created_by"] + (extra_exclude or [])
    return sqlalchemy_model_to_validated_pydantic(model, exclude_fields=exclude)