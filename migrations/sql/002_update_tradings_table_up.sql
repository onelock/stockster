-- Rename columns
BEGIN;

ALTER TABLE stock_historical RENAME COLUMN year_high TO ath;
ALTER TABLE stock_historical RENAME COLUMN date_year_high TO date_ath;
ALTER TABLE stock_historical RENAME COLUMN period_1d TO one_day_change;
ALTER TABLE stock_historical RENAME COLUMN period_1m TO one_month_change;
ALTER TABLE stock_historical RENAME COLUMN period_ytd TO year_to_date_change;
ALTER TABLE stock_historical RENAME COLUMN period_1y TO one_year_change;

COMMIT;