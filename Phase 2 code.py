import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# =========================================================
# DATABASE
# =========================================================

DB = "phase2_inventory.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    price REAL,
    stock INTEGER,
    min_stock INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS purchases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    quantity INTEGER,
    cost REAL,
    vendor TEXT,
    date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice TEXT,
    customer TEXT,
    product TEXT,
    quantity INTEGER,
    price REAL,
    total REAL,
    date TEXT
)
""")

conn.commit()

# Add demo products if database is empty
cursor.execute("SELECT COUNT(*) FROM products")
if cursor.fetchone()[0] == 0:
    demo_products = [
        ("Laptop", 55000, 10, 3),
        ("Keyboard", 1200, 20, 5),
        ("Mouse", 700, 25, 5),
        ("Monitor", 12000, 8, 2),
        ("Printer", 15000, 6, 2)
    ]

    cursor.executemany("""
    INSERT INTO products(name,price,stock,min_stock)
    VALUES(?,?,?,?)
    """, demo_products)

    conn.commit()


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()
root.title("StockPro - Phase 2")
root.geometry("1200x720")
root.configure(bg="#eef2f7")

SIDEBAR = "#172554"
BLUE = "#2563eb"
GREEN = "#16a34a"
ORANGE = "#f97316"
RED = "#dc2626"
TEXT = "#1e293b"

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    rowheight=32,
    font=("Arial", 10)
)

style.configure(
    "Treeview.Heading",
    background="#dbeafe",
    foreground="#1e3a8a",
    font=("Arial", 10, "bold")
)


# =========================================================
# SIDEBAR
# =========================================================

sidebar = tk.Frame(
    root,
    bg=SIDEBAR,
    width=230
)

sidebar.pack(
    side="left",
    fill="y"
)

sidebar.pack_propagate(False)

tk.Label(
    sidebar,
    text="📦 STOCKPRO",
    bg=SIDEBAR,
    fg="white",
    font=("Arial", 22, "bold")
).pack(pady=35)


# =========================================================
# CONTENT
# =========================================================

content = tk.Frame(
    root,
    bg="#eef2f7"
)

content.pack(
    side="right",
    fill="both",
    expand=True
)


def clear_content():

    for widget in content.winfo_children():
        widget.destroy()


def heading(title, subtitle):

    tk.Label(
        content,
        text=title,
        bg="#eef2f7",
        fg=TEXT,
        font=("Arial", 27, "bold")
    ).pack(
        anchor="w",
        padx=30,
        pady=(25, 5)
    )

    tk.Label(
        content,
        text=subtitle,
        bg="#eef2f7",
        fg="#64748b",
        font=("Arial", 11)
    ).pack(
        anchor="w",
        padx=30,
        pady=(0, 20)
    )


def button(parent, text, command, color=BLUE):

    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=color,
        fg="white",
        activebackground=color,
        activeforeground="white",
        relief="flat",
        padx=18,
        pady=10,
        font=("Arial", 10, "bold"),
        cursor="hand2"
    )


# =========================================================
# PHASE 2 DASHBOARD
# =========================================================

def dashboard():

    clear_content()

    heading(
        "📊 Phase 2 Dashboard",
        "Purchase, billing, stock alerts and sales analytics"
    )

    cursor.execute(
        "SELECT COUNT(*) FROM products"
    )
    products = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(stock),0) FROM products"
    )
    stock = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(total),0) FROM sales"
    )
    revenue = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM products
        WHERE stock <= min_stock
    """)

    alerts = cursor.fetchone()[0]

    card_frame = tk.Frame(
        content,
        bg="#eef2f7"
    )

    card_frame.pack(
        fill="x",
        padx=22
    )

    create_card(
        card_frame,
        "📦 Products",
        products,
        BLUE
    )

    create_card(
        card_frame,
        "📈 Stock",
        stock,
        GREEN
    )

    create_card(
        card_frame,
        "💰 Sales",
        f"₹{revenue:,.2f}",
        ORANGE
    )

    create_card(
        card_frame,
        "⚠️ Alerts",
        alerts,
        RED
    )

    # Quick Actions

    panel = tk.Frame(
        content,
        bg="white"
    )

    panel.pack(
        fill="x",
        padx=30,
        pady=25
    )

    tk.Label(
        panel,
        text="⚡ Quick Actions",
        bg="white",
        fg=TEXT,
        font=("Arial", 17, "bold")
    ).pack(
        anchor="w",
        padx=20,
        pady=15
    )

    button(
        panel,
        "🛒 Purchase Stock",
        purchase_page,
        ORANGE
    ).pack(
        side="left",
        padx=20,
        pady=15
    )

    button(
        panel,
        "🧾 Create Bill",
        billing_page,
        RED
    ).pack(
        side="left",
        padx=10
    )

    button(
        panel,
        "⚠️ Stock Alerts",
        alerts_page,
        BLUE
    ).pack(
        side="left",
        padx=10
    )

    button(
        panel,
        "📊 Sales Report",
        reports_page,
        GREEN
    ).pack(
        side="left",
        padx=10
    )


def create_card(parent, title, value, color):

    frame = tk.Frame(
        parent,
        bg="white",
        highlightbackground="#dbe3ef",
        highlightthickness=1
    )

    frame.pack(
        side="left",
        fill="both",
        expand=True,
        padx=8
    )

    tk.Label(
        frame,
        text=title,
        bg="white",
        fg="#64748b",
        font=("Arial", 11)
    ).pack(
        anchor="w",
        padx=20,
        pady=(18, 5)
    )

    tk.Label(
        frame,
        text=value,
        bg="white",
        fg=color,
        font=("Arial", 24, "bold")
    ).pack(
        anchor="w",
        padx=20,
        pady=(0, 18)
    )


# =========================================================
# PURCHASE ORDERS
# =========================================================

def purchase_page():

    clear_content()

    heading(
        "🛒 Purchase Orders",
        "Purchase stock from vendors and automatically update inventory"
    )

    products = cursor.execute(
        "SELECT name FROM products"
    ).fetchall()

    product_names = [
        p[0] for p in products
    ]

    form = tk.LabelFrame(
        content,
        text=" New Purchase Order ",
        bg="white",
        fg=TEXT,
        font=("Arial", 12, "bold"),
        padx=20,
        pady=20
    )

    form.pack(
        fill="x",
        padx=30
    )

    tk.Label(
        form,
        text="Product",
        bg="white"
    ).grid(
        row=0,
        column=0
    )

    product = ttk.Combobox(
        form,
        values=product_names,
        width=25
    )

    product.grid(
        row=1,
        column=0,
        padx=10
    )

    tk.Label(
        form,
        text="Quantity",
        bg="white"
    ).grid(
        row=0,
        column=1
    )

    quantity = tk.Entry(form)

    quantity.grid(
        row=1,
        column=1,
        padx=10
    )

    tk.Label(
        form,
        text="Purchase Cost",
        bg="white"
    ).grid(
        row=0,
        column=2
    )

    cost = tk.Entry(form)

    cost.grid(
        row=1,
        column=2,
        padx=10
    )

    tk.Label(
        form,
        text="Vendor",
        bg="white"
    ).grid(
        row=0,
        column=3
    )

    vendor = tk.Entry(form)

    vendor.grid(
        row=1,
        column=3,
        padx=10
    )

    def save_purchase():

        try:

            p = product.get()
            q = int(quantity.get())
            c = float(cost.get())
            v = vendor.get()

            if q <= 0:
                raise ValueError

            date = datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )

            cursor.execute("""
            INSERT INTO purchases
            (product,quantity,cost,vendor,date)
            VALUES(?,?,?,?,?)
            """, (
                p, q, c, v, date
            ))

            cursor.execute("""
            UPDATE products
            SET stock = stock + ?
            WHERE name = ?
            """, (
                q, p
            ))

            conn.commit()

            messagebox.showinfo(
                "Purchase Successful",
                f"{q} units added to stock."
            )

            purchase_page()

        except:

            messagebox.showerror(
                "Error",
                "Enter valid purchase details."
            )

    button(
        form,
        "➕ Add Purchase",
        save_purchase,
        ORANGE
    ).grid(
        row=2,
        column=0,
        pady=15
    )

    # Purchase History

    frame = tk.Frame(
        content,
        bg="white"
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=20
    )

    tree = ttk.Treeview(
        frame,
        columns=(
            "ID",
            "Product",
            "Quantity",
            "Cost",
            "Vendor",
            "Date"
        ),
        show="headings"
    )

    for c in (
        "ID",
        "Product",
        "Quantity",
        "Cost",
        "Vendor",
        "Date"
    ):
        tree.heading(c, text=c)

    tree.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    cursor.execute("""
    SELECT * FROM purchases
    ORDER BY id DESC
    """)

    for row in cursor.fetchall():

        tree.insert(
            "",
            "end",
            values=row
        )


# =========================================================
# BILLING
# =========================================================

def billing_page():

    clear_content()

    heading(
        "🧾 Billing & Invoice",
        "Generate invoices and automatically reduce product stock"
    )

    products = cursor.execute("""
    SELECT name FROM products
    WHERE stock > 0
    """).fetchall()

    names = [
        p[0] for p in products
    ]

    form = tk.LabelFrame(
        content,
        text=" Create New Invoice ",
        bg="white",
        fg=TEXT,
        font=("Arial", 12, "bold"),
        padx=20,
        pady=20
    )

    form.pack(
        fill="x",
        padx=30
    )

    tk.Label(
        form,
        text="Customer Name",
        bg="white"
    ).grid(
        row=0,
        column=0
    )

    customer = tk.Entry(
        form,
        width=25
    )

    customer.grid(
        row=1,
        column=0,
        padx=10
    )

    tk.Label(
        form,
        text="Product",
        bg="white"
    ).grid(
        row=0,
        column=1
    )

    product = ttk.Combobox(
        form,
        values=names,
        width=25
    )

    product.grid(
        row=1,
        column=1,
        padx=10
    )

    tk.Label(
        form,
        text="Quantity",
        bg="white"
    ).grid(
        row=0,
        column=2
    )

    quantity = tk.Entry(form)

    quantity.grid(
        row=1,
        column=2,
        padx=10
    )

    def generate_bill():

        try:

            customer_name = customer.get()
            product_name = product.get()
            qty = int(quantity.get())

            cursor.execute("""
            SELECT price,stock
            FROM products
            WHERE name=?
            """, (product_name,))

            data = cursor.fetchone()

            if not data:
                raise ValueError

            price = data[0]
            stock = data[1]

            if qty <= 0:
                raise ValueError

            if qty > stock:

                messagebox.showwarning(
                    "Insufficient Stock",
                    f"Only {stock} units available."
                )

                return

            total = price * qty

            invoice = (
                "INV-" +
                datetime.now().strftime(
                    "%Y%m%d%H%M%S"
                )
            )

            date = datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )

            cursor.execute("""
            INSERT INTO sales
            (invoice,customer,product,quantity,
             price,total,date)
            VALUES(?,?,?,?,?,?,?)
            """, (
                invoice,
                customer_name,
                product_name,
                qty,
                price,
                total,
                date
            ))

            cursor.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE name=?
            """, (
                qty,
                product_name
            ))

            conn.commit()

            show_invoice(
                invoice,
                customer_name,
                product_name,
                qty,
                price,
                total,
                date
            )

        except:

            messagebox.showerror(
                "Error",
                "Please enter valid billing details."
            )

    button(
        form,
        "🧾 Generate Invoice",
        generate_bill,
        RED
    ).grid(
        row=2,
        column=0,
        pady=15
    )


# =========================================================
# INVOICE
# =========================================================

def show_invoice(
    invoice,
    customer,
    product,
    quantity,
    price,
    total,
    date
):

    win = tk.Toplevel(root)

    win.title("Invoice " + invoice)

    win.geometry("650x600")

    win.configure(bg="white")

    tk.Label(
        win,
        text="📦 STOCKPRO",
        bg="white",
        fg=SIDEBAR,
        font=("Arial", 25, "bold")
    ).pack(pady=(30, 5))

    tk.Label(
        win,
        text="Automated Inventory & Billing System",
        bg="white",
        fg="#64748b",
        font=("Arial", 11)
    ).pack()

    tk.Frame(
        win,
        bg="#cbd5e1",
        height=2
    ).pack(
        fill="x",
        padx=40,
        pady=20
    )

    tk.Label(
        win,
        text=f"Invoice No: {invoice}",
        bg="white",
        font=("Arial", 11, "bold")
    ).pack(anchor="w", padx=50)

    tk.Label(
        win,
        text=f"Customer: {customer}",
        bg="white"
    ).pack(anchor="w", padx=50)

    tk.Label(
        win,
        text=f"Date: {date}",
        bg="white"
    ).pack(anchor="w", padx=50)

    table = tk.Frame(
        win,
        bg="white"
    )

    table.pack(
        padx=50,
        pady=30
    )

    headers = [
        "Product",
        "Quantity",
        "Price",
        "Total"
    ]

    values = [
        product,
        quantity,
        f"₹{price:.2f}",
        f"₹{total:.2f}"
    ]

    for i in range(4):

        tk.Label(
            table,
            text=headers[i],
            bg="#dbeafe",
            fg="#1e3a8a",
            width=15,
            font=("Arial", 10, "bold")
        ).grid(
            row=0,
            column=i,
            padx=1,
            pady=1
        )

        tk.Label(
            table,
            text=values[i],
            bg="#f8fafc",
            width=15
        ).grid(
            row=1,
            column=i,
            padx=1,
            pady=1
        )

    tk.Label(
        win,
        text=f"GRAND TOTAL: ₹{total:,.2f}",
        bg="white",
        fg=GREEN,
        font=("Arial", 22, "bold")
    ).pack(pady=20)

    button(
        win,
        "✓ Close",
        win.destroy
    ).pack()


# =========================================================
# STOCK ALERTS
# =========================================================

def alerts_page():

    clear_content()

    heading(
        "⚠️ Stock Alerts",
        "Products that have reached their minimum stock level"
    )

    frame = tk.Frame(
        content,
        bg="white"
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=20
    )

    tree = ttk.Treeview(
        frame,
        columns=(
            "Product",
            "Stock",
            "Minimum Stock",
            "Status"
        ),
        show="headings"
    )

    for c in (
        "Product",
        "Stock",
        "Minimum Stock",
        "Status"
    ):
        tree.heading(c, text=c)

    tree.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )

    cursor.execute("""
    SELECT name,stock,min_stock
    FROM products
    WHERE stock <= min_stock
    """)

    rows = cursor.fetchall()

    if not rows:

        tree.insert(
            "",
            "end",
            values=(
                "All Products",
                "-",
                "-",
                "✓ STOCK OK"
            )
        )

    else:

        for row in rows:

            tree.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    row[2],
                    "⚠ LOW STOCK"
                )
            )


# =========================================================
# SALES REPORT
# =========================================================

def reports_page():

    clear_content()

    heading(
        "📊 Sales Report",
        "Revenue and sales performance"
    )

    cursor.execute("""
    SELECT COALESCE(SUM(total),0)
    FROM sales
    """)

    revenue = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM sales
    """)

    invoices = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COALESCE(SUM(quantity),0)
    FROM sales
    """)

    units = cursor.fetchone()[0]

    cards = tk.Frame(
        content,
        bg="#eef2f7"
    )

    cards.pack(
        fill="x",
        padx=22
    )

    create_card(
        cards,
        "💰 Revenue",
        f"₹{revenue:,.2f}",
        GREEN
    )

    create_card(
        cards,
        "🧾 Invoices",
        invoices,
        BLUE
    )

    create_card(
        cards,
        "📦 Units Sold",
        units,
        ORANGE
    )

    frame = tk.Frame(
        content,
        bg="white"
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=25
    )

    tree = ttk.Treeview(
        frame,
        columns=(
            "Invoice",
            "Customer",
            "Product",
            "Quantity",
            "Price",
            "Total",
            "Date"
        ),
        show="headings"
    )

    for c in (
        "Invoice",
        "Customer",
        "Product",
        "Quantity",
        "Price",
        "Total",
        "Date"
    ):
        tree.heading(c, text=c)

    tree.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=15
    )

    cursor.execute("""
    SELECT invoice,customer,product,
           quantity,price,total,date
    FROM sales
    ORDER BY id DESC
    """)

    for row in cursor.fetchall():

        tree.insert(
            "",
            "end",
            values=(
                row[0],
                row[1],
                row[2],
                row[3],
                f"₹{row[4]:.2f}",
                f"₹{row[5]:.2f}",
                row[6]
            )
        )


# =========================================================
# NAVIGATION
# =========================================================

def nav(text, command):

    tk.Button(
        sidebar,
        text=text,
        command=command,
        bg=SIDEBAR,
        fg="white",
        activebackground="#1e40af",
        activeforeground="white",
        relief="flat",
        anchor="w",
        padx=30,
        pady=14,
        font=("Arial", 11),
        cursor="hand2"
    ).pack(fill="x")


nav("📊  Dashboard", dashboard)
nav("🛒  Purchase Orders", purchase_page)
nav("🧾  Billing & Invoice", billing_page)
nav("⚠️  Stock Alerts", alerts_page)
nav("📈  Sales Reports", reports_page)

tk.Frame(
    sidebar,
    bg=SIDEBAR,
    height=30
).pack()

nav(
    "❌  Exit",
    root.destroy
)


# =========================================================
# START
# =========================================================

dashboard()

root.mainloop()

conn.close()