BEGIN;
ALTER TABLE stock_historical DROP COLUMN date_ath;
ALTER TABLE stock_historical ADD COLUMN date_ath DATE;
COMMIT;