-- upgrade --
ALTER TABLE "telegramorder" ADD "status" VARCHAR(255) NOT NULL  DEFAULT 'Создано';
-- downgrade --
ALTER TABLE "telegramorder" DROP COLUMN "status";
