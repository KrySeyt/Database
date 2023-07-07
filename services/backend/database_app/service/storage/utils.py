import decimal
from decimal import Decimal

from aiohttp import ClientSession
from async_lru import alru_cache

from ...config import get_settings
from . import schema
from . import exceptions


# Exchange rates api JSON response example:
# {
# 'base': 'EUR',
#  'date': '2023-07-07',
#  'rates': {'AUD': 1.639843,
#            'CAD': 1.455524,
#            'MXN': 18.818486,
#            'PLN': 4.481929,
#            'USD': 1.089028},
#  'success': True,
#  'timestamp': 1688728803
#  }

@alru_cache(ttl=3600)
async def get_currency_course(
        first_currency: schema.Currency,
        second_currency: schema.Currency,
) -> decimal.Decimal:
    """
    :param first_currency:
    :param second_currency:
    :return: Exchange course for currency to another_currency. If one of currency unknown - return 0
    """

    if __debug__:
        response_json = {
            'base': 'EUR',
            'date': '2023-07-07',
            'rates': {
                'AED': 4.008051,
                'AUD': 1.638818,
                'BRL': 5.325988,
                'CAD': 1.452003,
                'CHF': 0.974357,
                'CLP': 879.750645,
                'CNY': 7.885376,
                'COP': 4599.499003,
                'CZK': 23.861087,
                'DKK': 7.449929,
                'EUR': 1,
                'GBP': 0.853273,
                'HKD': 8.540661,
                'HUF': 385.642006,
                'IDR': 16535.246493,
                'ILS': 4.038633,
                'INR': 90.153233,
                'JPY': 155.661603,
                'KRW': 1420.588891,
                'MXN': 18.702732,
                'MYR': 5.095315,
                'NOK': 11.673589,
                'NZD': 1.762955,
                'PHP': 60.594871,
                'PLN': 4.464846,
                'RON': 4.954331,
                'RUB': 99.980355,
                'SAR': 4.093722,
                'SEK': 11.904599,
                'SGD': 1.472207,
                'THB': 38.34389,
                'TRY': 28.408712,
                'TWD': 34.126436,
                'USD': 1.091191,
                'ZAR': 20.69241
            },
            'success': True,
            'timestamp': 1688738643
        }

    else:
        api_url = get_settings().currency_exchange_rates.api_url
        params = {
            "access_key": get_settings().currency_exchange_rates.api_key,
            "symbols": ",".join((first_currency.name, second_currency.name))
        }

        async with ClientSession() as session:
            async with session.get(rf"{api_url}/latest" , params=params) as response:
                response_json = await response.json()
                if not isinstance(response_json, dict):
                    raise exceptions.ExchangeRatesAPIWrongJson("exchangeratesapi.io json response has wrong schema")

                is_success = response_json.get("success", None)
                if not (200 <= response.status < 300) or not is_success:
                    raise exceptions.ExchangeRatesAPIError(f"Status code is {response.status}, success: {is_success}")

    if not isinstance(response_json["rates"], dict):
        raise exceptions.ExchangeRatesAPIWrongJson("exchangeratesapi.io json response has not 'rates' dict")

    try:
        first_curr_to_euro = Decimal(response_json["rates"][first_currency.name])
        second_curr_to_euro = Decimal(response_json["rates"][second_currency.name])
        return Decimal(1) / first_curr_to_euro * second_curr_to_euro
    except KeyError:
        raise exceptions.ExchangeRatesUnknownCurrency("Currency name is unknown")
