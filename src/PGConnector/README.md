# PostgreSQL Connector

A simple Python class for managing PostgreSQL database connections and cryptocurrency price data.

## Main Features

- Database creation and connection management
- Automatic table creation from SQL schema files
- Daily cryptocurrency price data insertion
- Monthly price aggregation
- Query execution with Pandas DataFrame output

## Setup

1. Create a `.env` file with your database credentials:
```
PG_HOST=localhost
PG_PORT=5432
PG_USER=your_username
PG_PASSWORD=your_password
```

2. Place your SQL schema files in a `./schemas` directory

## Basic Usage

```python
from src.PGConnector.pgconnector import PGConnector

# Initialize and connect
db = PGConnector('crypto_database')
db.create_database()
db.connect()

# Insert price data
db.insert_daily_price(
    coin_id='bitcoin',
    price_usd=50000.50,
    date='2024-01-01',
    full_response={'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin'}
)

# Close connection
db.close_connection()
```

