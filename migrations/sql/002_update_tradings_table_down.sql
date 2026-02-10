-- Revert column names
BEGIN;

ALTER TABLE stock_historical RENAME COLUMN ath TO year_high;
ALTER TABLE stock_historical RENAME COLUMN date_ath TO date_year_high;
ALTER TABLE stock_historical RENAME COLUMN one_day_change TO period_1d;
ALTER TABLE stock_historical RENAME COLUMN one_month_change TO period_1m;
ALTER TABLE stock_historical RENAME COLUMN year_to_date_change TO period_ytd;
ALTER TABLE stock_historical RENAME COLUMN one_year_change TO period_1y;

COMMIT;