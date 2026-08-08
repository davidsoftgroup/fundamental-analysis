# test_codal.py
import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# جستجوی نماد
symbol = "شپنا"
url = f"https://search.codal.ir/api/search/v2/q?Symbol={symbol}"

print(f"🔍 در حال جستجوی نماد {symbol}...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"✅ داده دریافت شد!")
    print(f"تعداد اطلاعیه‌ها: {len(data.get('letters', []))}")
    
    # نمایش اولین اطلاعیه
    letters = data.get('letters', [])
    if letters:
        first = letters[0]
        print(f"\n📄 آخرین اطلاعیه:")
        print(f"عنوان: {first.get('title', 'بدون عنوان')}")
        print(f"تاریخ انتشار: {first.get('publishDateTime', '')}")
        print(f"ناشر: {first.get('issuer', {}).get('name', '')}")
else:
    print(f"❌ خطا: {response.status_code}")