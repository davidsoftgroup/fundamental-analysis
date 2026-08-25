# pages/check_db.py
# -*- coding: utf-8 -*-

import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.database import get_connection, get_all_volumes, init_db
from utils.styles import apply_styles

apply_styles()


# =====================================================
# =============== دکمه‌های اصلی =======================
# =====================================================

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 نمایش همه داده‌های حجم"):
        all_volumes = get_all_volumes()
        
        if all_volumes:
            df = pd.DataFrame(all_volumes, columns=['نماد', 'میانگین حجم', 'حجم امروز', 'قیمت', 'P/E', 'آخرین به‌روزرسانی'])
            st.dataframe(df, height=400)
            st.success(f"✅ {len(df)} رکورد در دیتابیس وجود دارد.")
        else:
            st.warning("⚠️ هیچ داده‌ای در دیتابیس وجود ندارد.")

with col2:
    if st.button("🔄 مقداردهی مجدد دیتابیس"):
        try:
            init_db()
            st.success("✅ دیتابیس با موفقیت مقداردهی شد!")
        except Exception as e:
            st.error(f"❌ خطا در مقداردهی: {e}")

# =====================================================
# =============== بررسی مستقیم با SQL =================
# =====================================================

st.markdown("---")
st.subheader("🔍 بررسی مستقیم با SQL")

if st.button("🔍 بررسی ساختار دیتابیس"):
    conn = get_connection()
    cursor = conn.cursor()
    
    # بررسی وجود جدول
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='monthly_volume'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        st.success("✅ جدول monthly_volume وجود دارد.")
        
        # تعداد رکوردها
        cursor.execute("SELECT COUNT(*) FROM monthly_volume")
        count = cursor.fetchone()[0]
        st.metric("تعداد رکوردها", count)
        
        # نمایش نمونه
        if count > 0:
            cursor.execute("SELECT * FROM monthly_volume LIMIT 5")
            rows = cursor.fetchall()
            
            st.write("نمونه داده‌ها:")
            for row in rows:
                st.write(dict(row))
        else:
            st.warning("جدول خالی است.")
    else:
        st.error("❌ جدول monthly_volume وجود ندارد. لطفاً دکمه 'مقداردهی مجدد دیتابیس' را بزنید.")
    
    conn.close()

# =====================================================
# =============== نمایش همه جداول =====================
# =====================================================

st.markdown("---")
st.subheader("📋 لیست همه جداول")

if st.button("📋 نمایش همه جداول"):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    if tables:
        table_names = [t[0] for t in tables]
        st.write("جداول موجود:")
        for table in table_names:
            # تعداد رکوردهای هر جدول
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            st.write(f"• {table}: {count} رکورد")
    else:
        st.warning("هیچ جدولی در دیتابیس وجود ندارد.")
    
    conn.close()

st.caption("📌 این صفحه برای عیب‌یابی و بررسی دیتابیس استفاده می‌شود.")