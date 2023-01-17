-- Run this using sqlite3 stooges.db < create_stooges_db.sql

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS stooges (
    id          INTEGER PRIMARY KEY NOT NULL,
    name        TEXT,
    saying      TEXT
);
INSERT INTO STOOGES VALUES(null, "Moe", "Why, I oughta...");
INSERT INTO STOOGES VALUES(null, "Larry", "Hey, Moe!");
INSERT INTO STOOGES VALUES(null, "Curly", "Nyuk, nyuk, nyuk");
COMMIT;
