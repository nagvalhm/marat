from TAALC.decorators import msg_handler
from TAALC.tg_environment.t_user import TUser
from aiogram import types

@msg_handler(r'(?i).*марат.*')
async def process_msg(message: types.Message, user: TUser, match):
    if 'пиво' in message.text.lower():
            return await message.reply(f"где сходка?")
    else:
        return await message.reply(f"{message.from_user.first_name} - шлюха")