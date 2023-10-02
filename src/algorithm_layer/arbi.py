import pandas as pd
import json

# Link with some useful info:
# https://en.m.wikipedia.org/wiki/Arbitrage_betting#:~:text=The%20idea%20of%20arbitrage%20betting,used%20to%20obtain%20a%20profit.&text=on%20outcome%202%20at%20bookmaker%201%20would%20ensure%20the%20bettor%20a%20profit.


def the_odds_read_json(path) -> pd.DataFrame:
    # Reads in our collected json data from the odds api

    try:
        with open(path) as f:
            raw_json = json.load(f)

    except (FileNotFoundError, PermissionError) as e:
        print(f'Error accessing or modifying the file: {e}')
        return None
    except Exception as e:
        print(f'Error opening data: {e}')
        return None

    df = pd.json_normalize(raw_json, record_path=['bookmakers', 'markets', 'outcomes'],
                           meta=['id', 'sport_key', 'commence_time', 'sport_title', ['bookmakers', 'title'],
                                 ['bookmakers', 'key'], ['bookmakers', 'last_update'], ['bookmakers', 'markets', 'key']])
    return df


class TheOddsArbitrageDetector():
    def __init__(self):
        pass

    def _read_data(self) -> pd.DataFrame:
        return the_odds_read_json('./saved_data/apis/the_odds.json')

    def even_profit(self, df: pd.DataFrame) -> dict:
        # Iterate through each possible outcome (win, draw, lose) and then follow the equations
        # s1*o1 = s2*o2 = s3*o3
        # which means we can solve it for each one with

        num_outcomes = df.shape[0]
        ratios = {}

        for i in range(num_outcomes):
            divisor = 0

            for j in range(num_outcomes):
                divisor = divisor + \
                    (df.iloc[i]['price_df']/df.iloc[j]['price_df'])

            ratios[df.iloc[i]['name']] = 1/divisor

        return ratios

    def hedged_bet(self, df: pd.DataFrame):
        pass

    def find_arbitrage_opportunities(self) -> list:
        # returns a list of ArbitrageOpportunities

        df = self._read_data()
        # 1. Find the max odds for each outcome on an event from all bookmakers
        df = df.loc[df[df['bookmakers.markets.key'] == 'h2h'].groupby(['name', 'id'])[
            'price'].idxmax()]

        # 2. Sum the implied probabilities (1/odds)
        df['one-on-price'] = 1.0 / df['price']

        summed_odds = df.groupby(['id']).sum(numeric_only=True)

        # 3. If the result is less than 1, an opportunity exists
        arbi_opportunities = summed_odds[summed_odds['one-on-price'] < 1]

        # Combine arbi_opportunities into the same df
        combined = df.join(arbi_opportunities, on='id',
                           how='inner', lsuffix='_df', rsuffix='_arbi')

        # Iterate through each event and create an arbitrage opportunity object
        ids = df['id']
        ops = []

        for event_id in ids:
            relevant_info = combined[combined['id'] == event_id]

            if not relevant_info.empty:
                ops.append(relevant_info)

        return ops

    def opportunity_to_string(self, df: pd.DataFrame) -> str:
        '''
        Converts the gross Dataframe into a nice readable string for our message library
        '''
        arbi_string = ''
        for i in range(df.shape[0]):
            name = df.loc[i]['name']
            arbi_string = arbi_string + \
                'For OUTCOME: {} place bet proportion {} for EQUAL and {} if FAVOURED\n'.format(
                    name, self.even_profit(df)[name], 'TODO')

        return arbi_string


if __name__ == '__main__':
    # df = the_odds_read_json("../saved_data/apis/the_odds.json")
    # print(df['id'])
    test_obj = TheOddsArbitrageDetector()
    print(test_obj.find_arbitrage_opportunities())
