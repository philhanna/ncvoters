PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE status_codes(
  status_cd TEXT,
  voter_status_desc TEXT
);
INSERT INTO status_codes VALUES('A','ACTIVE');
INSERT INTO status_codes VALUES('D','DENIED');
INSERT INTO status_codes VALUES('I','INACTIVE');
INSERT INTO status_codes VALUES('R','REMOVED');
INSERT INTO status_codes VALUES('S','TEMPORARY');
COMMIT;
