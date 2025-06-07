from pytest import fixture, mark
import pytest
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

def give_money_to_bots_migration(bot, currency):
    # user1 = TUser.resource.read(first_name = 'Никита', last_name = 'Сексова')[0]
    # from .. import __main__ as main
    # config = IniFile("./pyt/pyconfig.ini")
    # tested_bot = main.get_bot(config)

    from TAALC.tg_environment.t_user import TUser
    
    from TAALC.finance.currency_transaction import CurrencyTransaction

    # user1 = TUser.resource.read(username='test_user11_bot')[0]
    # user2 = TUser.resource.read(username='test_user22_bot')[0]
    marat = TUser.resource.read(username='MaaratBot')[0]
    me = TUser.resource.read(username='epyre')[0]
    
    tr = CurrencyTransaction(marat, bot, currency, 10000)
    tr.save()
    tr = CurrencyTransaction(marat, me, currency, 10000)
    tr.save()
    # tr = Transaction(marat, user2, solt, 10000)
    # tr.save()

@mark.asyncio
async def test_give_currency(user1, user2):
    user1 = await user1
    user2 = await user2

    res = await user1.msg('марат передай')
    assert res.response and 'кому ты пытаешься' in res.response.text.lower()

    with pytest.raises(Exception) as e_info:
        res1 = await user2.reply(res.orig, 'марат передай')
        a = 1
    assert 'there is no currency with передай alias' in e_info.value.args[0]
    # assert res1.response and 'there is no currency with передай alias' in res1.response.text.lower()

    from TAALC.finance.currency import Currency
    solt = Currency.resource.read(name='Solt')[0]
    if user2.t_user.wallet.amount(solt) < 100:
        give_money_to_bots_migration(user2.t_user, solt)
    

    res = await user2.reply(res.orig, 'марат передай 100 соли')
    assert res.response and 'передал тебе соли, 100.0 грамм' in res.response.text.lower()

    res = await user2.reply(res.orig, 'марат передай -100 соли')
    assert res.response and 'А нахуй сходить не хочешь?' in res.response.text


@mark.asyncio
async def test_check_ballance(user1, user2):
    user1 = await user1
    user2 = await user2

    res = await user1.msg('марат петух')
    assert res.response and 'Сам ты петух! Тэгни сообщение чтобы проверить балланс' in res.response.text

    res = await user2.reply(res.orig, 'марат петух')
    assert res.response and 'А твоя мамка дешевая подзаборная шлюха' in res.response.text
    assert res.response and 'медок' in res.response.text.lower()
    assert res.response and 'соль' in res.response.text.lower()