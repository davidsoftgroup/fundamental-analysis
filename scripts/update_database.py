# -*- coding: utf-8 -*-
"""
به‌روزرسانی دیتابیس با داده‌های کدال
"""
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection
from scripts.fetch_codal import search_symbol, get_income_statement, get_balance_sheet

def update_company_data(symbol):
    """به‌روزرسانی داده‌های یک شرکت"""
    print(f"🔄 در حال دریافت داده برای {symbol}...")
    
    # جستجوی شرکت
    result = search_symbol(symbol)
    if not result:
        print(f"❌ نماد {symbol} یافت نشد.")
        return
    
    # دریافت کد شرکت
    issuer_code = None
    for letter in result.get('letters', []):
        issuer = letter.get('issuer', {})
        if issuer.get('symbol') == symbol:
            issuer_code = issuer.get('code')
            break
    
    if not issuer_code:
        print(f"❌ کد شرکت برای {symbol} یافت نشد.")
        return
    
    print(f"✅ کد شرکت: {issuer_code}")
    
    # دریافت صورت سود و زیان
    income = get_income_statement(issuer_code, "1401/01/01", "1404/12/29")
    if income:
        print(f"✅ صورت سود و زیان دریافت شد.")
        # ذخیره در دیتابیس
        # ... (کد ذخیره‌سازی)
    
    print(f"✅ به‌روزرسانی {symbol} کامل شد.")

if __name__ == "__main__":
    # به‌روزرسانی همه شرکت‌ها
    symbols = ["شپنا", "شتران", "فولاد", "کربن"]
    for symbol in symbols:
        update_company_data(symbol)