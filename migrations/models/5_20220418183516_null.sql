-- upgrade --
ALTER TABLE "telegramorder" ALTER COLUMN "postcode" DROP NOT NULL;
ALTER TABLE "telegramorder" ALTER COLUMN "address1" DROP NOT NULL;
ALTER TABLE "telegramorder" ALTER COLUMN "city" DROP NOT NULL;
ALTER TABLE "telegramorder" ALTER COLUMN "region" DROP NOT NULL;
-- downgrade --
ALTER TABLE "telegramorder" ALTER COLUMN "postcode" SET NOT NULL;
ALTER TABLE "telegramorder" ALTER COLUMN "address1" SET NOT NULL;
ALTER TABLE "telegramorder" ALTER COLUMN "city" SET NOT NULL;
ALTER TABLE "telegramorder" ALTER COLUMN "region" SET NOT NULL;
