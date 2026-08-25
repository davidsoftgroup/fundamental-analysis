# -*- coding: utf-8 -*-
"""
دریافت داده از کدال
"""
import requests
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def search_symbol(symbol):
    """جستجوی نماد در کدال"""
    url = f"https://search.codal.ir/api/search/v2/q?Symbol={symbol}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

def get_income_statement(issuer_code, from_date, to_date):
    """دریافت صورت سود و زیان"""
    url = "https://search.codal.ir/api/search/v2/income-statement"
    params = {"issuer": issuer_code, "fromDate": from_date, "toDate": to_date}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_balance_sheet(issuer_code, from_date, to_date):
    """دریافت ترازنامه"""
    url = "https://search.codal.ir/api/search/v2/balance-sheet"
    params = {"issuer": issuer_code, "fromDate": from_date, "toDate": to_date}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def get_new_notices():
    """دریافت اطلاعیه‌های جدید"""
    url = "https://search.codal.ir/api/search/v2/new-notices"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    return None

if __name__ == "__main__":
    # تست
    result = search_symbol("شپنا")
    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))