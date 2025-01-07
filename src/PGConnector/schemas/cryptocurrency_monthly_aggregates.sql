
CREATE TABLE IF NOT EXISTS cryptocurrency_monthly_aggregates (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    min_price NUMERIC(20, 8) NOT NULL,
    max_price NUMERIC(20, 8) NOT NULL,
    UNIQUE(coin_id, year, month)
);
        