import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "utils")))

st.set_page_config(
    page_title="تحلیل بنیادی بورس",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.styles import apply_styles
apply_styles()

st.title("سامانه تحلیل بنیادی بورس")
# ... بقیه
st.markdown("---")

st.markdown("""
### خوش آمدید

این سامانه برای تحلیل بنیادی شرکت‌های بورسی طراحی شده است.

از منوی سمت راست صفحات زیر را انتخاب کنید:

- **داشبورد**: خلاصه وضعیت و شاخص‌های کلیدی
- **صورت‌های مالی**: جزئیات درآمد، سود و ترازنامه
- **برآوردها**: پیش‌بینی فروش و سود سال جاری
""")

st.info("لطفاً از منوی سمت راست یک صفحه را انتخاب کنید.")