# -*- coding: utf-8 -*-
"""
به‌روزرسانی جدول meeting_decisions با فیلدهای جدید
"""

import sys
import os
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection

def update_table():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # بررسی وجود جدول
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='meeting_decisions'")
        if not cursor.fetchone():
            print("❌ جدول meeting_decisions وجود ندارد!")
            print("   لطفاً ابتدا init_db() را اجرا کنید.")
            return
        
        # دریافت ستون‌های موجود
        cursor.execute("PRAGMA table_info(meeting_decisions)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        print("📊 ستون‌های موجود:")
        for col in existing_columns:
            print(f"   - {col}")
        
        # فیلدهای جدید
        new_columns = {
            'retained_earnings': 'REAL',
            'dividend_percent': 'REAL'
        }
        
        print("\n🔄 اضافه کردن ستون‌های جدید...")
        
        added = 0
        for col_name, col_type in new_columns.items():
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE meeting_decisions ADD COLUMN {col_name} {col_type}")
                    print(f"   ✅ ستون {col_name} اضافه شد")
                    added += 1
                except Exception as e:
                    print(f"   ❌ خطا در اضافه کردن {col_name}: {e}")
            else:
                print(f"   ⏭️ ستون {col_name} قبلاً وجود دارد")
        
        conn.commit()
        conn.close()
        
        if added > 0:
            print(f"\n✅ {added} ستون جدید اضافه شد!")
        else:
            print("\n✅ همه ستون‌ها وجود دارند!")
        
        # نمایش ساختار نهایی
        print("\n📋 ساختار نهایی جدول:")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(meeting_decisions)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"   - {col[1]}: {col[2]}")
            conn.close()
        except Exception as e:
            print(f"   ❌ خطا: {e}")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 به‌روزرسانی جدول تصمیمات مجمع")
    print("=" * 60)
    update_table()
    print("\n✅ فرآیند کامل شد!")