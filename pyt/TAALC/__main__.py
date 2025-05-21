from .bots.telegram_bot import TelegramBot
# from epure.files import IniFile
import asyncio
import argparse

class Config:
    pass

if __name__ == '__main__':
    # config = IniFile('./pyconfig.ini')
    parser = argparse.ArgumentParser(description='bot token')
    parser.add_argument('--token', type=str, help='bot token', required=True)
    args = parser.parse_args()
    # config = {'bot_token': args.token}
    config = Config()
    config.bot_token = args.token
    bot = TelegramBot(config)
    asyncio.run(bot.start())