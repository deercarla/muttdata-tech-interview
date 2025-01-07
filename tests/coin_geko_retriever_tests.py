#External imports:
import pytest
import os
import json
from unittest.mock import patch, mock_open
from datetime import datetime
import requests
from requests.exceptions import RequestException
from freezegun import freeze_time

#Internal imports:
from src.CoinGekoRetriever.coin_geko_retriever import CoinGekoRetriever


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Fixture to set up environment variables"""
    monkeypatch.setenv('GEKO_API_KEY', 'test_api_key_123')


@pytest.fixture
def client(mock_env_vars):
    """Fixture to create a client instance"""
    return CoinGekoRetriever()


@pytest.fixture
def sample_coin_data():
    """Fixture with sample coin historical data"""
    return {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "market_data": {
            "current_price": {
                "usd": 14000.0
            },
            "market_cap": {
                "usd": 234234234.0
            }
        }
    }


class TestCoinGekoClient:
    """Test suite for CoinGeckoClient"""

    def test_init_missing_api_key(self, monkeypatch):
        """Test initialization fails when API key is missing"""

        monkeypatch.delenv('GEKO_API_KEY', raising=False)
        monkeypatch.setattr(os, 'getenv', lambda key: None)

        with pytest.raises(ValueError) as exc_info:
            CoinGekoRetriever()
        assert "GEKO_API_KEY not found in environment variables" in str(exc_info.value)

    def test_init_success(self, client):
        """Test successful initialization"""
        assert client.api_key == 'test_api_key_123'

    @patch('requests.get')
    def test_check_geko_api_status_success(self, mock_get, client):
        """Test successful API status check"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"geko_says": "(V3) To the Moon!"}

        assert client.check_geko_api_status() is True
        mock_get.assert_called_once_with(
            f"{client.BASE_URL}/ping",
            params={'x_cg_demo_api_key': 'test_api_key_123'}
        )

    @patch('requests.get')
    def test_check_geko_api_status_failure(self, mock_get, client):
        """Test failed API status check"""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        assert client.check_geko_api_status() is False

    @patch('requests.get')
    @freeze_time("2024-01-15")
    def test_download_coin_data_success(self, mock_get, client, sample_coin_data, tmp_path):
        """Test successful coin data download"""

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = sample_coin_data

        coin_data_dir = tmp_path / "coin_data"
        os.makedirs(coin_data_dir, exist_ok=True)


        with patch('os.makedirs') as mock_makedirs, \
                patch('builtins.open', mock_open()) as mock_file_open:
            filename = client.download_coin_data_from('bitcoin', '2024-01-15')


            mock_get.assert_called_once_with(
                f"{client.BASE_URL}/coins/bitcoin/history",
                params={
                    'date': '15-01-2024',
                    'x_cg_demo_api_key': client.api_key
                }
            )

            mock_makedirs.assert_called_once_with('coin_data', exist_ok=True)
            assert filename == 'coin_data/bitcoin_2024-01-15.json'
            mock_file_open.assert_called_once_with('coin_data/bitcoin_2024-01-15.json', 'w')

    @patch('requests.get')
    def test_download_coin_data_invalid_date(self, mock_get, client):
        """Test download with invalid date format"""
        with pytest.raises(ValueError):
            client.download_coin_data_from('bitcoin', 'invalid-date')

        mock_get.assert_not_called()

    @patch('requests.get')
    def test_download_coin_data_api_error(self, mock_get, client):
        """Test download with API error"""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        with pytest.raises(requests.exceptions.RequestException):
            client.download_coin_data_from('bitcoin', '2024-01-15')

    @patch('requests.get')
    def test_make_request_adds_api_key(self, mock_get, client):
        """Test that _make_request adds API key to parameters"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": "test"}

        client._make_request('test-endpoint', {'param1': 'value1'})

        mock_get.assert_called_once_with(
            f"{client.BASE_URL}/test-endpoint",
            params={
                'param1': 'value1',
                'x_cg_demo_api_key': 'test_api_key_123'
            }
        )

    @patch('requests.get')
    def test_make_request_handles_error(self, mock_get, client):
        """Test that _make_request handles API errors properly"""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")

        with pytest.raises(requests.exceptions.RequestException):
            client._make_request('test-endpoint')