# -*- coding: utf-8 -*-
"""
تست مستقیم تابع save_meeting_decision
"""

import sys
import os
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.database import get_connection, save_meeting_decision

def test_save():
    print("=" * 60)
    print("🧪 تست مستقیم save_meeting_decision")
    print("=" * 60)
    
    # داده تست
    test_data = {
        'symbol': 'شسپا',
        'year_solar': 1403,
        'capital': 56000000,
        'net_profit': 195495785,
        'retained_earnings': 195495785,
        'approved_dividend': 112000000,
        'eps': 3491,
        'dps': 2000,
        'dividend_percent': 57.3,
        'meeting_date': '1403/04/15',
        'decision_date': '1403/04/15',
        'is_approved': 1,
        'notes': 'تست مستقیم',
        'source': 'تست'
    }
    
    print("\n📝 داده تست:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    # 1. بررسی اتصال به دیتابیس
    print("\n1. بررسی اتصال به دیتابیس...")
    try:
        conn = get_connection()
        print("   ✅ اتصال برقرار شد")
        conn.close()
    except Exception as e:
        print(f"   ❌ خطا: {e}")
        return
    
    # 2. بررسی وجود جدول
    print("\n2. بررسی وجود جدول meeting_decisions...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meeting_decisions'")
        if cursor.fetchone():
            print("   ✅ جدول وجود دارد")
        else:
            print("   ❌ جدول وجود ندارد!")
            print("   لطفاً ابتدا init_db() را اجرا کنید.")
            conn.close()
            return
        conn.close()
    except Exception as e:
        print(f"   ❌ خطا: {e}")
        return
    
    # 3. بررسی ساختار جدول
    print("\n3. بررسی ساختار جدول...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(meeting_decisions)")
        columns = cursor.fetchall()
        print("   ستون‌های موجود:")
        for col in columns:
            print(f"      - {col[1]}: {col[2]}")
        conn.close()
    except Exception as e:
        print(f"   ❌ خطا: {e}")
        return
    
    # 4. بررسی تکراری نبودن
    print("\n4. بررسی رکورد تکراری...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM meeting_decisions 
            WHERE symbol = ? AND year_solar = ?
        """, ('شسپا', 1403))
        existing = cursor.fetchone()
        if existing:
            print(f"   ⚠️ رکورد تکراری وجود دارد! (id: {existing[0]})")
            print("   در حال حذف رکورد تکراری...")
            cursor.execute("DELETE FROM meeting_decisions WHERE symbol = ? AND year_solar = ?", ('شسپا', 1403))
            conn.commit()
            print("   ✅ رکورد تکراری حذف شد")
        else:
            print("   ✅ هیچ رکورد تکراری وجود ندارد")
        conn.close()
    except Exception as e:
        print(f"   ❌ خطا: {e}")
        return
    
    # 5. اجرای تابع save_meeting_decision
    print("\n5. اجرای save_meeting_decision...")
    try:
        result = save_meeting_decision(test_data)
        if result:
            print("   ✅ ذخیره با موفقیت انجام شد!")
        else:
            print("   ❌ save_meeting_decision مقدار False برگرداند")
            
            # بررسی دقیق‌تر با SQL مستقیم
            print("\n6. تلاش با SQL مستقیم...")
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO meeting_decisions (
                        symbol, year_solar, capital, net_profit, retained_earnings,
                        approved_dividend, eps, dps, dividend_percent,
                        meeting_date, decision_date, is_approved, notes, source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    test_data['symbol'],
                    test_data['year_solar'],
                    test_data['capital'],
                    test_data['net_profit'],
                    test_data['retained_earnings'],
                    test_data['approved_dividend'],
                    test_data['eps'],
                    test_data['dps'],
                    test_data['dividend_percent'],
                    test_data['meeting_date'],
                    test_data['decision_date'],
                    test_data['is_approved'],
                    test_data['notes'],
                    test_data['source']
                ))
                conn.commit()
                print("   ✅ ذخیره با SQL مستقیم موفق بود!")
                conn.close()
            except sqlite3.IntegrityError as e:
                print(f"   ❌ خطای IntegrityError: {e}")
            except Exception as e:
                print(f"   ❌ خطا در SQL مستقیم: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"   ❌ خطا: {e}")
        import traceback
        traceback.print_exc()
    
    # 7. بررسی نهایی
    print("\n7. بررسی نهایی دیتابیس...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM meeting_decisions")
        count = cursor.fetchone()[0]
        print(f"   📊 تعداد کل رکوردها: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM meeting_decisions ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            print("   آخرین رکورد:")
            for i, col in enumerate(cursor.description):
                print(f"      {col[0]}: {row[i]}")
        conn.close()
    except Exception as e:
        print(f"   ❌ خطا: {e}")

if __name__ == "__main__":
    test_save()