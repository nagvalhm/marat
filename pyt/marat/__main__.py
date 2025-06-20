from TAALC import TaalcBot
from epure.files import IniFile
import asyncio
import argparse
from epure.dbs import GresDb
from .handlers.general import *
from .handlers.finance import *
from .handlers.administration import *
from .handlers.bidding import *

class Config:
    pass

def get_bot(config):
    from TAALC.bidding.message_offer import MessageOffer
    from TAALC.finance.message_nft_token import MessageNftToken
    db = GresDb(config.db_conn_str,
        log_level=config.log_level, 
        default_namespace=config.default_namespace)
    db.connect()
    
    bot = TaalcBot(config.bot_token, db, config)    
    return bot

if __name__ == '__main__':
    # config = IniFile('./pyconfig.ini')    
    parser = argparse.ArgumentParser(description='bot token')
    parser.add_argument('--token', type=str, help='bot token', required=False)
    parser.add_argument('--config', type=str, help='configuration file', required=False)
    args = parser.parse_args()
    # config = {'bot_token': args.token}

    config = Config()
    if hasattr(args, 'token') and args.token:
        config.bot_token = args.token
    if hasattr(args, 'config') and args.config:
        config = IniFile(args.config)

    bot = get_bot(config)
    bot.start()
