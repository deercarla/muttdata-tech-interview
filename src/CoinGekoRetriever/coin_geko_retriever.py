import os
import requests
import logging
from datetime import datetime
import json
from dotenv import load_dotenv


class CoinGekoRetriever:
    """
    A client for interacting with the CoinGecko API.
    Requires an API key stored in .env file as GEKO_API_KEY.
    """

    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        load_dotenv()
        self.api_key = os.getenv('GEKO_API_KEY')
        if not self.api_key:
            error_msg = "GEKO_API_KEY not found in environment variables"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.logger.info("CoinGeckoClient initialized successfully")

    def _make_request(self, endpoint, params=None):
        """
        Helper method to make API requests with the API key included.

        :param endpoint: API endpoint to request
        :param params: Optional query parameters dictionary
        """
        if params is None:
            params = {}

        params['x_cg_demo_api_key'] = self.api_key

        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise

    def check_geko_api_status(self):
        """
        Check if the CoinGecko API is operational by making a request to /ping endpoint
        Returns: bool indicating if API is operational
        """
        try:
            self._make_request('ping')
            self.logger.info("API status check successful")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API status check failed: {str(e)}")
            return False

    def download_coin_data_from(self, coin, date):
        """
        Download historical data for a specific coin on a given date.

        :param coin: Coin identifier (e.g., 'bitcoin')
        :param date: Date in ISO8601 format (YYYY-MM-DD)
        """
        try:
            parsed_date = datetime.fromisoformat(date)
            formatted_date = parsed_date.strftime('%d-%m-%Y')

            endpoint = f"coins/{coin}/history"
            data = self._make_request(endpoint, params={'date': formatted_date})

            os.makedirs('coin_data', exist_ok=True)

            filename = f"coin_data/{coin}_{date}.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"Successfully downloaded data for {coin} on {date}")
            return filename

        except ValueError as e:
            self.logger.error(f"Invalid date format: {str(e)}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download coin data: {str(e)}")
            raise
        except IOError as e:
            self.logger.error(f"Failed to save data to file: {str(e)}")
            raise


