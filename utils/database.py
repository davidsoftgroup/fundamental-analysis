import sqlite3
import os

DB_PATH = os.path.join("data", "fundamental.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("data", exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    # جدول شرکت‌ها
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

    # جدول دوره‌های مالی
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

    # جدول صورت‌های مالی
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

    # جدول فروش ماهانه
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

    # جدول برآوردها
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

    # جدول اقلام درآمد غیرعملیاتی / سایر
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

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()