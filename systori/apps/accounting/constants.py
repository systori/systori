# TODO: This constants file should be removed. Instead the tax and the schedule of accounts coding scheme
#       should be looked up dynamically at runtime.

from decimal import Decimal
from .account_codes import CODES

TAX_RATE = Decimal('0.19')

DEBTOR_CODE_RANGE = CODES['SKR03']['DEBTOR_RANGE']

BANK_CODE_RANGE = CODES['SKR03']['BANK_RANGE']

SKR03_BANK_CODE = CODES['SKR03']['BANK']  # Entry.GROSS
SKR03_PROMISED_PAYMENTS_CODE = CODES['SKR03']['PROMISED_PAYMENTS']  # Entry.GROSS
SKR03_PARTIAL_PAYMENTS_CODE = CODES['SKR03']['PARTIAL_PAYMENTS']  # Entry.NET
SKR03_TAX_PAYMENTS_CODE = CODES['SKR03']['TAX_PAYMENTS']  # Entry.TAX
SKR03_INCOME_CODE = CODES['SKR03']['INCOME']  # Entry.NET
SKR03_CASH_DISCOUNT_CODE = CODES['SKR03']['CASH_DISCOUNT']  # Entry.NET
