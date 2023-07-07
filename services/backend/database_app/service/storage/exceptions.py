class EmployeeServiceNumberNotUnique(ValueError):
    pass


class EmployeeIDDoesntExist(ValueError):
    pass


class ExchangeRatesAPIError(IOError):
    pass


class ExchangeRatesUnknownCurrency(ValueError):
    pass


class ExchangeRatesAPIWrongJson(ValueError):
    pass
