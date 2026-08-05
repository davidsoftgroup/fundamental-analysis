# -*- coding: utf-8 -*-
"""دریافت داده از BrsApi"""

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = "B9a9DpJKnmEAbgXDVkzh3kL3f7EzVSsd"
BASE = "https://Api.BrsApi.ir/Tsetmc"

def _session():
    s = requests.Session()
    s.trust_env = False
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
    })
    return s

def fetch_all_symbols(type_=1, timeout=60):
    url = "{}/AllSymbols.php?key={}&type={}".format(BASE, API_KEY, type_)
    s = _session()
    r = s.get(url, timeout=timeout, proxies={"http": None, "https": None}, verify=False)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                return v
    return []

def fetch_one_symbol(symbol, timeout=30):
    url = "{}/Symbol.php?key={}&l18={}".format(BASE, API_KEY, symbol)
    s = _session()
    r = s.get(url, timeout=timeout, proxies={"http": None, "https": None}, verify=False)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and data:
        return data[0]
    if isinstance(data, dict):
        return data
    return None

def find_symbol_in_all(symbol, all_data=None):
    symbol = (symbol or "").strip()
    if all_data is None:
        all_data = fetch_all_symbols()
    for item in all_data:
        if not isinstance(item, dict):
            continue
        if (item.get("l18") or "").strip() == symbol:
            return item
    return None

def market_value_billion_from_item(item):
    """تبدیل mv ریال → میلیارد تومان"""
    if not item:
        return None
    mv = item.get("mv")
    if mv is None:
        return None
    try:
        return float(mv) / 1e9 / 10   # میلیارد ریال → میلیارد تومان
    except Exception:
        return None

def calc_market_value_billion(symbol):
    item = None
    try:
        item = fetch_one_symbol(symbol)
    except Exception:
        item = None

    if not item or item.get("mv") is None:
        item = find_symbol_in_all(symbol)

    if not item:
        raise ValueError("نماد پیدا نشد: {}".format(symbol))

    mv_b = market_value_billion_from_item(item)
    if mv_b is None:
        raise ValueError("ارزش بازار (mv) برای {} موجود نیست".format(symbol))

    return {
        "symbol": item.get("l18") or symbol,
        "name": item.get("l30"),
        "price": item.get("pc") or item.get("pl"),
        "shares": item.get("z"),
        "market_value_rial": item.get("mv"),
        "market_value_billion": mv_b,
        "pe": item.get("pe"),
        "raw": item,
    }

def update_company_market_value(symbol, get_connection):
    result = calc_market_value_billion(symbol)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE companies SET market_value = ? WHERE symbol = ?",
        (result["market_value_billion"], symbol.strip())
    )
    if cur.rowcount == 0:
        cur.execute(
            "UPDATE companies SET market_value = ? WHERE upper(symbol) = upper(?)",
            (result["market_value_billion"], symbol.strip())
        )
    conn.commit()
    conn.close()
    return result

def update_all_companies_market_value(get_connection, get_companies_fn):
    all_data = fetch_all_symbols()
    by_symbol = {}
    for item in all_data:
        if isinstance(item, dict) and item.get("l18"):
            by_symbol[item["l18"].strip()] = item

    companies = get_companies_fn()
    ok, fail = 0, 0
    details = []
    conn = get_connection()
    cur = conn.cursor()

    for c in companies:
        sym = (c["symbol"] or "").strip()
        item = by_symbol.get(sym)
        if not item:
            item = by_symbol.get(sym.replace("ي", "ی").replace("ك", "ک"))
        if not item or item.get("mv") is None:
            fail += 1
            details.append({"نماد": sym, "وضعیت": "پیدا نشد", "ارزش بازار": None})
            continue
        mv_b = market_value_billion_from_item(item)
        cur.execute(
            "UPDATE companies SET market_value = ? WHERE symbol = ?",
            (mv_b, c["symbol"])
        )
        ok += 1
        details.append({"نماد": sym, "وضعیت": "OK", "ارزش بازار": round(mv_b, 1)})

    conn.commit()
    conn.close()
    return ok, fail, details