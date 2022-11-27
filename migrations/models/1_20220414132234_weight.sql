-- upgrade --
ALTER TABLE "product" ADD "weight" INT NOT NULL  DEFAULT 0;
-- downgrade --
ALTER TABLE "product" DROP COLUMN "weight";
