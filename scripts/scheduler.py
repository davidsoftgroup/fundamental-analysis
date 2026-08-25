# -*- coding: utf-8 -*-
"""
زمان‌بندی اجرای خودکار به‌روزرسانی داده‌ها
"""
import time
import schedule
from scripts.update_database import update_company_data

def job():
    """کار اجرای به‌روزرسانی"""
    print("🔄 شروع به‌روزرسانی خودکار...")
    symbols = ["شپنا", "شتران", "فولاد", "کربن"]
    for symbol in symbols:
        update_company_data(symbol)
    print("✅ به‌روزرسانی خودکار کامل شد.")

# برنامه‌ریزی اجرا هر ۲۴ ساعت یکبار
schedule.every(24).hours.do(job)

if __name__ == "__main__":
    print("⏰ زمان‌بندی به‌روزرسانی خودکار شروع شد...")
    while True:
        schedule.run_pending()
        time.sleep(60)