

    -- ============================================================
    -- DROP ALL TABLES
    -- ============================================================
    DROP TABLE IF EXISTS main.content_definition_items CASCADE;
    DROP TABLE IF EXISTS main.content_element_groups CASCADE;
    DROP TABLE IF EXISTS main.content_tags CASCADE;
    DROP TABLE IF EXISTS main.content_elements CASCADE;
    DROP TABLE IF EXISTS main.folders CASCADE;
    DROP TABLE IF EXISTS main.content CASCADE;
    DROP TABLE IF EXISTS main.allowed_children CASCADE;
    DROP TABLE IF EXISTS main.folder_allowed_children CASCADE;
    DROP TABLE IF EXISTS main.cms_nodes CASCADE;
    DROP TABLE IF EXISTS main.data_fields CASCADE;
    DROP TABLE IF EXISTS main.content_groups CASCADE;
    DROP TABLE IF EXISTS main.content_definitions CASCADE;
    DROP TABLE IF EXISTS main.categories CASCADE;
    DROP TABLE IF EXISTS main.content_types CASCADE;
    DROP TABLE IF EXISTS main.data_types CASCADE;
    DROP TABLE IF EXISTS main.media_types CASCADE;
    DROP TABLE IF EXISTS main.mime_types CASCADE;
    DROP TABLE IF EXISTS main.media_tags CASCADE;
    DROP TABLE IF EXISTS main.media CASCADE;
    DROP TABLE IF EXISTS main.media_variant CASCADE;
    DROP TABLE IF EXISTS main.tags CASCADE;
    DROP TABLE IF EXISTS main.users CASCADE;
    DROP TABLE IF EXISTS main.status CASCADE;



    -- ============================================================
    -- CREATE ALL TABLES (no foreign keys)
    -- ============================================================

    CREATE TABLE main."status"
    (
        "id"          bigserial not null,
        "name"        varchar(255),
        "description" text,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(50),
        "updated_by"  varchar(50),
        CONSTRAINT status_pkey PRIMARY KEY (id)
    );

    CREATE TABLE main."data_types"
    (
        "id"          varchar(50) NOT NULL,
        "name"        varchar(255),
        "description" text,
        "scala"       varchar(255),
        "typescript"  varchar(255),
        "status_id"   bigint,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(50),
        "updated_by"  varchar(50),
        CONSTRAINT data_types_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."content_types"
    (
        "id"          bigserial not null,
        "name"        varchar(255),
        "description" text,
        "status_id"   bigint,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(50),
        "updated_by"  varchar(50),
        CONSTRAINT content_types_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."categories"
    (
        "id"          bigserial not null,
        "name"        varchar(255),
        "description" text,
        "meta_data"   jsonb,
        "status_id"   bigint,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(50),
        "updated_by"  varchar(50),
        CONSTRAINT categories_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."data_fields"
    (
        "id"          bigserial not null,
        "name"        varchar(255),
        "description" text,
        "datatype_id" varchar(50),
        "pattern"     varchar(255),
        "max_length"  int,
        "min_length"  int,
        "required"    boolean,
        "format"      varchar(255),
        "schema"      jsonb,
        "status_id"   bigint,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(50),
        "updated_by"  varchar(50),
        CONSTRAINT data_fields_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."content_elements"
    (
        "id"           int          NOT NULL,
        "name"         varchar(255),
        "description"  text,
        "sort_order"   int,
        "field_id"     bigint,
        "control_name" varchar(255) NOT NULL,
        "schema"       jsonb,
        "status_id"    bigint,
        "version"      bigint,
        "created_at"   timestamptz,
        "updated_at"   timestamptz,
        "created_by"   varchar(50),
        "updated_by"   varchar(50),
        CONSTRAINT content_elements_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."content_groups"
    (
        "id"          bigserial not null,
        "name"        varchar(255),
        "description" text,
        "status_id"   bigint,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(50),
        "updated_by"  varchar(50),
        CONSTRAINT content_groups_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."content_element_groups"
    (
        "id"                 bigserial not null,
        "content_element_id" bigint,
        "content_group_id"   bigint,
        "name"               varchar(255),
        "sort_order"         int,
        "schema"             jsonb,
        "status_id"          bigint,
        "version"            bigint,
        "created_at"         timestamptz,
        "updated_at"         timestamptz,
        "created_by"         varchar(50),
        "updated_by"         varchar(50),
        CONSTRAINT content_element_groups_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."content_definitions"
    (
        "id"          bigserial not null,
        "name"        varchar(255),
        "description" text,
        "sort_order"  int,
        "container"   boolean,
        "comment"     text,
        "schema"      jsonb,
        "status_id"   bigint,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(50),
        "updated_by"  varchar(50),
        CONSTRAINT content_definitions_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."content_definition_items"
    (
        "id"                       bigserial not null,
        "content_definition_id"    int       NOT NULL,
        "content_element_id"       bigint,
        "content_element_group_id" bigint,
        "sort_order"               int       NOT NULL DEFAULT 0,
        "override_schema"          jsonb,
        "status_id"                bigint,
        "version"                  bigint,
        "created_at"               timestamptz,
        "updated_at"               timestamptz,
        "created_by"               varchar(50),
        "updated_by"               varchar(50),
        CONSTRAINT content_definition_items_pk PRIMARY KEY (id),
        CONSTRAINT exactly_one_reference CHECK (
            (content_element_id IS NOT NULL AND content_element_group_id IS NULL)
                OR
            (content_element_id IS NULL AND content_element_group_id IS NOT NULL)
            )
    );

    CREATE TABLE main."cms_nodes"
    (
        "id"            bigserial not null,
        "parent_id"     bigint,
        "cms_node_type" varchar(20),
        "path"          ltree,
        "sort_order"    int,
        "status_id"     bigint,
        "version"       bigint,
        "created_at"    timestamptz,
        "updated_at"    timestamptz,
        "created_by"    varchar(50),
        "updated_by"    varchar(50),
        CONSTRAINT cms_nodes_pk PRIMARY KEY (id)
    );



    CREATE TABLE main."folders"
    (
        "id"          bigserial not null,
        "cms_node_id" bigint,
        "name"        varchar(255),
        "description" text,
        "meta_data"   jsonb,
        "icon"        varchar(255),
        "category_id" bigint,
        "status_id"   bigint,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(50),
        "updated_by"  varchar(50),
        CONSTRAINT folders_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."content"
    (
        "id"                    bigserial not null,
        "cms_node_id"           bigint,
        "content_definition_id" bigint,
        "title"                 varchar(255),
        "description"           text,
        "meta_data"             jsonb,
        "data"                  jsonb,
        "category_id"           bigint,
        "status_id"             bigint,
        "version"               bigint,
        "created_at"            timestamptz,
        "updated_at"            timestamptz,
        "created_by"            varchar(50),
        "updated_by"            varchar(50),
        CONSTRAINT content_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."allowed_children"
    (
        "id"                   bigserial not null,
        "parent_definition_id" bigint,
        "child_definition_id"  bigint,
        "max_count"            int,
        "min_count"            int,
        "sort_order"           int,
        "status_id"            bigint,
        "version"              bigint,
        "created_at"           timestamptz,
        "updated_at"           timestamptz,
        "created_by"           varchar(50),
        "updated_by"           varchar(50),
        CONSTRAINT allowed_children_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."folder_allowed_children"
    (
        "id"                    bigserial not null,
        "allowed_definition_id" bigint,
        "allow_folders"         boolean,
        "allow_all_content"     boolean,
        "status_id"             bigint,
        "version"               bigint,
        "created_at"            timestamptz,
        "updated_at"            timestamptz,
        "created_by"            varchar(50),
        "updated_by"            varchar(50),
        CONSTRAINT folder_allowed_children_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."tags"
    (
        "id"         bigserial not null,
        "name"       varchar(255),
        "status_id"  bigint,
        "version"    bigint,
        "created_at" timestamptz,
        "updated_at" timestamptz,
        "created_by" varchar(50),
        "updated_by" varchar(50),
        CONSTRAINT tags_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."content_tags"
    (
        "id"         bigserial not null,
        "content_id" bigint,
        "tag_id"     bigint,
        "version"    bigint,
        "created_at" timestamptz,
        "updated_at" timestamptz,
        "created_by" varchar(50),
        "updated_by" varchar(50),
        CONSTRAINT content_tags_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."media_types"
    (
        "id"          bigserial not null,
        "name"        varchar(255),
        "description" text,
        "status_id"   bigint,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(50),
        "updated_by"  varchar(50),
        CONSTRAINT media_types_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."mime_types"
    (
        "id"          varchar(50) NOT NULL,
        "name"        varchar(255),
        "description" text,
        "version"     bigint,
        "created_at"  timestamptz,
        "updated_at"  timestamptz,
        "created_by"  varchar(255),
        "updated_by"  varchar(255),
        CONSTRAINT mime_types_pk PRIMARY KEY (id)
    );



    create table main."media"
    (
        "id"                bigserial not null,
        "name"              varchar(255),
        "description"       text,
        "media_type_id"     bigint,
        "mime_type_id"      varchar(50),
        "original_filename" varchar(255),
        "stored_filename"   varchar(255),
        "extension"         varchar(255),
        "size_bytes"        int,
        "object_key"        varchar(255),
        "checksum_sha256"   varchar(255),
        "url"               varchar(255),
        "status_id"         int,
        "version"           bigint,
        "created_at"        timestamptz,
        "updated_at"        timestamptz,
        "created_by"        varchar(50),
        "updated_by"        varchar(50),
        constraint media_pk primary key (id)
    );

    create table main."media_variant"
    (
        "id"              bigserial not null,
        "media_id"        bigint    not null,
        "filename"        varchar(255),
        "variant_type"    varchar(50),
        "mime_type_id"    varchar(50),
        "bucket"          varchar(255),
        "object_key"      varchar(255),
        "aspect_ratio"    float,
        "width"           int,
        "height"          int,
        "checksum_sha256" varchar(255),
        "url"             varchar(255),
        "status_id"       int,
        "version"         bigint,
        "created_at"      timestamptz,
        "updated_at"      timestamptz,
        "created_by"      varchar(50),
        "updated_by"      varchar(50),
        CONSTRAINT media_variant_pk PRIMARY KEY (id)
    );


    CREATE TABLE main."media_tags"
    (
        "id"               bigserial not null,
        "media_variant_id" bigint,
        "tag_id"           bigint,
        "version"          bigint,
        "created_at"       timestamptz,
        "updated_at"       timestamptz,
        "created_by"       varchar(255),
        "updated_by"       varchar(255),
        CONSTRAINT media_tags_pk PRIMARY KEY (id)
    );

    CREATE TABLE main."users"
    (
        "id"            bigserial    not null,
        "username"      varchar(255) NOT NULL,
        "email"         varchar(255) NOT NULL,
        "password_hash" varchar(255) NOT NULL,
        "role"          varchar(50) NOT NULL ,
        "status_id"     bigint,
        "version"       bigint,
        "created_at"    timestamptz,
        "updated_at"    timestamptz,
        CONSTRAINT users_pk PRIMARY KEY (id)
    );


    -- ============================================================
    -- FOREIGN KEYS
    -- ============================================================

    -- data_types
    ALTER TABLE main.data_types
        ADD CONSTRAINT data_types_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- content_types
    ALTER TABLE main.content_types
        ADD CONSTRAINT content_types_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- categories
    ALTER TABLE main.categories
        ADD CONSTRAINT categories_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- data_fields
    ALTER TABLE main.data_fields
        ADD CONSTRAINT data_fields_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- content_elements
    ALTER TABLE main.content_elements
        ADD CONSTRAINT content_elements_data_fields_fk
            FOREIGN KEY (field_id) REFERENCES main.data_fields (id);

    ALTER TABLE main.content_elements
        ADD CONSTRAINT content_elements_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- content_groups
    ALTER TABLE main.content_groups
        ADD CONSTRAINT content_groups_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- content_element_groups
    ALTER TABLE main.content_element_groups
        ADD CONSTRAINT content_element_groups_content_elements_fk
            FOREIGN KEY (content_element_id) REFERENCES main.content_elements (id);

    ALTER TABLE main.content_element_groups
        ADD CONSTRAINT content_element_groups_content_groups_fk
            FOREIGN KEY (content_group_id) REFERENCES main.content_groups (id);

    ALTER TABLE main.content_element_groups
        ADD CONSTRAINT content_element_groups_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- content_definitions
    ALTER TABLE main.content_definitions
        ADD CONSTRAINT content_definitions_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- content_definition_items
    ALTER TABLE main.content_definition_items
        ADD CONSTRAINT content_definition_items_def_fk
            FOREIGN KEY (content_definition_id) REFERENCES main.content_definitions (id);

    ALTER TABLE main.content_definition_items
        ADD CONSTRAINT content_definition_items_element_fk
            FOREIGN KEY (content_element_id) REFERENCES main.content_elements (id);

    ALTER TABLE main.content_definition_items
        ADD CONSTRAINT content_definition_items_group_fk
            FOREIGN KEY (content_element_group_id) REFERENCES main.content_element_groups (id);

    ALTER TABLE main.content_definition_items
        ADD CONSTRAINT content_definition_items_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- cms_nodes (self-referencing)
    ALTER TABLE main.cms_nodes
        ADD CONSTRAINT cms_nodes_parent_fk
            FOREIGN KEY (parent_id) REFERENCES main.cms_nodes (id);

    ALTER TABLE main.cms_nodes
        ADD CONSTRAINT cms_nodes_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- folders
    ALTER TABLE main.folders
        ADD CONSTRAINT folders_cms_node_fk
            FOREIGN KEY (cms_node_id) REFERENCES main.cms_nodes (id);

    ALTER TABLE main.folders
        ADD CONSTRAINT folders_category_fk
            FOREIGN KEY (category_id) REFERENCES main.categories (id);

    ALTER TABLE main.folders
        ADD CONSTRAINT folders_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- content
    ALTER TABLE main.content
        ADD CONSTRAINT content_cms_node_fk
            FOREIGN KEY (cms_node_id) REFERENCES main.cms_nodes (id);

    ALTER TABLE main.content
        ADD CONSTRAINT content_definition_fk
            FOREIGN KEY (content_definition_id) REFERENCES main.content_definitions (id);

    ALTER TABLE main.content
        ADD CONSTRAINT content_category_fk
            FOREIGN KEY (category_id) REFERENCES main.categories (id);

    ALTER TABLE main.content
        ADD CONSTRAINT content_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- allowed_children
    ALTER TABLE main.allowed_children
        ADD CONSTRAINT allowed_children_parent_fk
            FOREIGN KEY (parent_definition_id) REFERENCES main.content_definitions (id);

    ALTER TABLE main.allowed_children
        ADD CONSTRAINT allowed_children_child_fk
            FOREIGN KEY (child_definition_id) REFERENCES main.content_definitions (id);

    ALTER TABLE main.allowed_children
        ADD CONSTRAINT allowed_children_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- folder_allowed_children
    ALTER TABLE main.folder_allowed_children
        ADD CONSTRAINT folder_allowed_children_definition_fk
            FOREIGN KEY (allowed_definition_id) REFERENCES main.content_definitions (id);

    ALTER TABLE main.folder_allowed_children
        ADD CONSTRAINT folder_allowed_children_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- tags
    ALTER TABLE main.tags
        ADD CONSTRAINT tags_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- content_tags
    ALTER TABLE main.content_tags
        ADD CONSTRAINT content_tags_content_fk
            FOREIGN KEY (content_id) REFERENCES main.content (id);

    ALTER TABLE main.content_tags
        ADD CONSTRAINT content_tags_tag_fk
            FOREIGN KEY (tag_id) REFERENCES main.tags (id);

    -- media_types
    ALTER TABLE main.media_types
        ADD CONSTRAINT media_types_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    -- media
    ALTER TABLE main.media
        ADD CONSTRAINT media_media_type_fk
            FOREIGN KEY (media_type_id) REFERENCES main.media_types (id);

    ALTER TABLE main.media
        ADD CONSTRAINT media_mime_type_fk
            FOREIGN KEY (mime_type_id) REFERENCES main.mime_types (id);

    ALTER TABLE main.media
        ADD CONSTRAINT media_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    ALTER TABLE main.media_variant
        ADD CONSTRAINT media_variant_media_fk
            FOREIGN KEY (media_id) REFERENCES main.media (id);

    ALTER TABLE main.media_variant
        ADD CONSTRAINT media_variant_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    ALTER TABLE main.media_tags
        ADD CONSTRAINT media_tags_tags_fk
            FOREIGN KEY (tag_id) REFERENCES main.tags (id);

    ALTER TABLE main.media_tags
        ADD CONSTRAINT media_tags_media_variant_fk
            FOREIGN KEY (media_variant_id) REFERENCES main.media_variant (id);

    -- users
    ALTER TABLE main.users
        ADD CONSTRAINT users_status_fk
            FOREIGN KEY (status_id) REFERENCES main.status (id);

    ALTER TABLE main.data_fields
        ADD CONSTRAINT data_fields_data_types_fk
            FOREIGN KEY (datatype_id) REFERENCES main.data_types (id);


    -- ============================================================
    -- INDEXES
    -- ============================================================

    CREATE INDEX idx_status_name ON main.status (name);
    CREATE INDEX idx_data_types_name ON main.data_types (name);
    CREATE INDEX idx_content_types_name ON main.content_types (name);
    CREATE INDEX idx_categories_name ON main.categories (name);
    CREATE INDEX idx_data_fields_name ON main.data_fields (name);
    CREATE INDEX idx_content_elements_name ON main.content_elements (name);
    CREATE INDEX idx_content_elements_sort_order ON main.content_elements (sort_order);
    CREATE INDEX idx_content_elements_control_name ON main.content_elements (control_name);
    CREATE INDEX idx_content_groups_name ON main.content_groups (name);
    CREATE INDEX idx_content_element_groups_name ON main.content_element_groups (name);
    CREATE INDEX idx_content_element_groups_element ON main.content_element_groups (content_element_id);
    CREATE INDEX idx_content_definitions_name ON main.content_definitions (name);
    CREATE INDEX idx_content_definitions_sort_order ON main.content_definitions (sort_order);
    CREATE INDEX idx_def_items_definition ON main.content_definition_items (content_definition_id, sort_order);
    CREATE INDEX idx_cms_nodes_path ON main.cms_nodes USING GIST (path);
    CREATE INDEX idx_cms_nodes_sort_order ON main.cms_nodes (sort_order);
    CREATE INDEX idx_cms_nodes_type ON main.cms_nodes (cms_node_type);
    CREATE INDEX idx_folders_name ON main.folders (name);
    CREATE INDEX idx_content_title ON main.content (title);
    CREATE INDEX idx_allowed_children_sort_order ON main.allowed_children (sort_order);
    CREATE INDEX idx_folder_allowed_children_allow_folders ON main.folder_allowed_children (allow_folders);
    CREATE INDEX idx_folder_allowed_children_allow_all_content ON main.folder_allowed_children (allow_all_content);
    CREATE INDEX idx_tags_name ON main.tags (name);
    CREATE INDEX idx_media_types_name ON main.media_types (name);
    CREATE INDEX idx_mime_types_name ON main.mime_types (name);
    CREATE INDEX idx_media_name ON main.media (name);
    CREATE UNIQUE INDEX idx_users_username ON main.users (username);
    CREATE UNIQUE INDEX idx_users_email ON main.users (email);


