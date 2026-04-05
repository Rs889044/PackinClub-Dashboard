"""
database.py — SQLite Database Layer
====================================
Handles schema creation and all CRUD operations for:
Users, Customers, Products, Orders, Invoices, Quotations, Line_Items
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "dashboard.db")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)


def get_connection():
    """Return a new SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ──────────────────────────────────────────────
# SCHEMA INITIALIZATION
# ──────────────────────────────────────────────

def init_db():
    """Create all tables if they don't already exist."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name  TEXT,
            address       TEXT,
            phone         TEXT,
            website       TEXT,
            email         TEXT,
            gst_number    TEXT,
            logo_path     TEXT,
            updated_at    TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS Customers (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id      TEXT UNIQUE NOT NULL,
            name             TEXT NOT NULL,
            address          TEXT,
            phone            TEXT,
            state            TEXT,
            onboarding_date  TEXT DEFAULT (date('now')),
            created_at       TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id   TEXT UNIQUE NOT NULL,
            name         TEXT NOT NULL,
            price        REAL NOT NULL DEFAULT 0,
            created_at   TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS Invoices (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number  TEXT UNIQUE NOT NULL,
            customer_id     INTEGER REFERENCES Customers(id),
            total_amount    REAL DEFAULT 0,
            gst_amount      REAL DEFAULT 0,
            grand_total     REAL DEFAULT 0,
            gst_rate        REAL DEFAULT 18,
            status          TEXT DEFAULT 'active',
            source          TEXT DEFAULT 'invoice',   -- 'invoice' or 'quotation'
            created_at      TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS Quotations (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            quotation_number   TEXT UNIQUE NOT NULL,
            customer_id        INTEGER REFERENCES Customers(id),
            total_amount       REAL DEFAULT 0,
            gst_amount         REAL DEFAULT 0,
            grand_total        REAL DEFAULT 0,
            gst_rate           REAL DEFAULT 18,
            status             TEXT DEFAULT 'draft',   -- 'draft' or 'confirmed'
            created_at         TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number  TEXT UNIQUE NOT NULL,
            source_type   TEXT NOT NULL,      -- 'invoice' or 'quotation'
            source_id     INTEGER NOT NULL,
            customer_id   INTEGER REFERENCES Customers(id),
            total_amount  REAL DEFAULT 0,
            gst_amount    REAL DEFAULT 0,
            grand_total   REAL DEFAULT 0,
            created_at    TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS Line_Items (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            ref_type      TEXT NOT NULL,   -- 'invoice' or 'quotation'
            ref_id        INTEGER NOT NULL,
            product_id    INTEGER REFERENCES Products(id),
            product_name  TEXT,
            price         REAL DEFAULT 0,
            quantity      INTEGER DEFAULT 1,
            subtotal      REAL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# USER PROFILE CRUD
# ──────────────────────────────────────────────

def get_user_profile():
    conn = get_connection()
    row = conn.execute("SELECT * FROM Users ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


def save_user_profile(data: dict):
    """Insert or update the single company profile."""
    conn = get_connection()
    existing = conn.execute("SELECT id FROM Users LIMIT 1").fetchone()
    if existing:
        conn.execute("""
            UPDATE Users SET company_name=?, address=?, phone=?, website=?,
                             email=?, gst_number=?, logo_path=?, updated_at=?
            WHERE id=?
        """, (data["company_name"], data["address"], data["phone"],
              data["website"], data["email"], data["gst_number"],
              data.get("logo_path", ""), datetime.now().isoformat(), existing["id"]))
    else:
        conn.execute("""
            INSERT INTO Users (company_name, address, phone, website, email, gst_number, logo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data["company_name"], data["address"], data["phone"],
              data["website"], data["email"], data["gst_number"],
              data.get("logo_path", "")))
    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# CUSTOMER CRUD
# ──────────────────────────────────────────────

def get_all_customers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Customers ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_customer_by_id(row_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM Customers WHERE id=?", (row_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_customer(data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO Customers (customer_id, name, address, phone, state, onboarding_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data["customer_id"], data["name"], data["address"],
          data["phone"], data["state"], data["onboarding_date"]))
    conn.commit()
    conn.close()


def update_customer(row_id, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE Customers SET customer_id=?, name=?, address=?, phone=?, state=?, onboarding_date=?
        WHERE id=?
    """, (data["customer_id"], data["name"], data["address"],
          data["phone"], data["state"], data["onboarding_date"], row_id))
    conn.commit()
    conn.close()


def delete_customer(row_id):
    conn = get_connection()
    conn.execute("DELETE FROM Customers WHERE id=?", (row_id,))
    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# PRODUCT CRUD
# ──────────────────────────────────────────────

def get_all_products():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM Products ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_product_by_id(row_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM Products WHERE id=?", (row_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO Products (product_id, name, price) VALUES (?, ?, ?)
    """, (data["product_id"], data["name"], data["price"]))
    conn.commit()
    conn.close()


def update_product(row_id, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE Products SET product_id=?, name=?, price=? WHERE id=?
    """, (data["product_id"], data["name"], data["price"], row_id))
    conn.commit()
    conn.close()


def delete_product(row_id):
    conn = get_connection()
    conn.execute("DELETE FROM Products WHERE id=?", (row_id,))
    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# INVOICE CRUD
# ──────────────────────────────────────────────

def get_next_invoice_number():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM Invoices").fetchone()
    conn.close()
    return f"INV-{row['cnt'] + 1:05d}"


def get_all_invoices():
    conn = get_connection()
    rows = conn.execute("""
        SELECT i.*, c.name as customer_name, c.customer_id as cust_code
        FROM Invoices i LEFT JOIN Customers c ON i.customer_id = c.id
        ORDER BY i.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_invoice_by_id(row_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT i.*, c.name as customer_name, c.customer_id as cust_code,
               c.address as customer_address, c.phone as customer_phone,
               c.state as customer_state
        FROM Invoices i LEFT JOIN Customers c ON i.customer_id = c.id
        WHERE i.id=?
    """, (row_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_invoice(customer_id, line_items, gst_rate=18, source="invoice"):
    """Create an invoice record + line items, then push to Orders."""
    total = sum(item["price"] * item["quantity"] for item in line_items)
    gst_amount = round(total * gst_rate / 100, 2)
    grand_total = round(total + gst_amount, 2)
    inv_number = get_next_invoice_number()

    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO Invoices (invoice_number, customer_id, total_amount,
                              gst_amount, grand_total, gst_rate, source)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (inv_number, customer_id, total, gst_amount, grand_total, gst_rate, source))
    inv_id = cur.lastrowid

    for item in line_items:
        conn.execute("""
            INSERT INTO Line_Items (ref_type, ref_id, product_id, product_name, price, quantity, subtotal)
            VALUES ('invoice', ?, ?, ?, ?, ?, ?)
        """, (inv_id, item["product_id"], item["product_name"],
              item["price"], item["quantity"],
              round(item["price"] * item["quantity"], 2)))

    # Auto-push to Orders
    order_number = f"ORD-{inv_id:05d}"
    conn.execute("""
        INSERT INTO Orders (order_number, source_type, source_id, customer_id,
                            total_amount, gst_amount, grand_total)
        VALUES (?, 'invoice', ?, ?, ?, ?, ?)
    """, (order_number, inv_id, customer_id, total, gst_amount, grand_total))

    conn.commit()
    conn.close()
    return inv_id, inv_number


def update_invoice(inv_id, customer_id, line_items, gst_rate=18):
    """Update an existing invoice and its line items."""
    total = sum(item["price"] * item["quantity"] for item in line_items)
    gst_amount = round(total * gst_rate / 100, 2)
    grand_total = round(total + gst_amount, 2)

    conn = get_connection()
    conn.execute("""
        UPDATE Invoices SET customer_id=?, total_amount=?, gst_amount=?,
                            grand_total=?, gst_rate=? WHERE id=?
    """, (customer_id, total, gst_amount, grand_total, gst_rate, inv_id))

    # Replace line items
    conn.execute("DELETE FROM Line_Items WHERE ref_type='invoice' AND ref_id=?", (inv_id,))
    for item in line_items:
        conn.execute("""
            INSERT INTO Line_Items (ref_type, ref_id, product_id, product_name, price, quantity, subtotal)
            VALUES ('invoice', ?, ?, ?, ?, ?, ?)
        """, (inv_id, item["product_id"], item["product_name"],
              item["price"], item["quantity"],
              round(item["price"] * item["quantity"], 2)))

    # Update corresponding order
    conn.execute("""
        UPDATE Orders SET customer_id=?, total_amount=?, gst_amount=?, grand_total=?
        WHERE source_type='invoice' AND source_id=?
    """, (customer_id, total, gst_amount, grand_total, inv_id))

    conn.commit()
    conn.close()


def delete_invoice(inv_id):
    conn = get_connection()
    conn.execute("DELETE FROM Line_Items WHERE ref_type='invoice' AND ref_id=?", (inv_id,))
    conn.execute("DELETE FROM Orders WHERE source_type='invoice' AND source_id=?", (inv_id,))
    conn.execute("DELETE FROM Invoices WHERE id=?", (inv_id,))
    conn.commit()
    conn.close()


def get_line_items(ref_type, ref_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM Line_Items WHERE ref_type=? AND ref_id=?
    """, (ref_type, ref_id)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ──────────────────────────────────────────────
# QUOTATION CRUD
# ──────────────────────────────────────────────

def get_next_quotation_number():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM Quotations").fetchone()
    conn.close()
    return f"QUO-{row['cnt'] + 1:05d}"


def get_all_quotations():
    conn = get_connection()
    rows = conn.execute("""
        SELECT q.*, c.name as customer_name, c.customer_id as cust_code
        FROM Quotations q LEFT JOIN Customers c ON q.customer_id = c.id
        ORDER BY q.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_quotation_by_id(row_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT q.*, c.name as customer_name, c.customer_id as cust_code,
               c.address as customer_address, c.phone as customer_phone,
               c.state as customer_state
        FROM Quotations q LEFT JOIN Customers c ON q.customer_id = c.id
        WHERE q.id=?
    """, (row_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_quotation(customer_id, line_items, gst_rate=18):
    total = sum(item["price"] * item["quantity"] for item in line_items)
    gst_amount = round(total * gst_rate / 100, 2)
    grand_total = round(total + gst_amount, 2)
    quo_number = get_next_quotation_number()

    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO Quotations (quotation_number, customer_id, total_amount,
                                gst_amount, grand_total, gst_rate)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (quo_number, customer_id, total, gst_amount, grand_total, gst_rate))
    quo_id = cur.lastrowid

    for item in line_items:
        conn.execute("""
            INSERT INTO Line_Items (ref_type, ref_id, product_id, product_name, price, quantity, subtotal)
            VALUES ('quotation', ?, ?, ?, ?, ?, ?)
        """, (quo_id, item["product_id"], item["product_name"],
              item["price"], item["quantity"],
              round(item["price"] * item["quantity"], 2)))

    conn.commit()
    conn.close()
    return quo_id, quo_number


def update_quotation(quo_id, customer_id, line_items, gst_rate=18):
    total = sum(item["price"] * item["quantity"] for item in line_items)
    gst_amount = round(total * gst_rate / 100, 2)
    grand_total = round(total + gst_amount, 2)

    conn = get_connection()
    conn.execute("""
        UPDATE Quotations SET customer_id=?, total_amount=?, gst_amount=?,
                              grand_total=?, gst_rate=? WHERE id=?
    """, (customer_id, total, gst_amount, grand_total, gst_rate, quo_id))

    conn.execute("DELETE FROM Line_Items WHERE ref_type='quotation' AND ref_id=?", (quo_id,))
    for item in line_items:
        conn.execute("""
            INSERT INTO Line_Items (ref_type, ref_id, product_id, product_name, price, quantity, subtotal)
            VALUES ('quotation', ?, ?, ?, ?, ?, ?)
        """, (quo_id, item["product_id"], item["product_name"],
              item["price"], item["quantity"],
              round(item["price"] * item["quantity"], 2)))

    conn.commit()
    conn.close()


def delete_quotation(quo_id):
    conn = get_connection()
    conn.execute("DELETE FROM Line_Items WHERE ref_type='quotation' AND ref_id=?", (quo_id,))
    conn.execute("DELETE FROM Quotations WHERE id=?", (quo_id,))
    conn.commit()
    conn.close()


def confirm_quotation(quo_id):
    """Convert a quotation → confirmed. Push to Invoices + Orders."""
    conn = get_connection()
    quo = conn.execute("SELECT * FROM Quotations WHERE id=?", (quo_id,)).fetchone()
    if not quo:
        conn.close()
        return None, None

    # Mark quotation as confirmed
    conn.execute("UPDATE Quotations SET status='confirmed' WHERE id=?", (quo_id,))

    # Create a matching Invoice
    inv_number = get_next_invoice_number()
    cur = conn.execute("""
        INSERT INTO Invoices (invoice_number, customer_id, total_amount,
                              gst_amount, grand_total, gst_rate, source)
        VALUES (?, ?, ?, ?, ?, ?, 'quotation')
    """, (inv_number, quo["customer_id"], quo["total_amount"],
          quo["gst_amount"], quo["grand_total"], quo["gst_rate"]))
    inv_id = cur.lastrowid

    # Copy line items
    items = conn.execute(
        "SELECT * FROM Line_Items WHERE ref_type='quotation' AND ref_id=?", (quo_id,)
    ).fetchall()
    for item in items:
        conn.execute("""
            INSERT INTO Line_Items (ref_type, ref_id, product_id, product_name, price, quantity, subtotal)
            VALUES ('invoice', ?, ?, ?, ?, ?, ?)
        """, (inv_id, item["product_id"], item["product_name"],
              item["price"], item["quantity"], item["subtotal"]))

    # Create Order entry
    order_number = f"ORD-{inv_id:05d}"
    conn.execute("""
        INSERT INTO Orders (order_number, source_type, source_id, customer_id,
                            total_amount, gst_amount, grand_total)
        VALUES (?, 'quotation', ?, ?, ?, ?, ?)
    """, (order_number, quo_id, quo["customer_id"],
          quo["total_amount"], quo["gst_amount"], quo["grand_total"]))

    conn.commit()
    conn.close()
    return inv_id, inv_number


# ──────────────────────────────────────────────
# ORDERS (read-only + export)
# ──────────────────────────────────────────────

def get_all_orders():
    conn = get_connection()
    rows = conn.execute("""
        SELECT o.*, c.name as customer_name, c.customer_id as cust_code
        FROM Orders o LEFT JOIN Customers c ON o.customer_id = c.id
        ORDER BY o.id DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]
