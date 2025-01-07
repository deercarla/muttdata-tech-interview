# External imports
import argparse
import logging
import sys
from datetime import datetime, timedelta
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
import json
import tqdm

# Internal imports
from CoinGekoRetriever.coin_geko_retriever import CoinGekoRetriever
from PGConnector.pgconnector import PGConnector


def setup_logging(log_file: str = "coin_geko_retriever.log"):
    """Configure logging to both file and console"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def validate_date(date_str: str) -> datetime:
    """Validate ISO8601 date string"""
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def get_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """Generate list of dates between start and end dates"""
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    return dates


def process_single_day(client: CoinGekoRetriever,
                       coin_id: str,
                       date: datetime,
                       pg_connector: Optional[PGConnector] = None) -> Optional[str]:
    """
    Process data for a single coin and date

    :param client: CoinGecko retriever client
    :param coin_id: Cryptocurrency identifier
    :param date: Date to retrieve data for
    :param pg_connector: Optional PostgreSQL connector for storing data
    :return: Filename of downloaded data or None
    """
    logger = logging.getLogger(__name__)
    try:
        filename = client.download_coin_data_from(coin_id, date.strftime('%Y-%m-%d'))

        if pg_connector:
            with open(filename, 'r') as f:
                coin_data = json.load(f)

            price_usd = coin_data.get('market_data', {}).get('current_price', {}).get('usd', 0)

            pg_connector.insert_daily_price(
                coin_id=coin_id,
                price_usd=price_usd,
                date=date.strftime('%Y-%m-%d'),
                full_response=coin_data
            )

            pg_connector.update_monthly_aggregates(
                coin_id=coin_id,
                date=date.strftime('%Y-%m-%d'),
                price_usd=price_usd
            )

        logger.info(f"Successfully processed {coin_id} for {date.date()}")
        return filename
    except Exception as e:
        logger.error(f"Failed to process {coin_id} for {date.date()}: {str(e)}")
        return None


def bulk_process(client: CoinGekoRetriever,
                 coin_ids: List[str],
                 start_date: datetime,
                 end_date: datetime,
                 max_workers: int = 5,
                 pg_connector: Optional[PGConnector] = None) -> None:
    """
    Process multiple dates and coins in parallel

    :param client: CoinGecko retriever client
    :param coin_ids: List of cryptocurrency identifiers
    :param start_date: Start date for data retrieval
    :param end_date: End date for data retrieval
    :param max_workers: Number of parallel workers
    :param pg_connector: Optional PostgreSQL connector for storing data
    """
    logger = logging.getLogger(__name__)
    dates = get_date_range(start_date, end_date)
    total_tasks = len(dates) * len(coin_ids)

    logger.info(f"Starting bulk processing for {len(coin_ids)} coins over {len(dates)} days")

    tasks = [
        (coin_id, date)
        for date in dates
        for coin_id in coin_ids
    ]

    # Process tasks with progress bar
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single_day, client, coin_id, date, pg_connector): (coin_id, date)
            for coin_id, date in tasks
        }

        with tqdm.tqdm(total=total_tasks, desc="Processing data") as pbar:
            for future in as_completed(futures):
                coin_id, date = futures[future]
                try:
                    result = future.result()
                    if result:
                        logger.debug(f"Processed {coin_id} for {date.date()}")
                except Exception as e:
                    logger.error(f"Error processing {coin_id} for {date.date()}: {str(e)}")
                finally:
                    pbar.update(1)


def main():
    parser = argparse.ArgumentParser(description="Coin Geko Retriever")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Single day processing
    single_parser = subparsers.add_parser("single", help="Process single day")
    single_parser.add_argument("coin_id", help="Coin identifier (e.g., bitcoin)")
    single_parser.add_argument("date", type=validate_date, help="Date in ISO8601 format (YYYY-MM-DD)")
    single_parser.add_argument("--pg", action="store_true", help="Store data in PostgreSQL")

    # Bulk processing
    bulk_parser = subparsers.add_parser("bulk", help="Process date range")
    bulk_parser.add_argument("coin_ids", nargs="+", help="Coin identifiers (e.g., bitcoin ethereum)")
    bulk_parser.add_argument("start_date", type=validate_date, help="Start date (YYYY-MM-DD)")
    bulk_parser.add_argument("end_date", type=validate_date, help="End date (YYYY-MM-DD)")
    bulk_parser.add_argument("--workers", type=int, default=5, help="Number of parallel workers")
    bulk_parser.add_argument("--pg", action="store_true", help="Store data in PostgreSQL")

    args = parser.parse_args()

    logger = setup_logging()

    try:
        client = CoinGekoRetriever()
        pg_connector = None

        if not client.check_geko_api_status():
            logger.error("CoinGecko API is not available")
            sys.exit(1)

        # Initialize PostgreSQL connection if requested
        if getattr(args, 'pg', False):
            try:
                pg_connector = PGConnector('crypto_database')
                pg_connector.create_database()
                pg_connector.connect()
                pg_connector.create_tables()
            except Exception as e:
                logger.error(f"Failed to set up PostgreSQL connection: {e}")
                sys.exit(1)

        try:
            if args.command == "single":
                process_single_day(client, args.coin_id, args.date, pg_connector)
            elif args.command == "bulk":
                if args.start_date > args.end_date:
                    logger.error("Start date must be before or equal to end date")
                    sys.exit(1)
                bulk_process(
                    client,
                    args.coin_ids,
                    args.start_date,
                    args.end_date,
                    getattr(args, 'workers', 5),
                    pg_connector
                )
            else:
                parser.print_help()
                sys.exit(1)
        finally:
            if pg_connector:
                pg_connector.close_connection()

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()