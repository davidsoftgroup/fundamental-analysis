# -*- coding: utf-8 -*-
"""
سرویس پایش کدال - فقط از دیتابیس موجود استفاده می‌کند
"""

import sys
import os
import json
import requests
import time
import re
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# اضافه کردن مسیر اصلی
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection

class CodalMonitorService:
    """سرویس پایش کدال - یکپارچه با دیتابیس موجود"""
    
    def __init__(self):
        self.base_url = "https://search.codal.ir/api/search/v2/q"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive'
        }
        
        # ایجاد جدول‌های مورد نیاز برای پایش (اگر وجود نداشته باشند)
        self._init_monitor_tables()
    
    def _init_monitor_tables(self):
        """ایجاد جدول‌های مورد نیاز برای پایش"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # جدول تاریخچه پایش
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitor_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    check_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_symbols INTEGER DEFAULT 0,
                    checked_symbols INTEGER DEFAULT 0,
                    new_reports INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    details TEXT,
                    status TEXT DEFAULT 'completed'
                )
            """)
            
            # جدول گزارش‌های کدال
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS codal_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    tracing_no TEXT,
                    title TEXT,
                    letter_code TEXT,
                    report_type TEXT,
                    sent_date TEXT,
                    publish_date TEXT,
                    has_pdf INTEGER DEFAULT 0,
                    has_attachment INTEGER DEFAULT 0,
                    pdf_url TEXT,
                    attachment_url TEXT,
                    financial_year TEXT,
                    period_months INTEGER,
                    is_new INTEGER DEFAULT 1,
                    seen INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, tracing_no)
                )
            """)
            
            # ایندکس‌ها
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_codal_reports_symbol ON codal_reports(symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_codal_reports_sent_date ON codal_reports(sent_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_codal_reports_is_new ON codal_reports(is_new)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_monitor_history_date ON monitor_history(check_date)")
            
            conn.commit()
            conn.close()
            print("✅ جداول پایش کدال آماده شد")
        except Exception as e:
            print(f"⚠️ خطا در ایجاد جداول پایش: {e}")
    
    def get_all_symbols_from_db(self) -> List[Dict]:
        """
        دریافت همه نمادها از دیتابیس موجود (جدول companies)
        """
        try:
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # خواندن از جدول companies موجود
            cursor.execute("""
                SELECT symbol, name_fa as company_name, industry 
                FROM companies 
                ORDER BY symbol
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ خطا در دریافت نمادها از دیتابیس: {e}")
            return []
    
    def fetch_codal_data(self, symbol: str, max_retries: int = 3) -> Optional[Dict]:
        """دریافت داده‌های کدال برای یک نماد"""
        params = {
            "Symbol": symbol,
            "PageNumber": 1,
            "Audited": "true",
            "Mains": "true",
            "NotAudited": "true",
            "Childs": "true",
            "Publisher": "false",
            "Length": "-1",
            "search": "true",
            "CompanyState": 0,
            "CompanyType": -1,
            "Consolidatable": True,
            "IsNotAudited": False,
            "NotConsolidatable": True,
            "Category": -1,
            "AuditorRef": -1,
            "IndustryGroup": -1,
            "ReportingType": 1000000,
            "TracingNo": -1
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return None
                    
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    return None
        
        return None
    
    def parse_report_data(self, symbol: str, letter: Dict) -> Dict:
        """پردازش یک گزارش"""
        report_types = {
            "ن-13": "زمانبندی پرداخت سود",
            "ن-10": "اطلاعات و صورت‌های مالی",
            "ن-11": "گزارش فعالیت هیئت مدیره",
            "ن-30": "گزارش فعالیت ماهانه",
            "ن-26": "توضیحات در خصوص صورت‌های مالی",
            "ن-20": "افشای اطلاعات با اهمیت",
            "ن-42": "آگهی ثبت تصمیمات مجمع عادی سالیانه",
            "ن-52": "تصمیمات مجمع عمومی عادی سالیانه",
            "ن-51": "خلاصه تصمیمات مجمع عمومی سالیانه",
            "ن-50": "آگهی دعوت به مجمع عمومی",
            "ن-57": "تصمیمات مجمع عمومی فوق‌العاده",
            "ن-67": "آگهی ثبت افزایش سرمایه",
            "ن-60": "پیشنهاد هیئت مدیره جهت افزایش سرمایه",
            "ن-62": "مدارک و مستندات درخواست افزایش سرمایه",
            "ن-61": "اظهارنظر حسابرس در مورد افزایش سرمایه"
        }
        
        letter_code = letter.get("LetterCode", "")
        report_type = report_types.get(letter_code, letter_code)
        
        title = letter.get("Title", "")
        year_match = re.search(r'منتهی به\s+(\d{4})', title)
        financial_year = year_match.group(1) if year_match else None
        
        period_match = re.search(r'دوره\s+(\d+)\s+ماهه', title)
        period_months = int(period_match.group(1)) if period_match else None
        
        return {
            "symbol": symbol,
            "tracing_no": letter.get("TracingNo"),
            "title": title,
            "letter_code": letter_code,
            "report_type": report_type,
            "sent_date": letter.get("SentDateTime"),
            "publish_date": letter.get("PublishDateTime"),
            "has_pdf": 1 if letter.get("HasPdf", False) else 0,
            "has_attachment": 1 if letter.get("HasAttachment", False) else 0,
            "pdf_url": self._build_full_url(letter.get("PdfUrl")),
            "attachment_url": self._build_full_url(letter.get("AttachmentUrl")),
            "financial_year": financial_year,
            "period_months": period_months,
            "is_new": 1,
            "seen": 0
        }
    
    def _build_full_url(self, url: str) -> Optional[str]:
        """ساخت لینک کامل"""
        if not url:
            return None
        if url.startswith('http'):
            return url
        if url.startswith('/'):
            return f"https://www.codal.ir{url}"
        return f"https://www.codal.ir/{url}"
    
    def save_report_to_db(self, report_data: Dict) -> bool:
        """ذخیره گزارش در دیتابیس"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM codal_reports 
                WHERE symbol = ? AND tracing_no = ?
            """, (report_data.get('symbol'), report_data.get('tracing_no')))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE codal_reports SET
                        title = ?, letter_code = ?, report_type = ?,
                        sent_date = ?, publish_date = ?, has_pdf = ?,
                        has_attachment = ?, pdf_url = ?, attachment_url = ?,
                        financial_year = ?, period_months = ?
                    WHERE id = ?
                """, (
                    report_data.get('title'),
                    report_data.get('letter_code'),
                    report_data.get('report_type'),
                    report_data.get('sent_date'),
                    report_data.get('publish_date'),
                    report_data.get('has_pdf', 0),
                    report_data.get('has_attachment', 0),
                    report_data.get('pdf_url'),
                    report_data.get('attachment_url'),
                    report_data.get('financial_year'),
                    report_data.get('period_months'),
                    existing[0]
                ))
            else:
                cursor.execute("""
                    INSERT INTO codal_reports (
                        symbol, tracing_no, title, letter_code, report_type,
                        sent_date, publish_date, has_pdf, has_attachment,
                        pdf_url, attachment_url, financial_year, period_months,
                        is_new, seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_data.get('symbol'),
                    report_data.get('tracing_no'),
                    report_data.get('title'),
                    report_data.get('letter_code'),
                    report_data.get('report_type'),
                    report_data.get('sent_date'),
                    report_data.get('publish_date'),
                    report_data.get('has_pdf', 0),
                    report_data.get('has_attachment', 0),
                    report_data.get('pdf_url'),
                    report_data.get('attachment_url'),
                    report_data.get('financial_year'),
                    report_data.get('period_months'),
                    1,  # is_new
                    0   # seen
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره گزارش: {e}")
            return False
    
    def get_latest_report_from_db(self, symbol: str) -> Optional[Dict]:
        """دریافت آخرین گزارش ذخیره شده از دیتابیس"""
        try:
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM codal_reports 
                WHERE symbol = ? 
                ORDER BY sent_date DESC, created_at DESC 
                LIMIT 1
            """, (symbol,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"❌ خطا در دریافت آخرین گزارش: {e}")
            return None
    
    def check_symbol(self, symbol: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """بررسی یک نماد برای گزارش جدید"""
        try:
            data = self.fetch_codal_data(symbol)
            if not data:
                return False, None, "خطا در دریافت داده از کدال"
            
            letters = data.get("Letters", [])
            if not letters:
                return False, None, "هیچ گزارشی یافت نشد"
            
            latest_letter = letters[0]
            report_data = self.parse_report_data(symbol, latest_letter)
            
            last_report = self.get_latest_report_from_db(symbol)
            
            if not last_report:
                return True, report_data, "اولین گزارش"
            
            if last_report.get('tracing_no') == report_data.get('tracing_no'):
                return False, None, "گزارش تکراری"
            
            last_date = last_report.get('sent_date')
            new_date = report_data.get('sent_date')
            
            if last_date and new_date:
                last_num = self._date_to_number(last_date)
                new_num = self._date_to_number(new_date)
                
                if new_num <= last_num:
                    return False, None, "گزارش قدیمی‌تر"
            
            return True, report_data, None
            
        except Exception as e:
            return False, None, f"خطا: {str(e)}"
    
    def _date_to_number(self, date_str: str) -> int:
        """تبدیل تاریخ شمسی به عدد برای مقایسه"""
        try:
            if not date_str:
                return 0
            parts = date_str.split('/')
            if len(parts) >= 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2][:2])
                return (year * 10000) + (month * 100) + day
            return 0
        except:
            return 0
    
    def check_all_symbols(self, max_workers: int = 3) -> Dict:
        """بررسی تمام نمادها به صورت موازی"""
        # دریافت همه نمادها از دیتابیس موجود
        symbols = self.get_all_symbols_from_db()
        
        if not symbols:
            return {
                "total": 0,
                "checked": 0,
                "new_reports": 0,
                "errors": 0,
                "details": [],
                "status": "no_symbols",
                "message": "هیچ نمادی در دیتابیس یافت نشد"
            }
        
        results = {
            "total": len(symbols),
            "checked": 0,
            "new_reports": 0,
            "errors": 0,
            "details": [],
            "status": "completed"
        }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {
                executor.submit(self.check_symbol, symbol['symbol']): symbol['symbol']
                for symbol in symbols
            }
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                results["checked"] += 1
                
                try:
                    has_new, report_data, error = future.result()
                    
                    if has_new and report_data:
                        self.save_report_to_db(report_data)
                        results["new_reports"] += 1
                        results["details"].append({
                            "symbol": symbol,
                            "status": "new_report",
                            "report_type": report_data.get('report_type'),
                            "sent_date": report_data.get('sent_date'),
                            "title": report_data.get('title')[:80] + "..." if len(report_data.get('title', '')) > 80 else report_data.get('title'),
                            "has_pdf": report_data.get('has_pdf'),
                            "has_attachment": report_data.get('has_attachment')
                        })
                    elif error and ("خطا" in error or "error" in error.lower()):
                        results["errors"] += 1
                        results["details"].append({
                            "symbol": symbol,
                            "status": "error",
                            "message": error
                        })
                    else:
                        results["details"].append({
                            "symbol": symbol,
                            "status": "no_change",
                            "message": error or "بدون تغییر"
                        })
                        
                except Exception as e:
                    results["errors"] += 1
                    results["details"].append({
                        "symbol": symbol,
                        "status": "error",
                        "message": str(e)
                    })
        
        self.save_check_history(results)
        return results
    
    def save_check_history(self, results: Dict) -> bool:
        """ذخیره تاریخچه بررسی"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO monitor_history (
                    total_symbols, checked_symbols, new_reports,
                    errors, details, status
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                results.get('total', 0),
                results.get('checked', 0),
                results.get('new_reports', 0),
                results.get('errors', 0),
                json.dumps(results.get('details', [])),
                results.get('status', 'completed')
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره تاریخچه: {e}")
            return False
    
    def get_check_history(self, limit: int = 10) -> List[Dict]:
        """دریافت تاریخچه بررسی‌ها"""
        try:
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM monitor_history 
                ORDER BY check_date DESC 
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ خطا در دریافت تاریخچه: {e}")
            return []
    
    def get_new_reports(self, symbol: str = None) -> List[Dict]:
        """دریافت گزارش‌های جدید"""
        try:
            conn = get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                    SELECT * FROM codal_reports 
                    WHERE symbol = ? AND is_new = 1
                    ORDER BY sent_date DESC
                """, (symbol,))
            else:
                cursor.execute("""
                    SELECT * FROM codal_reports 
                    WHERE is_new = 1
                    ORDER BY sent_date DESC
                """)
            
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"❌ خطا در دریافت گزارش‌های جدید: {e}")
            return []
    
    def mark_reports_as_seen(self, symbol: str = None) -> int:
        """علامت‌گذاری گزارش‌ها به عنوان دیده شده"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if symbol:
                cursor.execute("""
                    UPDATE codal_reports 
                    SET is_new = 0, seen = 1
                    WHERE symbol = ? AND is_new = 1
                """, (symbol,))
            else:
                cursor.execute("""
                    UPDATE codal_reports 
                    SET is_new = 0, seen = 1
                    WHERE is_new = 1
                """)
            
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            return affected
        except Exception as e:
            print(f"❌ خطا در علامت‌گذاری: {e}")
            return 0
    
    def get_statistics(self) -> Dict:
        """دریافت آمار از دیتابیس"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # تعداد نمادها از جدول companies
            cursor.execute("SELECT COUNT(*) FROM companies")
            total_symbols = cursor.fetchone()[0]
            
            # تعداد گزارش‌ها
            cursor.execute("SELECT COUNT(*) FROM codal_reports")
            total_reports = cursor.fetchone()[0]
            
            # تعداد گزارش‌های جدید
            cursor.execute("SELECT COUNT(*) FROM codal_reports WHERE is_new = 1")
            new_reports = cursor.fetchone()[0]
            
            # آخرین بررسی
            cursor.execute("""
                SELECT check_date, new_reports, total_symbols 
                FROM monitor_history 
                ORDER BY check_date DESC 
                LIMIT 1
            """)
            last_check = cursor.fetchone()
            
            conn.close()
            
            return {
                "total_symbols": total_symbols or 0,
                "total_reports": total_reports or 0,
                "new_reports": new_reports or 0,
                "last_check": last_check[0] if last_check else None,
                "last_check_new_reports": last_check[1] if last_check else 0,
                "last_check_symbols": last_check[2] if last_check else 0
            }
        except Exception as e:
            print(f"❌ خطا در دریافت آمار: {e}")
            return {
                "total_symbols": 0,
                "total_reports": 0,
                "new_reports": 0,
                "last_check": None,
                "last_check_new_reports": 0,
                "last_check_symbols": 0
            }