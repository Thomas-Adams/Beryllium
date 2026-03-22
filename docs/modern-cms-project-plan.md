# Modern CMS — Project Plan

## Project Vision

A headless, schema-driven CMS replacing Apache Sling. Authors define their own content structures through a visual builder; the system stores them as JSON Schema, validates all content against those schemas, and delivers it through a publish pipeline to server-rendered frontends.

---

## Architecture Overview

| Layer | Technology | Purpose |
|---|---|---|
| Database | PostgreSQL (JSONB) | Content, schemas, users, versioning |
| Object Storage | MinIO (S3-compatible) | Images, media, documents |
| API | PostgREST / PostGraphile | Auto-generated REST + GraphQL from Postgres |
| Backend Services | Scala (ZIO / http4s) | Auth, publish pipeline, media processing, SSR orchestration |
| Search | Meilisearch | Full-text search, facets, typo tolerance |
| Admin UI | Angular | Content type builder, content editor, media manager |
| Delivery | SvelteKit | Public site SSR, templates, hydration |
| Animations | CSS transitions, GSAP, Three.js | Motion and 3D on delivery tier |
| Cache | Redis | Publish-side content + SSR fragment cache |

---

## Phase 1 — Content Definition & Editor (Angular)

**Goal:** Authors can define custom content types via a visual form builder, and edit content instances using dynamically generated forms. All data lives in PostgreSQL; no media handling yet.

### 1.1 Project Scaffold & Dev Environment

**Duration:** 1 week

- Initialize Angular workspace (`ng new cms-admin --routing --style=scss`)
- Set up Nx or standalone monorepo structure if shared libraries are planned
- Configure PostgreSQL dev instance (Docker Compose)
- Configure PostgREST and/or PostGraphile pointing at the database
- Set up Scala backend scaffold (sbt, ZIO or http4s, Flyway for migrations)
- Basic CI pipeline (lint, test, build)

**Deliverables:**
- Running Angular dev server
- Running Postgres + PostgREST/PostGraphile
- Running Scala service skeleton
- Docker Compose for local dev
- First Flyway migration (empty schema baseline)

### 1.2 Core Database Schema

**Duration:** 1 week

**Tables:**

```
-- Identity & access
user_account (
  id UUID PK DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'author',  -- 'admin', 'editor', 'author'
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
)

-- Content type definitions (the schema of schemas)
content_type (
  id UUID PK DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,           -- e.g. 'blog-post', 'product-page'
  display_name TEXT NOT NULL,
  description TEXT,
  icon TEXT,                           -- icon identifier for the admin UI
  schema_jsonb JSONB NOT NULL,         -- the JSON Schema
  ui_hints_jsonb JSONB,               -- field order, grouping, widget prefs
  created_by UUID FK -> user_account,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
)

-- Schema version history
content_type_version (
  id UUID PK DEFAULT gen_random_uuid(),
  content_type_id UUID FK -> content_type,
  version_number INT NOT NULL,
  schema_jsonb JSONB NOT NULL,
  ui_hints_jsonb JSONB,
  change_summary TEXT,
  created_by UUID FK -> user_account,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (content_type_id, version_number)
)

-- Content instances
content (
  id UUID PK DEFAULT gen_random_uuid(),
  content_type_id UUID FK -> content_type,
  slug TEXT NOT NULL,
  current_version_id UUID,             -- FK set after first version created
  status TEXT DEFAULT 'draft',         -- 'draft', 'published', 'archived'
  created_by UUID FK -> user_account,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (content_type_id, slug)
)

-- Content version history
content_version (
  id UUID PK DEFAULT gen_random_uuid(),
  content_id UUID FK -> content,
  schema_version_id UUID FK -> content_type_version,
  version_number INT NOT NULL,
  body_jsonb JSONB NOT NULL,           -- the actual content, validated against schema
  status TEXT DEFAULT 'draft',
  created_by UUID FK -> user_account,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (content_id, version_number)
)
```

**PostgREST / PostGraphile exposure:**
- Create Postgres roles (`cms_admin`, `cms_editor`, `cms_anonymous`)
- Use Row Level Security (RLS) policies so PostgREST handles authorization natively
- Create views/functions for common operations (e.g., `publish_content(content_id)` as a Postgres function)

**Deliverables:**
- Flyway migrations for all tables
- RLS policies
- PostgREST config exposing the schema
- PostGraphile running with auto-generated GraphQL
- Seed data: one admin user, one sample content type

### 1.3 Content Type Builder UI

**Duration:** 3–4 weeks

This is the core of Phase 1. Authors build content structures visually; the system generates JSON Schema behind the scenes.

**Field Type Palette:**

| UI Label | JSON Schema Mapping | Widget |
|---|---|---|
| Short Text | `{ "type": "string", "maxLength": 255 }` | `<input type="text">` |
| Long Text | `{ "type": "string", "x-ui-widget": "textarea" }` | `<textarea>` |
| Rich Text | `{ "type": "string", "x-ui-widget": "richtext" }` | TipTap / ProseMirror |
| Number | `{ "type": "number" }` | `<input type="number">` |
| Integer | `{ "type": "integer" }` | `<input type="number" step="1">` |
| Boolean | `{ "type": "boolean" }` | Toggle switch |
| Date | `{ "type": "string", "format": "date" }` | Date picker |
| DateTime | `{ "type": "string", "format": "date-time" }` | DateTime picker |
| Select (single) | `{ "type": "string", "enum": [...] }` | Dropdown |
| Select (multi) | `{ "type": "array", "items": { "enum": [...] } }` | Multi-select chips |
| Media Reference | `{ "$ref": "#/$defs/media_ref", "x-ui-widget": "media-picker" }` | Media picker (Phase 2) |
| Content Reference | `{ "$ref": "#/$defs/content_ref", "x-ui-widget": "content-picker" }` | Content search & link |
| Group | `{ "type": "object", "properties": {...} }` | Collapsible fieldset |
| Repeatable | `{ "type": "array", "items": { "type": "object", ... } }` | Add/remove/reorder rows |
| Slug | `{ "type": "string", "pattern": "^[a-z0-9-]+$", "x-ui-widget": "slug" }` | Auto-generated from title |

**Builder UI Components:**

```
ContentTypeBuilderPage
├── ContentTypeMetaForm          -- name, slug, description, icon
├── FieldPalette                 -- draggable field types
├── FieldCanvas                  -- drop zone, ordered list of fields
│   └── FieldConfigCard (×N)    -- one per added field
│       ├── FieldHeader          -- drag handle, label, type badge, delete
│       ├── FieldGeneralConfig   -- display name, machine key, required toggle
│       ├── FieldValidationConfig -- min/max, pattern, custom rules (varies by type)
│       └── FieldAdvancedConfig  -- placeholder, help text, default value
├── SchemaPreviewPanel           -- live JSON Schema output (collapsible, for devs)
└── SaveBar                      -- Save draft / Save & activate
```

**Key interactions:**
- Drag from palette → drop on canvas → opens field config inline
- Reorder fields via drag-and-drop on canvas (Angular CDK DragDrop)
- Machine key auto-generated from display name (camelCase), editable
- Validation rules contextual to field type (e.g., "max length" for text, "min/max" for numbers)
- Groups and repeatables allow nesting (fields dropped inside a group card)
- Live preview panel shows the generated JSON Schema updating in real time
- On save: POST schema + ui_hints to backend, which validates and versions it

**Schema Generation Logic (Angular service):**

```typescript
// Simplified — the FieldDefinition is the UI model, toJsonSchema() converts it
interface FieldDefinition {
  key: string;               // machine name
  displayName: string;
  fieldType: FieldType;      // enum: 'shortText', 'richText', 'number', ...
  required: boolean;
  validation: Record<string, any>;  // type-specific
  uiHints: Record<string, any>;
  children?: FieldDefinition[];     // for groups and repeatables
}

function toJsonSchema(fields: FieldDefinition[]): JSONSchema {
  const properties: Record<string, any> = {};
  const required: string[] = [];
  for (const field of fields) {
    properties[field.key] = mapFieldToSchema(field);
    if (field.required) required.push(field.key);
  }
  return { type: 'object', properties, required };
}
```

**Deliverables:**
- Content type CRUD pages (list, create, edit)
- Visual field builder with drag-and-drop
- JSON Schema generation from UI model
- Schema preview panel
- Content type versioning (save creates a new version)
- Field types: all primitives + group + repeatable (media picker stubbed out for Phase 2)

### 1.4 Dynamic Content Editor

**Duration:** 3–4 weeks (overlaps with 1.3)

Given a content type's JSON Schema + UI hints, render a full editing form dynamically.

**Dynamic Form Architecture:**

```
ContentEditorPage
├── ContentMetaBar               -- title, slug, status badge, save/publish buttons
├── DynamicFormHost              -- receives schema, renders recursively
│   └── DynamicFieldRenderer     -- switches on schema type/widget
│       ├── TextField
│       ├── TextAreaField
│       ├── RichTextField         -- TipTap editor
│       ├── NumberField
│       ├── BooleanField
│       ├── DateField
│       ├── SelectField
│       ├── MultiSelectField
│       ├── SlugField             -- auto-generates from a source field
│       ├── ContentRefField       -- search + pick another content item
│       ├── MediaRefField         -- stubbed, shows placeholder in Phase 1
│       ├── GroupField            -- collapsible, recurses into children
│       └── RepeatableField       -- array: add/remove/reorder, each item recurses
├── VersionHistoryPanel          -- sidebar: list of versions, diff, restore
└── ValidationSummary            -- shows all current errors
```

**Form rendering approach:**

```typescript
@Component({ selector: 'dynamic-field', template: `
  <ng-container [ngSwitch]="resolveWidget(fieldSchema)">
    <text-field        *ngSwitchCase="'text'"       [schema]="fieldSchema" [control]="control" />
    <richtext-field    *ngSwitchCase="'richtext'"   [schema]="fieldSchema" [control]="control" />
    <number-field      *ngSwitchCase="'number'"     [schema]="fieldSchema" [control]="control" />
    <group-field       *ngSwitchCase="'group'"      [schema]="fieldSchema" [control]="control" />
    <repeatable-field  *ngSwitchCase="'repeatable'" [schema]="fieldSchema" [control]="control" />
    <!-- ... -->
  </ng-container>
`})
export class DynamicFieldComponent {
  @Input() fieldSchema: any;
  @Input() control: AbstractControl;

  resolveWidget(schema: any): string {
    if (schema['x-ui-widget']) return schema['x-ui-widget'];
    if (schema.type === 'string' && schema.format === 'date') return 'date';
    if (schema.type === 'object' && schema.properties) return 'group';
    if (schema.type === 'array') return 'repeatable';
    if (schema.type === 'string') return 'text';
    if (schema.type === 'number' || schema.type === 'integer') return 'number';
    if (schema.type === 'boolean') return 'boolean';
    return 'text'; // fallback
  }
}
```

**Validation integration:**
- Client-side: Angular reactive forms with validators derived from JSON Schema (required, minLength, maxLength, pattern, min, max, enum)
- Server-side: Scala backend validates body_jsonb against the content type's schema using a JSON Schema validator (e.g., `networknt/json-schema-validator`) before persisting
- Dual validation guarantees no invalid content reaches the database

**Version history & comparison:**
- Each save creates a new `content_version` row
- Version panel shows chronological list with author + timestamp
- Diff view: JSON diff between two versions, rendered as highlighted field-level changes
- Restore: creates a new version with the body of a previous version

**Autosave:**
- Debounced save (e.g., 30 seconds of inactivity) writes a draft version
- Visual indicator: "Saved" / "Unsaved changes" / "Saving..."
- Explicit "Publish" action promotes a draft version to published status

**Deliverables:**
- Dynamic form renderer driven by JSON Schema
- All field widgets for primitive types
- Group and repeatable (nested) field support
- Reactive form validation derived from schema
- Content CRUD: list, create, edit, delete
- Version history panel with diff
- Autosave + explicit publish
- Server-side JSON Schema validation in Scala

### 1.5 Authentication & Basic Authorization

**Duration:** 1–2 weeks (can run in parallel)

- JWT-based auth via the Scala backend
- Login page in Angular
- PostgREST receives JWT in `Authorization` header, uses claims for RLS
- Roles: `admin` (manage content types + content), `editor` (edit content), `author` (create/edit own content)
- Angular route guards per role

**Deliverables:**
- Login / logout flow
- JWT issuance and refresh
- Role-based menu and route visibility
- PostgREST RLS integration tested

---

## Phase 2 — Media Management & MinIO

**Goal:** Upload, process, and serve images, documents, and media files. Integrate the media picker into the content editor.

**Duration:** 3–4 weeks

### 2.1 MinIO Setup & Media Data Model

- MinIO instance in Docker Compose (buckets: `originals`, `variants`, `documents`)
- `media_asset` + `media_variant` tables in Postgres
- Presigned upload URL endpoint in Scala backend
- Direct browser → MinIO upload flow

### 2.2 Media Processing Pipeline

- Scala worker or separate service (could be a lightweight process using ZIO)
- Image processing: thumbnails, WebP conversion at multiple breakpoints, EXIF extraction
- PDF: first-page thumbnail, text extraction for search
- Video: poster frame extraction (optional, defer if not critical)
- Writes variants to MinIO, records in `media_variant` table

### 2.3 Media Library UI (Angular)

- Grid/list view of all media assets with thumbnails
- Upload dropzone (single + batch)
- Upload progress indicator
- Filter by type (image, document, video), date, uploader
- Detail panel: preview, metadata, variant list, usage (which content references this asset)
- Delete with orphan check

### 2.4 Media Picker Widget Integration

- Activate the `MediaRefField` widget in the dynamic form renderer
- Opens media library as a modal/drawer
- Supports selection, inline preview, alt-text editing
- Stores `media_asset.id` in content body_jsonb
- API response resolves asset IDs → CDN URLs with variant map

---

## Phase 3 — Author → Publish Pipeline

**Goal:** Separate authoring from delivery. Content flows from draft → reviewed → published with data sync to a read-optimized publish store.

**Duration:** 3–4 weeks

### 3.1 Publish Workflow

- Status state machine: `draft` → `in_review` → `published` → `archived`
- Configurable per content type (some types may skip review)
- Publish action triggers event (Postgres `NOTIFY` / application event bus)
- Unpublish / schedule publish (future timestamp)

### 3.2 Publish Data Sync

**Option A — Logical Replication (simpler):**
- Postgres logical replication slot filtered to published content
- Read replica serves the delivery tier
- Pros: native, low latency, transactional consistency
- Cons: same schema on both sides, publish DB includes draft tables (just empty)

**Option B — Event-Driven Promotion (more flexible):**
- Publish event triggers Scala service to write a denormalized JSON document to a `published_content` table (or separate database)
- JSON includes resolved media URLs, flattened relations, rendered rich text
- Pros: publish schema optimized for reads, decoupled
- Cons: more code to maintain, eventual consistency

**Recommended:** Start with Option A, migrate to Option B when performance or schema divergence demands it.

### 3.3 Search Index Sync

- On publish event: index content to Meilisearch
- On unpublish: remove from Meilisearch index
- Index fields: title, body (stripped of markup), slug, categories, tags, content type, author, dates
- Configure filterable attributes: content_type, status, categories, tags, created_at

### 3.4 Cache Layer

- Redis cache in front of publish database
- Cache key: `content:{type}:{slug}` → serialized JSON
- Invalidate on publish / unpublish events
- TTL as fallback safety net

---

## Phase 4 — SvelteKit Delivery & SSR

**Goal:** Public-facing website rendered server-side from CMS content, with template-based layouts and modern animations.

**Duration:** 4–6 weeks

### 4.1 SvelteKit Project Setup

- SvelteKit with adapter-node for SSR
- Consumes content from PostgREST/PostGraphile (publish database) or Scala API
- Template registry: maps content types → Svelte components

### 4.2 Template System

- Each content type gets a default Svelte template
- Templates are Svelte components that receive typed content as props
- Template overrides per slug (e.g., homepage gets a special layout)
- Layout hierarchy: base layout → content type layout → template → component slots

```
routes/
├── [contentType]/
│   └── [slug]/
│       └── +page.server.ts    -- load function: fetch content by type + slug
│       └── +page.svelte       -- dynamic template resolver
templates/
├── blog-post.svelte
├── product-page.svelte
├── landing-page.svelte
└── _default.svelte
```

### 4.3 Snippet / Component Rendering

- CMS delivers content blocks as structured JSON
- SvelteKit renders each block type with a corresponding component
- Supports embedding interactive islands (Three.js scenes, GSAP animations) within otherwise static content
- SSR renders the static shell; client hydrates interactive parts

### 4.4 Animation & Graphics Integration

- CSS transitions/animations as the default for motion (scroll-triggered via Intersection Observer)
- GSAP for complex sequenced animations (loaded client-side, progressive enhancement)
- Three.js for 3D scenes (rendered in `<canvas>`, loaded lazily)
- All animations degrade gracefully (content remains accessible without JS)

### 4.5 Search Integration

- Search page consumes Meilisearch directly (or via a thin proxy for API key protection)
- Instant search with typo tolerance
- Faceted filtering by content type, category, date range

---

## Phase 5 — Categories, Tags & Cataloguing

**Duration:** 2–3 weeks

- `taxonomy` table (id, slug, name, type: 'category' | 'tag' | 'custom')
- `taxonomy_term` table (id, taxonomy_id, slug, name, parent_id for hierarchy)
- `content_taxonomy` join table (content_id, term_id)
- Tree-based category editor in Angular admin
- Tag autocomplete in content editor
- Taxonomy-aware URL routes in SvelteKit (`/category/{slug}`, `/tag/{slug}`)
- Meilisearch faceting on taxonomy terms

---

## Phase 6 — User-Generated Content

**Duration:** 3–4 weeks

- Public-facing authoring: registration, profile, user dashboard
- UGC content types (blog posts, articles, comments, media galleries)
- Moderation workflow: submitted → under_review → approved → published
- Rate limiting, spam detection (basic heuristics + optional Akismet integration)
- User media uploads with size/type restrictions (separate MinIO bucket)
- Public profiles with authored content listings

---

## Cross-Cutting Concerns (Throughout All Phases)

### Testing Strategy

- **Unit tests:** Angular (Jasmine/Karma or Jest), Scala (ScalaTest / ZIO Test)
- **Integration tests:** PostgREST API tests, database migration tests
- **E2E tests:** Playwright for Angular admin flows, SvelteKit delivery flows
- **Schema validation tests:** ensure schema generation produces valid JSON Schema

### DevOps & Infrastructure

- Docker Compose for local development (Postgres, MinIO, Redis, Meilisearch, PostgREST, PostGraphile)
- CI/CD: GitHub Actions or GitLab CI
- Environment parity: staging mirrors production topology
- Infrastructure as Code (Terraform or Pulumi) for production deployment

### Security

- JWT with short-lived access tokens + refresh tokens
- CORS configuration for admin UI and delivery origins
- Content Security Policy headers on delivery tier
- Input sanitization on rich text fields (prevent XSS in stored HTML)
- Presigned URLs for media uploads (no direct MinIO access from browsers)
- Rate limiting on public APIs

---

## Timeline Summary

| Phase | Focus | Duration | Dependencies |
|---|---|---|---|
| **1.1** | Scaffold & dev environment | 1 week | — |
| **1.2** | Core database schema | 1 week | 1.1 |
| **1.3** | Content type builder UI | 3–4 weeks | 1.2 |
| **1.4** | Dynamic content editor | 3–4 weeks | 1.2, partially 1.3 |
| **1.5** | Auth & authorization | 1–2 weeks | 1.1 (parallel) |
| **2** | Media management & MinIO | 3–4 weeks | 1.4 |
| **3** | Author → Publish pipeline | 3–4 weeks | 1.4, 2 |
| **4** | SvelteKit delivery & SSR | 4–6 weeks | 3 |
| **5** | Categories & cataloguing | 2–3 weeks | 1.4 (can start earlier) |
| **6** | User-generated content | 3–4 weeks | 4, 5 |

**Phase 1 total: ~8–10 weeks** for a working content type builder + dynamic editor with versioning.

**Full project: ~6–8 months** to feature parity with a Sling-class CMS, assuming a small team (2–3 developers).

---

## Phase 1 Immediate Next Steps

1. **Set up the monorepo** — Angular workspace + Scala sbt project + Docker Compose
2. **Write the first Flyway migration** — `user_account`, `content_type`, `content_type_version` tables
3. **Configure PostgREST** — expose content_type endpoints with RLS
4. **Build the field palette component** — draggable field types, basic config panel
5. **Implement `toJsonSchema()` service** — convert UI field model → JSON Schema
6. **Build 3 field widgets** — TextField, NumberField, BooleanField as proof of the dynamic renderer
7. **Wire it end-to-end** — create a content type in the builder, create a content item using the generated form, save to Postgres, verify the JSON Schema validation works
