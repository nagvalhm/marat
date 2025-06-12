from TAALC.decorators import msg_handler
from TAALC.tg_environment.t_user import TUser
from TAALC.finance.currency import Currency
from aiogram import types
from aiogram.enums.chat_type import ChatType
from TAALC.tg_environment.t_message import TMessage
from TAALC.bidding.message_offer import MessageOffer
from ..enums.marat_offer_state import MaratOfferState
from ..enums.marat_offer_type import MaratOfferType
from ..enums.marat_nft_state import MaratNftState
from TAALC.finance.taalc_nft import TaalcNft
from TAALC.finance.message_nft_token import MessageNftToken
from TAALC.finance.nft_transaction import NftTransaction
from TAALC.finance.currency_transaction import CurrencyTransaction
from TAALC.finance.transaction_batch import TransactionBatch
from TAALC.finance.message_transaction import MessageTransaction

# @msg_handler(r'(?i)покупаю,? .*')
@msg_handler(r'(?i)^покупаю,? (\d|\.)*')
async def offer(message: types.Message, user: TUser, match):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP) \
        or not message.reply_to_message:
        return await message.answer("Что ты пытаешься купить?")
    
    msg_text = message.text.lower()

    msg_split = msg_text.split()
    amount = float(msg_split[-1])

    solt = Currency.resource.read(name='Solt')[0]
    wallet_amount = user.wallet.amount(solt)
    if amount <= 0:
        return await message.reply('А нахуй сходить не хочешь?')
        
    
    if amount > wallet_amount:
        res = f"У тебя нет столько {solt.aliases[1]}, кого ты пытаешься наебать? "+\
            f"У тебя всего лишь {wallet_amount} грамм, иди поработай жопой, нищук."
        return await message.reply(res)
    
    
    replied_message = TMessage.get_t_message(message.reply_to_message)

    taalc_coin = Currency.resource.read(name='TAALC')[0]

    if replied_message.taalc_offer:
        return await reply_sell_offer(message, user, replied_message, amount, taalc_coin)

    return await reply_subject(message, user, replied_message, amount, taalc_coin)

@msg_handler(r'(?i)^согласен,? я - дешевая шлюха')
async def accept_offer(message: types.Message, user: TUser, match):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP) \
        or not message.reply_to_message:
        return await message.answer("С чем ты согласен?")    
      
    replied_message = TMessage.get_t_message(message.reply_to_message)

    taalc_offer = replied_message.taalc_offer
    if not (taalc_offer \
        and taalc_offer.offer_type in (MaratOfferType.BUY.value, MaratOfferType.SELL.value) \
        and taalc_offer.offer_state == MaratOfferState.IN_PROCESS.value):
        return await message.reply("С чем ты согласен? Сообщение не является действующим предложением покупки.")
    
    subject_mgs = taalc_offer.subject
    if taalc_offer.offer_type == MaratOfferType.BUY.value and\
          subject_mgs.owner.telegram_id != user.telegram_id:
        return await message.reply("Это не твое сообщение, петух!")
    
    buyer = None
    seller = None
    if taalc_offer.offer_type == MaratOfferType.BUY.value:
        buyer = taalc_offer.from_user
        seller = user
    else:
        buyer = user
        seller = taalc_offer.from_user
    
    solt = Currency.resource.read(name='Solt')[0]
    
    buyer_wallet_amount = buyer.wallet.amount(solt)
    price = taalc_offer.price
    if buyer_wallet_amount < price:
        return await message.reply(f"Поздно! {buyer} уже сторчал всю соль, у него всего лишь {buyer_wallet_amount} грамм")
    
    subject_msg = taalc_offer.subject

    marat = TUser.resource.read(username='MaaratBot')[0]
    honey = Currency.resource.read(name='Honey')[0]
    batch = TransactionBatch()
    solt_transaction = CurrencyTransaction(buyer, marat, solt, price, batch)
    honey_transaction = CurrencyTransaction(marat, seller, honey, price, batch)
    solt_transaction.save(True)
    honey_transaction.save(True)

    subject_msg.message_nft_token.nft_state = MaratNftState.FREE.value
    # subject_msg.taalc_offer = subject_msg.taalc_offer.data_id
    subject_msg.message_nft_token = subject_msg.message_nft_token.data_id
    # subject_msg.save(True)

    taalc_offer.offer_state = MaratOfferState.SOLD.value
    # taalc_offer.subject = taalc_offer.subject.data_id
    taalc_offer.offer_message = taalc_offer.offer_message.data_id
    taalc_offer.save(True)
    
    message_transaction = MessageTransaction(seller, buyer, subject_msg.message_nft_token, batch)
    message_transaction.save()
    res = f'поздравляю, теперь это <a href="{subject_msg.get_url()}">говно</a> принадлежит {buyer}, пусть делает с ним что хочет. \n'
    res += f'В течении суток сообщение будет опубликовано в сети TON как nft, а {seller} получит {taalc_offer.price} TAALC коинов'
    return await message.reply(res, parse_mode="HTML")
    
    
@msg_handler(r'(?i)^пошел нахуй,? чмоня')
async def decline_offer(message: types.Message, user: TUser, match):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP) \
        or not message.reply_to_message:
        return await message.answer("Иди сам на хуй")
    
    replied_message = TMessage.get_t_message(message.reply_to_message)
    
    if not (replied_message.taalc_offer \
        and replied_message.taalc_offer.offer_type == MaratOfferType.BUY.value \
        and replied_message.taalc_offer.offer_state == MaratOfferState.IN_PROCESS.value):
        return await message.reply("Иди сам на хуй, сообщение не является действующим предложением покупки.")
    
    subject_mgs = replied_message.taalc_offer.subject
    owner = subject_mgs.owner
    if owner.telegram_id != user.telegram_id:
        return await message.reply("Это не твое сообщение, петух!")
    
    replied_message.taalc_offer.offer_state = MaratOfferState.REJECTED.value
    replied_message.taalc_offer.save()

    return await message.reply(f'{owner} отказался продавать <a href="{subject_mgs.get_url()}">сообщение</a> в рамках текущих торгов.',
                               parse_mode='HTML')
    
@msg_handler(r'(?i)^продаю,? (\d|\.)*')
async def decline_offer(message: types.Message, user: TUser, match):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP) \
        or not message.reply_to_message:
        return await message.answer("Мамку свою продай")
    
    replied_message = TMessage.get_t_message(message.reply_to_message)
    
    if not (replied_message.taalc_offer \
        and replied_message.taalc_offer.offer_type == MaratOfferType.BUY.value \
        and replied_message.taalc_offer.offer_state == MaratOfferState.IN_PROCESS.value):
        return await message.reply("Мамку свою продай, сообщение не является действующим предложением покупки.")
    
    msg_text = message.text.lower()

    msg_split = msg_text.split()
    new_price = float(msg_split[-1])

    if new_price <= 0:
        return await message.reply('А нахуй сходить не хочешь?')
    
    old_offer = replied_message.taalc_offer

    subject_message = old_offer.subject

    if subject_message.owner.telegram_id != user.telegram_id:
        return await message.reply("Это не твое сообщение, петух!")
    
    owner = subject_message.owner
    if owner.telegram_id != user.telegram_id:
        return await message.reply("Это не твое сообщение, петух!")

    if new_price <= old_offer.price:
        return await message.reply("Предлагай цену выше, долбайоп!")

    buyer = old_offer.from_user
    solt = Currency.resource.read(name='Solt')[0]
    buyer_wallet_amount = buyer.wallet.amount(solt)

    if buyer_wallet_amount < new_price:
        return await message.reply(f"Поздно! {buyer} уже сторчал всю соль, у него всего лишь {buyer_wallet_amount} грамм")

    
    new_offer_message = TMessage.get_t_message(message)

    solt = Currency.resource.read(name='Solt')[0]

    
    new_offer = MessageOffer(\
        from_user = owner,
        to_user = buyer,
        offer_type = MaratOfferType.SELL.value,
        offer_state = MaratOfferState.IN_PROCESS.value,
        subject = subject_message,
        currency = solt,
        price = new_price,
        offer_message = new_offer_message.data_id
    )
    new_offer.save(True)
    old_offer.offer_state = MaratOfferState.REJECTED.value
    old_offer.offer_message = old_offer.offer_message.data_id
    old_offer.save(True)

    new_offer_message.taalc_offer = new_offer
    new_offer_message.save()

    return await message.reply(f'{buyer}, {user} поднял ставку на ' + \
                            f'<a href="{subject_message.get_url()}">сообщение</a> до '+\
                            f'{new_price} {solt.aliases[1]}', parse_mode="HTML")
    

    
@msg_handler(r'(?i)^марат,? чьё говно?')
async def decline_offer(message: types.Message, user: TUser, match):
    if message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP) \
        or not message.reply_to_message:
        return await message.answer("Папка твой - говно")
    
    replied_message = TMessage.get_t_message(message.reply_to_message)
    res = f'этот <a href="{replied_message.get_url()}">кусок говна</a> принадлежит {replied_message.owner}, '
    res += 'похоже, он балуется копро'
    return await message.reply(res, parse_mode="HTML")

    
async def reply_sell_offer(message: types.Message, user: TUser,
                       replied_msg: TMessage, new_price: float,
                       currency: Currency):
    
    old_offer = replied_msg.taalc_offer
    
    if not (old_offer.offer_state == MaratOfferState.IN_PROCESS.value and\
        old_offer.offer_type == MaratOfferType.SELL.value):
        
        return await message.reply(f'Это <a href="{message.reply_to_message.get_url()}">сообщение</a> '\
                                   + f'является торговым предложением со статусом {old_offer.offer_state} '\
                                    + f'типа {old_offer.offer_type} ' \
                                    + 'и не продаётся, долбайоп!', parse_mode="HTML")
    
    if new_price >= old_offer.price:
        return await message.reply("Предлагай цену ниже, долбайоп!")
    
    
    subject_message = old_offer.subject
    new_offer_message = TMessage.get_t_message(message)

    owner = subject_message.owner
    new_offer = MessageOffer(\
        from_user = user,
        to_user = owner,
        offer_type = MaratOfferType.BUY.value,
        offer_state = MaratOfferState.IN_PROCESS.value,
        subject = subject_message,
        currency = currency,
        price = new_price,
        offer_message = new_offer_message.data_id
    )
    new_offer.save(True)
    old_offer.offer_state = MaratOfferState.REJECTED.value
    old_offer.offer_message = old_offer.offer_message.data_id
    old_offer.save(True)

    new_offer_message.taalc_offer = new_offer
    new_offer_message.save()

    return await message.reply(f'{owner}, {user} опустил ставку на ' + \
                               f'<a href="{subject_message.get_url()}">сообщение</a> до '+\
                                f'{new_price} {currency.aliases[1]}', parse_mode="HTML")



    


async def reply_subject(message: types.Message, user: TUser,
                       subject_msg: TMessage, new_price: float,
                       currency: Currency):
    
    if subject_msg.message_nft_token and subject_msg.message_nft_token.nft_state != MaratNftState.FREE.value:
        return await message.reply(f'Это <a href="{message.reply_to_message.get_url()}">сообщение</a> '\
                                   + f'было продано или торгуется как nft со статусом {subject_msg.message_nft_token.nft_state} '\
                                    + 'и не продаётся, долбайоп!', parse_mode="HTML")
    
    if not subject_msg.message_nft_token:
        nft = TaalcNft.resource.read(name='taalc_mini_msg')
        if not nft:
            nft = TaalcNft(name='taalc_mini_msg')
            nft.save()
        else:
            nft = nft[0]
        nft_token = MessageNftToken()
        nft_token.nft_state = MaratNftState.ON_BIDDING.value
        subject_msg.message_nft_token = nft_token

    offer_message = TMessage.get_t_message(message)
    # to_user = TUser.user_by_tg_user(subject_msg.owner)
    owner = subject_msg.owner
    offer = MessageOffer(\
        from_user = user,
        to_user = owner,
        offer_type = MaratOfferType.BUY.value,
        offer_state = MaratOfferState.IN_PROCESS.value,
        subject = subject_msg,
        currency = currency,
        price = new_price,
        offer_message = offer_message.data_id
    )
    offer.save()
    offer_message.taalc_offer = offer.data_id
    offer_message.save()

    res = f'{owner}, {user} предлагает тебе продать это ' + \
            f'<a href="{subject_msg.get_url()}">сообщение</a> за '+\
            f'{new_price} {currency.aliases[1]}. После продажи оно перейдет к ' +\
            f'{user}, и он сможет делать с ним все что люди делают со своими сообщениями, ' +\
            'а ты будешь кикнут и обоссан за попытку его переслать.\n\n' +\
            'Чтобы принять предложение о покупке, реплайни его предложение сообщением "согласен, я - дешевая шлюха", ' +\
            'либо предложи свою цену, реплайнув предложение сообщением "продаю {цена}", например "продаю 200". ' +\
            'Если не хочешь продавать сообщение, реплайни предложение сообщением "пошел нахуй, чмоня"'

    return await message.reply(res, parse_mode="HTML")
