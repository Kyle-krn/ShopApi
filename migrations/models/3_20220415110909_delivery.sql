-- upgrade --
CREATE TABLE IF NOT EXISTS "couriercitysettings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "city" VARCHAR(255) NOT NULL,
    "amount" INT NOT NULL
);;
CREATE TABLE IF NOT EXISTS "pickupsettings" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "city" VARCHAR(255) NOT NULL,
    "address" VARCHAR(255) NOT NULL,
    "latitude" DOUBLE PRECISION NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL
);-- downgrade --
DROP TABLE IF EXISTS "couriercitysettings";
DROP TABLE IF EXISTS "pickupsettings";
