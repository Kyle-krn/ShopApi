-- upgrade --
ALTER TABLE "telegramorder" ADD "pickup_code" INT;
-- downgrade --
ALTER TABLE "telegramorder" DROP COLUMN "pickup_code";
