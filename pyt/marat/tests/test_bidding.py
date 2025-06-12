from pytest import fixture, mark
from TAALC.teest.tester import Tester
from epure.files import IniFile
from .. import __main__ as main

@fixture
async def user1():
    config = IniFile("./pyt/pyconfig.ini")
    tested_bot = main.get_bot(config)
    # tested_bot = None
    tested_bot.start()
    res = Tester(config.test_user1_token, tested_bot, config.test_chat_id)
    return res

@fixture
async def user2():
    config = IniFile("./pyt/pyconfig.ini")
    tested_bot = main.get_bot(config)
    # tested_bot = None
    tested_bot.start()
    res = Tester(config.test_user2_token, tested_bot, config.test_chat_id)
    return res

@mark.asyncio
async def test_offer(user1, user2):
    user1 = await user1
    user2 = await user2

    fail_offer = await user1.msg('покупаю 100')
    assert fail_offer.response and 'Что ты пытаешься купить?' in fail_offer.response.text

    to_sell = await user1.msg('сообщение на продажу')
    
    from TAALC.finance.currency import Currency
    taalc_coin = Currency.resource.read(name='TAALC')
    if not taalc_coin:
        taalc_coin = Currency(name='TAALC', \
                        aliases=['TAALC коины','TAALC коинов', 'TAALC коинов', 'TAALC коинов', 'TAALC коинам', 'TAALC коинов']).save()

    offer = await user2.reply(to_sell.orig, 'покупаю 100')
    assert offer.response and 'предлагает тебе продать это сообщение за' in offer.response.text
    assert offer.response and 'TAALC коинов. После продажи оно перейдет к' in offer.response.text
    assert offer.response and 'и он сможет делать с ним все что люди делают со своими сообщениями' in offer.response.text
    assert offer.response and 'а ты будешь кикнут и обоссан за попытку его переслать.' in offer.response.text
    assert offer.response and 'Чтобы принять предложение о покупке, реплайни его предложение сообщением "согласен, я - дешевая шлюха"' in offer.response.text
    assert offer.response and 'либо предложи свою цену, реплайнув предложение сообщением "продаю {цена}", например "продаю 200"' in offer.response.text
    
    accept = await user1.reply(offer.orig, 'согласен, я - дешевая шлюха')
    assert accept.response and 'поздравляю, теперь это говно принадлежит' in accept.response.text
    
    check_owner = await user2.reply(to_sell.orig, 'марат чьё говно?')
    assert check_owner.response and 'принадлежит' in check_owner.response.text
    assert check_owner.response and 'похоже, он балуется копро' in check_owner.response.text

    fail_offer = await user1.reply(offer.orig, 'покупаю 100')
    assert fail_offer.response and 'является торговым предложением со статусом' in fail_offer.response.text



    to_sell = await user1.msg('сообщение на продажу')

    offer = await user2.reply(to_sell.orig, 'покупаю 100')
    assert offer.response and 'предлагает тебе продать это сообщение за' in offer.response.text
    barging = await user1.reply(offer.orig, 'продаю 200')
    assert barging.response and 'поднял ставку на' in barging.response.text
    barging2 = await user2.reply(barging.orig, 'покупаю 150')
    assert barging2.response and 'опустил ставку на' in barging2.response.text
    barging3 = await user1.reply(barging2.orig, 'продаю 170')
    assert barging3.response and 'поднял ставку на' in barging3.response.text
    accept = await user2.reply(barging3.orig, 'согласен, я - дешевая шлюха')
    assert accept.response and 'поздравляю, теперь это говно принадлежит' in accept.response.text