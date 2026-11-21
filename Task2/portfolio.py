
import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import yfinance as yf
except ImportError:
    raise SystemExit("yfinance is not installed. Run:  pip install yfinance")

SUMMARY_FILE = "portfolio_summary.csv"

BG = "#f4f7fb"        # page background
CARD = "#ffffff"      # white cards
HEADER = "#6c5ce7"    
TEXT = "#2d3436"
MUTED = "#636e72"
GREEN = "#00b894"
RED = "#d63031"
BLUE = "#0984e3"
ORANGE = "#e17055"
PURPLE = "#6c5ce7"


# =====================================================================
# PART 1: GETTING THE LIVE PRICE
# =====================================================================
def get_price(ticker):
    """Latest closing price from Yahoo Finance. Returns None if not found."""
    try:
        data = yf.Ticker(ticker).history(period="5d")
        if len(data) > 0:
            return float(data["Close"].iloc[-1])
    except Exception:
        pass
    return None


# =====================================================================
# PART 2: THE PORTFOLIO (a dictionary)
#   {"AAPL": {"buy": 150, "shares": 10, "now": 190}}
# =====================================================================
portfolio = {}


def calculate():
    """Do all the maths. Returns (rows, total_invested, total_value, total_pct)."""
    rows = []
    total_invested = 0
    total_value = 0

    for ticker, info in portfolio.items():
        invested = info["buy"] * info["shares"]      # money you spent
        value = info["now"] * info["shares"]         # what it is worth today
        pct = (value - invested) / invested * 100    # gain or loss in %

        rows.append((ticker, info["shares"], info["buy"], info["now"],
                     invested, value, pct))
        total_invested += invested
        total_value += value

    total_pct = 0
    if total_invested > 0:
        total_pct = (total_value - total_invested) / total_invested * 100
    return rows, total_invested, total_value, total_pct


# =====================================================================
# PART 3: BUTTON ACTIONS
# =====================================================================
def add_stock(event=None):
    ticker = ticker_entry.get().strip().upper()
    try:
        buy = float(buy_entry.get())
        shares = float(shares_entry.get())
        if buy <= 0 or shares <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Oops", "Buy price and shares must be numbers above 0.")
        return
    if not ticker:
        messagebox.showerror("Oops", "Please type a ticker, e.g. AAPL.")
        return

    status.config(text=f"Looking up {ticker} ...")
    window.update()

    price = get_price(ticker)
    if price is None:
        messagebox.showerror("Not found",
                             f"No price found for '{ticker}'.\n"
                             "Check the symbol and your internet connection.")
        status.config(text="")
        return

    # Safety check: did the user make a typo in the buy price?
    if buy > price * 3 or buy < price / 3:
        sure = messagebox.askyesno(
            "Check your buy price",
            f"You typed buy price {buy:,.2f}, but today's price of {ticker} "
            f"is {price:,.2f}.\n\nIs that correct?")
        if not sure:
            status.config(text="")
            return

    portfolio[ticker] = {"buy": buy, "shares": shares, "now": price}
    for box in (ticker_entry, buy_entry, shares_entry):
        box.delete(0, tk.END)
    ticker_entry.focus()
    refresh_screen()


def remove_stock():
    selected = table.selection()
    if not selected:
        messagebox.showinfo("Info", "Click a row in the table first.")
        return
    ticker = str(table.item(selected[0])["values"][0])
    portfolio.pop(ticker, None)
    refresh_screen()


def refresh_prices():
    """Fetch fresh prices for every stock we already have."""
    status.config(text="Refreshing prices ...")
    window.update()
    for ticker, info in portfolio.items():
        price = get_price(ticker)
        if price is not None:
            info["now"] = price
    refresh_screen()


def save_csv():
    if not portfolio:
        messagebox.showinfo("Info", "Add at least one stock first.")
        return
    rows, invested, value, pct = calculate()
    with open(SUMMARY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Ticker", "Shares", "Buy Price", "Current Price",
                         "Invested", "Current Value", "Gain/Loss %"])
        for t, sh, buy, now, inv, val, p in rows:
            writer.writerow([t, sh, buy, now, round(inv, 2),
                             round(val, 2), round(p, 2)])
        writer.writerow(["TOTAL", "", "", "", round(invested, 2),
                         round(value, 2), round(pct, 2)])
    messagebox.showinfo("Saved", f"Saved to {os.path.abspath(SUMMARY_FILE)}")


# =====================================================================
# PART 4: DRAWING THE SCREEN
# =====================================================================
def draw_chart(rows):
    """Simple bar chart: green bar = profit, red bar = loss."""
    chart.delete("all")
    if not rows:
        return
    width = chart.winfo_width()
    height = chart.winfo_height()
    if height < 70:
        return
    mid = height // 2
    biggest = max(abs(r[6]) for r in rows) or 1
    slot = width / len(rows)

    chart.create_line(0, mid, width, mid, fill="#b2bec3")
    for i, r in enumerate(rows):
        x0 = i * slot + slot * 0.25
        x1 = i * slot + slot * 0.75
        bar = r[6] / biggest * (mid - 28)          # bar height in pixels
        color = GREEN if bar >= 0 else "#ff7675"
        chart.create_rectangle(x0, mid, x1, mid - bar, fill=color, outline="")
        label_y = mid - bar - 10 if bar >= 0 else mid - bar + 10
        chart.create_text((x0 + x1) / 2, label_y, text=f"{r[6]:+.1f}%",
                          fill=TEXT, font=("Arial", 9))
        chart.create_text((x0 + x1) / 2, height - 8, text=r[0],
                          fill=MUTED, font=("Arial", 9, "bold"))


def refresh_screen():
    rows, invested, value, pct = calculate()
    profit = value - invested
    color = GREEN if profit >= 0 else RED

    # cards
    invested_val.config(text=f"{invested:,.2f}")
    value_val.config(text=f"{value:,.2f}")
    profit_val.config(text=f"{profit:+,.2f}  ({pct:+.2f}%)", fg=color)

    # table
    table.delete(*table.get_children())
    for t, sh, buy, now, inv, val, p in rows:
        tag = "profit" if p >= 0 else "loss"
        table.insert("", tk.END, tags=(tag,), values=(
            t, f"{sh:g}", f"{buy:.2f}", f"{now:.2f}",
            f"{inv:.2f}", f"{val:.2f}", f"{p:+.2f}%"))

    draw_chart(rows)
    status.config(text="Prices: live from Yahoo Finance" if portfolio else "")


# =====================================================================
# PART 5: BUILDING THE WINDOW
# =====================================================================
window = tk.Tk()
window.title("Portfolio Tracker")
window.geometry("900x640")
window.minsize(760, 520)
window.configure(bg=BG)


def make_button(parent, text, color, action, width=16):
    """A coloured button (made from a Label so the colour works everywhere)."""
    btn = tk.Label(parent, text=text, bg=color, fg="white", width=width,
                   font=("Arial", 10, "bold"), pady=7, cursor="hand2")
    btn.bind("<Button-1>", lambda e: action())
    return btn


# ---- purple header ----
header = tk.Frame(window, bg=HEADER)
header.pack(fill="x")
tk.Label(header, text="\U0001F4C8  My Portfolio Tracker", bg=HEADER, fg="white",
         font=("Arial", 20, "bold")).pack(pady=(10, 0))
tk.Label(header, text="Add your stocks and see if you are in profit or loss",
         bg=HEADER, fg="#dfe6e9", font=("Arial", 10)).pack(pady=(2, 10))

# ---- input row ----
form = tk.Frame(window, bg=CARD, padx=14, pady=12)
form.pack(padx=16, pady=10, fill="x")

for col, name in enumerate(["Ticker (e.g. AAPL)", "Buy price", "Shares"]):
    tk.Label(form, text=name, bg=CARD, fg=MUTED,
             font=("Arial", 9, "bold")).grid(row=0, column=col, sticky="w", padx=4)

entry_style = dict(font=("Arial", 12), bg="#f1f2f6", fg=TEXT, relief="flat",
                   insertbackground=TEXT)
ticker_entry = tk.Entry(form, width=18, **entry_style)
buy_entry = tk.Entry(form, width=12, **entry_style)
shares_entry = tk.Entry(form, width=12, **entry_style)
ticker_entry.grid(row=1, column=0, padx=4, pady=6, ipady=5)
buy_entry.grid(row=1, column=1, padx=4, ipady=5)
shares_entry.grid(row=1, column=2, padx=4, ipady=5)
shares_entry.bind("<Return>", add_stock)      # pressing Enter also adds

make_button(form, "+  Add Stock", GREEN, add_stock, width=14).grid(
    row=1, column=3, padx=10)

# ---- three summary cards (each has a coloured stripe on the left) ----
cards = tk.Frame(window, bg=BG)
cards.pack(padx=16, fill="x")


def make_card(parent, title, column, stripe_color):
    outer = tk.Frame(parent, bg=CARD)
    outer.grid(row=0, column=column, sticky="nsew", padx=5)
    parent.columnconfigure(column, weight=1)
    tk.Frame(outer, bg=stripe_color, width=6).pack(side="left", fill="y")
    inner = tk.Frame(outer, bg=CARD, padx=14, pady=12)
    inner.pack(side="left", fill="both", expand=True)
    tk.Label(inner, text=title, bg=CARD, fg=MUTED,
             font=("Arial", 9, "bold")).pack(anchor="w")
    value_label = tk.Label(inner, text="0.00", bg=CARD, fg=TEXT,
                           font=("Arial", 16, "bold"))
    value_label.pack(anchor="w")
    return value_label


invested_val = make_card(cards, "MONEY INVESTED", 0, BLUE)
value_val = make_card(cards, "WORTH TODAY", 1, ORANGE)
profit_val = make_card(cards, "PROFIT / LOSS", 2, GREEN)

# ---- bottom area first (so it is always visible) ----
status = tk.Label(window, text="", bg=BG, fg=MUTED, font=("Arial", 9))
status.pack(side="bottom", pady=(0, 6))

buttons = tk.Frame(window, bg=BG)
buttons.pack(side="bottom", pady=8)
make_button(buttons, "Remove Selected", RED, remove_stock, 18).pack(side="left", padx=6)
make_button(buttons, "Refresh Prices", BLUE, refresh_prices, 18).pack(side="left", padx=6)
make_button(buttons, "Save to CSV", PURPLE, save_csv, 18).pack(side="left", padx=6)

# ---- table ----
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background=CARD, fieldbackground=CARD,
                foreground=TEXT, rowheight=28, borderwidth=0,
                font=("Arial", 10))
style.configure("Treeview.Heading", background=PURPLE, foreground="white",
                font=("Arial", 10, "bold"), relief="flat")
style.map("Treeview", background=[("selected", "#dfe6fd")],
          foreground=[("selected", TEXT)])

columns = ("Ticker", "Shares", "Buy", "Now", "Invested", "Value", "Gain/Loss")
table = ttk.Treeview(window, columns=columns, show="headings", height=4)
for c in columns:
    table.heading(c, text=c)
    table.column(c, width=100, anchor="center")
table.tag_configure("profit", foreground=GREEN)
table.tag_configure("loss", foreground=RED)
table.pack(padx=16, pady=(12, 8), fill="x")

# ---- chart (takes whatever space is left) ----
chart = tk.Canvas(window, height=110, bg=CARD, highlightthickness=0)
chart.pack(padx=16, pady=(0, 4), fill="both", expand=True)
chart.bind("<Configure>", lambda e: refresh_screen())   # redraw if resized

refresh_screen()
window.mainloop()
