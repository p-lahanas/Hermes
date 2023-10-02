import requests
import json

# TODO: FIX THE SAVE PATH FOR THIS FILE (relative path is wrong atm)
API_DATA_PATH = './saved_data/apis/'  # API data stored at path

SPORT = 'upcoming'  # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports
REGIONS = 'au'  # uk | us | eu | au. Multiple can be specified if comma delimited
# h2h | spreads | totals. Multiple can be specified if comma delimited
MARKETS = 'h2h,spreads'
ODDS_FORMAT = 'decimal'  # decimal | american
DATE_FORMAT = 'iso'  # iso | unix


class ApiBase():

    def __init__(self, api_key: str, endpoint: str):
        self._api_key = api_key
        self._endpoint = endpoint

    def _fetch_data(self, params=None):
        # Fetch data from the API endpoint
        pass

    def _parse_data(self, data):
        pass

    def _store_data(self, data):
        # data is json object of some type
        pass

    def _handle_errors(self):
        pass

    def get_data(self):
        pass

# TODO: FEED OUT the number of remaining requests for the API?


class ApiTheOdds(ApiBase):

    def _fetch_data(self, params=None):
        remaining_requests = None

        try:
            # Status of 429 is caused by rate limiting
            response = requests.get(self._endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # Check the usage quota
            print('Remaining requests',
                  response.headers['x-requests-remaining'])
            # print('Used requests', response.headers['x-requests-used'])

            remaining_requests = response.headers['x-requests-remaining']
        except requests.exceptions.RequestException as e:
            print(f'Error fetching data from the The Odds API: {e}')

        return data, remaining_requests

    def _store_data(self, data):
        try:
            with open(API_DATA_PATH + 'the_odds.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        except (FileNotFoundError, PermissionError) as e:
            print(f'Error accessing or modifying the file: {e}')
        except Exception as e:
            print(f'Error storing data: {e}')

    def get_data(self):
        params = {'api_key': self._api_key, 'regions': REGIONS, 'markets': MARKETS,
                  'oddsFormat': ODDS_FORMAT, 'dateFormat': DATE_FORMAT}
        data, remaining_reqs = self._fetch_data(params=params)
        self._store_data(data=data)

        return remaining_reqs
