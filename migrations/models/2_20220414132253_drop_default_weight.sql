-- upgrade --
ALTER TABLE "product" ALTER COLUMN "weight" DROP DEFAULT;
-- downgrade --
ALTER TABLE "product" ALTER COLUMN "weight" SET DEFAULT 0;
