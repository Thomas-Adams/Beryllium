This is the classic "a definition is composed of items that can be one of two types" problem. You have three ways to model it, each with real tradeoffs.

## Option 1: Single Mapping Table with Polymorphic FK

One table, two nullable foreign keys, a check constraint ensuring exactly one is set:

```sql
create table "content_definition_items" (
    "id" int not null,
    "content_definition_id" int not null,
    "content_element_id" int,           -- FK, nullable
    "content_element_group_id" int,     -- FK, nullable
    "order_index" int not null default 0,
    "override_schema" jsonb,            -- optional: override element/group settings per definition
    "status_id" int,
    "version" int,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    "created_by" varchar(50),
    "updated_by" varchar(50),
    constraint content_definition_items_pk primary key (id),
    constraint content_definition_items_def_fk foreign key (content_definition_id)
        references content_definitions (id),
    constraint content_definition_items_element_fk foreign key (content_element_id)
        references content_elements (id),
    constraint content_definition_items_group_fk foreign key (content_element_group_id)
        references content_element_groups (id),
    constraint content_definition_items_status_fk foreign key (status_id)
        references status (id),
    -- exactly one must be set
    constraint exactly_one_reference check (
        (content_element_id is not null and content_element_group_id is null)
        or
        (content_element_id is null and content_element_group_id is not null)
    )
);

create index idx_def_items_definition 
    on content_definition_items (content_definition_id, order_index);
```

**Pros:** Single table, single query to get all items for a definition ordered correctly. The check constraint keeps it clean. Querying is straightforward:

```sql
-- get full definition composition, ordered
select 
    di.*,
    ce.name as element_name,
    ceg.name as group_name
from content_definition_items di
left join content_elements ce on ce.id = di.content_element_id
left join content_element_groups ceg on ceg.id = di.content_element_group_id
where di.content_definition_id = ?
order by di.order_index;
```

**Cons:** Nullable FKs are a mild code smell. If you add a third composable type later you add another nullable column.

## Option 2: Discriminated Type Column

Similar to option 1 but with an explicit type discriminator:

```sql
create table "content_definition_items" (
    "id" int not null,
    "content_definition_id" int not null,
    "item_type" varchar(20) not null,   -- 'element' | 'group'
    "item_id" int not null,             -- references either table based on item_type
    "order_index" int not null default 0,
    "override_schema" jsonb,
    "status_id" int,
    "version" int,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    "created_by" varchar(50),
    "updated_by" varchar(50),
    constraint content_definition_items_pk primary key (id),
    constraint content_definition_items_def_fk foreign key (content_definition_id)
        references content_definitions (id),
    constraint content_definition_items_status_fk foreign key (status_id)
        references status (id),
    constraint valid_item_type check (item_type in ('element', 'group'))
);
```

**Pros:** Scales to more types without schema changes. Single `item_id` column is cleaner.

**Cons:** You lose the foreign key constraint. Postgres can't enforce that `item_id` points to the right table based on `item_type`. Referential integrity becomes your application's problem. For a CMS where data integrity matters long-term, that's a real cost.

## Option 3: Two Separate Mapping Tables

```sql
create table "content_definition_elements" (
    "id" int not null,
    "content_definition_id" int not null,
    "content_element_id" int not null,
    "order_index" int not null default 0,
    "override_schema" jsonb,
    "status_id" int,
    "version" int,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    "created_by" varchar(50),
    "updated_by" varchar(50),
    constraint content_def_elements_pk primary key (id),
    constraint content_def_elements_def_fk foreign key (content_definition_id)
        references content_definitions (id),
    constraint content_def_elements_el_fk foreign key (content_element_id)
        references content_elements (id),
    constraint content_def_elements_status_fk foreign key (status_id)
        references status (id)
);

create table "content_definition_groups" (
    "id" int not null,
    "content_definition_id" int not null,
    "content_element_group_id" int not null,
    "order_index" int not null default 0,
    "override_schema" jsonb,
    "status_id" int,
    "version" int,
    "created_at" timestamptz,
    "updated_at" timestamptz,
    "created_by" varchar(50),
    "updated_by" varchar(50),
    constraint content_def_groups_pk primary key (id),
    constraint content_def_groups_def_fk foreign key (content_definition_id)
        references content_definitions (id),
    constraint content_def_groups_grp_fk foreign key (content_element_group_id)
        references content_element_groups (id),
    constraint content_def_groups_status_fk foreign key (status_id)
        references status (id)
);
```

**Pros:** Full referential integrity, no nullable FKs, no check constraints, completely normalized.

**Cons:** Ordering across both types requires a `UNION` and that's genuinely annoying:

```sql
select 'element' as item_type, id, content_definition_id, 
       content_element_id as item_id, order_index
from content_definition_elements
where content_definition_id = ?
union all
select 'group' as item_type, id, content_definition_id, 
       content_element_group_id as item_id, order_index
from content_definition_groups
where content_definition_id = ?
order by order_index;
```

Every time you load a definition's composition, you run that union. Not a performance problem, but it's friction in every query and every PostgREST/PostGraphile exposure.

## My Recommendation: Option 1

For Beryl, go with the single mapping table with dual nullable FKs. Here's why:

You have exactly two composable types and that's unlikely to grow — a content definition is made of elements and groups of elements, that's the natural ceiling of this abstraction. The check constraint enforces integrity at the database level. The single `order_index` across both types in one table means ordering just works without unions. And when your Angular UI renders the definition builder (dragging elements and groups into a definition), it maps directly to one list of `content_definition_items` ordered by `order_index`.

The `override_schema` JSONB column is worth noting — it lets you tweak an element's behaviour within a specific definition without modifying the shared element itself. For instance, a "title" element might have `max_length: 255` globally but a specific definition could override it to `max_length: 100`. Your form renderer checks `override_schema` first, falls back to the element's own schema.

Want me to integrate this into your full DDL and produce the updated PlantUML?
