# -*- coding: utf-8 -*-
"""
صفحه پایش خودکار کدال - نسخه دیباگ
"""

import streamlit as st
import sys
import os
import traceback

# ============================================================
# تنظیمات صفحه - مهم: باید اولین دستور باشد
# ============================================================
st.set_page_config(
    page_title="پایش خودکار کدال",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# اضافه کردن مسیرها
# ============================================================
# مسیر اصلی پروژه (یک سطح بالاتر از pages)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# نمایش مسیر برای دیباگ
print(f"📁 Project root: {project_root}")

# ============================================================
# ایمپورت‌ها با try-except برای دیباگ
# ============================================================
try:
    from utils.styles import apply_styles
    apply_styles()
    print("✅ styles loaded")
except Exception as e:
    print(f"❌ Error loading styles: {e}")
    st.error(f"خطا در بارگذاری استایل: {e}")

try:
    from services.codal_monitor_service import CodalMonitorService
    print("✅ CodalMonitorService loaded")
except Exception as e:
    print(f"❌ Error loading CodalMonitorService: {e}")
    st.error(f"خطا در بارگذاری سرویس: {e}")
    st.code(traceback.format_exc())

# ============================================================
# نمایش صفحه
# ============================================================
try:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
                color: white; padding: 2rem; border-radius: 12px; 
                margin-bottom: 2rem; text-align: center;">
        <h1 style="color: white !important;">🔍 پایش خودکار کدال</h1>
        <p style="color: #94a3b8 !important;">بررسی تمام نمادهای موجود در دیتابیس</p>
    </div>
    """, unsafe_allow_html=True)
    
    # نمایش اطلاعات برای دیباگ
    with st.expander("🔧 اطلاعات دیباگ", expanded=True):
        st.write("**مسیر پروژه:**", project_root)
        st.write("**مسیرهای جستجو:**", sys.path[:3])
        st.write("**فایل‌های موجود در services:**")
        services_path = os.path.join(project_root, "services")
        if os.path.exists(services_path):
            st.write(os.listdir(services_path))
        else:
            st.warning(f"پوشه services در {services_path} وجود ندارد!")
    
    # ============================================================
    # مقداردهی اولیه
    # ============================================================
    if 'monitor_service' not in st.session_state:
        try:
            st.session_state.monitor_service = CodalMonitorService()
            st.success("✅ سرویس پایش راه‌اندازی شد")
        except Exception as e:
            st.error(f"❌ خطا در راه‌اندازی سرویس: {e}")
            st.code(traceback.format_exc())

    if 'last_check_time' not in st.session_state:
        st.session_state.last_check_time = None

    if 'check_results' not in st.session_state:
        st.session_state.check_results = None

    # ============================================================
    # سایدبار
    # ============================================================
    with st.sidebar:
        st.header("⚙️ تنظیمات")
        
        max_workers = st.number_input(
            "تعداد بررسی همزمان",
            min_value=1,
            max_value=10,
            value=3
        )
        
        st.markdown("---")
        
        if st.button("🚀 شروع بررسی", use_container_width=True):
            with st.spinner("در حال بررسی تمام نمادها..."):
                try:
                    service = st.session_state.monitor_service
                    results = service.check_all_symbols(max_workers=max_workers)
                    st.session_state.check_results = results
                    st.session_state.last_check_time = datetime.now()
                    st.success("✅ بررسی کامل شد!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطا: {e}")
                    st.code(traceback.format_exc())
        
        if st.button("🔄 بروزرسانی", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        if st.button("✅ علامت‌گذاری همه", use_container_width=True):
            try:
                service = st.session_state.monitor_service
                count = service.mark_reports_as_seen()
                if count > 0:
                    st.success(f"✅ {count} گزارش علامت‌گذاری شد")
                    st.rerun()
                else:
                    st.info("هیچ گزارش جدیدی وجود ندارد")
            except Exception as e:
                st.error(f"❌ خطا: {e}")
        
        st.markdown("---")
        
        try:
            stats = st.session_state.monitor_service.get_statistics()
            st.info(f"📊 {stats.get('total_symbols', 0)} نماد در دیتابیس")
            st.metric("🆕 گزارش‌های جدید", stats.get('new_reports', 0))
            if stats.get('last_check'):
                from datetime import datetime
                last_check = datetime.fromisoformat(str(stats['last_check']))
                st.metric("🕐 آخرین بررسی", last_check.strftime("%H:%M:%S"))
        except Exception as e:
            st.error(f"خطا در دریافت آمار: {e}")

    # ============================================================
    # نمایش نتایج
    # ============================================================
    if st.session_state.check_results:
        results = st.session_state.check_results
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 کل نمادها", results.get('total', 0))
        with col2:
            st.metric("✅ بررسی شده", results.get('checked', 0))
        with col3:
            st.metric("🆕 گزارش جدید", results.get('new_reports', 0))
        with col4:
            st.metric("⚠️ خطا", results.get('errors', 0))
        
        new_reports = [d for d in results.get('details', []) if d.get('status') == 'new_report']
        
        if new_reports:
            st.markdown("---")
            st.subheader(f"🎉 گزارش‌های جدید ({len(new_reports)})")
            
            for report in new_reports:
                st.success(f"""
                **📌 {report.get('symbol')}**  
                📋 {report.get('report_type', '')}  
                📅 {report.get('sent_date', '')}  
                📄 {report.get('title', '')}
                """)
        
        errors = [d for d in results.get('details', []) if d.get('status') == 'error']
        if errors:
            st.markdown("---")
            st.subheader(f"⚠️ خطاها ({len(errors)})")
            for error in errors[:5]:
                st.warning(f"**{error.get('symbol')}**: {error.get('message')}")
        
        st.markdown("---")
        st.subheader("📋 تاریخچه")
        
        try:
            history = st.session_state.monitor_service.get_check_history(limit=5)
            if history:
                import pandas as pd
                df = pd.DataFrame([{
                    "تاریخ": h['check_date'][:19],
                    "کل": h['total_symbols'],
                    "جدید": h['new_reports'],
                    "خطا": h['errors']
                } for h in history])
                st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"خطا در نمایش تاریخچه: {e}")

    else:
        try:
            stats = st.session_state.monitor_service.get_statistics()
            if stats.get('total_symbols', 0) > 0:
                st.info(f"👈 {stats.get('total_symbols')} نماد در دیتابیس موجود است. برای شروع، دکمه 'شروع بررسی' را کلیک کنید.")
            else:
                st.warning("⚠️ هیچ نمادی در دیتابیس یافت نشد!")
                
                # نمایش محتوای دیتابیس برای دیباگ
                try:
                    from utils.database import get_connection
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    st.write("**جدول‌های موجود در دیتابیس:**")
                    st.write([t[0] for t in tables])
                    
                    cursor.execute("SELECT COUNT(*) FROM companies")
                    count = cursor.fetchone()[0]
                    st.write(f"**تعداد رکوردها در companies:** {count}")
                    
                    if count > 0:
                        cursor.execute("SELECT symbol FROM companies LIMIT 5")
                        samples = cursor.fetchall()
                        st.write("**نمونه نمادها:**", [s[0] for s in samples])
                    
                    conn.close()
                except Exception as e:
                    st.error(f"خطا در اتصال به دیتابیس: {e}")
        except Exception as e:
            st.error(f"خطا: {e}")

except Exception as e:
    st.error(f"خطای کلی در صفحه: {e}")
    st.code(traceback.format_exc())