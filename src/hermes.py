import os
import discord
import logging
import dotenv
import datetime

from discord.ext import commands, tasks

import data_layer.api
import algorithm_layer.arbi


class HermesState():
    def __init__(self, api_key, api_endpoint) -> None:
        self.odds_api = data_layer.api.ApiTheOdds(api_key, api_endpoint)
        self.arbi_detector = algorithm_layer.arbi.TheOddsArbitrageDetector()

    def _update_data(self):
        # Try fetch the data from our API
        return self.odds_api.get_data()

    def opportunities_message(self) -> str:
        # Query the API for updated odds
        remaining_reqs = self._update_data()

        # Run our algorithm that check for arbitrage opportunities
        arbi_opportunities = self.arbi_detector.find_arbitrage_opportunities()

        arbi_msg = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': '

        arbi_string = 'NONE' if len(arbi_opportunities) == 0 else ''
        for opportunity in arbi_opportunities:
            arbi_string += self.arbi_detector.opportunity_to_string(
                opportunity)

        return arbi_msg + arbi_string + '\n Number of the ODDS requests remaining {}'.format(remaining_reqs)


class HermesBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg_sent = False

        dotenv.load_dotenv()
        self.hermes = HermesState(api_key=os.getenv(
            'THE_ODDS_API_KEY'), api_endpoint=os.getenv('THE_ODDS_API_ENDPOINT'))
        self.arbi_channel = self.get_channel(1122214703901462530)

    async def on_ready(self):
        await self.timer.start(self.arbi_channel)

    @tasks.loop(seconds=1)
    async def timer(self, channel):
        time = datetime.datetime.now
        if time().hour == 12 and time().minute == 0 and not self.msg_sent:
            await channel.send(self.hermes.opportunities_message())
            self.msg_sent = True
        else:
            self.msg_sent = False


def init_logging():
    logging.basicConfig(filename='hermes.log',
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)


def main():
    init_logging()

    dotenv.load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    intents = discord.Intents().default()
    intents.message_content = True

    bot = HermesBot(command_prefix='!', intents=intents)
    logging.info('Hermes Bot up and Running')

    @bot.command(name='getodds')
    async def get_odds(ctx):
        await ctx.send(bot.hermes.opportunities_message())

    bot.run(TOKEN)


if __name__ == '__main__':
    main()