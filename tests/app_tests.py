#External imports
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import json
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from app import (
    validate_date,
    get_date_range,
    process_single_day,
    bulk_process
)


class TestCoinGekoRetriever(unittest.TestCase):
    def setUp(self):
        """Set up test cases - create mock objects"""
        self.mock_client = Mock()
        self.mock_pg = Mock()

    def test_validate_date(self):
        """Test date validation with valid and invalid dates"""
        # Test valid date
        valid_date = "2024-01-01"
        result = validate_date(valid_date)
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.strftime('%Y-%m-%d'), valid_date)

        # Test invalid date
        invalid_date = "2024/01/01"
        with self.assertRaises(Exception):
            validate_date(invalid_date)

    def test_get_date_range(self):
        """Test date range generation"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 3)
        dates = get_date_range(start_date, end_date)

        self.assertEqual(len(dates), 3)
        self.assertEqual(dates[0], datetime(2024, 1, 1))
        self.assertEqual(dates[-1], datetime(2024, 1, 3))

    @patch('builtins.open')
    def test_process_single_day_success(self, mock_open):
        """Test successful processing of a single day"""
        # Mock the file read operation
        mock_data = {
            'market_data': {
                'current_price': {
                    'usd': 50000.0
                }
            }
        }
        mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_data)

        # Mock successful download
        self.mock_client.download_coin_data_from.return_value = "test_file.json"

        result = process_single_day(
            self.mock_client,
            "bitcoin",
            datetime(2024, 1, 1),
            self.mock_pg
        )

        # Verify method calls
        self.mock_client.download_coin_data_from.assert_called_once()
        self.mock_pg.insert_daily_price.assert_called_once()
        self.mock_pg.update_