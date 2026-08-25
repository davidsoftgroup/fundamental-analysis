# utils/database.py
# -*- coding: utf-8 -*-

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "fundamental.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("data", exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # جدول شرکت‌ها
    # =====================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            name_fa TEXT,
            industry TEXT,
            market_value REAL,
            rank_in_industry INTEGER,
            fiscal_end_month INTEGER DEFAULT 12,
            fiscal_end_day INTEGER DEFAULT 29,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        cursor.execute("ALTER TABLE companies ADD COLUMN fiscal_end_month INTEGER DEFAULT 12")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE companies ADD COLUMN fiscal_end_day INTEGER DEFAULT 29")
    except:
        pass

    # =====================================================
    # جدول دوره‌های مالی
    # =====================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS periods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            year_solar INTEGER NOT NULL,
            period_type INTEGER NOT NULL,
            end_month INTEGER,
            end_day INTEGER,
            UNIQUE(company_id, year_solar, period_type),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # =====================================================
    # جدول صورت‌های مالی
    # =====================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            period_id INTEGER NOT NULL UNIQUE,
            operating_revenue REAL,
            cogs REAL,
            other_income REAL,
            non_operating_income REAL,
            net_profit REAL,
            comprehensive_income REAL,
            inventory REAL,
            trade_receivables REAL,
            equity REAL,
            current_assets REAL,
            total_assets REAL,
            approved_dividend REAL,
            FOREIGN KEY (period_id) REFERENCES periods(id)
        )
    """)

    try:
        cursor.execute("ALTER TABLE financials ADD COLUMN other_income REAL")
    except:
        pass

    # =====================================================
    # جدول فروش ماهانه
    # =====================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            year_solar INTEGER NOT NULL,
            month INTEGER NOT NULL,
            domestic_sales REAL,
            export_sales REAL,
            total_sales REAL,
            UNIQUE(company_id, year_solar, month),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # =====================================================
    # جدول برآوردها
    # =====================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estimates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            target_year INTEGER NOT NULL,
            estimated_sales REAL,
            estimated_op_profit REAL,
            estimated_net_profit REAL,
            estimated_dividend REAL,
            pe_forward REAL,
            ps_forward REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # =====================================================
    # جدول اقلام درآمد غیرعملیاتی / سایر
    # =====================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS non_operating_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            year_solar INTEGER NOT NULL,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            is_recurring INTEGER DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    """)

    # =====================================================
    # جدول حجم ماهانه
    # =====================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_volume (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            tvol_avg_1m REAL,
            tvol_today REAL,
            pc REAL,
            pe REAL,
            last_update TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (symbol) REFERENCES companies(symbol)
        )
    """)

    try:
        cursor.execute("ALTER TABLE monthly_volume ADD COLUMN pc REAL")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE monthly_volume ADD COLUMN pe REAL")
    except:
        pass

    # =====================================================
    # جدول گزارش‌های کدال
    # =====================================================
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

    # ایندکس‌های جدول codal_reports
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_codal_reports_symbol ON codal_reports(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_codal_reports_sent_date ON codal_reports(sent_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_codal_reports_is_new ON codal_reports(is_new)")

    # =====================================================
    # جدول تاریخچه پایش
    # =====================================================
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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_monitor_history_date ON monitor_history(check_date)")

    # =====================================================
    # جدول تصمیمات مجمع سالیانه
    # =====================================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meeting_decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            year_solar INTEGER NOT NULL,
            capital REAL,
            net_profit REAL,
            retained_earnings REAL,
            approved_dividend REAL,
            eps REAL,
            dps REAL,
            dividend_percent REAL,
            meeting_date TEXT,
            decision_date TEXT,
            is_approved INTEGER DEFAULT 1,
            notes TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(symbol, year_solar)
        )
    """)

    # ایندکس‌های جدول meeting_decisions
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meeting_decisions_symbol ON meeting_decisions(symbol)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meeting_decisions_year ON meeting_decisions(year_solar)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_meeting_decisions_date ON meeting_decisions(meeting_date)")

    conn.commit()
    conn.close()
    print("Database initialized successfully with all tables.")


# =====================================================
# =============== توابع حجم ماهانه ====================
# =====================================================

def get_volume_from_db(symbol):
    """دریافت حجم ماهانه یک نماد از دیتابیس"""
    try:
        conn = get_connection()
        row = conn.execute("""
            SELECT tvol_avg_1m, tvol_today, pc, pe, last_update 
            FROM monthly_volume 
            WHERE symbol = ?
        """, (symbol,)).fetchone()
        conn.close()
        return row
    except Exception as e:
        print(f"Error in get_volume_from_db for {symbol}: {e}")
        return None

def save_volume_to_db(symbol, tvol_avg_1m, tvol_today=None, pc=None, pe=None):
    """ذخیره یا به‌روزرسانی حجم ماهانه در دیتابیس"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        existing = cursor.execute(
            "SELECT id FROM monthly_volume WHERE symbol = ?", 
            (symbol,)
        ).fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE monthly_volume 
                SET tvol_avg_1m = ?, tvol_today = ?, pc = ?, pe = ?, last_update = ?
                WHERE symbol = ?
            ''', (tvol_avg_1m, tvol_today, pc, pe, datetime.now().isoformat(), symbol))
        else:
            cursor.execute('''
                INSERT INTO monthly_volume 
                (symbol, tvol_avg_1m, tvol_today, pc, pe, last_update)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, tvol_avg_1m, tvol_today, pc, pe, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error in save_volume_to_db for {symbol}: {e}")
        return False

def get_all_volumes():
    """دریافت همه داده‌های حجم از دیتابیس"""
    try:
        conn = get_connection()
        rows = conn.execute("""
            SELECT symbol, tvol_avg_1m, tvol_today, pc, pe, last_update 
            FROM monthly_volume 
            ORDER BY symbol
        """).fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error in get_all_volumes: {e}")
        return []

def get_volume_status_from_db(symbol):
    """دریافت وضعیت به‌روزرسانی یک نماد"""
    try:
        row = get_volume_from_db(symbol)
        if row:
            return {
                'updated': True,
                'tvol_avg_1m': row[0],
                'tvol_today': row[1],
                'pc': row[2],
                'pe': row[3],
                'last_update': row[4]
            }
        return {'updated': False}
    except Exception as e:
        print(f"Error in get_volume_status_from_db for {symbol}: {e}")
        return {'updated': False}

def get_volume_stats():
    """دریافت آمار کلی حجم‌های ذخیره‌شده"""
    try:
        conn = get_connection()
        result = conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN tvol_avg_1m IS NOT NULL THEN 1 ELSE 0 END) as updated
            FROM monthly_volume
        """).fetchone()
        conn.close()
        
        if result:
            return {
                'total': result[0] if result[0] is not None else 0,
                'updated': result[1] if result[1] is not None else 0
            }
        return {'total': 0, 'updated': 0}
    except Exception as e:
        print(f"Error in get_volume_stats: {e}")
        return {'total': 0, 'updated': 0}


# =====================================================
# =============== توابع کمکی ===========================
# =====================================================

def get_all_symbols_from_db():
    """دریافت همه نمادها از دیتابیس"""
    try:
        conn = get_connection()
        rows = conn.execute("""
            SELECT symbol, name_fa, industry 
            FROM companies 
            ORDER BY symbol
        """).fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error in get_all_symbols_from_db: {e}")
        return []


# =====================================================
# =============== توابع گزارش‌های کدال ===============
# =====================================================

def get_codal_reports(symbol=None, limit=100):
    """دریافت گزارش‌های کدال از دیتابیس"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute("""
                SELECT * FROM codal_reports 
                WHERE symbol = ?
                ORDER BY sent_date DESC 
                LIMIT ?
            """, (symbol, limit))
        else:
            cursor.execute("""
                SELECT * FROM codal_reports 
                ORDER BY sent_date DESC 
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error in get_codal_reports: {e}")
        return []

def save_codal_report(report_data):
    """ذخیره یک گزارش کدال در دیتابیس"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO codal_reports (
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
            report_data.get('is_new', 1),
            report_data.get('seen', 0)
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error in save_codal_report: {e}")
        return False


# =====================================================
# =============== توابع تصمیمات مجمع سالیانه ==========
# =====================================================

def get_meeting_decisions(symbol=None, year=None, limit=50):
    """
    دریافت تصمیمات مجمع از دیتابیس
    
    Args:
        symbol: نماد شرکت (اختیاری)
        year: سال مالی (اختیاری)
        limit: تعداد رکوردها
    
    Returns:
        list: لیست تصمیمات مجمع
    """
    try:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM meeting_decisions 
            WHERE 1=1
        """
        params = []
        
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        
        if year:
            query += " AND year_solar = ?"
            params.append(year)
        
        query += " ORDER BY year_solar DESC, meeting_date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except Exception as e:
        print(f"Error in get_meeting_decisions: {e}")
        return []

def save_meeting_decision(data):
    """
    ذخیره یک تصمیم مجمع در دیتابیس
    
    Args:
        data: dict شامل اطلاعات تصمیم مجمع
    
    Returns:
        bool: موفقیت یا عدم موفقیت
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # بررسی تکراری نبودن
        cursor.execute("""
            SELECT id FROM meeting_decisions 
            WHERE symbol = ? AND year_solar = ?
        """, (data.get('symbol'), data.get('year_solar')))
        
        existing = cursor.fetchone()
        
        if existing:
            # به‌روزرسانی
            cursor.execute("""
                UPDATE meeting_decisions SET
                    capital = ?,
                    net_profit = ?,
                    retained_earnings = ?,
                    approved_dividend = ?,
                    eps = ?,
                    dps = ?,
                    dividend_percent = ?,
                    meeting_date = ?,
                    decision_date = ?,
                    is_approved = ?,
                    notes = ?,
                    source = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data.get('capital'),
                data.get('net_profit'),
                data.get('retained_earnings'),
                data.get('approved_dividend'),
                data.get('eps'),
                data.get('dps'),
                data.get('dividend_percent'),
                data.get('meeting_date'),
                data.get('decision_date'),
                data.get('is_approved', 1),
                data.get('notes'),
                data.get('source'),
                existing[0]
            ))
        else:
            # درج جدید
            cursor.execute("""
                INSERT INTO meeting_decisions (
                    symbol, year_solar, capital, net_profit, retained_earnings,
                    approved_dividend, eps, dps, dividend_percent,
                    meeting_date, decision_date, is_approved, notes, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('symbol'),
                data.get('year_solar'),
                data.get('capital'),
                data.get('net_profit'),
                data.get('retained_earnings'),
                data.get('approved_dividend'),
                data.get('eps'),
                data.get('dps'),
                data.get('dividend_percent'),
                data.get('meeting_date'),
                data.get('decision_date'),
                data.get('is_approved', 1),
                data.get('notes'),
                data.get('source')
            ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error in save_meeting_decision: {e}")
        return False

def get_meeting_decisions_stats(symbol=None):
    """
    دریافت آمار تصمیمات مجمع
    
    Args:
        symbol: نماد شرکت (اختیاری)
    
    Returns:
        dict: آمار
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM meeting_decisions"
        params = []
        
        if symbol:
            query += " WHERE symbol = ?"
            params.append(symbol)
        
        cursor.execute(query, params)
        total = cursor.fetchone()[0]
        
        if symbol:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    MAX(year_solar) as last_year,
                    AVG(eps) as avg_eps,
                    AVG(dps) as avg_dps,
                    AVG(dividend_percent) as avg_percent
                FROM meeting_decisions 
                WHERE symbol = ?
            """, (symbol,))
            stats = cursor.fetchone()
            
            result = {
                'total': total,
                'last_year': stats[1] if stats else None,
                'avg_eps': stats[2] if stats else 0,
                'avg_dps': stats[3] if stats else 0,
                'avg_percent': stats[4] if stats else 0
            }
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT symbol) as symbols_count
                FROM meeting_decisions
            """)
            stats = cursor.fetchone()
            result = {
                'total': stats[0] if stats else 0,
                'symbols': stats[1] if stats else 0
            }
        
        conn.close()
        return result
        
    except Exception as e:
        print(f"Error in get_meeting_decisions_stats: {e}")
        return {'total': 0}

def delete_meeting_decision(symbol, year_solar):
    """حذف یک تصمیم مجمع"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM meeting_decisions 
            WHERE symbol = ? AND year_solar = ?
        """, (symbol, year_solar))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
        
    except Exception as e:
        print(f"Error in delete_meeting_decision: {e}")
        return False


if __name__ == "__main__":
    init_db()