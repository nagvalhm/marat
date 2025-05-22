from ..token.currency import Currency

def migration():
    solt = Currency.resource.read(name='Solt')
    if not solt:
        Currency(name='Solt').save()

    honey = Currency.resource.read(name='Honey')
    if not honey:
        Currency(name='Honey').save()