-- upgrade --
ALTER TABLE "telegramorder" DROP CONSTRAINT "fk_telegram_pickupse_a1bf9da1";
ALTER TABLE "telegramorder" RENAME COLUMN "pikcup_point_id" TO "pickup_point_id";
ALTER TABLE "telegramorder" ADD CONSTRAINT "fk_telegram_pickupse_3732fd0d" FOREIGN KEY ("pickup_point_id") REFERENCES "pickupsettings" ("id") ON DELETE SET NULL;
-- downgrade --
ALTER TABLE "telegramorder" DROP CONSTRAINT "fk_telegram_pickupse_3732fd0d";
ALTER TABLE "telegramorder" RENAME COLUMN "pickup_point_id" TO "pikcup_point_id";
ALTER TABLE "telegramorder" ADD CONSTRAINT "fk_telegram_pickupse_a1bf9da1" FOREIGN KEY ("pikcup_point_id") REFERENCES "pickupsettings" ("id") ON DELETE SET NULL;
