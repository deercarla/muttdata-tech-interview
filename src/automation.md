# Cryptocurrency Data Scheduler

This guide explains how to set up automated daily cryptocurrency data collection on Windows.

The .bat script runs the data collection for Bitcoin, Ethereum, and Cardano. It stores data in the already created PostgreSQL database.

The reason why I did not include CRON is because (to my understanding) it works with linux and I am currently working on Windows. While I am familiar with linux, I did not feel comfortable handing in a code I had not tested. So I searched for the Windows equivalent. 

### Windows Task Scheduler Configuration

1. **Create Basic Task**
   - Open Task Scheduler
   - Click "Create Basic Task"
   - Name: "Daily Crypto Data Retrieval"
   - Set to run daily at 3:00 AM

2. **Configure Task Properties**
   - Right-click task → Properties
   - Set to run with admin privileges
   - Enable running when user is logged out
   - Enable wake computer to run
   - Set up to retry 3 times if fails

## Troubleshooting
- Check Windows Event Viewer for any task execution errors
- Ensure PostgreSQL service is running
- Verify Python environment is correctly set up
- Make sure all paths in batch file are correct

## Requirements
- Windows OS
- Python installed
- PostgreSQL database
- Admin privileges for task scheduling