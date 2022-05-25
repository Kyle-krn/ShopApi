-- upgrade --
ALTER TABLE "telegramorder" ADD "pikcup_point_id" INT;
ALTER TABLE "telegramorder" ADD CONSTRAINT "fk_telegram_pickupse_a1bf9da1" FOREIGN KEY ("pikcup_point_id") REFERENCES "pickupsettings" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "telegramorder" DROP CONSTRAINT "fk_telegram_pickupse_a1bf9da1";
ALTER TABLE "telegramorder" DROP COLUMN "pikcup_point_id";
