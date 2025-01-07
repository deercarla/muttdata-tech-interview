# Coin Geko Retriever - User Guide

This guide explains how to use the Coin Geko Retriever to retrieve historical cryptocurrency data from the CoinGecko API. The tool provides both single-day and bulk collection capabilities with real-time progress monitoring.

## Quick Start

### 1. Single Day Collection

Collect data for a specific cryptocurrency on a particular date:

```bash
python app.py single bitcoin 2024-01-15
```

This will:
- Download Bitcoin's data for January 15, 2024
- Save it to `coin_data/bitcoin_2024-01-15.json`
- Create log entries in `coin_geko_retriever.log`

Sample output:
```
2024-01-15 10:30:01 - INFO - CoinGecko API is available
2024-01-15 10:30:02 - INFO - Successfully processed bitcoin for 2024-01-15
```

Sample data file (`bitcoin_2024-01-15.json`):
```json
{
  "id": "bitcoin",
  "symbol": "btc",
  "name": "Bitcoin",
  "market_data": {
    "current_price": {
      "usd": 42800.23
    },
    "market_cap": {
      "usd": 837492847232.43
    }
    // ... more data
  }
}
```

### 2. Bulk Collection

Collect data for multiple cryptocurrencies over a date range:

```bash
python app.py bulk bitcoin ethereum cardano 2024-01-01 2024-01-15 --workers 5
```

This will:
- Download data for Bitcoin, Ethereum, and Cardano
- Cover dates from January 1 to January 15, 2024
- Use 5 parallel workers for faster processing
- Show a progress bar
- Save individual JSON files for each coin/date combination

Sample output:
```
Processing data: 100%|██████████| 45/45 [00:32<00:00, 1.40it/s]
2024-01-15 10:35:01 - INFO - Successfully processed bitcoin for 2024-01-01
2024-01-15 10:35:02 - INFO - Successfully processed ethereum for 2024-01-01
2024-01-15 10:35:03 - INFO - Successfully processed cardano for 2024-01-01
... more processing logs ...
```

Generated files:
```
coin_data/
├── bitcoin_2024-01-01.json
├── bitcoin_2024-01-02.json
├── ...
├── ethereum_2024-01-01.json
├── ethereum_2024-01-02.json
├── ...
├── cardano_2024-01-01.json
├── cardano_2024-01-02.json
└── ...
```

## Error Handling Examples

### 1. API Unavailability
```bash
$ python app.py single bitcoin 2024-01-15
2024-01-15 10:40:01 - ERROR - CoinGecko API is not available
```

### 2. Invalid Date Format
```bash
$ python app.py single bitcoin 2024/01/15
error: argument date: Invalid date format: 2024/01/15. Use YYYY-MM-DD
```

### 3. Invalid Coin Identifier
```bash
$ python app.py single invalid_coin 2024-01-15
2024-01-15 10:45:01 - ERROR - Failed to process invalid_coin for 2024-01-15: API returned 404 Not Found
```

## Progress Monitoring

For bulk operations, you can monitor progress in several ways:

1. Progress Bar:
```
Processing data: 67%|███████    | 30/45 [00:21<00:10, 1.42it/s]
```

2. Log File:
```
tail -f coin_geko_retriever.log
```

3. Real-time Console Output:
```
2024-01-15 11:00:01 - INFO - Successfully processed bitcoin for 2024-01-01
2024-01-15 11:00:02 - INFO - Successfully processed ethereum for 2024-01-01
...
```

## Data Storage Structure

The collected data is organized by date and coin:

```
project_root/
├── coin_data/
│   ├── bitcoin_2024-01-15.json
│   ├── ethereum_2024-01-15.json
│   └── cardano_2024-01-15.json
├── coin_geko_retriever.log
└── .env
```

## Performance Tips

1. Adjust Workers:
   - Increase workers for faster processing:
   ```bash
   python app.py bulk bitcoin ethereum 2024-01-01 2024-01-15 --workers 8
   ```
   - Decrease workers if you hit rate limits:
   ```bash
   python app.py bulk bitcoin ethereum 2024-01-01 2024-01-15 --workers 3
   ```

2. Bulk Processing:
   - Process multiple days at once instead of individual calls
   - Uses parallel processing for better performance
   - Shows progress bar for monitoring

## Troubleshooting

1. Check API Status:
```bash
python app.py single bitcoin 2024-01-15
# Should show API availability message
```

2. Verify Log Files:
```bash
tail -n 50 coin_geko_retriever.log  # Last 50 application log entries
```

3. Check Data Files:
```bash
ls -l coin_data/                # List all collected data files
cat coin_data/bitcoin_2024-01-15.json  # View specific data file
```

# Viewing Logs on Windows

While Unix-like systems use the `tail` command, Windows provides different methods to view log files.

## PowerShell Commands

### 1. View Last N Lines
```bash
# View last 50 lines of a log file
Get-Content -Tail 50 coin_geko_retriever.log

# For real-time monitoring (similar to tail -f)
Get-Content -Wait coin_geko_retriever.log
```

### 2. View Entire File
```bash
# View entire log file
Get-Content coin_geko_retriever.log

# Or using familiar Windows commands
type coin_geko_retriever.log
```

### 3. Search in Log File
```bash
# Search for specific text (like grep)
Select-String "ERROR" coin_geko_retriever.log
```

### 4. Monitor in Real-time with PowerShell
```bash
# Create a continuous monitoring loop
while (1) {
    Get-Content coin_geko_retriever.log -Tail 10 -Wait
}
```
