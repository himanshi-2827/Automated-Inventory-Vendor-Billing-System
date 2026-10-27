import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3, csv
from datetime import datetime

# ================= DATABASE =================
conn = sqlite3.connect("phase3_inventory.db")
conn.executescript("""
CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, price REAL, stock INTEGER, min_stock INTEGER);
CREATE TABLE IF NOT EXISTS purchases(id INTEGER PRIMARY KEY AUTOINCREMENT, product TEXT, quantity INTEGER, cost REAL, vendor TEXT, date TEXT);
CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY AUTOINCREMENT, invoice TEXT, customer TEXT, product TEXT, quantity INTEGER, price REAL, total REAL, date TEXT);
""")


def q(sql, args=()):
    rows = conn.execute(sql, args).fetchall()
    conn.commit()
    return rows


if not q("SELECT 1 FROM products"):
    conn.executemany("INSERT INTO products(name,price,stock,min_stock) VALUES(?,?,?,?)",
                     [("Laptop", 55000, 10, 3), ("Keyboard", 1200, 20, 5), ("Mouse", 700, 25, 5),
                      ("Monitor", 12000, 8, 2), ("Printer", 15000, 6, 2)])
    conn.commit()

# ================= WINDOW & STYLE =================
BG, SIDEBAR, BLUE, GREEN, ORANGE, RED, TEXT, GST = "#eef2f7", "#172554", "#2563eb", "#16a34a", "#f97316", "#dc2626", "#1e293b", 0.18
root = tk.Tk()
root.title("StockPro - Phase 3 (Final)")
root.geometry("1250x740")
root.configure(bg=BG)
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", rowheight=32, font=("Arial", 10))
style.configure("Treeview.Heading", background="#dbeafe", foreground="#1e3a8a", font=("Arial", 10, "bold"))
navs = []


# ================= REUSABLE HELPERS =================
def clear():
    for w in content.winfo_children():
        w.destroy()


def heading(title, sub):
    tk.Label(content, text=title, bg=BG, fg=TEXT, font=("Arial", 27, "bold")).pack(anchor="w", padx=30, pady=(25, 5))
    tk.Label(content, text=sub, bg=BG, fg="#64748b", font=("Arial", 11)).pack(anchor="w", padx=30, pady=(0, 15))


def button(parent, text, cmd, color=BLUE):
    return tk.Button(parent, text=text, command=cmd, bg=color, fg="white", activebackground=color,
                     activeforeground="white", relief="flat", padx=18, pady=10, font=("Arial", 10, "bold"), cursor="hand2")


def card(parent, title, value, color):
    f = tk.Frame(parent, bg="white", highlightbackground="#dbe3ef", highlightthickness=1)
    f.pack(side="left", fill="both", expand=True, padx=8)
    tk.Label(f, text=title, bg="white", fg="#64748b", font=("Arial", 11)).pack(anchor="w", padx=20, pady=(18, 5))
    tk.Label(f, text=value, bg="white", fg=color, font=("Arial", 24, "bold")).pack(anchor="w", padx=20, pady=(0, 18))


def form(title):
    f = tk.LabelFrame(content, text=f" {title} ", bg="white", fg=TEXT, font=("Arial", 12, "bold"), padx=20, pady=15)
    f.pack(fill="x", padx=30)
    return f


def field(parent, label, col, widget=None):
    tk.Label(parent, text=label, bg="white").grid(row=0, column=col, sticky="w", padx=10)
    w = widget or tk.Entry(parent, width=20)
    w.grid(row=1, column=col, padx=10, pady=4)
    return w


def table(parent, cols, rows, search=True):
    """Searchable striped table. Mutate `rows` then call tree.refresh() to redraw."""
    box = tk.Frame(parent, bg="white")
    box.pack(fill="both", expand=True, padx=30, pady=(12, 25))
    key = tk.StringVar()
    if search:
        top = tk.Frame(box, bg="white")
        top.pack(fill="x", padx=15, pady=(12, 0))
        tk.Label(top, text="🔍 Search:", bg="white").pack(side="left")
        tk.Entry(top, textvariable=key, width=30).pack(side="left", padx=8)
    tree = ttk.Treeview(box, columns=cols, show="headings")
    sb = ttk.Scrollbar(box, command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y", pady=12, padx=(0, 10))
    tree.pack(fill="both", expand=True, padx=15, pady=12)
    tree.tag_configure("odd", background="#f1f5f9")
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, anchor="center", width=100)

    def refresh(*_):
        tree.delete(*tree.get_children())
        hits = [r for r in rows if key.get().lower() in " ".join(map(str, r)).lower()]
        for i, r in enumerate(hits):
            tree.insert("", "end", values=r, tags=("odd" if i % 2 else "",))

    key.trace_add("write", refresh)
    tree.refresh = refresh
    refresh()
    return tree


def money(x):
    return f"₹{x:,.2f}"


# ================= DASHBOARD =================
def chart(parent):
    data = q("SELECT name,stock,min_stock FROM products")
    c = tk.Canvas(parent, width=620, height=250, bg="white", highlightthickness=0)
    c.pack(padx=20, pady=(0, 15))
    mx, w = max([d[1] for d in data] + [1]), 620 / max(len(data), 1)
    for i, (n, s, m) in enumerate(data):
        x, h = i * w + w * .2, s / mx * 170
        c.create_rectangle(x, 210 - h, x + w * .6, 210, fill=RED if s <= m else BLUE, outline="")
        c.create_text(x + w * .3, 198 - h, text=s, font=("Arial", 10, "bold"), fill=TEXT)
        c.create_text(x + w * .3, 228, text=n[:10], font=("Arial", 9), fill="#64748b")


def dashboard():
    clear()
    heading("📊 Phase 3 Dashboard", "Live inventory, billing, alerts and analytics")
    n, s = q("SELECT COUNT(*),COALESCE(SUM(stock),0) FROM products")[0]
    rev = q("SELECT COALESCE(SUM(total),0) FROM sales")[0][0]
    low = q("SELECT COUNT(*) FROM products WHERE stock<=min_stock")[0][0]
    row = tk.Frame(content, bg=BG)
    row.pack(fill="x", padx=22)
    for t, v, c in [("📦 Products", n, BLUE), ("📈 Stock", s, GREEN), ("💰 Sales", money(rev), ORANGE), ("⚠️ Alerts", low, RED)]:
        card(row, t, v, c)
    body = tk.Frame(content, bg=BG)
    body.pack(fill="both", expand=True, padx=30, pady=20)
    left = tk.Frame(body, bg="white")
    left.pack(side="left", fill="both", expand=True)
    tk.Label(left, text="📊 Stock Levels  (red = low stock)", bg="white", fg=TEXT, font=("Arial", 15, "bold")).pack(anchor="w", padx=20, pady=15)
    chart(left)
    right = tk.Frame(body, bg="white", padx=25)
    right.pack(side="right", fill="y", padx=(20, 0))
    tk.Label(right, text="⚡ Quick Actions", bg="white", fg=TEXT, font=("Arial", 15, "bold")).pack(pady=15)
    for t, i, c in [("🛒 Purchase Stock", 2, ORANGE), ("🧾 Create Bill", 3, RED), ("⚠️ Stock Alerts", 4, BLUE), ("📊 Sales Report", 5, GREEN)]:
        button(right, t, lambda i=i: navs[i].invoke(), c).pack(fill="x", pady=8)


# ================= PRODUCTS (NEW) =================
def products_page():
    clear()
    heading("📦 Products", "Add, update or delete items — click a row to edit it")
    f = form("Product Details")
    e = [field(f, l, i) for i, l in enumerate(["Name", "Price", "Stock", "Min Stock"])]

    def save():
        try:
            n, p, s, m = e[0].get().strip(), float(e[1].get()), int(e[2].get()), int(e[3].get())
            if not n or min(p, s, m) < 0:
                raise ValueError
            q("INSERT INTO products(name,price,stock,min_stock) VALUES(?,?,?,?) ON CONFLICT(name) DO UPDATE "
              "SET price=excluded.price,stock=excluded.stock,min_stock=excluded.min_stock", (n, p, s, m))
            products_page()
        except ValueError:
            messagebox.showerror("Error", "Enter valid product details.")

    def delete():
        sel = tree.selection()
        if sel and messagebox.askyesno("Delete", "Delete selected product?"):
            q("DELETE FROM products WHERE id=?", (tree.item(sel[0])["values"][0],))
            products_page()

    def pick(_):
        sel = tree.selection()
        if sel:
            for w, v in zip(e, tree.item(sel[0])["values"][1:]):
                w.delete(0, "end")
                w.insert(0, v)

    button(f, "💾 Save / Update", save, GREEN).grid(row=1, column=4, padx=10)
    button(f, "🗑 Delete", delete, RED).grid(row=1, column=5)
    tree = table(content, ("ID", "Name", "Price", "Stock", "Min Stock"), q("SELECT * FROM products"))
    tree.bind("<<TreeviewSelect>>", pick)


# ================= PURCHASE ORDERS =================
def purchase_page():
    clear()
    heading("🛒 Purchase Orders", "Buy stock from vendors and update inventory automatically")
    f = form("New Purchase Order")
    p = field(f, "Product", 0, ttk.Combobox(f, values=[r[0] for r in q("SELECT name FROM products")], width=22, state="readonly"))
    qty, cost, vendor = field(f, "Quantity", 1), field(f, "Purchase Cost", 2), field(f, "Vendor", 3)

    def save():
        try:
            n, c = int(qty.get()), float(cost.get())
            if n <= 0 or not p.get() or not vendor.get().strip():
                raise ValueError
            q("INSERT INTO purchases(product,quantity,cost,vendor,date) VALUES(?,?,?,?,?)",
              (p.get(), n, c, vendor.get().strip(), datetime.now().strftime("%Y-%m-%d %H:%M")))
            q("UPDATE products SET stock=stock+? WHERE name=?", (n, p.get()))
            messagebox.showinfo("Purchase Successful", f"{n} units added to stock.")
            purchase_page()
        except ValueError:
            messagebox.showerror("Error", "Enter valid purchase details.")

    button(f, "➕ Add Purchase", save, ORANGE).grid(row=1, column=4, padx=10)
    table(content, ("ID", "Product", "Quantity", "Cost", "Vendor", "Date"), q("SELECT * FROM purchases ORDER BY id DESC"))


# ================= BILLING WITH CART + GST =================
def billing_page():
    clear()
    heading("🧾 Billing & Invoice", "Build a cart, add GST (18%) and generate invoices")
    f = form("Create New Invoice")
    cust = field(f, "Customer Name", 0)
    prod = field(f, "Product", 1, ttk.Combobox(f, values=[r[0] for r in q("SELECT name FROM products WHERE stock>0")], width=22, state="readonly"))
    qty = field(f, "Quantity", 2)
    cart, total = [], tk.StringVar()

    def update():
        sub = sum(r[3] for r in cart)
        total.set(f"Subtotal {money(sub)}   |   GST 18% {money(sub * GST)}   |   TOTAL {money(sub * (1 + GST))}")
        tree.refresh()

    def add_item():
        try:
            n = int(qty.get())
            price, stock = q("SELECT price,stock FROM products WHERE name=?", (prod.get(),))[0]
            if n <= 0 or n + sum(r[1] for r in cart if r[0] == prod.get()) > stock:
                return messagebox.showwarning("Insufficient Stock", f"Only {stock} units available.")
            cart.append((prod.get(), n, price, price * n))
            qty.delete(0, "end")
            update()
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Select a product and enter a valid quantity.")

    def remove_item():
        if tree.selection():
            cart.pop(tree.index(tree.selection()[0]))
            update()

    def generate():
        if not cart:
            return messagebox.showwarning("Empty Cart", "Add at least one item.")
        now, name = datetime.now(), cust.get().strip() or "Walk-in"
        inv, date = "INV-" + now.strftime("%Y%m%d%H%M%S"), now.strftime("%Y-%m-%d %H:%M")
        for p, n, pr, t in cart:
            q("INSERT INTO sales(invoice,customer,product,quantity,price,total,date) VALUES(?,?,?,?,?,?,?)", (inv, name, p, n, pr, t, date))
            q("UPDATE products SET stock=stock-? WHERE name=?", (n, p))
        items = list(cart)
        billing_page()
        show_invoice(inv, name, items, date)

    button(f, "➕ Add to Cart", add_item, BLUE).grid(row=1, column=3, padx=10)
    button(f, "🗑 Remove Item", remove_item, ORANGE).grid(row=1, column=4)
    button(f, "🧾 Generate Invoice", generate, RED).grid(row=1, column=5, padx=10)
    tree = table(content, ("Product", "Quantity", "Price", "Total"), cart, search=False)
    tk.Label(content, textvariable=total, bg=BG, fg=GREEN, font=("Arial", 16, "bold")).pack(pady=(0, 15))
    update()


# ================= INVOICE =================
def show_invoice(inv, customer, items, date):
    win = tk.Toplevel(root)
    win.title("Invoice " + inv)
    win.geometry("560x640")
    win.configure(bg="white")
    sub = sum(i[3] for i in items)
    tk.Label(win, text="📦 STOCKPRO", bg="white", fg=SIDEBAR, font=("Arial", 25, "bold")).pack(pady=(25, 0))
    tk.Label(win, text="Automated Inventory & Billing System", bg="white", fg="#64748b").pack()
    lines = [f"Invoice No : {inv}", f"Customer   : {customer}", f"Date       : {date}", "",
             f"{'Product':<18}{'Qty':>5}{'Price':>12}{'Total':>14}"]
    lines += [f"{p:<18}{n:>5}{pr:>12,.2f}{t:>14,.2f}" for p, n, pr, t in items]
    lines += ["-" * 49, f"{'Subtotal':<35}{sub:>14,.2f}", f"{'GST (18%)':<35}{sub * GST:>14,.2f}",
              f"{'GRAND TOTAL':<35}{sub * (1 + GST):>14,.2f}"]
    text = "\n".join(lines)
    box = tk.Text(win, font=("Courier New", 10), height=16, width=56, bg="#f8fafc", relief="flat", padx=15, pady=15)
    box.insert("1.0", text)
    box.config(state="disabled")
    box.pack(pady=15)
    tk.Label(win, text=f"GRAND TOTAL: {money(sub * (1 + GST))}", bg="white", fg=GREEN, font=("Arial", 20, "bold")).pack()

    def save():
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=inv + ".txt")
        if path:
            open(path, "w", encoding="utf-8").write("STOCKPRO\n\n" + text)

    bar = tk.Frame(win, bg="white")
    bar.pack(pady=20)
    button(bar, "💾 Save Invoice", save, BLUE).pack(side="left", padx=8)
    button(bar, "✓ Close", win.destroy, GREEN).pack(side="left", padx=8)


# ================= STOCK ALERTS =================
def alerts_page():
    clear()
    heading("⚠️ Stock Alerts", "Products at or below minimum stock, with suggested reorder quantity")
    rows = [(n, s, m, "⚠ LOW STOCK", m * 3 - s) for n, s, m in q("SELECT name,stock,min_stock FROM products WHERE stock<=min_stock")]
    table(content, ("Product", "Stock", "Minimum Stock", "Status", "Reorder Qty"),
          rows or [("All Products", "-", "-", "✓ STOCK OK", "-")])


# ================= SALES REPORT =================
def reports_page():
    clear()
    heading("📊 Sales Report", "Revenue, best seller and full invoice history")
    rev, inv, units = q("SELECT COALESCE(SUM(total),0),COUNT(DISTINCT invoice),COALESCE(SUM(quantity),0) FROM sales")[0]
    top = q("SELECT product FROM sales GROUP BY product ORDER BY SUM(quantity) DESC LIMIT 1")
    row = tk.Frame(content, bg=BG)
    row.pack(fill="x", padx=22)
    for t, v, c in [("💰 Revenue", money(rev), GREEN), ("🧾 Invoices", inv, BLUE), ("📦 Units Sold", units, ORANGE), ("🏆 Best Seller", top[0][0] if top else "-", RED)]:
        card(row, t, v, c)
    rows = [r[:5] + (money(r[5]), r[6]) for r in q("SELECT invoice,customer,product,quantity,price,total,date FROM sales ORDER BY id DESC")]

    def export():
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="sales_report.csv")
        if path:
            with open(path, "w", newline="", encoding="utf-8") as fh:
                csv.writer(fh).writerows([("Invoice", "Customer", "Product", "Qty", "Price", "Total", "Date")] + rows)
            messagebox.showinfo("Exported", "Sales report saved as CSV.")

    button(content, "📤 Export CSV", export, GREEN).pack(anchor="e", padx=30, pady=(15, 0))
    table(content, ("Invoice", "Customer", "Product", "Quantity", "Price", "Total", "Date"), rows)


# ================= NAVIGATION =================
def nav(text, cmd):
    b = tk.Button(sidebar, text=text, bg=SIDEBAR, fg="white", activebackground=BLUE, activeforeground="white",
                  relief="flat", anchor="w", padx=28, pady=14, font=("Arial", 11), cursor="hand2")

    def click():
        for x in navs:
            x.config(bg=SIDEBAR)
        b.config(bg=BLUE)
        cmd()

    b.config(command=click)
    b.pack(fill="x")
    navs.append(b)


def build_app():
    global sidebar, content
    sidebar = tk.Frame(root, bg=SIDEBAR, width=230)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    tk.Label(sidebar, text="📦 STOCKPRO", bg=SIDEBAR, fg="white", font=("Arial", 22, "bold")).pack(pady=(35, 2))
    tk.Label(sidebar, text="Phase 3 • Final", bg=SIDEBAR, fg="#93c5fd").pack(pady=(0, 25))
    content = tk.Frame(root, bg=BG)
    content.pack(side="right", fill="both", expand=True)
    for t, c in [("📊  Dashboard", dashboard), ("📦  Products", products_page), ("🛒  Purchase Orders", purchase_page),
                 ("🧾  Billing & Invoice", billing_page), ("⚠️  Stock Alerts", alerts_page), ("📈  Sales Reports", reports_page)]:
        nav(t, c)
    nav("❌  Exit", root.destroy)
    navs[0].invoke()


build_app()
root.mainloop()
conn.close()