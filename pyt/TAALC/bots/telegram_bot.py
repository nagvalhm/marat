from .worker import Worker
from aiogram import Bot, Dispatcher, types
# from asyncio import sleep, ensure_future, create_task
# from .statistic_bot import StatisticBot
# from .trading_bot import TradingBot
from epure.files import IniFile
from aiogram.filters.command import Command


class TelegramBot(Worker):
    bot_token:str
    telegram_api:Bot
    dsp:Dispatcher
    config:IniFile

    def __init__(self, config:IniFile):
        self.bot_token = config.bot_token
        self.config = config
        self.telegram_api = Bot(self.bot_token)        
        self.dsp = Dispatcher()
        # self.dsp.message(self.init_user_chat, commands=['start'])    
        self.dsp.message(Command("start"))(self.init_user_chat)    
        # self.dsp.register_message_handler(self.trade, commands=['trade'])
        # self.dsp.register_message_handler(self.stats, commands=['stats'])
        # self.dsp.register_message_handler(self.stop, commands=['stop'])
        # self.dsp.register_message_handler(self.message_handler)        
  
    # @dsp.message(Command("start"))
    async def init_user_chat(self, message: types.Message):
        # self.start_stats(self.telegram_api)        
        await message.reply("Добро пожаловать на сервер шизофрения :)))000")
        
    async def start(self):
        await self.dsp.start_polling(self.telegram_api, skip_updates=True)

    # async def init_user_chat(self, message):
    #     await message.reply("Добро пожаловать на сервер шизофрения :)))000")

    # async def trade(self, message):
    #     # answer = await dp.bot.send_message(dp.chat.id, 'введите логины и пароли:')
    #     bot = TradingBot(self.config)
    #     bot.start()

    # def start_stats(self, bot):
    #     if not (hasattr(self,'statistic_bot') and self.statistic_bot):
    #         self.statistic_bot = StatisticBot(self.config, bot)
    #     self.statistic_bot.start()

    # async def stats(self, message):
    #     await message.reply("статистика запускается...")
    #     self.start_stats(message.bot)
    #     await message.reply("статистика запущена")

    async def stop(self, message):
        if hasattr(self, "statistic_bot") and not self.statistic_bot == None:
            self.statistic_bot.stop()
            await message.reply("статистика остановлена")
        else:
            await message.reply("ты пес обоссаный")

    async def message_handler(self, dp: Dispatcher):
        await dp.bot.send_message(dp.chat.id, 'собачка')