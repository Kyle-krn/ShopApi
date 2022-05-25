-- upgrade --
CREATE TABLE IF NOT EXISTS "telegramorder" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL,
    "tg_username" VARCHAR(255) NOT NULL,
    "first_name" VARCHAR(200) NOT NULL,
    "last_name" VARCHAR(200),
    "patronymic_name" VARCHAR(200),
    "phone_number" VARCHAR(15) NOT NULL,
    "region" VARCHAR(255) NOT NULL,
    "city" VARCHAR(255) NOT NULL,
    "address1" VARCHAR(255) NOT NULL,
    "address2" VARCHAR(255),
    "postcode" INT NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "shipping_type" VARCHAR(100) NOT NULL,
    "amount" DECIMAL(1000,2),
    "shipping_amount" DECIMAL(1000,2) NOT NULL  DEFAULT 0
);
CREATE TABLE IF NOT EXISTS "saleproduct" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "price" DECIMAL(1000,2) NOT NULL,
    "discount" DECIMAL(1000,2) NOT NULL  DEFAULT 0,
    "name" VARCHAR(200) NOT NULL,
    "quantity" INT NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "order_id" INT NOT NULL REFERENCES "telegramorder" ("id") ON DELETE CASCADE,
    "product_id" INT REFERENCES "product" ("id") ON DELETE SET NULL
);;
-- downgrade --
DROP TABLE IF EXISTS "saleproduct";
DROP TABLE IF EXISTS "telegramorder";
