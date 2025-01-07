CREATE TABLE IF NOT EXISTS cryptocurrency_daily_prices (
    id SERIAL PRIMARY KEY,
    coin_id VARCHAR(50) NOT NULL,
    price_usd NUMERIC(20, 8) NOT NULL,
    date DATE NOT NULL,
    full_response JSONB NOT NULL,
    UNIQUE(coin_id, date)
);
