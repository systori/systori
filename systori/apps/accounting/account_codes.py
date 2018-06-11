# TODO: Store the chart of accounts coding scheme name in the Company object and then translate
#       the logical names to codes at runtime.
CODES = {
    "SKR03": {
        "DEBTOR_RANGE": (10000, 69999),
        "BANK_RANGE": (1200, 1288),
        "BANK": "1200",
        "PROMISED_PAYMENTS": "1710",
        "PARTIAL_PAYMENTS": "1718",
        "TAX_PAYMENTS": "1776",
        "INCOME": "8400",
        "CASH_DISCOUNT": "8736",
    }
}
