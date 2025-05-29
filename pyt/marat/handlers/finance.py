from TAALC.decorators import msg_handler
from TAALC.roles.user import User
from TAALC.token.currency import Currency
from aiogram import types
from aiogram.enums.chat_type import ChatType

@msg_handler(r'(?i).*марат.*')
async def process_msg(message: types.Message, user: User, match):
    if 'пиво' in message.text.lower():
            await message.reply(f"где сходка?")
    else:
        await message.reply(f"{message.from_user.first_name} - шлюха")


@msg_handler(r'(?i)^марат,? передай')
async def give_currency(message: types.Message, user: User, match):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.answer("Я слишком богат, кого ты пытаешься подкупить, нищук?")

    if message.reply_to_message:
        msg_text = message.text.lower()

        msg_split = msg_text.split()
        cur_alias = msg_split[-1]
        currency = Currency.get_by_alias(cur_alias)
        amount = float(msg_split[-2])
        wallet_amount = user.wallet.amount(currency)
        if amount <= 0 or wallet_amount <= 0:
            await message.reply('А нахуй сходить не хочешь?')
            return
        
        if amount > wallet_amount:
            res = f"У тебя нет столько {currency.aliases[1]}, кого ты пытаешься наебать? "+\
                f"У тебя всего лишь {wallet_amount} грамм, иди поработай жопой, нищук."
            await message.reply(res)
            return

        to_user = User.user_by_tg_user(message.reply_to_message.from_user)
        transaction = user.send_currency(to_user, currency, amount)

        await message.reply_to_message.reply(f"{to_user}, {user} передал тебе {currency.aliases[1]}, "+ \
                            f"{amount} грамм, запрвляй баян")



@msg_handler(r'(?i)^марат,? петух')
async def check_ballance(message: types.Message, user: User, match):

    res = "А твоя мамка дешевая подзаборная шлюха, и что? " +\
        "Ну давай посмотрим сколько этот петушок заработал своим очком: \n"
    
    if not message.reply_to_message:
        return await message.reply('Сам ты петух! Тэгни сообщение чтобы проверить балланс пользователя')
        
    
    checked_user = User.user_by_tg_user(message.reply_to_message.from_user)            
    total = 0
    for cr in Currency.currencies():
        amt = checked_user.wallet.amount(cr)
        total += amt
        res += f'{cr.aliases[0]}: {amt} грамм \n'
    if total <= 300:
        res += f'Петушок {checked_user} похож на нищука, скоро пойдёт нахуй отсюда!'
    else:
        res += f'Похоже петушок {checked_user} неплохо работает жопой!'

    await message.reply(res)