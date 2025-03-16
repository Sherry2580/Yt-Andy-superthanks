import os
import csv
import json
from datetime import datetime

def get_formatted_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def calculate_average(values):
    if not values:
        return 0
    return sum(values) / len(values)

def get_currency_symbol(currency_code):
    symbols = {
        'USD': 'US$',
        'TWD': '$',
        'CAD': 'CA$',
        'HKD': 'HK$',
        'SGD': 'SGD',
        'MYR': 'MYR',
        'JPY': '¥',
        'AUD': 'AU$',
        'GBP': '£',
        'EUR': '€',
        'NZD': 'NZ$',
        'PHP': 'PHP',
        'THB': 'THB',
        'IDR': 'IDR',
        'TRY': 'TRY'
    }
    return symbols.get(currency_code, currency_code)