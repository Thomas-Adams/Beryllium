-- Beryl CMS — Database Initialization
-- This runs once when the Postgres container is first created.

DROP ROLE IF EXISTS beryl_admin;
CREATE ROLE beryl_admin WITH
  LOGIN
  SUPERUSER
  INHERIT
  CREATEDB
  CREATEROLE
  REPLICATION
  BYPASSRLS
  ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:jC9dryHNtEQTyaML5+X3qg==$yWjOFbCc2pma4zwpH3bvOydX+5Ozi2FIMMbe/JoL590=:x2Ybup5kEM7Prv19RJAkUgx9psBBK6sZRKZQkORIYac=';



-- DROP DATABASE IF EXISTS beryl;

CREATE DATABASE beryl
    WITH
    OWNER = beryl_admin
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS ltree;       -- tree path queries
CREATE EXTENSION IF NOT EXISTS pgcrypto;    -- gen_random_uuid(), crypt()
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS hstore;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;


-- DROP SCHEMA IF EXISTS history ;

CREATE SCHEMA IF NOT EXISTS history
    AUTHORIZATION beryl_admin;

-- DROP SCHEMA IF EXISTS history ;

CREATE SCHEMA IF NOT EXISTS main
    AUTHORIZATION beryl_admin;



-- Roles for PostgREST
DO $$
BEGIN
    CREATE ROLE beryl_anonymous NOLOGIN;
    CREATE ROLE beryl_editor NOLOGIN;
    CREATE ROLE beryl_manager NOLOGIN;
END
$$;

-- Grant beryl_admin the ability to switch to these roles (required by PostgREST)
GRANT beryl_anonymous TO beryl_admin;
GRANT beryl_editor TO beryl_admin;
GRANT beryl_manager TO beryl_admin;

-- Anonymous can read published content and statuses
-- (Actual table grants will be added after Alembic creates the tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA main GRANT SELECT ON TABLES TO beryl_anonymous;
ALTER DEFAULT PRIVILEGES IN SCHEMA history GRANT SELECT ON TABLES TO beryl_anonymous;

-- Editors can read/write content
ALTER DEFAULT PRIVILEGES IN SCHEMA main GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO beryl_editor;
ALTER DEFAULT PRIVILEGES IN SCHEMA history GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO beryl_editor;

ALTER DEFAULT PRIVILEGES IN SCHEMA main GRANT USAGE, SELECT ON SEQUENCES TO beryl_editor;
ALTER DEFAULT PRIVILEGES IN SCHEMA history GRANT USAGE, SELECT ON SEQUENCES TO beryl_editor;

-- Authors can read/write their own content (enforced via RLS later)
ALTER DEFAULT PRIVILEGES IN SCHEMA main GRANT SELECT, INSERT, UPDATE ON TABLES TO beryl_manager;
ALTER DEFAULT PRIVILEGES IN SCHEMA history GRANT SELECT, INSERT, UPDATE ON TABLES TO beryl_manager;

ALTER DEFAULT PRIVILEGES IN SCHEMA main GRANT USAGE, SELECT ON SEQUENCES TO beryl_manager;
ALTER DEFAULT PRIVILEGES IN SCHEMA history GRANT USAGE, SELECT ON SEQUENCES TO beryl_manager;

ALTER DATABASE beryl SET search_path TO main, public;