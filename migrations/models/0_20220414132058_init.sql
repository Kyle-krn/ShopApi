-- upgrade --
CREATE TABLE IF NOT EXISTS "usermodel" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(1024) NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT True,
    "is_superuser" BOOL NOT NULL  DEFAULT False,
    "is_verified" BOOL NOT NULL  DEFAULT False
);
CREATE INDEX IF NOT EXISTS "idx_usermodel_email_7287ba" ON "usermodel" ("email");
CREATE TABLE IF NOT EXISTS "category" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(200) NOT NULL UNIQUE,
    "slug" VARCHAR(200) NOT NULL UNIQUE,
    "filters" JSONB,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "parent_id" INT REFERENCES "category" ("id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "product" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(200) NOT NULL UNIQUE,
    "price" DECIMAL(1000,2) NOT NULL,
    "discount" DECIMAL(1000,2) NOT NULL  DEFAULT 0,
    "description" TEXT NOT NULL,
    "slug" VARCHAR(200) NOT NULL UNIQUE,
    "photo" JSONB NOT NULL,
    "is_active" BOOL NOT NULL  DEFAULT False,
    "quantity" INT NOT NULL  DEFAULT 0,
    "attributes" JSONB NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "category_id" INT REFERENCES "category" ("id") ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
