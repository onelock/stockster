BEGIN;
UPDATE stock_historical SET ath = date_ath;
UPDATE stock_historical SET date_ath = NULL;
COMMIT;